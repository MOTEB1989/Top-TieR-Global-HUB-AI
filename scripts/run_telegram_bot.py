#!/usr/bin/env python3
"""
@LexnexuxBot - Full Featured Telegram Bot
بوت Telegram متكامل مع AI ودعم GitHub
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

# Setup unified logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import verify_env for environment validation
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from verify_env import check_variables, REQUIRED_NON_EMPTY
except ImportError:
    logger.warning("Could not import verify_env, skipping validation")
    def check_variables(required):
        return [], []
    REQUIRED_NON_EMPTY = []

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
        logger.info("Environment variables loaded from .env")
    else:
        logger.warning("No .env file found")

load_env()

# Check dependencies
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("❌ مكتبة python-telegram-bot غير مثبتة")
    print("💡 قم بتثبيتها: pip install python-telegram-bot")
    sys.exit(1)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWLIST = os.getenv("TELEGRAM_ALLOWLIST", "").split(",")
ALLOWLIST = [int(id.strip()) for id in ALLOWLIST if id.strip().isdigit()]
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

# Validate configuration
if not BOT_TOKEN or BOT_TOKEN.startswith("PASTE_"):
    logger.error("❌ TELEGRAM_BOT_TOKEN غير مُعدّ بشكل صحيح في .env")
    sys.exit(1)

def is_authorized(user_id: int) -> bool:
    """التحقق من صلاحية المستخدم"""
    if not ALLOWLIST:
        return True  # إذا لم تكن هناك قائمة، اسمح للجميع
    return user_id in ALLOWLIST

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start"""
    user = update.effective_user
    user_id = user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text(
            f"⛔ عذراً {user.first_name}، أنت غير مصرح لك باستخدام هذا البوت.\n"
            f"🆔 معرفك: {user_id}"
        )
        logger.warning(f"محاولة وصول غير مصرح بها من: {user_id} ({user.username})")
        return
    
    welcome_msg = f"""
🤖 مرحباً {user.first_name}!

أنا **@LexnexuxBot** - مساعدك الذكي للمشروع Top-TieR Global HUB AI

📋 **الأوامر المتاحة:**

🔹 `/start` - رسالة الترحيب
🔹 `/status` - حالة النظام والخدمات
🔹 `/preflight` - فحص شامل للنظام
🔹 `/keys` - فحص مفاتيح API المحلية
🔹 `/secrets` - فحص أسرار GitHub في المستودع
🔹 `/ai <سؤالك>` - اسأل AI (إذا كان OpenAI مفعّل)
🔹 `/help` - المساعدة والتعليمات

💬 **أو أرسل رسالة مباشرة وسأرد عليك!**

---
⚙️ الحالة: {"🟢 جاهز" if OPENAI_KEY and not OPENAI_KEY.startswith("${{") else "🟡 جزئي"}
🆔 معرفك: `{user_id}`
    """
    
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    logger.info(f"مستخدم جديد: {user.first_name} ({user_id})")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /status - حالة النظام"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح")
        return
    
    await update.message.reply_text("🔍 جاري فحص حالة النظام...")
    
    status_msg = "📊 **حالة النظام**\n\n"
    
    # Check services
    services = {
        "Telegram Bot": "🟢 يعمل",
        "OpenAI": "🟢 مُعدّ" if OPENAI_KEY and not OPENAI_KEY.startswith("${{") else "🔴 غير مُعدّ",
        "GitHub": "🟢 مُعدّ" if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("${{") else "🔴 غير مُعدّ",
    }
    
    for service, state in services.items():
        status_msg += f"{state} {service}\n"
    
    status_msg += f"\n⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def preflight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /preflight - تشغيل فحص شامل"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح")
        return
    
    script_path = os.getenv("ULTRA_PREFLIGHT_PATH", "scripts/ultra_preflight.sh")
    
    if not Path(script_path).exists():
        await update.message.reply_text(f"❌ السكربت غير موجود: {script_path}")
        return
    
    await update.message.reply_text("🚀 جاري تشغيل الفحص الشامل...\nقد يستغرق بضع ثوانٍ ⏳")
    
    try:
        # Run the preflight script
        process = await asyncio.create_subprocess_exec(
            'bash', script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            result = stdout.decode()[:4000]  # Telegram message limit
            await update.message.reply_text(f"✅ الفحص اكتمل بنجاح!\n\n```\n{result}\n```", parse_mode='Markdown')
        else:
            error = stderr.decode()[:1000]
            await update.message.reply_text(f"⚠️ الفحص اكتمل مع تحذيرات:\n\n```\n{error}\n```", parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في تشغيل الفحص: {str(e)}")
        logger.error(f"Preflight error: {e}")

async def check_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /keys - فحص مفاتيح API"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح")
        return
    
    await update.message.reply_text("🔍 جاري فحص المفاتيح...")
    
    try:
        process = await asyncio.create_subprocess_exec(
            'python3', 'scripts/check_all_keys.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        result = stdout.decode()[:4000]
        
        await update.message.reply_text(f"```\n{result}\n```", parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")

async def check_secrets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /secrets - فحص أسرار GitHub"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح")
        return
    
    await update.message.reply_text("🔐 جاري فحص أسرار GitHub في المستودع...")
    
    try:
        process = await asyncio.create_subprocess_exec(
            'python3', 'scripts/check_github_secrets.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        result = stdout.decode()
        
        # تقسيم النتيجة إذا كانت طويلة
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for i, part in enumerate(parts[:3]):  # أول 3 أجزاء فقط
                await update.message.reply_text(f"```\n{part}\n```", parse_mode='Markdown')
                await asyncio.sleep(0.5)
        else:
            await update.message.reply_text(f"```\n{result}\n```", parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
        logger.error(f"Secrets check error: {e}")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /ai - محادثة مع AI"""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⛔ غير مصرح")
        return
    
    if not OPENAI_KEY or OPENAI_KEY.startswith("${{"):
        await update.message.reply_text(
            "⚠️ OpenAI غير مُعدّ.\n"
            "أضف OPENAI_API_KEY في ملف .env للاستفادة من هذه الميزة."
        )
        return
    
    # Get the question
    question = ' '.join(context.args) if context.args else None
    
    if not question:
        await update.message.reply_text("💡 استخدام: `/ai <سؤالك>`", parse_mode='Markdown')
        return
    
    await update.message.reply_text("🤔 جاري التفكير...")
    
    try:
        import openai
        openai.api_key = OPENAI_KEY
        
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي للمشروع Top-TieR Global HUB AI. أجب بالعربية."},
                {"role": "user", "content": question}
            ],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        await update.message.reply_text(f"🤖 **الجواب:**\n\n{answer}", parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في AI: {str(e)}")
        logger.error(f"AI error: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /help"""
    help_text = """
📚 **دليل الاستخدام**

**الأوامر الأساسية:**
• `/start` - البداية
• `/status` - حالة الخدمات
• `/help` - هذه الرسالة

**أوامر الفحص:**
• `/preflight` - فحص شامل للنظام
• `/keys` - فحص مفاتيح API

**الذكاء الاصطناعي:**
• `/ai <سؤال>` - اسأل AI عن أي شيء

**أمثلة:**
```
/ai ما هو Docker؟
/ai كيف أحسن أداء Python؟
```

💡 يمكنك أيضاً إرسال رسالة مباشرة وسأرد عليك!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعامل مع الرسائل النصية"""
    if not is_authorized(update.effective_user.id):
        return
    
    text = update.message.text
    user = update.effective_user
    
    logger.info(f"رسالة من {user.first_name}: {text}")
    
    # رد تلقائي بسيط
    await update.message.reply_text(
        f"📨 استلمت رسالتك: \"{text}\"\n\n"
        f"💡 استخدم `/ai {text}` للحصول على رد ذكي من AI"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"خطأ: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ حدث خطأ في معالجة طلبك. جاري المحاولة مرة أخرى..."
        )

def safe_main():
    """الدالة الرئيسية wrapped in safe error handling"""
    try:
        # Verify critical environment variables
        critical_vars = ["TELEGRAM_BOT_TOKEN"]
        for var in critical_vars:
            value = os.getenv(var)
            if not value or value.startswith("PASTE_"):
                logger.error(f"❌ {var} غير مُعدّ بشكل صحيح في .env")
                return 1
        
        logger.info("🚀 بدء تشغيل @LexnexuxBot...")
        logger.info("✅ Environment variables validated")
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CommandHandler("preflight", preflight))
        application.add_handler(CommandHandler("keys", check_keys))
        application.add_handler(CommandHandler("secrets", check_secrets))
        application.add_handler(CommandHandler("ai", ai_chat))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start bot
        logger.info("✅ البوت يعمل الآن! اضغط Ctrl+C للإيقاف.")
        logger.info(f"🔐 المستخدمون المصرح لهم: {ALLOWLIST if ALLOWLIST else 'الجميع'}")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        return 0
        
    except Exception as e:
        logger.error(f"❌ خطأ فادح في التشغيل: {e}", exc_info=True)
        return 1

def main():
    """Entry point for the script"""
    sys.exit(safe_main())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️ تم إيقاف البوت")
        sys.exit(0)
