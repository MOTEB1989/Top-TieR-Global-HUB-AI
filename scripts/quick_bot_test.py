#!/usr/bin/env python3
"""
Quick Telegram Bot Test
اختبار سريع لبوت تيليجرام
"""

import os
import sys
from pathlib import Path

def load_env():
    """تحميل ملف .env"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print("✅ ملف .env موجود")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    if key and value:
                        os.environ[key.strip()] = value.strip()
    else:
        print("❌ ملف .env غير موجود")
        print("💡 قم بتنفيذ: cp .env.example .env")
        return False
    return True

def check_env_vars():
    """فحص المتغيرات المطلوبة"""
    print("\n🔍 فحص المتغيرات البيئية...")
    
    required = {
        "TELEGRAM_BOT_TOKEN": "توكن البوت من @BotFather",
        "OPENAI_API_KEY": "مفتاح OpenAI (اختياري للدردشة)",
        "GITHUB_TOKEN": "توكن GitHub (اختياري)",
    }
    
    missing = []
    placeholder = []
    
    for key, desc in required.items():
        value = os.getenv(key)
        if not value:
            missing.append(f"   ❌ {key}: غير موجود - {desc}")
        elif "PASTE_" in value or value.startswith("sk-..."):
            placeholder.append(f"   ⚠️  {key}: قيمة افتراضية - {desc}")
        else:
            print(f"   ✅ {key}: موجود ({len(value)} حرف)")
    
    if missing:
        print("\n❌ متغيرات مفقودة:")
        for m in missing:
            print(m)
    
    if placeholder:
        print("\n⚠️  متغيرات تحتاج تحديث:")
        for p in placeholder:
            print(p)
    
    return len(missing) == 0

def check_dependencies():
    """فحص المكتبات المطلوبة"""
    print("\n📦 فحص المكتبات...")
    
    missing = []
    
    try:
        import telegram
        print("   ✅ python-telegram-bot مثبتة")
    except ImportError:
        missing.append("python-telegram-bot")
        print("   ❌ python-telegram-bot غير مثبتة")
    
    try:
        import requests
        print("   ✅ requests مثبتة")
    except ImportError:
        missing.append("requests")
        print("   ❌ requests غير مثبتة")
    
    if missing:
        print(f"\n💡 لتثبيت المكتبات المفقودة:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def test_bot_token():
    """اختبار توكن البوت"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token or "PASTE_" in token:
        print("\n⚠️  لا يمكن اختبار البوت - التوكن غير مُعدّ")
        return False
    
    print("\n🤖 اختبار اتصال البوت...")
    
    try:
        import requests
        
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"   ✅ البوت متصل: @{bot_info.get('username')}")
                print(f"   📛 الاسم: {bot_info.get('first_name')}")
                print(f"   🆔 ID: {bot_info.get('id')}")
                return True
        
        print(f"   ❌ فشل الاتصال: {response.status_code}")
        print(f"   الرد: {response.text[:200]}")
        return False
        
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("="*60)
    print("🔍 فحص سريع لبوت Telegram")
    print("="*60)
    
    # تحميل .env
    if not load_env():
        return 1
    
    # فحص المتغيرات
    env_ok = check_env_vars()
    
    # فحص المكتبات
    deps_ok = check_dependencies()
    
    # اختبار البوت
    bot_ok = False
    if env_ok and deps_ok:
        bot_ok = test_bot_token()
    
    # النتيجة النهائية
    print("\n" + "="*60)
    print("📊 الملخص")
    print("="*60)
    
    if env_ok and deps_ok and bot_ok:
        print("✅ جميع الفحوصات نجحت!")
        print("\n🚀 يمكنك الآن تشغيل البوت:")
        print("   python scripts/telegram_chatgpt_mode.py")
        return 0
    else:
        print("⚠️  يوجد مشاكل تحتاج حل:")
        if not env_ok:
            print("   • أضف المفاتيح المطلوبة في .env")
        if not deps_ok:
            print("   • ثبّت المكتبات المطلوبة")
        if not bot_ok and env_ok and deps_ok:
            print("   • تحقق من صحة TELEGRAM_BOT_TOKEN")
        
        print("\n💡 اتبع الخطوات في SETUP_GUIDE.md")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  تم إيقاف الفحص")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
