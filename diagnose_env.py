#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnose_env.py
يفحص البيئة الحالية ويتأكد من وجود المفاتيح (secrets) اللازمة،
ويحاول اختبار الاتصال بالواجهات البرمجية المحددة دون طباعة القيم الحساسة.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Iterable, List, Sequence

import requests

# أسماء المتغيرات التي نتوقع وجودها (قم بتعديل القائمة وفقاً لاحتياجاتك)
EXPECTED_SECRETS: Sequence[str] = (
    "GIT_TOKEN",
    "CODEX_API_KEY",
    "OPENAI_API_KEY",
)

# واجهات اختبار الاتصال (يمكن تعديلها أو تعطيلها)
CHECK_ENDPOINTS: Dict[str, str] = {
    "codex": "https://api.lexcode.ai/v1/lex/run",
    "github": "https://api.github.com",
    "openai": "https://api.openai.com/v1/models",
}


def check_env_vars(expected: Iterable[str]) -> List[str]:
    """Return a list of missing environment variables after reporting their status."""
    print("🔍 فحص المتغيرات البيئية:")
    missing: List[str] = []
    for var in expected:
        if os.getenv(var):
            print(f"✅ {var} موجود")
        else:
            print(f"⚠️  {var} غير موجود")
            missing.append(var)
    return missing


def check_api_connectivity(endpoints: Dict[str, str]) -> None:
    """Attempt to reach each endpoint and report the HTTP status."""
    print("\n🌐 اختبار الاتصال بالواجهات:")
    for name, url in endpoints.items():
        try:
            resp = requests.get(url, timeout=5)
        except Exception as exc:  # noqa: BLE001 - broad to report connectivity issues
            print(f"❌ {name} فشل الاتصال: {exc}")
            continue

        status_code = resp.status_code
        if 200 <= status_code < 400:
            print(f"✅ {name} متاح ({status_code})")
        else:
            print(f"⚠️  {name} يُرجع حالة غير طبيعية ({status_code})")


def validate_missing(missing: Sequence[str]) -> None:
    """Print a summary of missing secrets."""
    if not missing:
        print("\n✅ جميع الأسرار المطلوبة متوفّرة.")
        return

    print("\n🚫 المتغيرات المفقودة:")
    for item in missing:
        print(f" - {item}")
    print("يرجى إضافتها في إعدادات GitHub → Secrets.")


def main(argv: Sequence[str] | None = None) -> int:
    """Entrypoint for the diagnostic tool."""
    _ = argv  # Currently unused but reserved for future CLI options.

    missing = check_env_vars(EXPECTED_SECRETS)
    check_api_connectivity(CHECK_ENDPOINTS)
    validate_missing(missing)
    print("\nانتهى التشخيص.")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
