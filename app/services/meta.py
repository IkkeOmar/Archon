from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MetaSender:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=10)

    async def send_message(self, platform: str, recipient_id: str, message: str) -> None:
        if platform == "messenger":
            url = "https://graph.facebook.com/v20.0/me/messages"
            params = {"access_token": self.settings.meta_page_access_token_value}
            payload: Dict[str, Any] = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
            }
        elif platform == "instagram":
            url = f"https://graph.facebook.com/v20.0/{self.settings.ig_business_id}/messages"
            params = {"access_token": self.settings.meta_page_access_token_value}
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
                "messaging_product": "instagram",
            }
        else:
            logger.warning("Unsupported Meta platform", extra={"props": {"platform": platform}})
            return

        response = await self.client.post(url, params=params, json=payload)
        if response.status_code >= 400:
            logger.error(
                "Meta send failed", extra={"props": {"status": response.status_code, "body": response.text}}
            )


def normalize_meta_events(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    entry_list = payload.get("entry", [])
    for entry in entry_list:
        messaging = entry.get("messaging", [])
        for message in messaging:
            sender_id = message.get("sender", {}).get("id")
            text = message.get("message", {}).get("text")
            if sender_id and text:
                events.append({"platform": "messenger", "sender_id": sender_id, "text": text})
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            if value.get("messaging_product") != "instagram":
                continue
            messages = value.get("messages", [])
            for msg in messages:
                sender_id = msg.get("from", {}).get("id")
                text = msg.get("text")
                if isinstance(text, dict):
                    text = text.get("body")
                if sender_id and isinstance(text, str):
                    events.append({"platform": "instagram", "sender_id": sender_id, "text": text})
    return events
