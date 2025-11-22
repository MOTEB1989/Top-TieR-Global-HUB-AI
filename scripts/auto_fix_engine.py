#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto-Fix Engine (Planning Layer)

This script does NOT directly mutate the repository.
Instead, it:
- Reads the latest health report file if present.
- Analyses common issues (missing env, unreachable services).
- Prints a list of suggested remediation actions as Markdown.
Later, Codex or a human can turn these suggestions into actual patches.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List


HEALTH_REPORT_PATH = Path("health_reports/latest_health_report.md")


def load_health_report() -> str:
    if HEALTH_REPORT_PATH.is_file():
        return HEALTH_REPORT_PATH.read_text(encoding="utf-8", errors="ignore")
    return ""


def suggest_actions(report: str) -> List[str]:
    suggestions: List[str] = []

    if "No .env file found" in report or "ملف .env غير موجود" in report:
        suggestions.append("- إنشاء ملف `.env` استناداً إلى `.env.example` وتعبئة مفاتيح الـ API.")

    if "OpenAI integration NOT configured" in report:
        suggestions.append("- ضبط متغير البيئة `OPENAI_API_KEY` في `.env` أو في Secrets الخاصة بـ GitHub.")

    if "Groq integration NOT configured" in report:
        suggestions.append("- ضبط متغير البيئة `GROQ_API_KEY` في `.env` أو في Secrets.")

    if "Rust Core غير متاح" in report or "API Gateway غير متاح" in report:
        suggestions.append("- التحقق من تشغيل `docker compose up --build` ومتابعة سجلات الخدمات الأساسية.")

    if "Streamlit Web UI غير متاح" in report:
        suggestions.append("- التأكد من أن خدمة واجهة Streamlit مفعّلة في ملفات الـ Docker Compose.")

    if not suggestions:
        suggestions.append("- لم يتم اكتشاف مشاكل نمطية، راجع التقرير يدويًا لمزيد من التفاصيل.")

    return suggestions


def build_suggestions_markdown(report: str) -> str:
    lines: List[str] = []
    lines.append("# 🔧 Auto-Fix Suggestions\n")
    if report:
        lines.append("## مقتطف من التقرير الصحي الأخير\n")
        lines.append("```markdown")
        lines.append(report[:2000])
        lines.append("```")
    lines.append("\n## خطوات مقترحة\n")
    for s in suggest_actions(report):
        lines.append(s)
    return "\n".join(lines)


def main() -> None:
    report = load_health_report()
    md = build_suggestions_markdown(report)
    print(md)


if __name__ == "__main__":
    main()

