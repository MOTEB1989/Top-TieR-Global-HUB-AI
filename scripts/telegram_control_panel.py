#!/usr/bin/env python3
import os
import subprocess
import logging
import textwrap
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telegram_control_panel")

# -------------------------
#     ENVIRONMENT VARS
# -------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")

ULTRA_PREFLIGHT_PATH = os.getenv("ULTRA_PREFLIGHT_PATH", "scripts/ultra_preflight.sh")
FULL_SCAN_SCRIPT = os.getenv("FULL_SCAN_SCRIPT", "scripts/execute_full_scan.sh")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "analysis/ULTRA_REPORT.md")

# Allowlist
ALLOWLIST_ENV = os.getenv("TELEGRAM_ALLOWLIST", "").strip()


def parse_allowlist(raw: str):
    if not raw:
        return set()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    ids = {int(p) for p in parts if p.isdigit()}
    return ids


USER_ALLOWLIST = parse_allowlist(ALLOWLIST_ENV)


def run_local(cmd: str) -> str:
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8", errors="ignore")


def truncate(txt: str, limit: int = 3500) -> str:
    return txt if len(txt) <= limit else txt[:limit] + "\n… [TRUNCATED]"


# -------------------------
#      AUTH CHECK
# -------------------------

def is_authorized(update: Update) -> bool:
    if not USER_ALLOWLIST:
        return True
    uid = update.effective_user.id if update.effective_user else None
    return uid in USER_ALLOWLIST


async def reject(update: Update):
    await update.message.reply_text(
        "❌ غير مصرح لك باستخدام هذا الأمر.\n"
        "استخدم /whoami وأرسل معرفك لمالك النظام."
    )


# -------------------------
#       COMMANDS
# -------------------------
HELP_TEXT = textwrap.dedent("""
🤖 *لوحة تحكم Telegram × GitHub*
الأوامر المتاحة:

/start — بدء الجلسة
/help — قائمة الأوامر
/whoami — عرض معرف المستخدم
/status — حالة المستودع
/prs — قائمة Pull Requests
/preflight — تشغيل فحص preflight
/scan — فحص شامل للمستودع
/auto_merge <PR> — دمج تلقائي مضبوط
/logs — قراءة آخر تقرير
""").strip()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 مرحباً بك في لوحة تحكم Top-TieR GitHub عبر Telegram.\nاستخدم /help للمساعدة."
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown(HELP_TEXT)


async def cmd_whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"🆔 معرفك هو: {uid}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject(update)
    txt = run_local("bash scripts/generate_repo_structure.py")
    await update.message.reply_text(truncate(txt))


async def cmd_prs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject(update)
    txt = run_local("gh pr list --limit 20")
    await update.message.reply_text(truncate(txt))


async def cmd_preflight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject(update)
    await update.message.reply_text("⏳ تشغيل preflight…")
    txt = run_local(f"bash {ULTRA_PREFLIGHT_PATH}")
    await update.message.reply_text(truncate(txt))


async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject(update)
    await update.message.reply_text("🔍 تشغيل scan...")
    txt = run_local(f"bash {FULL_SCAN_SCRIPT}")
    await update.message.reply_text(truncate(txt))


async def cmd_auto_merge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject(update)
    if not context.args:
        return await update.message.reply_text("❌ مثال الاستخدام: /auto_merge 123")
    pr_number = context.args[0]
    txt = run_local(f"gh pr merge {pr_number} --merge")
    await update.message.reply_text(truncate(txt))


async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return await reject(update)
    if not os.path.exists(LOG_FILE_PATH):
        return await update.message.reply_text("❌ لا يوجد تقرير.")
    with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
        txt = f.read()
    await update.message.reply_text(truncate(txt))


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ أمر غير معروف. استخدم /help.")


# -------------------------
#      MAIN ENTRY
# -------------------------

def main():
    logger.info("🚀 بدء تشغيل Telegram Control Panel...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("prs", cmd_prs))
    app.add_handler(CommandHandler("preflight", cmd_preflight))
    app.add_handler(CommandHandler("scan", cmd_scan))
    app.add_handler(CommandHandler("auto_merge", cmd_auto_merge))
    app.add_handler(CommandHandler("logs", cmd_logs))

    app.add_handler(CommandHandler(None, fallback))

    app.run_polling()


if __name__ == "__main__":
    main()
