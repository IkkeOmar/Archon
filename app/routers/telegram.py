from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import verify_telegram_token
from app.services.orchestrator import Orchestrator, build_orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


def get_orchestrator() -> Orchestrator:
    return build_orchestrator()


@router.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> dict[str, str]:
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not verify_telegram_token(secret):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid secret token")

    payload: Any = await request.json()
    message = payload.get("message") or payload.get("edited_message")
    if not message:
        return {"status": "ignored"}
    chat = message.get("chat", {})
    sender_id = chat.get("id")
    text = message.get("text")
    if sender_id is None or text is None:
        return {"status": "ignored"}
    await orchestrator.process_message("telegram", str(sender_id), text)
    return {"status": "ok"}
