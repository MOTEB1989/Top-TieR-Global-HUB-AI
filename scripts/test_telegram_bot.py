import logging
import os
import sys

import requests

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWLIST = os.getenv("TELEGRAM_ALLOWLIST")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ALLOWED_IDS = []
if TELEGRAM_ALLOWLIST:
    ALLOWED_IDS = [x.strip() for x in TELEGRAM_ALLOWLIST.split(",") if x.strip()]

def check_env(name, value):
    if value:
        logging.info(f"✔ {name} موجود")
        return True

    logging.error(f"❌ {name} غير موجود!")
    return False


def check_bot_identity():
    """يتأكد من صلاحية التوكن عبر استدعاء getMe."""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    resp = requests.get(url, timeout=10)

    if resp.status_code != 200:
        logging.error(f"❌ فشل اتصال getMe: {resp.status_code} / {resp.text}")
        return False

    data = resp.json()
    if not data.get("ok"):
        logging.error(f"❌ getMe رجّع ok=false: {data}")
        return False

    result = data.get("result", {})
    logging.info(
        "🤖 البوت متصل: username=%s, id=%s",
        result.get("username"),
        result.get("id"),
    )
    return True

def send_test_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    return resp.status_code, resp.text, resp.ok

def main():
    logging.info("=== فحص Telegram Bot Secrets ===")

    ok = True
    ok &= check_env("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    ok &= check_env("TELEGRAM_ALLOWLIST", TELEGRAM_ALLOWLIST)
    ok &= check_env("GITHUB_TOKEN", GITHUB_TOKEN)
    ok &= check_env("OPENAI_API_KEY", OPENAI_API_KEY)

    if not ok:
        logging.error("❌ فشل الفحص – أسرار ناقصة.")
        sys.exit(1)

    if not ALLOWED_IDS:
        logging.error("❌ لا توجد Allowlist – لن يتم الإرسال لأي حساب.")
        sys.exit(1)

    ok &= check_bot_identity()

    logging.info(f"📨 إرسال رسالة اختبار إلى {ALLOWED_IDS}")

    for uid in ALLOWED_IDS:
        logging.info(f"إرسال إلى {uid} ...")
        status, resp, success = send_test_message(
            uid,
            "🔧 اختبار ناجح: البوت يعمل وهذا تأكيد الاتصال! ✔",
        )
        logging.info(f"📡 الرد من Telegram: {status} / {resp}")
        ok &= success

    if ok:
        logging.info("🎉 اكتمل الفحص! النتيجة: OK")
        sys.exit(0)

    logging.error("❌ اكتمل الفحص مع أخطاء. النتيجة: FAILED")
    sys.exit(1)

if __name__ == "__main__":
    main()
