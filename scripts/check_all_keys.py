#!/usr/bin/env python3
"""
API Keys Validator
التحقق من جميع مفاتيح API والخدمات
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Setup unified logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("check_all_keys")

# Load .env file
def load_env():
    """تحميل ملف .env"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    if key and value:
                        os.environ[key.strip()] = value.strip()
        logger.info("Environment loaded from .env")

load_env()

class KeyStatus:
    """حالات المفاتيح"""
    VALID = "✅ صالح"
    MISSING = "❌ مفقود"
    PLACEHOLDER = "⚠️ قيمة افتراضية"
    EMPTY = "❌ فارغ"
    INVALID = "⚠️ غير صالح"

def check_key(key_name: str, validators: List[str] = None) -> Tuple[str, str]:
    """فحص مفتاح معين"""
    value = os.getenv(key_name)
    
    if not value:
        return KeyStatus.MISSING, "غير موجود"
    
    # تحقق من القيم الافتراضية
    placeholders = [
        "PASTE_",
        "your_",
        "YOUR_",
        "placeholder",
        "example",
        "${{",
        "sk-...",
        "xxx"
    ]
    
    if any(placeholder in value for placeholder in placeholders):
        return KeyStatus.PLACEHOLDER, f"القيمة: {value[:30]}..."
    
    if value.strip() == "":
        return KeyStatus.EMPTY, "فارغ"
    
    # تحقق مخصص للمفاتيح
    if validators:
        for validator in validators:
            if validator == "openai" and not value.startswith("sk-"):
                return KeyStatus.INVALID, "يجب أن يبدأ بـ sk-"
            elif validator == "telegram" and ":" not in value:
                return KeyStatus.INVALID, "تنسيق غير صحيح"
            elif validator == "github" and len(value) < 20:
                return KeyStatus.INVALID, "قصير جداً"
    
    return KeyStatus.VALID, f"موجود ({len(value)} حرف)"

def safe_main():
    """الدالة الرئيسية wrapped in safe error handling"""
    try:
        logger.info("="*60)
        logger.info("🔑 فحص جميع مفاتيح API والإعدادات")
        logger.info("="*60)
        
        # قائمة المفاتيح للفحص
        keys_to_check = {
            "مفاتيح AI/LLM": [
                ("OPENAI_API_KEY", ["openai"]),
                ("GROQ_API_KEY", None),
                ("ANTHROPIC_API_KEY", None),
            ],
            "Telegram Bot": [
                ("TELEGRAM_BOT_TOKEN", ["telegram"]),
                ("TELEGRAM_ALLOWLIST", None),
                ("TELEGRAM_CHAT_ID", None),
            ],
            "GitHub": [
                ("GITHUB_TOKEN", ["github"]),
                ("GITHUB_REPO", None),
            ],
            "قواعد البيانات": [
                ("DB_URL", None),
                ("REDIS_URL", None),
                ("NEO4J_URI", None),
                ("NEO4J_AUTH", None),
            ],
            "مسارات السكربتات": [
                ("ULTRA_PREFLIGHT_PATH", None),
                ("FULL_SCAN_SCRIPT", None),
                ("LOG_FILE_PATH", None),
            ]
        }
        
        total_keys = 0
        valid_keys = 0
        missing_keys = 0
        placeholder_keys = 0
        
        for category, keys in keys_to_check.items():
            logger.info(f"\n📂 {category}")
            logger.info("-" * 60)
            
            for key_info in keys:
                key_name = key_info[0]
                validators = key_info[1] if len(key_info) > 1 else None
                
                status, message = check_key(key_name, validators)
                logger.info(f"  {status} {key_name}")
                logger.info(f"     {message}")
                
                total_keys += 1
                if status == KeyStatus.VALID:
                    valid_keys += 1
                elif status == KeyStatus.MISSING:
                    missing_keys += 1
                elif status == KeyStatus.PLACEHOLDER:
                    placeholder_keys += 1
        
        # الملخص
        logger.info("="*60)
        logger.info("📊 الملخص")
        logger.info("="*60)
        logger.info(f"  إجمالي المفاتيح: {total_keys}")
        logger.info(f"  ✅ صالحة: {valid_keys}")
        logger.info(f"  ❌ مفقودة: {missing_keys}")
        logger.info(f"  ⚠️  قيم افتراضية: {placeholder_keys}")
        
        percentage = (valid_keys / total_keys * 100) if total_keys > 0 else 0
        logger.info(f"\n  نسبة الاكتمال: {percentage:.1f}%")
        
        # التوصيات
        if missing_keys > 0 or placeholder_keys > 0:
            logger.info("="*60)
            logger.info("💡 التوصيات")
            logger.info("="*60)
            
            if placeholder_keys > 0:
                logger.info("\n  🔧 يجب تحديث القيم الافتراضية:")
                logger.info("     - افتح ملف .env")
                logger.info("     - استبدل القيم التي تحتوي على PASTE_ أو ${{")
                logger.info("     - أضف المفاتيح الفعلية من الخدمات المعنية")
            
            if missing_keys > 0:
                logger.info("\n  📝 يجب إضافة المفاتيح المفقودة في ملف .env")
            
            logger.info("\n  📚 مصادر الحصول على المفاتيح:")
            logger.info("     • OpenAI: https://platform.openai.com/api-keys")
            logger.info("     • GitHub: https://github.com/settings/tokens")
            logger.info("     • Telegram: https://t.me/BotFather")
        
        logger.info("="*60)
        
        # كود الخروج
        if percentage >= 80:
            logger.info("✅ جاهز للعمل!")
            return 0
        elif percentage >= 50:
            logger.info("⚠️  يحتاج إلى بعض التحسينات")
            return 0
        else:
            logger.info("❌ يحتاج إلى إعداد إضافي")
            return 1
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1

def main():
    """Entry point for the script"""
    sys.exit(safe_main())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️ تم إيقاف الفحص")
        sys.exit(130)
