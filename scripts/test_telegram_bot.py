import os
import logging
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
    else:
        logging.error(f"❌ {name} غير موجود!")
        return False
    return True

def send_test_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text})
    return resp.status_code, resp.text

def main():
    logging.info("=== فحص Telegram Bot Secrets ===")

    ok = True
    ok &= check_env("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    ok &= check_env("TELEGRAM_ALLOWLIST", TELEGRAM_ALLOWLIST)
    ok &= check_env("GITHUB_TOKEN", GITHUB_TOKEN)
    ok &= check_env("OPENAI_API_KEY", OPENAI_API_KEY)

    if not ok:
        logging.error("❌ فشل الفحص – أسرار ناقصة.")
        return

    if not ALLOWED_IDS:
        logging.warning("⚠ لا توجد Allowlist — سيتم إرسال الرسالة للجميع")
        return

    logging.info(f"📨 إرسال رسالة اختبار إلى {ALLOWED_IDS}")

    for uid in ALLOWED_IDS:
        logging.info(f"إرسال إلى {uid} ...")
        status, resp = send_test_message(uid, "🔧 اختبار ناجح: البوت يعمل وهذا تأكيد الاتصال! ✔")
        logging.info(f"📡 الرد من Telegram: {status} / {resp}")

    logging.info("🎉 اكتمل الفحص!")

if __name__ == "__main__":
    main()
