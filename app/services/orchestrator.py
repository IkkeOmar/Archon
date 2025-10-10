from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.core.config import get_required_slots
from app.core.security import rate_limiter
from app.services.openai_client import NLUClient, build_nlu_client
from app.services.meta import MetaSender
from app.services.telegram import TelegramSender
from app.storage.db import AsyncSessionLocal
from app.storage.repositories import (
    clear_session,
    create_booking,
    get_session,
    upsert_session,
)
from app.storage.sheets import SheetsClient, build_sheets_client
from app.utils.time import utcnow

logger = logging.getLogger(__name__)

DEFAULT_REPLY = "Sorry, I didn't quite get that. Could you rephrase?"
CONFIRM_TEMPLATE = "Thanks {name}. Your {service} on {date} at {time} is booked. We’ll contact you at {phone}."


class Orchestrator:
    def __init__(
        self,
        *,
        session_factory=AsyncSessionLocal,
        nlu_client: Optional[NLUClient] = None,
        meta_sender: Optional[MetaSender] = None,
        telegram_sender: Optional[TelegramSender] = None,
        sheets_client: Optional[SheetsClient] = None,
    ) -> None:
        self.session_factory = session_factory
        self.nlu = nlu_client or build_nlu_client()
        self.meta_sender = meta_sender or MetaSender()
        self.telegram_sender = telegram_sender or TelegramSender()
        self.sheets_client = sheets_client or build_sheets_client()
        self.required_slots = get_required_slots()

    async def process_message(self, platform: str, sender_id: str, text: str) -> None:
        if not rate_limiter.hit(platform, sender_id):
            await self._send(platform, sender_id, "You are sending messages too quickly. Please wait a moment.")
            return

        async with self.session_factory() as session:
            state = await get_session(session, platform, sender_id)
            current_filled = state.filled if state and state.filled else {}
            context = {
                "filled": current_filled,
                "required": self.required_slots,
            }
            parsed = await self._call_nlu(text, context)
            intent = parsed.get("intent", "other")
            model_filled = parsed.get("filled", {}) or {}
            reply = parsed.get("reply") or DEFAULT_REPLY

            merged = {k: v for k, v in current_filled.items() if v}
            for key, value in model_filled.items():
                if value:
                    merged[key] = value

            missing = [slot for slot in self.required_slots if not merged.get(slot)]

            if intent == "booking":
                if missing:
                    await upsert_session(session, platform, sender_id, merged)
                    await session.commit()
                    missing_text = ", ".join(missing)
                    nudge = f"Could you share your {missing_text}?"
                    await self._send(platform, sender_id, nudge)
                    return

                booking = await create_booking(
                    session,
                    platform=platform,
                    user_id=sender_id,
                    name=merged["name"],
                    service=merged["service"],
                    date=merged["date"],
                    time=merged["time"],
                    phone=merged["phone"],
                )
                await clear_session(session, platform, sender_id)
                await session.commit()
                await self._mirror_booking(booking)
                confirmation = CONFIRM_TEMPLATE.format(**merged)
                await self._send(platform, sender_id, confirmation)
                return

            await upsert_session(session, platform, sender_id, merged)
            await session.commit()
            await self._send(platform, sender_id, reply)

    async def _mirror_booking(self, booking) -> None:
        if self.sheets_client is None:
            return
        try:
            self.sheets_client.ensure_header()
            row = [
                utcnow().isoformat(),
                booking.name,
                booking.service,
                booking.date,
                booking.time,
                booking.phone,
            ]
            self.sheets_client.append_booking(row)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to mirror booking to Google Sheets: %s", exc)

    async def _call_nlu(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            parsed = await self.nlu.parse(text, context)
        except Exception as exc:
            logger.exception("NLU call failed: %s", exc)
            return {
                "intent": "other",
                "filled": {},
                "missing": self.required_slots,
                "reply": DEFAULT_REPLY,
            }
        return self._normalize_nlu_output(parsed)

    def _normalize_nlu_output(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        try:
            intent = parsed.get("intent", "other")
            filled = parsed.get("filled") or {}
            missing = parsed.get("missing") or []
            reply = parsed.get("reply") or DEFAULT_REPLY
            valid_missing = [slot for slot in missing if slot in self.required_slots]
            clean_filled = {k: v for k, v in filled.items() if k in self.required_slots and isinstance(v, str) and v.strip()}
            return {
                "intent": intent,
                "filled": clean_filled,
                "missing": valid_missing,
                "reply": reply,
            }
        except Exception as exc:
            logger.exception("Failed to normalize NLU output: %s", exc)
            return {
                "intent": "other",
                "filled": {},
                "missing": self.required_slots,
                "reply": DEFAULT_REPLY,
            }

    async def _send(self, platform: str, sender_id: str, message: str) -> None:
        if platform in {"messenger", "instagram"}:
            await self.meta_sender.send_message(platform, sender_id, message)
        elif platform == "telegram":
            await self.telegram_sender.send_message(sender_id, message)
        else:
            logger.warning("Unknown platform for sending", extra={"props": {"platform": platform}})


def build_orchestrator() -> Orchestrator:
    return Orchestrator()
