from __future__ import annotations

import hmac
from hashlib import sha256

from app.core.security import verify_meta_signature, verify_telegram_token
from app.core.config import get_settings


def test_verify_meta_signature_valid(monkeypatch):
    secret = "secret"
    monkeypatch.setenv("META_APP_SECRET", secret)
    get_settings.cache_clear()  # type: ignore[attr-defined]
    body = b'{"test": "ok"}'
    signature = hmac.new(secret.encode(), body, sha256).hexdigest()
    header = f"sha256={signature}"
    assert verify_meta_signature(body, header) is True


def test_verify_meta_signature_invalid(monkeypatch):
    monkeypatch.setenv("META_APP_SECRET", "secret")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    body = b"payload"
    assert verify_meta_signature(body, "sha256=bad") is False
    assert verify_meta_signature(body, None) is False
    assert verify_meta_signature(body, "md5=abc") is False


def test_verify_telegram_token(monkeypatch):
    monkeypatch.setenv("TELEGRAM_SECRET_TOKEN", "token123")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    assert verify_telegram_token("token123") is True
    assert verify_telegram_token("other") is False
