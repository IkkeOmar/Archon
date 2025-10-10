#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_SECRET_TOKEN = os.getenv("TELEGRAM_SECRET_TOKEN")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        print("Missing TELEGRAM_BOT_TOKEN", file=sys.stderr)
        sys.exit(1)
    if not TELEGRAM_SECRET_TOKEN:
        print("Missing TELEGRAM_SECRET_TOKEN", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    payload = {
        "url": f"{BASE_URL}/webhook/telegram",
        "secret_token": TELEGRAM_SECRET_TOKEN,
    }
    response = httpx.post(url, json=payload, timeout=10)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
