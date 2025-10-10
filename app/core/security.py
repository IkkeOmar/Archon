from __future__ import annotations

import hmac
import logging
import time
from hashlib import sha256
from typing import Dict, Tuple

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._storage: Dict[Tuple[str, str], Tuple[int, int]] = {}

    def hit(self, platform: str, user_id: str) -> bool:
        key = (platform, user_id)
        now = int(time.time())
        window_start = now - self.window_seconds
        count, timestamp = self._storage.get(key, (0, now))
        if timestamp < window_start:
            count = 0
        count += 1
        self._storage[key] = (count, now)
        if count > self.max_requests:
            logger.warning("rate limit exceeded", extra={"props": {"platform": platform, "user_id": user_id}})
            return False
        return True


def verify_meta_signature(raw_body: bytes, signature_header: str | None) -> bool:
    if not signature_header:
        return False
    try:
        method, signature = signature_header.split("=", 1)
    except ValueError:
        return False
    if method != "sha256":
        return False
    secret = get_settings().meta_app_secret_value.encode("utf-8")
    computed = hmac.new(secret, raw_body, sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


def verify_telegram_token(provided: str | None) -> bool:
    if provided is None:
        return False
    expected = get_settings().telegram_secret_token_value
    return provided == expected


rate_limiter = RateLimiter(
    max_requests=get_settings().rate_limit_max_requests,
    window_seconds=get_settings().rate_limit_window_seconds,
)
