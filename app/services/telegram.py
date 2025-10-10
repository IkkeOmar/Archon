from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TelegramSender:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=10)

    async def send_message(self, chat_id: str, message: str) -> None:
        token = self.settings.telegram_bot_token_value
        if not token:
            logger.warning("Telegram token not configured")
            return
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = await self.client.post(url, json=payload)
        if response.status_code >= 400:
            logger.error(
                "Telegram send failed", extra={"props": {"status": response.status_code, "body": response.text}}
            )
