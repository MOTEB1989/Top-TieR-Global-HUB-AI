# TopTire AI - Telegram Bot

## Setup
1. Create a bot with @BotFather on Telegram
2. Copy the token to `.env`
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run:
```bash
python bot.py
```

## Deploy to Railway
Add environment variable `TELEGRAM_BOT_TOKEN` in Railway dashboard.

## Configuration
Create a `.env` file based on `.env.example`:
```
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
RAILWAY_API_URL=https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer
```

## Features
- Automatic message handling
- Connection to Railway-deployed backend
- Error handling and logging
- Arabic language support
- Simple command interface (/start)

## Commands
- `/start` - Start the bot and get welcome message
- `/clear` - Clear conversation history and start fresh
- Just send any text message to chat with the AI

## Features Details
- **Conversation History**: The bot maintains conversation context per user, allowing for coherent multi-turn conversations
- **Async HTTP**: Uses httpx for non-blocking API calls
- **Error Handling**: Gracefully handles API errors and timeouts
