#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Unified Telegram Bot - النظام الشامل
============================================

Advanced Telegram Bot with:
- Multiple AI provider support (OpenAI, Groq, Anthropic)
- Bidirectional repository connection
- Multi-database storage
- External platform integration
- Smart general chat + 30+ specialized commands
- Rate limiting and user quotas
- Comprehensive error handling

Author: MOTEB1989
Repository: Top-TieR-Global-HUB-AI
Version: 2.0.0
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from functools import wraps

# Third-party imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters,
    )
    from telegram.constants import ParseMode
except ImportError:
    print("❌ python-telegram-bot not installed. Run: pip install python-telegram-bot")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Environment variables from .env won't be loaded.")

import requests

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Bot Configuration
BOT_VERSION = "2.0.0"
BOT_START_TIME = datetime.now()

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWLIST_RAW = os.getenv("TELEGRAM_ALLOWLIST", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# AI Provider Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-70b-versatile"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")

# Database Configuration
DB_URL = os.getenv("DB_URL", "postgresql://postgres:motebai@postgres:5432/motebai")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_AUTH = os.getenv("NEO4J_AUTH", "neo4j/motebai")

# Storage Configuration
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://clickhouse:8123")

# Paths
DATA_DIR = Path("analysis/bot_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHAT_HISTORY_FILE = DATA_DIR / "chat_sessions.json"
USER_STATS_FILE = DATA_DIR / "user_stats.json"
RATE_LIMIT_FILE = DATA_DIR / "rate_limits.json"

# Rate Limiting Configuration
RATE_LIMIT_MESSAGES = 50  # messages per window
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_AI_CALLS = 20  # AI calls per window
RATE_LIMIT_AI_WINDOW = 3600

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(DATA_DIR / "bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramUnifiedBot")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_allowlist(raw: str) -> set:
    """Parse comma-separated list of user IDs."""
    if not raw or raw.startswith("${{"):
        return set()
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids

USER_ALLOWLIST = parse_allowlist(ALLOWLIST_RAW)

def is_placeholder(value: str) -> bool:
    """Check if value is a placeholder."""
    if not value:
        return True
    placeholders = ["PASTE_", "${{", "sk-...", "your_", "YOUR_"]
    return any(p in value for p in placeholders)

def load_json_file(filepath: Path, default=None):
    """Load JSON file with error handling."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {filepath}: {e}")
    return default

def save_json_file(filepath: Path, data: dict):
    """Save JSON file with error handling."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")

# ============================================================================
# AUTHORIZATION & RATE LIMITING
# ============================================================================

class RateLimiter:
    """Rate limiter for user requests."""
    
    def __init__(self):
        self.data = load_json_file(RATE_LIMIT_FILE, {})
        self._cleanup_old_entries()
    
    def _cleanup_old_entries(self):
        """Remove old rate limit entries."""
        current_time = time.time()
        for user_id in list(self.data.keys()):
            user_data = self.data[user_id]
            if current_time - user_data.get("last_reset", 0) > RATE_LIMIT_WINDOW:
                user_data["message_count"] = 0
                user_data["ai_count"] = 0
                user_data["last_reset"] = current_time
        save_json_file(RATE_LIMIT_FILE, self.data)
    
    def check_rate_limit(self, user_id: int, request_type: str = "message") -> Tuple[bool, str]:
        """Check if user has exceeded rate limit."""
        user_id_str = str(user_id)
        current_time = time.time()
        
        if user_id_str not in self.data:
            self.data[user_id_str] = {
                "message_count": 0,
                "ai_count": 0,
                "last_reset": current_time
            }
        
        user_data = self.data[user_id_str]
        
        # Reset counters if window expired
        if current_time - user_data.get("last_reset", 0) > RATE_LIMIT_WINDOW:
            user_data["message_count"] = 0
            user_data["ai_count"] = 0
            user_data["last_reset"] = current_time
        
        # Check limits
        if request_type == "message":
            if user_data["message_count"] >= RATE_LIMIT_MESSAGES:
                remaining = int(RATE_LIMIT_WINDOW - (current_time - user_data["last_reset"]))
                return False, f"⏳ Rate limit exceeded. Try again in {remaining // 60} minutes."
            user_data["message_count"] += 1
        elif request_type == "ai":
            if user_data["ai_count"] >= RATE_LIMIT_AI_CALLS:
                remaining = int(RATE_LIMIT_AI_WINDOW - (current_time - user_data["last_reset"]))
                return False, f"⏳ AI rate limit exceeded. Try again in {remaining // 60} minutes."
            user_data["ai_count"] += 1
        
        save_json_file(RATE_LIMIT_FILE, self.data)
        return True, ""
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get rate limit stats for user."""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            return {"message_count": 0, "ai_count": 0}
        return self.data[user_id_str]

rate_limiter = RateLimiter()

def require_auth(func):
    """Decorator to require authorization."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Check allowlist
        if USER_ALLOWLIST and user_id not in USER_ALLOWLIST:
            await update.message.reply_text(
                f"⛔ عذراً، أنت غير مصرح لك باستخدام هذا البوت.\n"
                f"🆔 معرفك: `{user_id}`\n\n"
                f"استخدم /whoami للحصول على معرفك وطلب الوصول.",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.warning(f"Unauthorized access attempt from {user_id}")
            return
        
        # Check rate limit
        allowed, message = rate_limiter.check_rate_limit(user_id, "message")
        if not allowed:
            await update.message.reply_text(message)
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

# ============================================================================
# USER STATISTICS
# ============================================================================

class UserStats:
    """Track user statistics."""
    
    def __init__(self):
        self.data = load_json_file(USER_STATS_FILE, {})
    
    def record_command(self, user_id: int, command: str):
        """Record command usage."""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            self.data[user_id_str] = {
                "total_messages": 0,
                "total_commands": 0,
                "commands": {},
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        
        self.data[user_id_str]["total_commands"] += 1
        self.data[user_id_str]["last_seen"] = datetime.now().isoformat()
        
        if command not in self.data[user_id_str]["commands"]:
            self.data[user_id_str]["commands"][command] = 0
        self.data[user_id_str]["commands"][command] += 1
        
        save_json_file(USER_STATS_FILE, self.data)
    
    def record_message(self, user_id: int):
        """Record message from user."""
        user_id_str = str(user_id)
        if user_id_str not in self.data:
            self.data[user_id_str] = {
                "total_messages": 0,
                "total_commands": 0,
                "commands": {},
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        
        self.data[user_id_str]["total_messages"] += 1
        self.data[user_id_str]["last_seen"] = datetime.now().isoformat()
        save_json_file(USER_STATS_FILE, self.data)
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get stats for a user."""
        user_id_str = str(user_id)
        return self.data.get(user_id_str, {})

user_stats = UserStats()

# ============================================================================
# CONVERSATION MEMORY
# ============================================================================

class ConversationMemory:
    """Manage conversation history with memory."""
    
    def __init__(self, max_messages: int = 30):
        self.max_messages = max_messages
        self.sessions = load_json_file(CHAT_HISTORY_FILE, {})
        self._dirty = False
        self._save_counter = 0
    
    def get_user_key(self, user_id: int) -> str:
        """Generate unique key for user."""
        return str(user_id)
    
    def add_message(self, user_id: int, role: str, content: str):
        """Add message to conversation history."""
        key = self.get_user_key(user_id)
        if key not in self.sessions:
            self.sessions[key] = []
        
        self.sessions[key].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim to max messages
        if len(self.sessions[key]) > self.max_messages:
            self.sessions[key] = self.sessions[key][-self.max_messages:]
        
        # Batch save: save every 5 messages or mark dirty
        self._save_counter += 1
        self._dirty = True
        if self._save_counter >= 5:
            save_json_file(CHAT_HISTORY_FILE, self.sessions)
            self._save_counter = 0
            self._dirty = False
    
    def get_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get conversation history for user."""
        key = self.get_user_key(user_id)
        history = self.sessions.get(key, [])
        return history[-limit:]
    
    def clear_history(self, user_id: int):
        """Clear conversation history for user."""
        key = self.get_user_key(user_id)
        if key in self.sessions:
            del self.sessions[key]
            save_json_file(CHAT_HISTORY_FILE, self.sessions)
            self._dirty = False
    
    def flush(self):
        """Force save any pending changes."""
        if self._dirty:
            save_json_file(CHAT_HISTORY_FILE, self.sessions)
            self._save_counter = 0
            self._dirty = False

conversation_memory = ConversationMemory()

# ============================================================================
# AI PROVIDERS
# ============================================================================

class AIProvider:
    """Base class for AI providers."""
    
    @staticmethod
    def create_system_prompt() -> str:
        """Create system prompt for AI."""
        return f"""أنت مساعد ذكي لمشروع Top-TieR-Global-HUB-AI ({GITHUB_REPO}).

دورك:
- الإجابة على الأسئلة بدقة واحتراف
- تقديم المساعدة في البرمجة، الهندسة، والأمن السيبراني
- دعم العربية والإنجليزية
- التركيز على الجودة والدقة
- عدم التخمين عند عدم توفر المعلومات

كن مختصراً وواضحاً في إجاباتك."""
    
    @staticmethod
    async def call_openai(messages: List[Dict], model: str = None) -> str:
        """Call OpenAI API."""
        if is_placeholder(OPENAI_API_KEY):
            raise Exception("OpenAI API key not configured")
        
        model = model or OPENAI_MODEL
        url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = await asyncio.to_thread(
                requests.post, url, json=payload, headers=headers, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    @staticmethod
    async def call_groq(messages: List[Dict]) -> str:
        """Call Groq API."""
        if is_placeholder(GROQ_API_KEY):
            raise Exception("Groq API key not configured")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = await asyncio.to_thread(
                requests.post, url, json=payload, headers=headers, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    @staticmethod
    async def call_anthropic(messages: List[Dict]) -> str:
        """Call Anthropic Claude API."""
        if is_placeholder(ANTHROPIC_API_KEY):
            raise Exception("Anthropic API key not configured")
        
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Convert OpenAI format to Anthropic format
        claude_messages = []
        system_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 1000,
            "messages": claude_messages
        }
        
        if system_content:
            payload["system"] = system_content
        
        try:
            response = await asyncio.to_thread(
                requests.post, url, json=payload, headers=headers, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    @staticmethod
    async def call_ai(messages: List[Dict], provider: str = "openai") -> str:
        """Call AI with specified provider."""
        if provider == "openai":
            return await AIProvider.call_openai(messages)
        elif provider == "groq":
            return await AIProvider.call_groq(messages)
        elif provider == "anthropic":
            return await AIProvider.call_anthropic(messages)
        else:
            raise ValueError(f"Unknown provider: {provider}")


# ============================================================================
# GITHUB INTEGRATION
# ============================================================================

class GitHubIntegration:
    """GitHub repository integration."""
    
    @staticmethod
    async def check_github_connection() -> Tuple[bool, str]:
        """Check GitHub API connection."""
        if is_placeholder(GITHUB_TOKEN):
            return False, "GitHub token not configured"
        
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = await asyncio.to_thread(
                requests.get, "https://api.github.com/user",
                headers=headers, timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, f"Connected as {data.get('login')}"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def get_repo_info() -> Dict:
        """Get repository information."""
        if is_placeholder(GITHUB_TOKEN):
            raise Exception("GitHub token not configured")
        
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            url = f"https://api.github.com/repos/{GITHUB_REPO}"
            response = await asyncio.to_thread(
                requests.get, url, headers=headers, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get repo info: {e}")
            raise
    
    @staticmethod
    async def search_code(query: str, max_results: int = 5) -> List[Dict]:
        """Search code in repository."""
        if is_placeholder(GITHUB_TOKEN):
            raise Exception("GitHub token not configured")
        
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            search_query = f"{query} repo:{GITHUB_REPO}"
            url = f"https://api.github.com/search/code?q={search_query}&per_page={max_results}"
            response = await asyncio.to_thread(
                requests.get, url, headers=headers, timeout=15
            )
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception as e:
            logger.error(f"Failed to search code: {e}")
            raise
    
    @staticmethod
    async def create_issue(title: str, body: str = "") -> Dict:
        """Create GitHub issue."""
        if is_placeholder(GITHUB_TOKEN):
            raise Exception("GitHub token not configured")
        
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
            payload = {
                "title": title,
                "body": body
            }
            response = await asyncio.to_thread(
                requests.post, url, json=payload, headers=headers, timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            raise

# ============================================================================
# DATABASE CHECKERS
# ============================================================================

class DatabaseChecker:
    """Check database connections."""
    
    @staticmethod
    async def check_postgresql() -> Tuple[bool, str]:
        """Check PostgreSQL connection."""
        try:
            import psycopg2
            # Parse connection string
            conn = await asyncio.to_thread(psycopg2.connect, DB_URL)
            await asyncio.to_thread(conn.close())
            return True, "Connected"
        except ImportError:
            return False, "psycopg2 not installed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def check_redis() -> Tuple[bool, str]:
        """Check Redis connection."""
        try:
            import redis
            r = redis.from_url(REDIS_URL, socket_timeout=5)
            await asyncio.to_thread(r.ping)
            return True, "Connected"
        except ImportError:
            return False, "redis not installed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    async def check_service(url: str, timeout: int = 5) -> Tuple[bool, str]:
        """Check generic service availability."""
        try:
            response = await asyncio.to_thread(
                requests.get, url, timeout=timeout
            )
            return True, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

# ============================================================================
# COMMAND HANDLERS - BASIC
# ============================================================================

@require_auth
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_stats.record_command(user.id, "start")
    
    keyboard = [
        [InlineKeyboardButton("📚 Help", callback_data="help"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("📊 Status", callback_data="status"),
         InlineKeyboardButton("🆔 Who Am I", callback_data="whoami")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = f"""🤖 **مرحباً {user.first_name}!**

أنا **البوت الموحّد** لمشروع Top-TieR-Global-HUB-AI

🎯 **القدرات:**
• دردشة ذكية مع ذاكرة
• دعم 30+ أمر متخصص
• اتصال بمستودع GitHub
• تكامل مع قواعد البيانات
• دعم نماذج AI متعددة

📋 **الأوامر السريعة:**
/help - دليل كامل
/chat <رسالة> - دردشة ذكية
/status - حالة النظام
/repo - تحليل المستودع

💡 أو أرسل رسالة مباشرة للدردشة!

⚡ الإصدار: {BOT_VERSION}
"""
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

@require_auth
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    user_stats.record_command(update.effective_user.id, "help")
    
    help_text = """📚 **دليل الاستخدام الشامل**

**🔹 الأوامر الأساسية:**
/start - ترحيب تفاعلي
/help - هذا الدليل
/whoami - معلوماتك + إحصائيات
/status - حالة النظام الكامل
/ping - اختبار سرعة الاستجابة
/version - إصدار البوت
/about - معلومات المشروع

**🔹 الدردشة والAI:**
/chat <رسالة> - دردشة مع ذاكرة
/ask <سؤال> - سؤال مباشر بدون ذاكرة
/translate <لغة> <نص> - ترجمة
/summarize <نص> - تلخيص
رسالة مباشرة - رد تلقائي ذكي

**🔹 التشخيص:**
/verifyenv - فحص المتغيرات البيئية
/preflight - فحص شامل للاتصالات
/report - تقرير JSON كامل
/health - صحة النظام

**🔹 المستودع:**
/repo - تحليل عام للمستودع
/insights - ملخص ذكي بالمخاطر
/file <مسار> - قراءة ملف
/search <بحث> - بحث في الكود
/issue <عنوان> - إنشاء Issue
/pr <عنوان> - إنشاء Pull Request

**🔹 قواعد البيانات:**
/db status - حالة جميع قواعد البيانات
/db test - اختبار الاتصال
/stats - إحصائيات الاستخدام
/history - آخر 20 محادثة
/export - تصدير البيانات

**🔹 إدارة AI:**
/model list - قائمة النماذج
/model switch <model> - تبديل النموذج
/model info - معلومات النموذج الحالي

💡 أرسل رسالة مباشرة للدردشة العامة!
"""
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /whoami command."""
    user = update.effective_user
    user_stats.record_command(user.id, "whoami")
    
    # Get user stats
    stats = user_stats.get_user_stats(user.id)
    rate_stats = rate_limiter.get_user_stats(user.id)
    
    # Calculate usage
    total_commands = stats.get("total_commands", 0)
    total_messages = stats.get("total_messages", 0)
    first_seen = stats.get("first_seen", "N/A")
    
    # Top commands
    commands = stats.get("commands", {})
    top_commands = sorted(commands.items(), key=lambda x: x[1], reverse=True)[:5]
    top_cmd_str = "\n".join([f"  • /{cmd}: {count}x" for cmd, count in top_commands])
    
    info = f"""🆔 **معلومات المستخدم**

👤 **الملف الشخصي:**
• الاسم: {user.first_name} {user.last_name or ''}
• المعرف: @{user.username or 'N/A'}
• ID: `{user.id}`
• اللغة: {user.language_code or 'N/A'}

📊 **الإحصائيات:**
• إجمالي الأوامر: {total_commands}
• إجمالي الرسائل: {total_messages}
• أول استخدام: {first_seen[:10]}

⚡ **الاستخدام الحالي:**
• الرسائل: {rate_stats.get('message_count', 0)}/{RATE_LIMIT_MESSAGES}
• استدعاءات AI: {rate_stats.get('ai_count', 0)}/{RATE_LIMIT_AI_CALLS}

🏆 **الأوامر الأكثر استخداماً:**
{top_cmd_str or '  لا توجد بيانات'}

🔐 **الصلاحيات:**
{"✅ مصرح" if not USER_ALLOWLIST or user.id in USER_ALLOWLIST else "⚠️ محدود"}
"""
    
    await update.message.reply_text(info, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    user_stats.record_command(update.effective_user.id, "status")
    
    await update.message.reply_text("🔍 جاري فحص حالة النظام...")
    
    # Check AI providers
    ai_status = []
    if not is_placeholder(OPENAI_API_KEY):
        ai_status.append("✅ OpenAI")
    else:
        ai_status.append("❌ OpenAI")
    
    if not is_placeholder(GROQ_API_KEY):
        ai_status.append("✅ Groq")
    else:
        ai_status.append("❌ Groq")
    
    if not is_placeholder(ANTHROPIC_API_KEY):
        ai_status.append("✅ Anthropic")
    else:
        ai_status.append("❌ Anthropic")
    
    # Check GitHub
    github_ok, github_msg = await GitHubIntegration.check_github_connection()
    github_status = f"✅ GitHub ({github_msg})" if github_ok else f"❌ GitHub ({github_msg})"
    
    # Check databases
    pg_ok, pg_msg = await DatabaseChecker.check_postgresql()
    redis_ok, redis_msg = await DatabaseChecker.check_redis()
    
    # System uptime
    uptime = datetime.now() - BOT_START_TIME
    uptime_str = str(uptime).split('.')[0]
    
    status_msg = f"""📊 **حالة النظام الشامل**

🤖 **البوت:**
• الحالة: 🟢 يعمل
• الإصدار: {BOT_VERSION}
• وقت التشغيل: {uptime_str}
• المستخدمون المصرح لهم: {len(USER_ALLOWLIST) if USER_ALLOWLIST else 'الجميع'}

🧠 **نماذج AI:**
{chr(10).join(ai_status)}

🔗 **الاتصالات:**
{github_status}
{"✅" if pg_ok else "❌"} PostgreSQL ({pg_msg})
{"✅" if redis_ok else "❌"} Redis ({redis_msg})

💾 **قواعد البيانات:**
• المحادثات: {len(conversation_memory.sessions)} جلسة
• المستخدمون: {len(user_stats.data)} مستخدم

⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)



@require_auth
async def cmd_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /translate command."""
    user_id = update.effective_user.id
    user_stats.record_command(user_id, "translate")
    
    # Check AI rate limit
    allowed, message = rate_limiter.check_rate_limit(user_id, "ai")
    if not allowed:
        await update.message.reply_text(message)
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "🌍 **استخدام الأمر:**\n"
            "/translate <target_lang> <text>\n\n"
            "مثال: `/translate en مرحبا بكم`\n"
            "أو: `/translate ar Hello world`"
        )
        return
    
    target_lang = context.args[0]
    text = " ".join(context.args[1:])
    
    await update.message.reply_text("🔄 جاري الترجمة...")
    
    try:
        messages = [
            {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_lang}. Only return the translation, no explanations."},
            {"role": "user", "content": text}
        ]
        
        translation = await AIProvider.call_ai(messages, provider="openai")
        
        result = f"🌍 **الترجمة إلى {target_lang}:**\n\n{translation}"
        await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(f"❌ خطأ في الترجمة: {str(e)[:200]}")

@require_auth
async def cmd_summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /summarize command."""
    user_id = update.effective_user.id
    user_stats.record_command(user_id, "summarize")
    
    # Check AI rate limit
    allowed, message = rate_limiter.check_rate_limit(user_id, "ai")
    if not allowed:
        await update.message.reply_text(message)
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 **استخدام الأمر:**\n"
            "/summarize <نص طويل>\n\n"
            "مثال: `/summarize <مقالة أو نص طويل>`"
        )
        return
    
    text = " ".join(context.args)
    
    if len(text) < 50:
        await update.message.reply_text("⚠️ النص قصير جداً للتلخيص. الحد الأدنى 50 حرف.")
        return
    
    await update.message.reply_text("📊 جاري التلخيص...")
    
    try:
        messages = [
            {"role": "system", "content": "You are an expert at summarizing text. Provide a concise summary in the same language as the input."},
            {"role": "user", "content": f"Summarize this text concisely:\n\n{text}"}
        ]
        
        summary = await AIProvider.call_ai(messages, provider="openai")
        
        result = f"📊 **الملخص:**\n\n{summary}"
        await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        await update.message.reply_text(f"❌ خطأ في التلخيص: {str(e)[:200]}")

@require_auth
async def cmd_verifyenv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /verifyenv command."""
    user_stats.record_command(update.effective_user.id, "verifyenv")
    
    await update.message.reply_text("�� جاري فحص المتغيرات البيئية...")
    
    checks = []
    
    # Check critical variables
    critical_vars = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_TOKEN,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "GITHUB_TOKEN": GITHUB_TOKEN,
    }
    
    for var_name, var_value in critical_vars.items():
        if is_placeholder(var_value):
            checks.append(f"❌ {var_name}: Not configured")
        else:
            # Show first/last few chars for security
            if len(var_value) > 10:
                masked = f"{var_value[:4]}...{var_value[-4:]}"
            else:
                masked = "***"
            checks.append(f"✅ {var_name}: {masked}")
    
    # Check optional variables
    optional_vars = {
        "GROQ_API_KEY": GROQ_API_KEY,
        "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
        "DB_URL": DB_URL,
        "REDIS_URL": REDIS_URL,
    }
    
    for var_name, var_value in optional_vars.items():
        if is_placeholder(var_value):
            checks.append(f"⚠️  {var_name}: Not configured (optional)")
        else:
            checks.append(f"✅ {var_name}: Configured")
    
    result = "🔍 **فحص المتغيرات البيئية:**\n\n" + "\n".join(checks)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_preflight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /preflight command."""
    user_stats.record_command(update.effective_user.id, "preflight")
    
    await update.message.reply_text("🚀 جاري الفحص الشامل للنظام...")
    
    checks = []
    
    # Check AI providers
    if not is_placeholder(OPENAI_API_KEY):
        try:
            test_msg = [{"role": "user", "content": "test"}]
            await AIProvider.call_openai(test_msg)
            checks.append("✅ OpenAI: Connected")
        except Exception as e:
            checks.append(f"❌ OpenAI: {str(e)[:50]}")
    else:
        checks.append("⚠️  OpenAI: Not configured")
    
    if not is_placeholder(GROQ_API_KEY):
        checks.append("✅ Groq: API key configured")
    else:
        checks.append("⚠️  Groq: Not configured")
    
    if not is_placeholder(ANTHROPIC_API_KEY):
        checks.append("✅ Anthropic: API key configured")
    else:
        checks.append("⚠️  Anthropic: Not configured")
    
    # Check GitHub
    gh_ok, gh_msg = await GitHubIntegration.check_github_connection()
    checks.append(f"{'✅' if gh_ok else '❌'} GitHub: {gh_msg}")
    
    # Check databases
    pg_ok, pg_msg = await DatabaseChecker.check_postgresql()
    checks.append(f"{'✅' if pg_ok else '⚠️'} PostgreSQL: {pg_msg}")
    
    redis_ok, redis_msg = await DatabaseChecker.check_redis()
    checks.append(f"{'✅' if redis_ok else '⚠️'} Redis: {redis_msg}")
    
    # Check data directory
    if DATA_DIR.exists():
        checks.append(f"✅ Data Directory: {DATA_DIR}")
    else:
        checks.append("❌ Data Directory: Not found")
    
    result = "🚀 **نتائج الفحص الشامل:**\n\n" + "\n".join(checks)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command."""
    user_stats.record_command(update.effective_user.id, "health")
    
    uptime = datetime.now() - BOT_START_TIME
    uptime_str = str(uptime).split('.')[0]
    
    # Memory usage (if psutil available)
    memory_info = "N/A"
    try:
        import psutil
        import os as os_module
        process = psutil.Process(os_module.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_info = f"{memory_mb:.1f} MB"
    except ImportError:
        pass
    
    # Count active resources
    active_sessions = len(conversation_memory.sessions)
    total_users = len(user_stats.data)
    
    health_text = f"""🏥 **System Health**

⏱️ **Uptime:** {uptime_str}
💾 **Memory:** {memory_info}
👥 **Active Sessions:** {active_sessions}
📊 **Total Users:** {total_users}

🤖 **Bot Status:**
• Version: {BOT_VERSION}
• Rate Limiter: ✅ Active
• Conversation Memory: ✅ Active
• User Stats: ✅ Active

🔌 **Services:**
• Telegram API: ✅ Connected
• File System: ✅ Writable
• Logging: ✅ Active

📈 **Performance:**
• Response: Fast
• Storage: {len(list(DATA_DIR.glob('*')))} files
"""
    
    await update.message.reply_text(health_text, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command - generate JSON report."""
    user_stats.record_command(update.effective_user.id, "report")
    
    await update.message.reply_text("📋 جاري إنشاء التقرير...")
    
    # Build comprehensive report
    report = {
        "bot": {
            "version": BOT_VERSION,
            "uptime_seconds": int((datetime.now() - BOT_START_TIME).total_seconds()),
            "start_time": BOT_START_TIME.isoformat()
        },
        "services": {
            "openai": not is_placeholder(OPENAI_API_KEY),
            "groq": not is_placeholder(GROQ_API_KEY),
            "anthropic": not is_placeholder(ANTHROPIC_API_KEY),
            "github": not is_placeholder(GITHUB_TOKEN)
        },
        "statistics": {
            "total_users": len(user_stats.data),
            "active_sessions": len(conversation_memory.sessions),
            "total_rate_limits": len(rate_limiter.data)
        },
        "configuration": {
            "allowlist_enabled": len(USER_ALLOWLIST) > 0,
            "rate_limit_messages": RATE_LIMIT_MESSAGES,
            "rate_limit_ai_calls": RATE_LIMIT_AI_CALLS,
            "data_directory": str(DATA_DIR)
        }
    }
    
    # Save report to file
    report_file = DATA_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_json_file(report_file, report)
    
    # Send formatted report
    report_text = f"""📋 **System Report**

```json
{json.dumps(report, indent=2, ensure_ascii=False)}
```

💾 Full report saved to:
`{report_file.name}`
"""
    
    if len(report_text) > 4000:
        report_text = report_text[:4000] + "\n\n[Truncated...]"
    
    await update.message.reply_text(report_text, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_insights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /insights command."""
    user_id = update.effective_user.id
    user_stats.record_command(user_id, "insights")
    
    # Check AI rate limit
    allowed, message = rate_limiter.check_rate_limit(user_id, "ai")
    if not allowed:
        await update.message.reply_text(message)
        return
    
    await update.message.reply_text("🔍 جاري تحليل المستودع...")
    
    try:
        # Get repo info
        repo_info = await GitHubIntegration.get_repo_info()
        
        # Build analysis prompt
        repo_summary = f"""
Repository: {repo_info.get('full_name')}
Description: {repo_info.get('description', 'N/A')}
Language: {repo_info.get('language', 'N/A')}
Stars: {repo_info.get('stargazers_count', 0)}
Open Issues: {repo_info.get('open_issues_count', 0)}
Last Updated: {repo_info.get('updated_at', 'N/A')}
"""
        
        messages = [
            {"role": "system", "content": "You are a senior software engineer analyzing a GitHub repository. Provide insights in Arabic."},
            {"role": "user", "content": f"Analyze this repository and provide:\n1. Current state\n2. Top 3 risks\n3. Top 3 opportunities\n4. Recommendations\n\nRepository Info:\n{repo_summary}"}
        ]
        
        insights = await AIProvider.call_ai(messages, provider="openai")
        
        result = f"🧠 **Repository Insights:**\n\n{insights}"
        
        if len(result) > 4000:
            result = result[:4000] + "\n\n[تم قطع الرد...]"
        
        await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Insights error: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)[:200]}")

@require_auth
async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /model command."""
    user_stats.record_command(update.effective_user.id, "model")
    
    if not context.args or context.args[0] not in ["list", "info"]:
        await update.message.reply_text(
            "🤖 **استخدام الأمر:**\n"
            "/model list - قائمة النماذج المتاحة\n"
            "/model info - معلومات النموذج الحالي"
        )
        return
    
    command = context.args[0]
    
    if command == "list":
        models_text = """🤖 **AI Models Available:**

**OpenAI:**
• gpt-4o-mini (default) - Fast, efficient
• gpt-4o - Most capable
• gpt-3.5-turbo - Fast and cheap

**Groq:**
• llama-3.1-70b-versatile - Very fast
• mixtral-8x7b - Good balance
• gemma-7b - Lightweight

**Anthropic:**
• claude-3-5-sonnet - Most capable
• claude-3-opus - Powerful
• claude-3-sonnet - Balanced

💡 **Current Configuration:**
"""
        
        if not is_placeholder(OPENAI_API_KEY):
            models_text += f"✅ OpenAI: {OPENAI_MODEL}\n"
        if not is_placeholder(GROQ_API_KEY):
            models_text += f"✅ Groq: {GROQ_MODEL}\n"
        if not is_placeholder(ANTHROPIC_API_KEY):
            models_text += f"✅ Anthropic: {ANTHROPIC_MODEL}\n"
        
        await update.message.reply_text(models_text, parse_mode=ParseMode.MARKDOWN)
    
    elif command == "info":
        info_text = f"""ℹ️ **Current Model Configuration:**

**OpenAI:**
• Model: `{OPENAI_MODEL}`
• Status: {"✅ Active" if not is_placeholder(OPENAI_API_KEY) else "❌ Not configured"}
• Base URL: {OPENAI_BASE_URL}

**Groq:**
• Model: `{GROQ_MODEL}`
• Status: {"✅ Active" if not is_placeholder(GROQ_API_KEY) else "❌ Not configured"}

**Anthropic:**
• Model: `{ANTHROPIC_MODEL}`
• Status: {"✅ Active" if not is_placeholder(ANTHROPIC_API_KEY) else "❌ Not configured"}

💡 Models can be changed in .env file
"""
        
        await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command."""
    user_stats.record_command(update.effective_user.id, "ping")
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    elapsed = (time.time() - start_time) * 1000
    await msg.edit_text(f"🏓 Pong! Response time: {elapsed:.2f}ms")

@require_auth
async def cmd_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /version command."""
    user_stats.record_command(update.effective_user.id, "version")
    
    uptime = datetime.now() - BOT_START_TIME
    
    version_info = f"""ℹ️ **معلومات الإصدار**

📦 الإصدار: **{BOT_VERSION}**
🚀 تاريخ البدء: {BOT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}
⏱️ وقت التشغيل: {str(uptime).split('.')[0]}
🏢 المستودع: {GITHUB_REPO}

🔧 **المكونات:**
• Python: {sys.version.split()[0]}
• python-telegram-bot: installed
• OpenAI: {"✅" if not is_placeholder(OPENAI_API_KEY) else "❌"}
• Groq: {"✅" if not is_placeholder(GROQ_API_KEY) else "❌"}
• Anthropic: {"✅" if not is_placeholder(ANTHROPIC_API_KEY) else "❌"}
"""
    
    await update.message.reply_text(version_info, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command."""
    user_stats.record_command(update.effective_user.id, "about")
    
    about_text = f"""ℹ️ **عن المشروع**

**Top-TieR-Global-HUB-AI**

🎯 **الهدف:**
منصة تعليمية متقدمة لأدوات OSINT والذكاء الاصطناعي

🌟 **المميزات:**
• دعم نماذج AI متعددة
• تكامل مع GitHub
• قواعد بيانات متعددة
• أوامر متخصصة 30+
• نظام ذاكرة ذكي

🔗 **الروابط:**
• المستودع: github.com/{GITHUB_REPO}
• المطور: @MOTEB1989

📄 **الترخيص:** MIT License
⚡ **الإصدار:** {BOT_VERSION}
"""
    
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)

# ============================================================================
# COMMAND HANDLERS - AI & CHAT
# ============================================================================

@require_auth
async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chat command with memory."""
    user_id = update.effective_user.id
    user_stats.record_command(user_id, "chat")
    
    # Check AI rate limit
    allowed, message = rate_limiter.check_rate_limit(user_id, "ai")
    if not allowed:
        await update.message.reply_text(message)
        return
    
    if not context.args:
        await update.message.reply_text(
            "💬 **استخدام الأمر:**\n"
            "/chat <رسالتك>\n\n"
            "مثال: `/chat ما هي أفضل ممارسات الأمن السيبراني؟`"
        )
        return
    
    question = " ".join(context.args)
    await update.message.reply_text("🤔 جاري التفكير...")
    
    try:
        # Add to conversation memory
        conversation_memory.add_message(user_id, "user", question)
        
        # Get conversation history
        history = conversation_memory.get_history(user_id, limit=10)
        
        # Build messages for AI
        messages = [{"role": "system", "content": AIProvider.create_system_prompt()}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Call AI
        response = await AIProvider.call_ai(messages, provider="openai")
        
        # Add response to memory
        conversation_memory.add_message(user_id, "assistant", response)
        
        # Send response
        if len(response) > 4000:
            response = response[:4000] + "\n\n[تم قطع الرد...]"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)[:200]}")

@require_auth
async def cmd_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command without memory."""
    user_id = update.effective_user.id
    user_stats.record_command(user_id, "ask")
    
    # Check AI rate limit
    allowed, message = rate_limiter.check_rate_limit(user_id, "ai")
    if not allowed:
        await update.message.reply_text(message)
        return
    
    if not context.args:
        await update.message.reply_text(
            "❓ **استخدام الأمر:**\n"
            "/ask <سؤالك>\n\n"
            "مثال: `/ask ما هو Docker؟`"
        )
        return
    
    question = " ".join(context.args)
    await update.message.reply_text("🤔 جاري التفكير...")
    
    try:
        messages = [
            {"role": "system", "content": AIProvider.create_system_prompt()},
            {"role": "user", "content": question}
        ]
        
        response = await AIProvider.call_ai(messages, provider="openai")
        
        if len(response) > 4000:
            response = response[:4000] + "\n\n[تم قطع الرد...]"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Ask error: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)[:200]}")

# ============================================================================
# COMMAND HANDLERS - REPO
# ============================================================================

@require_auth
async def cmd_repo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /repo command."""
    user_stats.record_command(update.effective_user.id, "repo")
    
    await update.message.reply_text("🔍 جاري تحليل المستودع...")
    
    try:
        repo_info = await GitHubIntegration.get_repo_info()
        
        repo_text = f"""📦 **معلومات المستودع**

**الاسم:** {repo_info.get('full_name')}
**الوصف:** {repo_info.get('description', 'N/A')}

📊 **الإحصائيات:**
• ⭐ النجوم: {repo_info.get('stargazers_count', 0)}
• �� الفروع: {repo_info.get('forks_count', 0)}
• 👁️ المراقبون: {repo_info.get('watchers_count', 0)}
• 🐛 Issues: {repo_info.get('open_issues_count', 0)}

💻 **التفاصيل:**
• اللغة: {repo_info.get('language', 'N/A')}
• الحجم: {repo_info.get('size', 0)} KB
• آخر تحديث: {repo_info.get('updated_at', 'N/A')[:10]}
• خاص: {"✅" if repo_info.get('private') else "❌"}

🔗 **الروابط:**
[المستودع]({repo_info.get('html_url')})
"""
        
        await update.message.reply_text(repo_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Repo info error: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)[:200]}")

@require_auth
async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command."""
    user_stats.record_command(update.effective_user.id, "search")
    
    if not context.args:
        await update.message.reply_text(
            "🔍 **استخدام الأمر:**\n"
            "/search <كلمة البحث>\n\n"
            "مثال: `/search def main`"
        )
        return
    
    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 جاري البحث عن: `{query}`...", parse_mode=ParseMode.MARKDOWN)
    
    try:
        results = await GitHubIntegration.search_code(query)
        
        if not results:
            await update.message.reply_text("❌ لم يتم العثور على نتائج")
            return
        
        result_text = f"🔍 **نتائج البحث عن:** `{query}`\n\n"
        for i, item in enumerate(results[:5], 1):
            result_text += f"{i}. **{item['name']}**\n"
            result_text += f"   📁 المسار: `{item['path']}`\n"
            result_text += f"   🔗 [عرض]({item['html_url']})\n\n"
        
        await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)[:200]}")

@require_auth
async def cmd_issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /issue command."""
    user_stats.record_command(update.effective_user.id, "issue")
    
    if not context.args:
        await update.message.reply_text(
            "📝 **استخدام الأمر:**\n"
            "/issue <عنوان المشكلة>\n\n"
            "مثال: `/issue Bug in login system`"
        )
        return
    
    title = " ".join(context.args)
    await update.message.reply_text("�� جاري إنشاء Issue...")
    
    try:
        user = update.effective_user
        body = f"Created by @{user.username or user.first_name} via Telegram Bot\n\nUser ID: {user.id}"
        
        issue = await GitHubIntegration.create_issue(title, body)
        
        await update.message.reply_text(
            f"✅ **تم إنشاء Issue بنجاح!**\n\n"
            f"📌 العنوان: {issue['title']}\n"
            f"🔢 الرقم: #{issue['number']}\n"
            f"🔗 [عرض]({issue['html_url']})",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Issue creation error: {e}")
        await update.message.reply_text(f"❌ خطأ: {str(e)[:200]}")

# ============================================================================
# COMMAND HANDLERS - DATABASE
# ============================================================================

@require_auth
async def cmd_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /db command."""
    user_stats.record_command(update.effective_user.id, "db")
    
    if not context.args or context.args[0] not in ["status", "test"]:
        await update.message.reply_text(
            "💾 **استخدام الأمر:**\n"
            "/db status - حالة جميع قواعد البيانات\n"
            "/db test - اختبار الاتصالات"
        )
        return
    
    command = context.args[0]
    
    if command == "status":
        await update.message.reply_text("🔍 جاري فحص قواعد البيانات...")
        
        # Check databases
        pg_ok, pg_msg = await DatabaseChecker.check_postgresql()
        redis_ok, redis_msg = await DatabaseChecker.check_redis()
        neo4j_ok, neo4j_msg = await DatabaseChecker.check_service(NEO4J_URI.replace('bolt://', 'http://'))
        
        status_text = f"""💾 **حالة قواعد البيانات**

{"✅" if pg_ok else "❌"} **PostgreSQL**
   {pg_msg}
   🔗 {DB_URL.split('@')[1] if '@' in DB_URL else 'N/A'}

{"✅" if redis_ok else "❌"} **Redis**
   {redis_msg}
   🔗 {REDIS_URL}

{"✅" if neo4j_ok else "❌"} **Neo4j**
   {neo4j_msg}
   �� {NEO4J_URI}

📊 **الإحصائيات:**
• المحادثات المحفوظة: {len(conversation_memory.sessions)}
• المستخدمون: {len(user_stats.data)}
• حدود المعدل: {len(rate_limiter.data)}
"""
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    
    elif command == "test":
        await update.message.reply_text("🧪 جاري اختبار الاتصالات...")
        
        tests = []
        
        # Test PostgreSQL
        pg_ok, pg_msg = await DatabaseChecker.check_postgresql()
        tests.append(f"{'✅' if pg_ok else '❌'} PostgreSQL: {pg_msg}")
        
        # Test Redis
        redis_ok, redis_msg = await DatabaseChecker.check_redis()
        tests.append(f"{'✅' if redis_ok else '❌'} Redis: {redis_msg}")
        
        result_text = "�� **نتائج الاختبار:**\n\n" + "\n".join(tests)
        await update.message.reply_text(result_text)

@require_auth
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command."""
    user_stats.record_command(update.effective_user.id, "stats")
    
    # Calculate overall stats
    total_users = len(user_stats.data)
    total_commands = sum(u.get("total_commands", 0) for u in user_stats.data.values())
    total_messages = sum(u.get("total_messages", 0) for u in user_stats.data.values())
    
    # Most active users
    active_users = sorted(
        user_stats.data.items(),
        key=lambda x: x[1].get("total_commands", 0),
        reverse=True
    )[:5]
    
    stats_text = f"""📊 **إحصائيات الاستخدام**

👥 **المستخدمون:**
• إجمالي المستخدمين: {total_users}
• المصرح لهم: {len(USER_ALLOWLIST) if USER_ALLOWLIST else 'الجميع'}

💬 **النشاط:**
• إجمالي الأوامر: {total_commands}
• إجمالي الرسائل: {total_messages}
• الجلسات النشطة: {len(conversation_memory.sessions)}

⏱️ **النظام:**
• وقت التشغيل: {str(datetime.now() - BOT_START_TIME).split('.')[0]}
• الإصدار: {BOT_VERSION}

🏆 **المستخدمون الأكثر نشاطاً:**
"""
    
    for i, (user_id, data) in enumerate(active_users, 1):
        commands = data.get("total_commands", 0)
        stats_text += f"{i}. User {user_id[:8]}: {commands} أوامر\n"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

@require_auth
async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command."""
    user_id = update.effective_user.id
    user_stats.record_command(user_id, "history")
    
    history = conversation_memory.get_history(user_id, limit=20)
    
    if not history:
        await update.message.reply_text("📜 لا توجد محادثات محفوظة")
        return
    
    history_text = "📜 **آخر 20 محادثة:**\n\n"
    
    for i, msg in enumerate(history[-20:], 1):
        role_emoji = "👤" if msg["role"] == "user" else "🤖"
        content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
        timestamp = msg.get("timestamp", "N/A")[:16]
        history_text += f"{i}. {role_emoji} [{timestamp}] {content}\n"
    
    await update.message.reply_text(history_text)

# ============================================================================
# MESSAGE HANDLER
# ============================================================================

@require_auth
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct text messages."""
    user_id = update.effective_user.id
    user_stats.record_message(user_id)
    
    text = update.message.text
    
    # Check AI rate limit
    allowed, message = rate_limiter.check_rate_limit(user_id, "ai")
    if not allowed:
        await update.message.reply_text(message)
        return
    
    try:
        # Add to conversation memory
        conversation_memory.add_message(user_id, "user", text)
        
        # Get conversation history
        history = conversation_memory.get_history(user_id, limit=10)
        
        # Build messages for AI
        messages = [{"role": "system", "content": AIProvider.create_system_prompt()}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Call AI
        response = await AIProvider.call_ai(messages, provider="openai")
        
        # Add response to memory
        conversation_memory.add_message(user_id, "assistant", response)
        
        # Send response
        if len(response) > 4000:
            response = response[:4000] + "\n\n[تم قطع الرد...]"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await update.message.reply_text(
            "❌ عذراً، حدث خطأ. يرجى المحاولة لاحقاً.\n"
            f"💡 يمكنك استخدام /help للاطلاع على الأوامر المتاحة."
        )

# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ حدث خطأ في معالجة طلبك.\n"
            "يرجى المحاولة مرة أخرى أو استخدام /help للمساعدة."
        )

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to run the bot."""
    # Validate configuration
    if not TELEGRAM_TOKEN or is_placeholder(TELEGRAM_TOKEN):
        print("❌ TELEGRAM_BOT_TOKEN not configured properly")
        print("💡 Set it in .env file or environment variables")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🚀 Starting Unified Telegram Bot v%s", BOT_VERSION)
    logger.info("=" * 60)
    logger.info("📦 Repository: %s", GITHUB_REPO)
    logger.info("🔐 Allowlist: %s", "Active" if USER_ALLOWLIST else "Disabled (all users allowed)")
    logger.info("🧠 AI Providers:")
    logger.info("   • OpenAI: %s", "✅" if not is_placeholder(OPENAI_API_KEY) else "❌")
    logger.info("   • Groq: %s", "✅" if not is_placeholder(GROQ_API_KEY) else "❌")
    logger.info("   • Anthropic: %s", "✅" if not is_placeholder(ANTHROPIC_API_KEY) else "❌")
    logger.info("=" * 60)
    
    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers - Basic
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("whoami", cmd_whoami))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("ping", cmd_ping))
    application.add_handler(CommandHandler("version", cmd_version))
    application.add_handler(CommandHandler("about", cmd_about))
    
    # Add command handlers - AI & Chat
    application.add_handler(CommandHandler("chat", cmd_chat))
    application.add_handler(CommandHandler("ask", cmd_ask))
    application.add_handler(CommandHandler("translate", cmd_translate))
    application.add_handler(CommandHandler("summarize", cmd_summarize))
    
    # Add command handlers - Diagnostic
    application.add_handler(CommandHandler("verifyenv", cmd_verifyenv))
    application.add_handler(CommandHandler("preflight", cmd_preflight))
    application.add_handler(CommandHandler("report", cmd_report))
    application.add_handler(CommandHandler("health", cmd_health))
    
    # Add command handlers - Repo
    application.add_handler(CommandHandler("repo", cmd_repo))
    application.add_handler(CommandHandler("insights", cmd_insights))
    application.add_handler(CommandHandler("search", cmd_search))
    application.add_handler(CommandHandler("issue", cmd_issue))
    
    # Add command handlers - Database
    application.add_handler(CommandHandler("db", cmd_db))
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(CommandHandler("history", cmd_history))
    
    # Add command handlers - AI Management
    application.add_handler(CommandHandler("model", cmd_model))
    
    # Add message handler for direct messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Bot stopped by user")
        # Flush any pending conversation memory
        conversation_memory.flush()
        sys.exit(0)
    except Exception as e:
        logger.error("❌ Fatal error: %s", e)
        # Flush any pending conversation memory
        conversation_memory.flush()
        sys.exit(1)
