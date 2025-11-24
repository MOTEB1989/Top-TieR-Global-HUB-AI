#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py

Main entry point for the modular ChatGPT-grade Telegram bot.
نقطة الدخول الرئيسية للبوت المتطور.
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core modules
from bot.core.session_store import SessionStore
from bot.core.rate_limiter import RateLimiter
from bot.core.model_registry import ModelRegistry
from bot.core.persona_manager import PersonaManager
from bot.core.tool_runner import ToolRunner

# Import adapters
from bot.adapters.openai_client import OpenAIClient
from bot.adapters.anthropic_client import AnthropicClient
from bot.adapters.groq_client import GroqClient

# Import utils
from bot.utils.response_builder import ResponseBuilder
from bot.utils.safety_filter import SafetyFilter

# Import command handlers
from bot.commands.meta import (
    cmd_help, cmd_start, cmd_whoami, cmd_status,
    cmd_model, cmd_provider, cmd_persona
)
from bot.commands.sessions import (
    cmd_sessions, cmd_new, cmd_switch, cmd_clear, cmd_export
)
from bot.commands.chat import cmd_chat, handle_text_message
from bot.commands.advanced import (
    cmd_summarize, cmd_continue, cmd_regen, cmd_share
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("bot.main")


# ==================== Configuration ====================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWLIST_ENV = os.getenv("TELEGRAM_ALLOWLIST", "").strip()

SESSION_BASE_PATH = os.getenv("SESSION_BASE_PATH", "analysis/sessions")
BOT_MAX_MESSAGES_PER_SESSION = int(os.getenv("BOT_MAX_MESSAGES_PER_SESSION", "50"))
BOT_RATE_WINDOW_SECONDS = int(os.getenv("BOT_RATE_WINDOW_SECONDS", "3600"))
BOT_RATE_MAX_MESSAGES = int(os.getenv("BOT_RATE_MAX_MESSAGES", "30"))
BOT_PERSONA = os.getenv("BOT_PERSONA", "default")
BOT_SILENT_SUGGESTIONS = os.getenv("BOT_SILENT_SUGGESTIONS", "false").lower() == "true"

GITHUB_REPO = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")


# ==================== Allowlist ====================

def parse_allowlist(raw: str):
    """Parse comma-separated allowlist."""
    if not raw:
        return set()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    ids = set()
    for p in parts:
        try:
            ids.add(int(p))
        except ValueError:
            continue
    return ids


USER_ALLOWLIST = parse_allowlist(ALLOWLIST_ENV)


def is_authorized(update: Update) -> bool:
    """Check if user is authorized."""
    if not USER_ALLOWLIST:
        return True  # Empty allowlist = allow all
    uid = update.effective_user.id if update.effective_user else None
    return uid in USER_ALLOWLIST


async def reject_if_unauthorized(update: Update) -> bool:
    """Reject unauthorized users."""
    if is_authorized(update):
        return False
    
    await update.message.reply_text(
        "❌ غير مصرح لك باستخدام هذا البوت.\n"
        "استخدم /whoami ثم اطلب إضافة معرفك إلى TELEGRAM_ALLOWLIST."
    )
    return True


# ==================== Middleware ====================

async def authorization_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Authorization middleware for all handlers."""
    if update.message and not is_authorized(update):
        await reject_if_unauthorized(update)
        return
    
    # Initialize user data if needed
    if "current_session" not in context.user_data:
        context.user_data["current_session"] = "default"
    if "provider" not in context.user_data:
        context.user_data["provider"] = "openai"
    if "model" not in context.user_data:
        context.user_data["model"] = "gpt-4o-mini"
    if "persona" not in context.user_data:
        context.user_data["persona"] = BOT_PERSONA


# ==================== Initialize Components ====================

def initialize_components(app: Application) -> None:
    """Initialize all bot components."""
    logger.info("[bot] Initializing components...")
    
    # Session store
    session_store = SessionStore(base_path=SESSION_BASE_PATH)
    session_store.max_messages = BOT_MAX_MESSAGES_PER_SESSION
    app.bot_data["session_store"] = session_store
    logger.info(f"[bot] Session store initialized: {SESSION_BASE_PATH}")
    
    # Rate limiter
    rate_limiter = RateLimiter(
        window_seconds=BOT_RATE_WINDOW_SECONDS,
        max_messages=BOT_RATE_MAX_MESSAGES
    )
    app.bot_data["rate_limiter"] = rate_limiter
    logger.info(f"[bot] Rate limiter initialized: {BOT_RATE_MAX_MESSAGES} msgs / {BOT_RATE_WINDOW_SECONDS}s")
    
    # Model registry
    model_registry = ModelRegistry()
    app.bot_data["model_registry"] = model_registry
    logger.info("[bot] Model registry initialized")
    
    # Persona manager
    persona_manager = PersonaManager(repo_name=GITHUB_REPO)
    app.bot_data["persona_manager"] = persona_manager
    logger.info("[bot] Persona manager initialized")
    
    # Tool runner
    tool_runner = ToolRunner()
    app.bot_data["tool_runner"] = tool_runner
    logger.info("[bot] Tool runner initialized")
    
    # AI clients
    openai_client = OpenAIClient()
    app.bot_data["openai_client"] = openai_client
    if openai_client.is_available():
        logger.info("[bot] ✅ OpenAI client available")
    else:
        logger.warning("[bot] ⚠️ OpenAI client not available (missing API key)")
    
    anthropic_client = AnthropicClient()
    app.bot_data["anthropic_client"] = anthropic_client
    if anthropic_client.is_available():
        logger.info("[bot] ✅ Anthropic client available")
    else:
        logger.warning("[bot] ⚠️ Anthropic client not available (missing API key)")
    
    groq_client = GroqClient()
    app.bot_data["groq_client"] = groq_client
    if groq_client.is_available():
        logger.info("[bot] ✅ Groq client available")
    else:
        logger.warning("[bot] ⚠️ Groq client not available (missing API key)")
    
    # Utils
    response_builder = ResponseBuilder(silent_suggestions=BOT_SILENT_SUGGESTIONS)
    app.bot_data["response_builder"] = response_builder
    logger.info("[bot] Response builder initialized")
    
    safety_filter = SafetyFilter()
    app.bot_data["safety_filter"] = safety_filter
    logger.info("[bot] Safety filter initialized")
    
    logger.info("[bot] ✅ All components initialized")


# ==================== Main ====================

def main() -> None:
    """Main entry point."""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment")
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
    
    logger.info("=" * 60)
    logger.info("🤖 Starting Modular ChatGPT-grade Telegram Bot")
    logger.info(f"📦 Repository: {GITHUB_REPO}")
    logger.info(f"📁 Session path: {SESSION_BASE_PATH}")
    logger.info(f"⏱️  Rate limit: {BOT_RATE_MAX_MESSAGES} msgs / {BOT_RATE_WINDOW_SECONDS}s")
    logger.info(f"💾 Max messages per session: {BOT_MAX_MESSAGES_PER_SESSION}")
    logger.info(f"🎭 Default persona: {BOT_PERSONA}")
    
    if USER_ALLOWLIST:
        logger.info(f"🔐 Allowlist enabled: {len(USER_ALLOWLIST)} users")
    else:
        logger.warning("⚠️  Allowlist disabled - all users allowed")
    
    logger.info("=" * 60)
    
    # Build application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Initialize components
    initialize_components(app)
    
    # Add middleware (pre-process all updates)
    app.add_handler(
        MessageHandler(filters.ALL, authorization_middleware),
        group=-1  # Run before other handlers
    )
    
    # Register command handlers
    logger.info("[bot] Registering command handlers...")
    
    # Meta commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("model", cmd_model))
    app.add_handler(CommandHandler("provider", cmd_provider))
    app.add_handler(CommandHandler("persona", cmd_persona))
    
    # Session commands
    app.add_handler(CommandHandler("sessions", cmd_sessions))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("switch", cmd_switch))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("export", cmd_export))
    
    # Chat commands
    app.add_handler(CommandHandler("chat", cmd_chat))
    
    # Advanced commands
    app.add_handler(CommandHandler("summarize", cmd_summarize))
    app.add_handler(CommandHandler("continue", cmd_continue))
    app.add_handler(CommandHandler("regen", cmd_regen))
    app.add_handler(CommandHandler("share", cmd_share))
    
    # Fallback text handler
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )
    
    logger.info("[bot] ✅ All handlers registered")
    logger.info("[bot] 🚀 Starting polling...")
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("[bot] 👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"[bot] ❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
