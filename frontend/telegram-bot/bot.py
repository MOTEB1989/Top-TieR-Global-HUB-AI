import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
RAILWAY_API_URL = os.getenv('RAILWAY_API_URL', 'https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer')

# Store conversation history per user
user_conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = [{'role': 'assistant', 'content': 'مرحباً! أنا TopTire AI Bot. أرسل لي أي سؤال وسأجيبك! 🤖'}]
    await update.message.reply_text('مرحباً! أنا TopTire AI Bot. أرسل لي أي سؤال وسأجيبك! 🤖\n\nاستخدم /clear لمسح سجل المحادثة.')

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text('✓ تم مسح سجل المحادثة. يمكنك البدء بمحادثة جديدة.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize conversation history if not exists
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    # Add user message to history
    user_conversations[user_id].append({'role': 'user', 'content': user_message})
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                RAILWAY_API_URL,
                json={
                    'messages': user_conversations[user_id]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('content') or data.get('message', {}).get('content') or 'لم أتمكن من الحصول على إجابة.'
                
                # Add AI response to history
                user_conversations[user_id].append({'role': 'assistant', 'content': ai_response})
                
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
    application.add_handler(CommandHandler('clear', clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print('🤖 Bot is running...')
    application.run_polling()

if __name__ == '__main__':
    main()
