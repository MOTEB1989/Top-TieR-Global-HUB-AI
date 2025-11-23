#!/usr/bin/env python3
"""
Environment Variable Verification Script
Validates required environment variables and optionally checks strict requirements.

Usage:
    python verify_env.py              # Normal mode
    python verify_env.py --strict     # Strict mode (fails on warnings)
"""

import os
import sys
import argparse

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required, env vars may be set directly


# Required environment variables (must be non-empty)
REQUIRED_NON_EMPTY = [
    "TELEGRAM_BOT_TOKEN",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",  # Now mandatory
    "GITHUB_REPO",
]

# Optional variables to display
OPTIONAL_SHOW = [
    "OPENAI_FALLBACK_MODEL",
    "TELEGRAM_ALLOWLIST",
    "OPENAI_BASE_URL",
    "TELEGRAM_RATE_LIMIT_PER_MIN",
]

# Sensitive suffixes for masking
SENSITIVE_SUFFIXES = ("_TOKEN", "_KEY", "_PASSWORD", "_PASS", "_AUTH")


def mask(value: str, key: str) -> str:
    """
    Mask sensitive values for safe display.
    
    Args:
        value: The value to potentially mask
        key: The environment variable key name
        
    Returns:
        Masked string if key is sensitive, otherwise original value
    """
    if not value:
        return "***EMPTY***"
    
    key_upper = key.upper()
    if any(key_upper.endswith(suffix) for suffix in SENSITIVE_SUFFIXES):
        if len(value) > 10:
            return value[:6] + "..." + value[-4:]
        return "***MASKED***"
    return value


def check_env_vars(strict: bool = False) -> int:
    """
    Check environment variables for completeness.
    
    Args:
        strict: If True, warnings become errors
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    missing = []
    empty = []
    warnings = []
    
    # Check required variables
    for k in REQUIRED_NON_EMPTY:
        v = os.getenv(k)
        if v is None:
            missing.append(k)
        elif v.strip() == "":
            empty.append(k)
    
    # Check for weak/placeholder values
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and (
        openai_key.startswith("PASTE_") or 
        openai_key.startswith("sk-proj-PASTE_")
    ):
        warnings.append("OPENAI_API_KEY appears to be a placeholder value")
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if telegram_token and telegram_token.startswith("PASTE_"):
        warnings.append("TELEGRAM_BOT_TOKEN appears to be a placeholder value")
    
    # Report results
    if missing or empty:
        print("=" * 60)
        print("❌ فشل فحص المتغيرات (Environment Check Failed)")
        print("=" * 60)
        if missing:
            print("  مفقود (Missing):", ", ".join(missing))
        if empty:
            print("  فارغ (Empty):", ", ".join(empty))
        print("\nسيتم إنهاء التشغيل لحماية البوت.")
        print("Exiting to protect bot from misconfiguration.")
        print("=" * 60)
        return 1
    
    # Handle warnings
    if warnings:
        print("=" * 60)
        print("⚠️ تحذيرات (Warnings)")
        print("=" * 60)
        for w in warnings:
            print(f"  - {w}")
        if strict:
            print("\n❌ Strict mode: treating warnings as errors")
            print("=" * 60)
            return 1
        print("=" * 60)
    
    # Success - show safe values
    print("=" * 60)
    print("✅ جميع المتغيرات الحرجة موجودة (All Critical Variables Present)")
    print("=" * 60)
    print("عرض آمن (Safe Display):")
    print()
    
    for k in REQUIRED_NON_EMPTY:
        v = os.getenv(k, "")
        print(f"  {k:30s} = {mask(v, k)}")
    
    print("\nمتغيرات اختيارية (Optional Variables):")
    for k in OPTIONAL_SHOW:
        v = os.getenv(k)
        if v:
            print(f"  {k:30s} = {mask(v, k)}")
        else:
            print(f"  {k:30s} = (not set)")
    
    print("=" * 60)
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify environment variables for Top-TieR-Global-HUB-AI"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (warnings become errors)"
    )
    
    args = parser.parse_args()
    exit_code = check_env_vars(strict=args.strict)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()