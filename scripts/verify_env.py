#!/usr/bin/env python3
"""
verify_env.py - Environment variable validation for Top-TieR-Global-HUB-AI

Validates required and optional environment variables before starting services.
Supports strict mode for treating optional variables as required.
"""

import os
import sys
import logging
import argparse
from typing import List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("verify_env")

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

# Additional optional variables that become required in strict mode
STRICT_MODE_REQUIRED = [
    "OPENAI_MODEL",
]


def mask(value: str, key: str) -> str:
    """Mask sensitive values for safe display."""
    if key.endswith("_TOKEN") or key.endswith("_KEY"):
        return value[:6] + "..." if len(value) > 10 else "***MASKED***"
    return value


def check_variables(required: List[str]) -> Tuple[List[str], List[str]]:
    """
    Check if required variables are set and non-empty.
    
    Args:
        required: List of required variable names
        
    Returns:
        Tuple of (missing_vars, empty_vars)
    """
    missing = []
    empty = []
    
    for k in required:
        v = os.getenv(k)
        if v is None:
            missing.append(k)
        elif v.strip() == "":
            empty.append(k)
    
    return missing, empty


def safe_main() -> int:
    """
    Main function wrapped in safe error handling.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        parser = argparse.ArgumentParser(
            description="Verify environment variables for Top-TieR-Global-HUB-AI"
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Strict mode: treat optional variables as required"
        )
        args = parser.parse_args()
        
        # Determine which variables to check
        required_vars = REQUIRED_NON_EMPTY.copy()
        if args.strict:
            required_vars.extend(STRICT_MODE_REQUIRED)
            logger.info("Running in strict mode - additional variables required")
        
        # Check variables
        missing, empty = check_variables(required_vars)
        
        if missing or empty:
            logger.error("====================================")
            logger.error("❌ فشل فحص المتغيرات:")
            if missing:
                logger.error(" - مفقود: %s", ", ".join(missing))
            if empty:
                logger.error(" - فارغ: %s", ", ".join(empty))
            logger.error("سيتم إنهاء التشغيل لحماية البوت.")
            logger.error("====================================")
            return 1
        
        logger.info("✅ جميع المتغيرات الحرجة موجودة وليست فارغة.")
        logger.info("عرض آمن (مقنع) للقيم:")
        
        # Display all variables (required + optional)
        all_vars = required_vars + OPTIONAL_SHOW
        for k in all_vars:
            v = os.getenv(k)
            if v is None:
                continue
            logger.info("%s = %s", k, mask(v, k))
        
        logger.info("====================================")
        return 0
        
    except Exception as e:
        logger.error("❌ Fatal error during environment verification: %s", e)
        return 1


def main():
    """Entry point for the script."""
    sys.exit(safe_main())


if __name__ == "__main__":
    main()