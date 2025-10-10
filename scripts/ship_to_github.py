#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "IkkeOmar/appointment-bot-meta-telegram")
AUTHOR_NAME = os.getenv("GIT_AUTHOR_NAME", "codex-bot")
AUTHOR_EMAIL = os.getenv("GIT_AUTHOR_EMAIL", "codex-bot@example.com")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        sys.exit(1)

    run(["git", "init"])
    run(["git", "config", "user.name", AUTHOR_NAME])
    run(["git", "config", "user.email", AUTHOR_EMAIL])
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", "feat: appointment bot (Meta + Telegram)"])
    run(["git", "branch", "-M", "main"])
    remote = f"https://oauth2:{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
    run(["git", "remote", "add", "origin", remote])
    run(["git", "push", "-u", "origin", "main"])


if __name__ == "__main__":
    main()
