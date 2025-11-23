"""
Telegram Bot Service for Top-TieR Global HUB AI
خدمة بوت تيليجرام لمركز Top-TieR العالمي للذكاء الاصطناعي
"""
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handle /start command
    معالج أمر /start
    """
    welcome_text = (
        "🤖 مرحباً بك في Top-TieR Global HUB AI!\n"
        "Welcome to Top-TieR Global HUB AI!\n\n"
        "Available commands / الأوامر المتاحة:\n"
        "/start - Start the bot / بدء البوت\n"
        "/help - Show help / عرض المساعدة\n"
        "/health - Check system health / فحص صحة النظام\n"
    )
    await message.answer(welcome_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """
    Handle /help command
    معالج أمر /help
    """
    help_text = (
        "📚 Help - المساعدة\n\n"
        "This bot is part of the Top-TieR Global HUB AI platform.\n"
        "هذا البوت جزء من منصة Top-TieR Global HUB AI.\n\n"
        "Commands / الأوامر:\n"
        "/start - Start the bot / بدء البوت\n"
        "/help - Show this help message / عرض هذه الرسالة\n"
        "/health - Check backend health / فحص صحة الخلفية\n"
    )
    await message.answer(help_text)


@dp.message(Command("health"))
async def cmd_health(message: Message):
    """
    Handle /health command - aggregates backend health status
    معالج أمر /health - يجمع حالة صحة الخلفية
    """
    try:
        # Call backend health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_API_URL}/health",
                timeout=10.0
            )
            response.raise_for_status()
            health_data = response.json()
        
        status_emoji = "✅" if health_data.get("status") == "healthy" else "❌"
        health_text = (
            f"{status_emoji} System Health Status / حالة صحة النظام\n\n"
            f"Backend Status: {health_data.get('status', 'unknown')}\n"
            f"Service: {health_data.get('service', 'unknown')}\n"
            f"Environment: {health_data.get('environment', 'unknown')}\n"
            f"Version: {health_data.get('version', 'unknown')}\n"
        )
        await message.answer(health_text)
        
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to backend: {e}")
        await message.answer(
            "❌ Failed to connect to backend service.\n"
            "فشل الاتصال بخدمة الخلفية.\n\n"
            f"Error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        await message.answer(
            "❌ Error checking system health.\n"
            "خطأ في فحص صحة النظام.\n\n"
            f"Error: {str(e)}"
        )


@dp.message()
async def echo_handler(message: Message):
    """
    Echo handler for unrecognized messages
    معالج الصدى للرسائل غير المعروفة
    """
    # TODO: Add i18n support for Arabic/English localization
    await message.answer(
        "I received your message. Use /help to see available commands.\n"
        "استلمت رسالتك. استخدم /help لرؤية الأوامر المتاحة."
    )


async def main():
    """
    Main bot runner
    المشغل الرئيسي للبوت
    """
    logger.info("Starting Top-TieR Global HUB AI Bot...")
    logger.info(f"Backend API URL: {BACKEND_API_URL}")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
