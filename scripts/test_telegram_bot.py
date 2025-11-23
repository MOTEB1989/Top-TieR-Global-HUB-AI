#!/usr/bin/env python3
"""
Telegram Bot Test Script
سكربت اختبار بوت Telegram
"""

import os
import sys
import asyncio
from typing import Optional
from pathlib import Path

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
        print("❌ مكتبات مفقودة:")
        for lib in missing:
            print(f"   - {lib}")
        print("\n💡 للتثبيت:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

async def test_telegram_bot():
    """اختبار بوت Telegram"""
    print("🤖 اختبار بوت Telegram")
    print("=" * 50)
    
    # التحقق من المفتاح
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN غير موجود في متغيرات البيئة")
        print("💡 أضف المفتاح في ملف .env:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return False
    
    print(f"✅ تم العثور على المفتاح: {bot_token[:10]}...")
    
    try:
        from telegram import Bot
        from telegram.error import TelegramError
        
        # إنشاء البوت
        bot = Bot(token=bot_token)
        
        # اختبار الاتصال
        print("\n🔍 اختبار الاتصال...")
        me = await bot.get_me()
        
        print(f"✅ البوت متصل بنجاح!")
        print(f"   - الاسم: {me.first_name}")
        print(f"   - Username: @{me.username}")
        print(f"   - ID: {me.id}")
        
        # اختبار الحصول على التحديثات
        print("\n🔍 اختبار جلب التحديثات...")
        updates = await bot.get_updates(limit=5)
        
        if updates:
            print(f"✅ تم جلب {len(updates)} تحديثات")
            for update in updates[:3]:
                if update.message:
                    print(f"   - رسالة من: {update.message.from_user.first_name}")
        else:
            print("ℹ️  لا توجد تحديثات جديدة")
        
        # اختبار إرسال رسالة (اختياري)
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id:
            print(f"\n📤 اختبار إرسال رسالة إلى {chat_id}...")
            try:
                message = await bot.send_message(
                    chat_id=chat_id,
                    text="🤖 رسالة اختبار من Top-TieR AI System\n✅ البوت يعمل بنجاح!"
                )
                print("✅ تم إرسال الرسالة بنجاح!")
            except TelegramError as e:
                print(f"⚠️  فشل إرسال الرسالة: {e}")
        else:
            print("\nℹ️  لإرسال رسالة اختبار، أضف TELEGRAM_CHAT_ID في .env")
        
        print("\n" + "=" * 50)
        print("✅ جميع الاختبارات نجحت!")
        print("=" * 50)
        return True
        
    except TelegramError as e:
        print(f"\n❌ خطأ في Telegram: {e}")
        if "Unauthorized" in str(e):
            print("💡 المفتاح غير صالح. تحقق من TELEGRAM_BOT_TOKEN")
        return False
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        return False

async def main():
    """الدالة الرئيسية"""
    # التحقق من المكتبات
    if not check_dependencies():
        sys.exit(1)
    
    # تشغيل الاختبار
    success = await test_telegram_bot()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  تم إيقاف الاختبار")
        sys.exit(130)
