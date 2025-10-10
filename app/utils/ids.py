from __future__ import annotations

from typing import Tuple


def get_platform_and_user(platform: str, sender_id: str) -> Tuple[str, str]:
    return platform, sender_id
