"""Telegram bot with i18n support using aiogram."""
import os
import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

from i18n import t

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get configuration from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_LOCALE = os.getenv("BOT_DEFAULT_LOCALE", "ar")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command."""
    await message.reply(t("start", DEFAULT_LOCALE))


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command."""
    await message.reply(t("help", DEFAULT_LOCALE))


@dp.message(Command("health"))
async def cmd_health(message: types.Message):
    """Handle /health command."""
    await message.reply(t("health", DEFAULT_LOCALE))


@dp.message()
async def handle_unknown(message: types.Message):
    """Handle unknown commands and messages."""
    await message.reply(t("unknown_command", DEFAULT_LOCALE))


async def main():
    """Start the bot."""
    logger.info(f"Starting bot with default locale: {DEFAULT_LOCALE}")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
