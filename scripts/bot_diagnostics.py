#!/usr/bin/env python3
"""
bot_diagnostics.py
مساعد أوامر تشخيص للبوت:
- /verifyenv   : فحص المتغيرات الحرجة عبر scripts/verify_env.py
- /preflight   : تشغيل scripts/check_connections.sh وتلخيص النتائج
- /report      : إرسال ملف reports/check_connections.json

ملاحظات:
- يعتمد على python-telegram-bot v21+
- يفترض وجود scripts/verify_env.py و scripts/check_connections.sh
"""

import asyncio
import json
import os
import shlex
from pathlib import Path
from typing import Any

from telegram import Update  # python-telegram-bot >= 21
from telegram.ext import CommandHandler, ContextTypes

# إعدادات عامة
REPO_DEFAULT = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")
REPORT_PATH = Path("reports/check_connections.json")
API_PORT = int(os.getenv("API_PORT", "3000"))

def _env_allowlist() -> list[int]:
    raw = os.getenv("TELEGRAM_ALLOWLIST", "").strip()
    if not raw:
        return []
    out = []
    for p in raw.split(","):
        p = p.strip()
        if p.isdigit():
            out.append(int(p))
    return out

def _is_authorized(user_id: int) -> bool:
    allow = _env_allowlist()
    if not allow:
        return True
    return user_id in allow

def _mask_value(k: str, v: str) -> str:
    if v is None:
        return "missing"
    if k.endswith("_KEY") or k.endswith("_TOKEN"):
        return (v[:6] + "...") if len(v) > 10 else "***MASKED***"
    return v if v else "empty"

async def _run_cmd(cmd: str, timeout: int = 120, env: dict = None) -> tuple[int, str, str]:
    """
    تشغيل أمر شيل مع timeout. يرجع (returncode, stdout, stderr)
    """
    proc = await asyncio.create_subprocess_exec(
        *shlex.split(cmd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return (124, "", f"Timeout after {timeout}s: {cmd}")
    return (proc.returncode, stdout.decode("utf-8", "ignore"), stderr.decode("utf-8", "ignore"))

def _summarize_env_text(output: str) -> str:
    """
    يحاول استخراج سطور ملخص scripts/verify_env.py كما هي لعرضها في الدردشة.
    إن تعذّر، يطبع المخرجات كاملة مقصوصة.
    """
    lines = [line for line in output.strip().splitlines() if line.strip()]
    if not lines:
        return "لم يتم استلام أي مخرجات من verify_env.py."
    # ابحث عن سطر "جميع المتغيرات الحرجة..." وما بعده
    ok_idx = None
    for i, line in enumerate(lines):
        if "جميع المتغيرات الحرجة" in line or "All critical env" in line:
            ok_idx = i
            break
    if ok_idx is not None:
        frag = lines[ok_idx: ok_idx + 20]
        return "\n".join(frag)
    # وإلا أعِد أول ~40 سطر كحد أقصى
    return "\n".join(lines[:40])

def _load_report() -> dict[str, Any] | None:
    if REPORT_PATH.exists():
        try:
            return json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def _summarize_report(data: dict[str, Any]) -> str:
    """
    يبني ملخصاً قصيراً من تقارير check_connections.json
    """
    repo = data.get("repo") or REPO_DEFAULT
    api = data.get("api_port", {})
    port = api.get("port", API_PORT)
    listening = api.get("listening", "unknown")

    telegram_test = data.get("telegram_test", "n/a")
    models_count = data.get("models_found_count", 0)
    env = data.get("env", {}) if isinstance(data.get("env"), dict) else {}

    wanted = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TELEGRAM_ALLOWLIST",
              "OPENAI_API_KEY", "GITHUB_TOKEN", "REDIS_URL"]
    env_lines = []
    for k in wanted:
        env_lines.append(f"- {k}: {env.get(k, 'missing')}")

    return (
        f"📊 Preflight Summary\n"
        f"- Repo: {repo}\n"
        f"- API Port: {port} (listening: {listening})\n"
        f"- Telegram: {telegram_test}\n"
        f"- Models found: {models_count}\n"
        f"🔐 Env status:\n" + "\n".join(env_lines)
    )

async def handle_verifyenv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return
    if not _is_authorized(user.id):
        await update.message.reply_text("⛔ غير مصرح. أضف معرفك إلى TELEGRAM_ALLOWLIST.")
        return

    if not Path("scripts/verify_env.py").exists():
        await update.message.reply_text("❌ لم يتم العثور على scripts/verify_env.py")
        return

    await update.message.reply_text("⏱️ تشغيل فحص البيئة verify_env.py ...")
    rc, out, err = await _run_cmd("python scripts/verify_env.py", timeout=60)
    if rc == 0:
        summary = _summarize_env_text(out)
        await update.message.reply_text(f"✅ تحقق البيئة:\n{summary}")
    else:
        msg = f"❌ فشل verify_env.py (rc={rc})\nSTDERR:\n{err or 'no stderr'}\nSTDOUT:\n{out or 'no stdout'}"
        # قص الرسالة حتى لا تتجاوز حدود تيليجرام
        await update.message.reply_text(msg[:3500])

async def handle_preflight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return
    if not _is_authorized(user.id):
        await update.message.reply_text("⛔ غير مصرح. أضف معرفك إلى TELEGRAM_ALLOWLIST.")
        return

    sh = Path("scripts/check_connections.sh")
    if not sh.exists():
        await update.message.reply_text("❌ لم يتم العثور على scripts/check_connections.sh")
        return

    try:
        sh.chmod(0o755)
    except Exception:
        pass

    await update.message.reply_text("⏱️ تشغيل فحص الاتصالات (preflight)...")
    env = os.environ.copy()
    env["API_PORT"] = str(API_PORT)
    # تشغيل السكربت مع تمرير المتغيرات البيئية بشكل آمن
    rc, out, err = await _run_cmd("scripts/check_connections.sh", timeout=180, env=env)

    if rc != 0:
        msg = f"⚠️ انتهى الفحص برمز {rc} — قد يستمر إنشاء التقرير رغم ذلك.\nSTDERR:\n{(err or '')[:1500]}"
        await update.message.reply_text(msg)

    data = _load_report()
    if not data:
        # أرسل جزءاً من المخرجات لمساعدتك في التشخيص
        tail = (out or err or "no output")[-1500:]
        await update.message.reply_text("❌ لم يتم العثور على التقرير reports/check_connections.json.\n"
                                        "مقتطف مخرجات:\n" + tail)
        return

    summary = _summarize_report(data)
    await update.message.reply_text(summary)

async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return
    if not _is_authorized(user.id):
        await update.message.reply_text("⛔ غير مصرح. أضف معرفك إلى TELEGRAM_ALLOWLIST.")
        return

    if REPORT_PATH.exists():
        try:
            with REPORT_PATH.open("rb") as report_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=report_file,
                    filename=REPORT_PATH.name,
                    caption="📑 تقرير check_connections.json"
                )
        except Exception as e:
            await update.message.reply_text(f"⚠️ تعذر إرسال الملف: {e}")
    else:
        await update.message.reply_text("❌ لا يوجد تقرير حالياً. شغّل /preflight أولاً.")

def register_diag_handlers(app) -> None:
    """
    اربط أوامر التشخيص بالتطبيق:
      /verifyenv
      /preflight
      /report
    """
    app.add_handler(CommandHandler("verifyenv", handle_verifyenv))
    app.add_handler(CommandHandler("preflight", handle_preflight))
    app.add_handler(CommandHandler("report", handle_report))
