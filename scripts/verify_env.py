#!/usr/bin/env python3
"""
Environment variable verification script for all services
سكريبت التحقق من متغيرات البيئة لجميع الخدمات

Usage:
  python scripts/verify_env.py                    # Check all services
  python scripts/verify_env.py --service backend  # Check specific service
  python scripts/verify_env.py --service bot
  python scripts/verify_env.py --service frontend
"""
import os
import sys
import argparse

# Service-specific required variables
SERVICE_VARS = {
    "backend": {
        "required": ["DATABASE_URL", "JWT_SECRET", "TELEGRAM_BOT_TOKEN", "ADMIN_CHAT_ID"],
        "optional": ["REDIS_URL", "OPENAI_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY"],
    },
    "bot": {
        "required": ["TELEGRAM_BOT_TOKEN", "BACKEND_API_URL", "ADMIN_CHAT_ID"],
        "optional": [],
    },
    "frontend": {
        "required": ["NEXT_PUBLIC_API_BASE"],
        "optional": ["NEXT_PUBLIC_WS_URL"],
    },
}

# Legacy support - general required variables
REQUIRED_NON_EMPTY = [
    "TELEGRAM_BOT_TOKEN",
    "OPENAI_API_KEY",
    "GITHUB_REPO",
]

OPTIONAL_SHOW = [
    "OPENAI_MODEL",
    "TELEGRAM_ALLOWLIST",
    "OPENAI_BASE_URL",
]


def mask(value: str, key: str) -> str:
    """Mask sensitive values for display"""
    sensitive_patterns = ["_TOKEN", "_KEY", "_SECRET", "PASSWORD", "_PASS", "_AUTH", "API_KEY"]
    key_upper = key.upper()
    if any(pattern in key_upper for pattern in sensitive_patterns):
        return value[:6] + "..." if len(value) > 10 else "***MASKED***"
    return value


def check_service(service_name: str) -> bool:
    """
    Check environment variables for a specific service
    التحقق من متغيرات البيئة لخدمة محددة
    """
    if service_name not in SERVICE_VARS:
        print(f"❌ Unknown service: {service_name}")
        print(f"Available services: {', '.join(SERVICE_VARS.keys())}")
        return False

    config = SERVICE_VARS[service_name]
    missing = []
    empty = []

    print(f"\n{'='*50}")
    print(f"Checking environment for: {service_name.upper()}")
    print(f"فحص البيئة لـ: {service_name.upper()}")
    print(f"{'='*50}\n")

    # Check required variables
    for var in config["required"]:
        value = os.getenv(var)
        if value is None:
            missing.append(var)
        elif value.strip() == "":
            empty.append(var)

    if missing or empty:
        print(f"❌ فشل فحص المتغيرات لـ {service_name}:")
        if missing:
            print(f" - مفقود (Missing): {', '.join(missing)}")
        if empty:
            print(f" - فارغ (Empty): {', '.join(empty)}")
        print(f"\nسيتم إنهاء التشغيل لحماية الخدمة.")
        print(f"Please set these variables in your .env file or environment.")
        print(f"{'='*50}")
        return False

    print(f"✅ جميع المتغيرات الحرجة موجودة وليست فارغة.")
    print(f"All critical variables are present and non-empty.\n")

    # Show masked values
    print("عرض آمن (مقنع) للقيم:")
    print("Masked display of values:")
    for var in config["required"] + config["optional"]:
        value = os.getenv(var)
        if value is not None:
            print(f"  {var} = {mask(value, var)}")
        else:
            print(f"  {var} = (not set)")

    print(f"{'='*50}\n")
    return True


def check_all_services() -> bool:
    """Check all services"""
    results = {}
    for service in SERVICE_VARS.keys():
        results[service] = check_service(service)

    print("\n" + "="*50)
    print("SUMMARY / الملخص")
    print("="*50)
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service.upper()}: {status}")
    print("="*50 + "\n")

    return all(results.values())


def check_legacy() -> bool:
    """Check legacy environment variables (backward compatibility)"""
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
        return False

    print("✅ جميع المتغيرات الحرجة موجودة وليست فارغة.")
    print("عرض آمن (مقنع) للقيم:")
    for k in REQUIRED_NON_EMPTY + OPTIONAL_SHOW:
        v = os.getenv(k)
        if v is None:
            continue
        print(f"{k} = {mask(v, k)}")
    print("====================================")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Verify environment variables for Top-TieR Global HUB AI services"
    )
    parser.add_argument(
        "--service",
        type=str,
        choices=list(SERVICE_VARS.keys()) + ["all", "legacy"],
        default="all",
        help="Service to check (default: all)"
    )
    args = parser.parse_args()

    try:
        if args.service == "all":
            success = check_all_services()
        elif args.service == "legacy":
            success = check_legacy()
        else:
            success = check_service(args.service)

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n❌ Error during environment check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()