#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram notifier for system diagnostics.

Usage:
- Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
- Exposes a simple send_message(text: str) function.
- Can be invoked as a CLI tool:
    python scripts/telegram_notifier.py "Message here"
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import requests


def send_message(text: str, parse_mode: Optional[str] = "Markdown") -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram env vars missing (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID); skipping.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Telegram notification sent.")
    except Exception as e:  # noqa: BLE001
        print(f"Failed to send Telegram notification: {e}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python telegram_notifier.py 'message text'")
        return
    message = " ".join(sys.argv[1:])
    send_message(message)


if __name__ == "__main__":
    main()

