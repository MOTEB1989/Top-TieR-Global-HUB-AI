#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
telegram_chatgpt_mode.py

بوت تيليجرام متقدم يعمل كـ ChatGPT داخل مستودع Top-TieR-Global-HUB-AI
- /chat        : دردشة تفاعلية مع ذاكرة لكل مستخدم
- /repo        : تحليل المستودع باستخدام تقارير ULTRA + ARCHITECTURE
- /insights    : ملخص ذكي عن حالة المشروع
- /file        : تحليل مبدئي للملفات المرسلة
- /status      : حالة البوت والمستودع
- /help        : مساعدة
- /whoami      : معرفة Telegram ID لإضافته في Allowlist

يعتمد على نفس الأسرار:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_ALLOWLIST
- OPENAI_API_KEY
- OPENAI_MODEL (اختياري، افتراضي gpt-4o-mini)
- GITHUB_REPO (اسم المستودع للعرض فقط)
- ULTRA_PREFLIGHT_PATH / FULL_SCAN_SCRIPT / LOG_FILE_PATH (اختياري لدمج أعمق)
"""

import os
import json
import logging
import textwrap
import subprocess
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple

import requests
from telegram import Update, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# ---------------------- إعداد السجل ----------------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telegram_chatgpt_mode")

# ---------------------- المتغيرات البيئية ----------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWLIST_ENV = os.getenv("TELEGRAM_ALLOWLIST", "").strip()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

GITHUB_REPO = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")

ULTRA_PREFLIGHT_PATH = os.getenv("ULTRA_PREFLIGHT_PATH", "scripts/ultra_preflight.sh")
FULL_SCAN_SCRIPT = os.getenv("FULL_SCAN_SCRIPT", "scripts/execute_full_scan.sh")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "analysis/ULTRA_REPORT.md")

CHAT_HISTORY_PATH = Path(os.getenv("CHAT_HISTORY_PATH", "analysis/chat_sessions.json"))
CHAT_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

# RAG Configuration
ENABLE_RAG = os.getenv("ENABLE_RAG", "false").lower() in ("true", "1", "yes")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_INDEX_PATH = os.getenv("EMBEDDING_INDEX_PATH", "analysis/embeddings/index.json")
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "6"))

# ---------------------- Allowlist ----------------------
def parse_allowlist(raw: str):
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
    """تحقق من أن المستخدم ضمن الـ Allowlist (إذا كانت القائمة غير فارغة)."""
    if not USER_ALLOWLIST:
        # إذا القائمة فارغة: نسمح للجميع (ويمكن لاحقاً تشديدها)
        return True
    uid = update.effective_user.id if update.effective_user else None
    return uid in USER_ALLOWLIST


async def reject_if_unauthorized(update: Update) -> bool:
    if is_authorized(update):
        return False
    await update.message.reply_text(
        "❌ غير مصرح لك باستخدام هذا الأمر.\n"
        "استخدم /whoami ثم اطلب إضافة معرفك إلى TELEGRAM_ALLOWLIST."
    )
    return True


# ---------------------- إدارة الذاكرة (التاريخ) ----------------------
def load_sessions() -> Dict[str, List[Dict[str, str]]]:
    if not CHAT_HISTORY_PATH.exists():
        return {}
    try:
        with CHAT_HISTORY_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("فشل قراءة ملف التاريخ: %s", e)
        return {}


def save_sessions(sessions: Dict[str, List[Dict[str, str]]]) -> None:
    try:
        with CHAT_HISTORY_PATH.open("w", encoding="utf-8") as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("فشل حفظ ملف التاريخ: %s", e)


def get_user_key(update: Update) -> str:
    uid = update.effective_user.id if update.effective_user else 0
    uname = update.effective_user.username or ""
    return f"{uid}:{uname}"


def append_message(
    sessions: Dict[str, List[Dict[str, str]]],
    user_key: str,
    role: str,
    content: str,
    max_messages: int = 30,
) -> None:
    if user_key not in sessions:
        sessions[user_key] = []
    sessions[user_key].append({"role": role, "content": content})
    # قصّ التاريخ لتجنب التضخم
    if len(sessions[user_key]) > max_messages:
        sessions[user_key] = sessions[user_key][-max_messages:]


# ---------------------- استدعاء OpenAI ----------------------
class OpenAIError(Exception):
    pass


def call_openai_chat(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.4,
    max_tokens: int = 700,
) -> str:
    if not OPENAI_API_KEY:
        raise OpenAIError("OPENAI_API_KEY غير موجود في المتغيرات البيئية")

    model = model or OPENAI_MODEL
    url = f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        logger.error("خطأ من OpenAI: %s - %s", resp.status_code, resp.text[:500])
        raise OpenAIError(f"OpenAI error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error("استجابة غير متوقعة من OpenAI: %s | %s", e, data)
        raise OpenAIError("Unexpected OpenAI response structure")


def make_system_prompt() -> str:
    return textwrap.dedent(
        f"""
        أنت وكيل ذكي يعمل داخل مستودع GitHub باسم {GITHUB_REPO}.
        دورك:
        - الإجابة مثل ChatGPT لكن مع تركيز على:
          • هندسة المستودع
          • الأمن والحَوْكمة
          • الأتمتة (Agents / Workflows)
          • تحسين جودة الكود والـ CI/CD
        - استخدم أسلوب محترف، مختصر، بالعربية الفصحى ما لم يُطلب غير ذلك.
        - عند تحليل المستودع، اعتمد على الوصف التالي إن توفر:
          • ARCHITECTURE.md
          • SECURITY_POSTURE.md
          • AGENT_PLAYBOOK.md
          • WORKFLOW_MAP.md
          • ULTRA_REPORT.md
        - إذا كانت المعلومات غير كافية: قل بوضوح "لا توجد بيانات كافية" بدلاً من التخمين.
        """
    ).strip()


# ---------------------- RAG Embedding Functions ----------------------
def create_embedding(text: str) -> List[float]:
    """
    Create embedding for a single text using OpenAI API.
    Returns embedding vector or empty list on failure.
    """
    if not OPENAI_API_KEY:
        logger.error("Cannot create embedding: OPENAI_API_KEY not set")
        return []
    
    url = f"{OPENAI_BASE_URL.rstrip('/')}/embeddings"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": EMBEDDING_MODEL,
        "input": [text],
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
    
    except Exception as e:
        logger.error(f"Failed to create embedding: {e}")
        return []


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    Handles edge cases: empty vectors, mismatched lengths.
    """
    if not vec1 or not vec2:
        return 0.0
    
    # Handle mismatched lengths by using shorter length
    min_len = min(len(vec1), len(vec2))
    vec1 = vec1[:min_len]
    vec2 = vec2[:min_len]
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def load_embeddings_index() -> List[Dict[str, Any]]:
    """Load embeddings index from file. Returns empty list on failure."""
    index_path = Path(EMBEDDING_INDEX_PATH)
    if not index_path.is_absolute():
        repo_root = Path(__file__).parent.parent
        index_path = repo_root / index_path
    
    if not index_path.exists():
        logger.warning(f"Embeddings index not found: {index_path}")
        return []
    
    try:
        with index_path.open("r", encoding="utf-8") as f:
            index = json.load(f)
        logger.info(f"Loaded embeddings index with {len(index)} chunks")
        return index
    except Exception as e:
        logger.error(f"Failed to load embeddings index: {e}")
        return []


def retrieve_context_via_embeddings(query: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retrieve relevant context chunks from embeddings index.
    Returns (formatted_context, results_list).
    """
    if not ENABLE_RAG:
        return "", []
    
    index = load_embeddings_index()
    if not index:
        logger.warning("RAG enabled but index is empty or failed to load")
        return "", []
    
    # Create query embedding
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return "", []
    
    # Calculate similarities
    results = []
    for chunk in index:
        if "embedding" not in chunk:
            continue
        
        similarity = cosine_similarity(query_embedding, chunk["embedding"])
        results.append((chunk, similarity))
    
    # Sort by similarity (highest first) and take top-k
    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:VECTOR_TOP_K]
    
    if not top_results:
        return "", []
    
    # Format context
    context_parts = []
    result_list = []
    
    for i, (chunk, score) in enumerate(top_results):
        path = chunk.get("path", "unknown")
        content = chunk.get("content", "")
        
        context_parts.append(f"[{i+1}] {path} (score: {score:.3f})")
        context_parts.append(content[:500])  # Limit chunk size
        context_parts.append("")
        
        result_list.append({
            "rank": i + 1,
            "path": path,
            "score": round(score, 4),
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
        })
    
    formatted_context = "\n".join(context_parts)
    logger.info(f"Retrieved {len(top_results)} context chunks for query")
    
    return formatted_context, result_list


# ---------------------- أدوات (Tools) ----------------------
def run_local_script(cmd: str) -> str:
    """تشغيل سكربت محلي (مثل preflight أو scan) وإرجاع المخرجات."""
    try:
        out = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            timeout=300,
        )
        return out[:3500]
    except subprocess.CalledProcessError as e:
        return f"❌ فشل تنفيذ الأمر:\n{cmd}\n\nالمخرجات:\n{e.output[:2000]}"
    except Exception as e:
        return f"❌ خطأ أثناء تنفيذ الأمر:\n{cmd}\n{e}"


def read_small_file(path: str, max_chars: int = 4000) -> str:
    p = Path(path)
    if not p.exists():
        return f"❌ الملف غير موجود: {path}"
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if len(txt) > max_chars:
            return txt[:max_chars] + "\n...\n[تم قطع المحتوى]"
        return txt
    except Exception as e:
        return f"❌ تعذر قراءة الملف {path}: {e}"


def build_repo_context() -> str:
    """جمع سياق من ملفات الهندسة/الأمن/التقارير."""
    parts = []
    candidates = [
        "ARCHITECTURE.md",
        "SECURITY_POSTURE.md",
        "AGENT_PLAYBOOK.md",
        "WORKFLOW_MAP.md",
        "analysis/ULTRA_REPORT.md",
        "README.md",
    ]
    for path in candidates:
        if Path(path).exists():
            parts.append(f"\n===== {path} =====\n")
            parts.append(read_small_file(path, max_chars=2500))
    if not parts:
        return "لا توجد ملفات هندسية/أمنية كافية لتمثيل حالة المستودع."
    return "\n".join(parts)


# ---------------------- أوامر تيليجرام ----------------------
HELP_TEXT = textwrap.dedent(
    """
    🤖 *وضع ChatGPT متقدم – Top-TieR-Global-HUB-AI*

    الأوامر المتاحة:

    /start      → رسالة ترحيب
    /help       → هذه الرسالة
    /whoami     → عرض Telegram ID لاستخدامه في الـ Allowlist

    💬 وضع الدردشة:
    /chat نص السؤال...
      • دردشة تفاعلية مع ذاكرة لكل مستخدم
      • مثال: `/chat ما هي حالة البنية الحالية في المستودع؟`

    🔍 البحث المتجه (RAG):
    /search نص البحث...
      • بحث متجه في ملفات المستودع باستخدام embeddings
      • مثال: `/search authentication implementation`
      • يتطلب تفعيل ENABLE_RAG

    🧠 تحليلات متقدمة:
    /repo
      • تحليل سريع للمستودع اعتماداً على ARCHITECTURE/SECURITY/ULTRA_REPORT
    /insights
      • ملخص ذكي عن حالة المشروع (مخاطر، فرص تحسين، أولويات)

    📂 تحليل ملفات:
    أرسل ملفاً نصياً (txt/md/json/log) أو سكربت، وسيقوم البوت بتحليل مبدئي له.

    ⚙️ حالة تشغيل:
    /status
      • عرض حالة التكوين (OpenAI, GitHub, Allowlist, RAG)

    ⚠️ الملاحظات:
    - بعض الأوامر متاحة فقط للمستخدمين داخل Allowlist (TELEGRAM_ALLOWLIST).
    """
).strip()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 أهلاً بك في وضع ChatGPT المتقدم داخل مستودع Top-TieR-Global-HUB-AI.\n"
        "استخدم /help لاستعراض الأوامر المتاحة."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(HELP_TEXT)


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id if update.effective_user else "N/A"
    uname = update.effective_user.username if update.effective_user else ""
    await update.message.reply_text(
        f"🆔 معرفك في تيليجرام: `{uid}`\n"
        f"👤 اسم المستخدم: @{uname}\n\n"
        "أضف هذا المعرف في TELEGRAM_ALLOWLIST (كمثال):\n"
        f"TELEGRAM_ALLOWLIST={uid}"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parts = []

    parts.append("📊 *حالة النظام – ChatGPT Mode*")
    parts.append(f"- المستودع: `{GITHUB_REPO}`")

    # OpenAI
    if OPENAI_API_KEY:
        parts.append("🧠 OpenAI: ✅ مضبوط (OPENAI_API_KEY موجود)")
        parts.append(f"   • النموذج: `{OPENAI_MODEL}`")
    else:
        parts.append("🧠 OpenAI: ❌ مفقود (OPENAI_API_KEY غير موجود)")

    # RAG Status
    if ENABLE_RAG:
        parts.append("🔍 RAG: ✅ مفعّل")
        parts.append(f"   • نموذج Embedding: `{EMBEDDING_MODEL}`")
        parts.append(f"   • Top-K: `{VECTOR_TOP_K}`")
        
        # Check index file
        index_path = Path(EMBEDDING_INDEX_PATH)
        if not index_path.is_absolute():
            repo_root = Path(__file__).parent.parent
            index_path = repo_root / index_path
        
        if index_path.exists():
            try:
                with index_path.open("r") as f:
                    index = json.load(f)
                parts.append(f"   • ملف الفهرس: ✅ ({len(index)} chunks)")
            except Exception:
                parts.append(f"   • ملف الفهرس: ⚠️ موجود لكن به خطأ")
        else:
            parts.append(f"   • ملف الفهرس: ❌ غير موجود")
    else:
        parts.append("🔍 RAG: ⚠️ غير مفعّل (ENABLE_RAG=false)")

    # Allowlist
    if USER_ALLOWLIST:
        parts.append("🔐 Allowlist: ✅ مفعّل")
        parts.append("   • المستخدمون المصرح لهم:")
        for uid in USER_ALLOWLIST:
            parts.append(f"     - {uid}")
    else:
        parts.append("🔐 Allowlist: ⚠️ غير مفعّل (القائمة فارغة، جميع المستخدمين مسموح لهم حالياً)")

    # ملفات هندسية
    exist_flags = []
    for p in ["ARCHITECTURE.md", "SECURITY_POSTURE.md", "AGENT_PLAYBOOK.md", "WORKFLOW_MAP.md", "analysis/ULTRA_REPORT.md"]:
        if Path(p).exists():
            exist_flags.append(f"   • ✅ {p}")
        else:
            exist_flags.append(f"   • ❌ {p}")
    parts.append("📂 ملفات الهندسة/الأمن:")
    parts.extend(exist_flags)

    await update.message.reply_markdown("\n".join(parts))


async def cmd_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await reject_if_unauthorized(update):
        return

    if not OPENAI_API_KEY:
        await update.message.reply_text("❌ لا يمكن استخدام /chat لأن OPENAI_API_KEY غير مهيأ.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء كتابة سؤالك بعد الأمر.\n"
            "مثال:\n"
            "/chat ما هي حالة الـ CI/CD في المستودع؟"
        )
        return

    user_question = " ".join(context.args).strip()
    user_key = get_user_key(update)

    # Retrieve context via RAG if enabled
    rag_context = ""
    if ENABLE_RAG:
        retrieved_context, _ = retrieve_context_via_embeddings(user_question)
        if retrieved_context:
            rag_context = f"\n\n**سياق من المستودع (RAG):**\n{retrieved_context}\n"
            logger.info(f"RAG context added to chat for user {user_key}")

    sessions = load_sessions()
    
    # Add user message with optional RAG context
    user_message_with_context = user_question
    if rag_context:
        user_message_with_context = user_question + rag_context
    
    append_message(sessions, user_key, "user", user_message_with_context)

    # بناء الرسائل مع System Prompt + تاريخ المستخدم
    messages = [{"role": "system", "content": make_system_prompt()}]
    messages.extend(sessions[user_key])

    try:
        reply = call_openai_chat(messages)
    except OpenAIError as e:
        await update.message.reply_text(f"❌ خطأ من نموذج الذكاء الاصطناعي:\n{e}")
        return

    append_message(sessions, user_key, "assistant", reply)
    save_sessions(sessions)

    # تقطيع الرد إذا كان طويلاً
    if len(reply) > 3500:
        reply = reply[:3500] + "\n...\n[تم قطع الرد لطوله]"

    await update.message.reply_text(reply)


async def cmd_repo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await reject_if_unauthorized(update):
        return

    context_text = build_repo_context()

    if not OPENAI_API_KEY:
        # إذا لا يوجد OpenAI، نعيد النص الخام
        await update.message.reply_text(
            "⚠️ OPENAI_API_KEY غير مهيأ، سيتم عرض سياق المستودع مباشرة:\n\n"
            + context_text[:3500]
        )
        return

    prompt = textwrap.dedent(
        """
        حلّل سياق المستودع التالي وقدم:
        - ملخص عالي المستوى (High-level summary)
        - أبرز المخاطر الهندسية أو الأمنية
        - أهم نقاط القوة
        - 3 توصيات عملية قصيرة

        سياق المستودع:
        """
    ).strip()

    messages = [
        {"role": "system", "content": make_system_prompt()},
        {"role": "user", "content": prompt + "\n\n" + context_text},
    ]

    try:
        reply = call_openai_chat(messages, max_tokens=700)
    except OpenAIError as e:
        await update.message.reply_text(f"❌ خطأ أثناء تحليل المستودع:\n{e}")
        return

    await update.message.reply_text(reply[:3500])


async def cmd_insights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await reject_if_unauthorized(update):
        return

    context_text = build_repo_context()

    if not OPENAI_API_KEY:
        await update.message.reply_text(
            "⚠️ OPENAI_API_KEY غير مهيأ، سيتم عرض السياق الخام فقط:\n\n"
            + context_text[:3500]
        )
        return

    prompt = textwrap.dedent(
        """
        تصرف كمهندس برمجيات مسؤول عن منصة ذكاء اصطناعي.
        بناءً على سياق المستودع، أعطني:

        1) حالة النظام الحالية (Current State)
        2) أهم 5 مخاطر أو فجوات (Risks / Gaps)
        3) خطة تنفيذ من 3 مراحل (قصيرة، متوسطة، طويلة الأجل)
        4) أي تحذير يجب الانتباه له

        اجعل الإجابة مقسّمة بعناوين واضحة ونقاط.
        """
    ).strip()

    messages = [
        {"role": "system", "content": make_system_prompt()},
        {"role": "user", "content": prompt + "\n\nسياق المستودع:\n" + context_text},
    ]

    try:
        reply = call_openai_chat(messages, max_tokens=900)
    except OpenAIError as e:
        await update.message.reply_text(f"❌ خطأ أثناء توليد الـ Insights:\n{e}")
        return

    await update.message.reply_text(reply[:3500])


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """استقبال ملف من المستخدم وتحليله مبدئياً."""
    if await reject_if_unauthorized(update):
        return

    message = update.message
    doc: Document = message.document
    if not doc:
        return

    # تنزيل الملف مؤقتاً
    try:
        file = await doc.get_file()
        tmp_path = Path("analysis/uploads")
        tmp_path.mkdir(parents=True, exist_ok=True)
        local_file = tmp_path / f"{doc.file_unique_id}_{doc.file_name}"
        await file.download_to_drive(str(local_file))
    except Exception as e:
        await message.reply_text(f"❌ تعذر تنزيل الملف من تيليجرام: {e}")
        return

    # قراءة المحتوى النصي إذا أمكن
    suffix = local_file.suffix.lower()
    text_content = ""
    if suffix in [".txt", ".md", ".log", ".json", ".yaml", ".yml", ".py", ".ts", ".sh"]:
        try:
            text_content = local_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            await message.reply_text(f"⚠️ تم تنزيل الملف، لكن تعذر قراءته كنص: {e}")
            return
    else:
        await message.reply_text(
            f"📁 تم تنزيل الملف: {local_file.name}\n"
            f"النوع: {suffix or 'غير معروف'}\n\n"
            "حالياً لا أدعم إلا الملفات النصية البسيطة (txt, md, log, json, yaml, py, ts, sh)."
        )
        return

    # إذا لا يوجد OpenAI: نعيد مقتطف فقط
    if not OPENAI_API_KEY:
        snippet = text_content[:1500]
        await message.reply_text(
            "⚠️ لا يوجد OPENAI_API_KEY، سأعرض مقتطفاً من محتوى الملف:\n\n" + snippet
        )
        return

    prompt = textwrap.dedent(
        f"""
        تم تزويدك بمحتوى ملف من مستودع برمجي.

        المطلوب:
        - أعطني ملخصاً قصيراً عن محتوى الملف
        - إن كان سكربت أو كود: وضّح ما الذي يفعله
        - إن كان تكوين (config): وضّح المخاطر أو الأخطاء المحتملة
        - لا تخمن إذا لم يكن النص واضحاً، وقل "لا توجد بيانات كافية" عند الحاجة

        محتوى الملف (مقتطف):
        """
    ).strip()

    snippet = text_content[:4000]
    messages = [
        {"role": "system", "content": make_system_prompt()},
        {"role": "user", "content": prompt + "\n\n" + snippet},
    ]

    try:
        reply = call_openai_chat(messages, max_tokens=700)
    except OpenAIError as e:
        await message.reply_text(f"❌ خطأ أثناء تحليل الملف:\n{e}")
        return

    await message.reply_text(reply[:3500])


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """البحث المتجه في فهرس المستودع."""
    if await reject_if_unauthorized(update):
        return

    if not ENABLE_RAG:
        await update.message.reply_text(
            "⚠️ ميزة البحث المتجه غير مفعّلة.\n"
            "لتفعيلها، اضبط ENABLE_RAG=true في المتغيرات البيئية."
        )
        return

    if not OPENAI_API_KEY:
        await update.message.reply_text("❌ لا يمكن استخدام /search لأن OPENAI_API_KEY غير مهيأ.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ الرجاء كتابة استعلام بحث بعد الأمر.\n"
            "مثال:\n"
            "/search authentication implementation"
        )
        return

    query = " ".join(context.args).strip()
    
    await update.message.reply_text("🔍 جاري البحث في فهرس المستودع...")

    try:
        retrieved_context, results = retrieve_context_via_embeddings(query)
        
        if not results:
            await update.message.reply_text(
                "❌ لم يتم العثور على نتائج.\n"
                "تأكد من أن ملف الفهرس موجود وليس فارغاً."
            )
            return
        
        # Format results for display
        response_parts = [f"🔍 *نتائج البحث لـ:* {query}\n"]
        
        for result in results:
            rank = result["rank"]
            score = result["score"]
            path = result["path"]
            preview = result["content_preview"]
            
            response_parts.append(f"**[{rank}] {path}** (score: {score})")
            response_parts.append(f"```\n{preview}\n```\n")
        
        response_text = "\n".join(response_parts)
        
        # Split if too long
        if len(response_text) > 3500:
            response_text = response_text[:3500] + "\n...\n[تم قطع النتائج لطولها]"
        
        await update.message.reply_markdown(response_text)
        logger.info(f"Search completed for query: {query}, found {len(results)} results")
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        await update.message.reply_text(f"❌ فشل البحث:\n{e}")


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """التعامل مع رسائل نصية لا تبدأ بأمر /."""
    text = update.message.text or ""
    if not text.strip():
        return

    # تعامل معها كرسالة دردشة قصيرة
    if not OPENAI_API_KEY:
        await update.message.reply_text(
            "📨 استلمت رسالتك، لكن لا يوجد OPENAI_API_KEY حالياً.\n"
            "استخدم /help للاطلاع على الأوامر المتاحة."
        )
        return

    user_key = get_user_key(update)
    sessions = load_sessions()
    append_message(sessions, user_key, "user", text.strip())

    messages = [{"role": "system", "content": make_system_prompt()}]
    messages.extend(sessions[user_key])

    try:
        reply = call_openai_chat(messages, max_tokens=500)
    except OpenAIError as e:
        await update.message.reply_text(f"❌ خطأ أثناء الرد على الرسالة:\n{e}")
        return

    append_message(sessions, user_key, "assistant", reply)
    save_sessions(sessions)

    await update.message.reply_text(reply[:3500])


# ---------------------- main ----------------------
def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN غير موجود في المتغيرات البيئية")

    logger.info("بدء تشغيل Telegram ChatGPT Mode Bot ...")
    logger.info("المستودع: %s", GITHUB_REPO)
    if USER_ALLOWLIST:
        logger.info("Allowlist مفعّل للمستخدمين: %s", USER_ALLOWLIST)
    else:
        logger.warning("Allowlist فارغ - جميع المستخدمين مسموح لهم حالياً.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("chat", cmd_chat))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("repo", cmd_repo))
    app.add_handler(CommandHandler("insights", cmd_insights))

    # استقبال ملفات
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # fallback للنصوص العادية
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
