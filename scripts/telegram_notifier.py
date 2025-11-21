#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Lightweight Telegram notifier used by the auto-diagnose workflow."""

import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def notify_telegram(message: str) -> bool:
    """Send a Markdown-formatted message to the configured Telegram chat.

    Returns True when the message was sent, False when Telegram is not configured
    or the request fails.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram not configured.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}

    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print("Telegram notify failed:", exc)
        return False


if __name__ == "__main__":
    notify_telegram("🤖 Test message from auto-diagnose script.")
