from __future__ import annotations

import httpx
import pytest

from app.core.config import get_settings
from app.services.meta import MetaSender
from app.services.telegram import TelegramSender


@pytest.mark.asyncio
async def test_meta_sender_messenger(monkeypatch):
    monkeypatch.setenv("META_PAGE_ACCESS_TOKEN", "token")
    monkeypatch.setenv("META_APP_SECRET", "secret")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    sender = MetaSender()
    called = {}

    async def fake_post(self, url, params=None, json=None):  # type: ignore[override]
        called["url"] = url
        called["params"] = params
        called["json"] = json
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    await sender.send_message("messenger", "123", "hi")
    assert called["url"].endswith("/me/messages")
    assert called["json"]["recipient"]["id"] == "123"


@pytest.mark.asyncio
async def test_meta_sender_instagram(monkeypatch):
    monkeypatch.setenv("META_PAGE_ACCESS_TOKEN", "token")
    monkeypatch.setenv("META_APP_SECRET", "secret")
    monkeypatch.setenv("IG_BUSINESS_ID", "biz")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    sender = MetaSender()
    called = {}

    async def fake_post(self, url, params=None, json=None):  # type: ignore[override]
        called["url"] = url
        called["json"] = json
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    await sender.send_message("instagram", "abc", "hello")
    assert "/messages" in called["url"]
    assert called["json"]["messaging_product"] == "instagram"


@pytest.mark.asyncio
async def test_telegram_sender(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "telegram-token")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    sender = TelegramSender()
    called = {}

    async def fake_post(self, url, json=None):  # type: ignore[override]
        called["url"] = url
        called["json"] = json
        return httpx.Response(200)

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    await sender.send_message("555", "hello")
    assert "sendMessage" in called["url"]
    assert called["json"]["chat_id"] == "555"
