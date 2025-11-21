#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main entrypoint for auto diagnosis, auto-fix, and notifications."""

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from auto_fix_engine import auto_fix_everything
from telegram_notifier import notify_telegram
import system_health_and_codex_notify as base_report


def run():
    # 1) التشخيص
    report = base_report.build_markdown_report()

    # 2) إصلاح تلقائي
    fixes = auto_fix_everything()

    final_report = (
        "# 🧠 Auto Diagnostic + Auto Fix Report\n\n"
        "## 📄 Health Report\n"
        f"{report}\n\n"
        "## 🔧 Auto Fixes Applied\n"
        f"{fixes}\n\n"
    )

    print(final_report)

    # 3) Telegram
    notify_telegram("🚨 *System Check Completed*\n\n" + fixes)

    # 4) Codex notification (CI only)
    base_report.notify_codex_if_ci(final_report)


if __name__ == "__main__":
    run()
