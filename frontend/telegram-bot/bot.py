import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
RAILWAY_API_URL = os.getenv('RAILWAY_API_URL', 'https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحباً! أنا TopTire AI Bot. أرسل لي أي سؤال وسأجيبك! 🤖')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        response = requests.post(
            RAILWAY_API_URL,
            json={
                'messages': [{'role': 'user', 'content': user_message}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('content') or data.get('message', {}).get('content') or 'لم أتمكن من الحصول على إجابة.'
            await update.message.reply_text(ai_response)
        else:
            await update.message.reply_text(f'⚠️ خطأ: {response.status_code}')
            
    except Exception as e:
        logging.error(f'Error: {e}')
        await update.message.reply_text('⚠️ فشل الاتصال بالخادم. حاول مرة أخرى.')

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError('TELEGRAM_BOT_TOKEN is required!')
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print('🤖 Bot is running...')
    application.run_polling()

if __name__ == '__main__':
    main()
