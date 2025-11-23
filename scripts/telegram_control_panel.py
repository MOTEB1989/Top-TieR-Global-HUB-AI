#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram × GitHub Control Panel
بوابة تحكم مركزية عبر تيليجرام للتحكم في:
- فحص المستودع (ultra_preflight.sh)
- تشغيل سكربتات الفحص (execute_full_scan.sh)
- متابعة الـ PRs
- إدارة الوسوم (ready-for-auto-merge)
- استدعاء GPT (اختياري إذا وُضع OPENAI_API_KEY)

المتغيرات البيئية المطلوبة:
- TELEGRAM_BOT_TOKEN
- GITHUB_TOKEN
- GITHUB_REPO  (مثال: MOTEB1989/Top-TieR-Global-HUB-AI)

المتغيرات الاختيارية:
- OPENAI_API_KEY
- ULTRA_PREFLIGHT_PATH   (مثال: scripts/ultra_preflight.sh)
- FULL_SCAN_SCRIPT       (مثال: scripts/execute_full_scan.sh)
- LOG_FILE_PATH          (مثال: analysis/ULTRA_REPORT.md)
"""

import os
import logging
import subprocess
import textwrap
from typing import Optional

import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============== الإعداد العام ============== 

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telegram_control_panel")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ULTRA_PREFLIGHT_PATH = os.getenv("ULTRA_PREFLIGHT_PATH", "scripts/ultra_preflight.sh")
FULL_SCAN_SCRIPT = os.getenv("FULL_SCAN_SCRIPT", "scripts/execute_full_scan.sh")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "analysis/ULTRA_REPORT.md")

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN غير موجود في المتغيرات البيئية")

if not GITHUB_TOKEN:
    logger.warning("⚠️ GITHUB_TOKEN غير موجود، سيتم تعطيل أوامر GitHub المعتمدة على API.")

# ============== أدوات مساعدة ============== 

def truncate(text: str, limit: int = 3500) -> str:
    """تقليص النص حتى لا يتجاوز حدود تيليجرام."""
    if len(text) <= limit:
        return text
    return text[: limit - 50] + "\n\n... [تم التقصير]"

def run_local_script(cmd: str) -> str:
    """تشغيل سكربت محلي عبر subprocess وإرجاع stdout/stderr بشكل مقروء."""
    try:
        logger.info("تشغيل الأمر: %s", cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10 دقائق
        )
        out = ""
        out += f"Exit code: {result.returncode}\n\n"
        if result.stdout:
            out += "STDOUT:\n" + result.stdout + "\n"
        if result.stderr:
            out += "\nSTDERR:\n" + result.stderr + "\n"
        return out.strip()
    except Exception as e:
        logger.exception("فشل تشغيل الأمر")
        return f"❌ حدث خطأ أثناء تشغيل الأمر: {e}"

def gh_headers() -> dict:
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

def gh_get(path: str, params: Optional[dict] = None) -> requests.Response:
    url = f"https://api.github.com{path}"
    return requests.get(url, headers=gh_headers(), params=params)

def gh_post(path: str, json: Optional[dict] = None) -> requests.Response:
    url = f"https://api.github.com{path}"
    return requests.post(url, headers=gh_headers(), json=json)

# ============== أوامر GitHub ============== 
def list_open_prs(limit: int = 10) -> str:
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN غير مكوَّن؛ لا يمكن الوصول إلى GitHub API."

    r = gh_get(f"/repos/{GITHUB_REPO}/pulls", params={"state": "open", "per_page": limit})
    if r.status_code != 200:
        return f"❌ GitHub API Error ({r.status_code}): {r.text}"

    prs = r.json()
    if not prs:
        return "✅ لا توجد Pull Requests مفتوحة حالياً."

    lines = ["📌 قائمة الـ PRs المفتوحة:"]
    for pr in prs:
        lines.append(
            f"- #{pr['number']} | {pr['title']} | by {pr['user']['login']} | state={pr['state']}"
        )
    return "\n".join(lines)

def label_pr_ready_for_auto_merge(pr_number: int) -> str:
    """
    إضافة وسم ready-for-auto-merge للـ PR المحدد.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN غير مكوَّن؛ لا يمكن تعديل الـ PR."

    # التأكد من وجود الوسم أو إنشاؤه من قبل workflow آخر – هنا نكتفي بالإضافة.
    path = f"/repos/{GITHUB_REPO}/issues/{pr_number}/labels"
    r = gh_post(path, json={"labels": ["ready-for-auto-merge"]})
    if r.status_code not in (200, 201):
        return f"❌ فشل إضافة الوسم: ({r.status_code}) {r.text}"

    return f"✅ تم إضافة الوسم ready-for-auto-merge إلى PR رقم #{pr_number}."

def get_repo_status() -> str:
    """
    ملخص بسيط: عدد الـ PRs المفتوحة + آخر حالة CI للفرع main.
    """
    if not GITHUB_TOKEN:
        return "❌ GITHUB_TOKEN غير مكوَّن؛ لا يمكن جلب حالة المستودع."

    # عدد الـ PRs
    prs_resp = gh_get(f"/repos/{GITHUB_REPO}/pulls", params={"state": "open", "per_page": 50})
    if prs_resp.status_code != 200:
        return f"❌ GitHub PRs Error: {prs_resp.status_code} {prs_resp.text}"
    open_prs = len(prs_resp.json())

    # آخر تشغيل CI للفرع main
    runs_resp = gh_get(
        f"/repos/{GITHUB_REPO}/actions/runs",
        params={"branch": "main", "per_page": 1},
    )
    ci_line = "حالة CI: غير معروفة"
    if runs_resp.status_code == 200 and runs_resp.json().get("workflow_runs"):
        run = runs_resp.json()["workflow_runs"][0]
        ci_line = (
            f"آخر CI: {run.get('name','N/A')} | "
            f"النتيجة: {run.get('conclusion','in_progress')} | "
            f"الحالة: {run.get('status')}"
        )

    return f"📊 حالة المستودع: {GITHUB_REPO}\n- PRs مفتوحة: {open_prs}\n- {ci_line}"

# ============== GPT (اختياري) ============== 
def ask_gpt(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "❌ OPENAI_API_KEY غير مكوَّن؛ لا يمكن استدعاء GPT."

    url = "https://api.openai.com/v1/chat/completions"
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    if r.status_code != 200:
        return f"❌ OpenAI Error {r.status_code}: {r.text}"
    data = r.json()
    return data["choices"][0]["message"]["content"]

# ============== أوامر تيليجرام ============== 

HELP_TEXT = textwrap.dedent(
    '''
    🤖 *لوحة تحكم Telegram × GitHub*

    الأوامر المتاحة:

    /help - عرض هذه القائمة
    /status - ملخص حالة المستودع والـ CI
    /prs - عرض قائمة الـ PRs المفتوحة
    /preflight - تشغيل فحص preflight (ultra_preflight.sh)
    /scan - تشغيل فحص شامل (execute_full_scan.sh إن وجد)
    /auto_merge <رقم PR> - تمييز PR بأنه جاهز للدمج (ready-for-auto-merge)
    /logs - عرض آخر جزء من تقرير (مثل ULTRA_REPORT.md)
    /ai <سؤال> - استدعاء GPT (إذا كان OPENAI_API_KEY مكوَّناً)

    ملاحظة:
    - يتم تنفيذ السكربتات محلياً داخل الـ Codespace / الخادم الذي يشغّل هذا البوت.
    - أوامر GitHub تحتاج GITHUB_TOKEN بصلاحيات repo.
    '''
).strip()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🤖 أهلاً بك في لوحة تحكم Top-TieR-Global-HUB-AI عبر تيليجرام.\nاستخدم /help لاستعراض الأوامر.")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_markdown(HELP_TEXT)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = get_repo_status()
    await update.message.reply_text(truncate(text))

async def cmd_prs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = list_open_prs(limit=15)
    await update.message.reply_text(truncate(text))

async def cmd_preflight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not os.path.exists(ULTRA_PREFLIGHT_PATH):
        await update.message.reply_text(f"❌ الملف {ULTRA_PREFLIGHT_PATH} غير موجود.")
        return
    await update.message.reply_text("⏳ تشغيل preflight... يرجى الانتظار.")
    output = run_local_script(f"bash {ULTRA_PREFLIGHT_PATH}")
    await update.message.reply_text(truncate(output))

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not os.path.exists(FULL_SCAN_SCRIPT):
        await update.message.reply_text(f"❌ الملف {FULL_SCAN_SCRIPT} غير موجود.")
        return
    await update.message.reply_text("🔍 تشغيل فحص شامل للمستودع...")
    output = run_local_script(f"bash {FULL_SCAN_SCRIPT}")
    await update.message.reply_text(truncate(output))

async def cmd_auto_merge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("❌ الرجاء تزويد رقم PR. مثال: /auto_merge 123")
        return
    try:
        pr_number = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ رقم PR غير صالح.")
        return

    result = label_pr_ready_for_auto_merge(pr_number)
    await update.message.reply_text(result)

async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not os.path.exists(LOG_FILE_PATH):
        await update.message.reply_text(f"❌ ملف السجل {LOG_FILE_PATH} غير موجود.")
        return
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        await update.message.reply_text(truncate(content))
    except Exception as e:
        await update.message.reply_text(f"❌ تعذر قراءة السجل: {e}")

async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("❌ الرجاء كتابة سؤالك بعد الأمر. مثال: /ai ما حالة المشروع؟")
        return
    prompt = " ".join(context.args)
    reply = ask_gpt(prompt)
    await update.message.reply_text(truncate(reply))

async def fallback_echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # رسائل نصية عادية بدون أوامر
    text = update.message.text or ""
    if text.strip().startswith("/"):
        # أمر غير معرّف
        await update.message.reply_text("❓ أمر غير معروف. استخدم /help لعرض الأوامر المتاحة.")
    else:
        await update.message.reply_text(f"📨 استلمت رسالتك:\n{text}")

# ============== نقطة الدخول ============== 
def main() -> None:
    logger.info("بدء تشغيل Telegram × GitHub Control Panel ...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("prs", cmd_prs))
    app.add_handler(CommandHandler("preflight", cmd_preflight))
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("auto_merge", cmd_auto_merge))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("ai", cmd_ai))

    # Fallback لأي رسالة نصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_echo))

    app.run_polling()

if __name__ == "__main__":
    main()