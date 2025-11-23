#!/usr/bin/env python3
"""
Telegram Bot Test Script
سكربت اختبار بوت Telegram
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from pathlib import Path

# Setup unified logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("test_telegram_bot")

# Import verify_env for environment validation
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from verify_env import check_variables
except ImportError:
    logger.warning("Could not import verify_env")
    def check_variables(required):
        return [], []

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
    else:
        logger.warning("No .env file found")

load_env()

def check_dependencies():
    """التحقق من المكتبات المطلوبة"""
    missing = []
    
    try:
        import telegram
    except ImportError:
        missing.append("python-telegram-bot")
    
    try:
        import requests
    except ImportError:
        missing.append("requests")
    
    if missing:
        logger.error("❌ مكتبات مفقودة:")
        for lib in missing:
            logger.error(f"   - {lib}")
        logger.info("💡 للتثبيت: pip install %s", ' '.join(missing))
        return False
    
    logger.info("✅ All dependencies available")
    return True

async def test_telegram_bot():
    """اختبار بوت Telegram"""
    logger.info("🤖 اختبار بوت Telegram")
    logger.info("=" * 50)
    
    # التحقق من المفتاح
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN غير موجود في متغيرات البيئة")
        logger.info("💡 أضف المفتاح في ملف .env:")
        logger.info("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return False
    
    logger.info(f"✅ تم العثور على المفتاح: {bot_token[:10]}...")
    
    try:
        from telegram import Bot
        from telegram.error import TelegramError
        
        # إنشاء البوت
        bot = Bot(token=bot_token)
        
        # اختبار الاتصال
        logger.info("🔍 اختبار الاتصال...")
        me = await bot.get_me()
        
        logger.info(f"✅ البوت متصل بنجاح!")
        logger.info(f"   - الاسم: {me.first_name}")
        logger.info(f"   - Username: @{me.username}")
        logger.info(f"   - ID: {me.id}")
        
        # اختبار الحصول على التحديثات
        logger.info("🔍 اختبار جلب التحديثات...")
        updates = await bot.get_updates(limit=5)
        
        if updates:
            logger.info(f"✅ تم جلب {len(updates)} تحديثات")
            for update in updates[:3]:
                if update.message:
                    logger.info(f"   - رسالة من: {update.message.from_user.first_name}")
        else:
            logger.info("ℹ️  لا توجد تحديثات جديدة")
        
        # اختبار إرسال رسالة (اختياري)
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id:
            logger.info(f"📤 اختبار إرسال رسالة إلى {chat_id}...")
            try:
                message = await bot.send_message(
                    chat_id=chat_id,
                    text="🤖 رسالة اختبار من Top-TieR AI System\n✅ البوت يعمل بنجاح!"
                )
                logger.info("✅ تم إرسال الرسالة بنجاح!")
            except TelegramError as e:
                logger.warning(f"⚠️  فشل إرسال الرسالة: {e}")
        else:
            logger.info("ℹ️  لإرسال رسالة اختبار، أضف TELEGRAM_CHAT_ID في .env")
        
        logger.info("=" * 50)
        logger.info("✅ جميع الاختبارات نجحت!")
        logger.info("=" * 50)
        return True
        
    except TelegramError as e:
        logger.error(f"❌ خطأ في Telegram: {e}")
        if "Unauthorized" in str(e):
            logger.error("💡 المفتاح غير صالح. تحقق من TELEGRAM_BOT_TOKEN")
        return False
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع: {e}", exc_info=True)
        return False

async def safe_main():
    """الدالة الرئيسية wrapped in safe error handling"""
    try:
        # التحقق من المكتبات
        if not check_dependencies():
            return 1
        
        # تشغيل الاختبار
        success = await test_telegram_bot()
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Fatal error during testing: {e}", exc_info=True)
        return 1

def main():
    """Entry point for the script"""
    try:
        exit_code = asyncio.run(safe_main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n⚠️  تم إيقاف الاختبار")
        sys.exit(130)

if __name__ == "__main__":
    main()
