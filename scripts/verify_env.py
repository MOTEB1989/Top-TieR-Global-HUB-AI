#!/usr/bin/env python3
import os
import sys

REQUIRED_NON_EMPTY = [
    "TELEGRAM_BOT_TOKEN",
    "OPENAI_API_KEY",
    "GITHUB_REPO",
    "OPENAI_MODEL",
]

OPTIONAL_SHOW = [
    "TELEGRAM_ALLOWLIST",
    "OPENAI_BASE_URL",
]

def mask(value: str, key: str) -> str:
    if key.endswith("_TOKEN") or key.endswith("_KEY"):
        return value[:6] + "..." if len(value) > 10 else "***MASKED***"
    return value

def main():
    missing = []
    empty = []
    for k in REQUIRED_NON_EMPTY:
        v = os.getenv(k)
        if v is None:
            missing.append(k)
        elif v.strip() == "":
            empty.append(k)

    if missing or empty:
        print("====================================")
        print("❌ فشل فحص المتغيرات:")
        if missing:
            print(" - مفقود:", ", ".join(missing))
        if empty:
            print(" - فارغ:", ", ".join(empty))
        print("سيتم إنهاء التشغيل لحماية البوت.")
        print("====================================")
        sys.exit(1)

    print("✅ جميع المتغيرات الحرجة موجودة وليست فارغة.")
    print("عرض آمن (مقنع) للقيم:")
    for k in REQUIRED_NON_EMPTY + OPTIONAL_SHOW:
        v = os.getenv(k)
        if v is None:
            continue
        print(f"{k} = {mask(v, k)}")
    print("====================================")

if __name__ == "__main__":
    main()