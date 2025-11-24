# LexCode Hybrid Stack 🚀

هندسة هجينة متينة:
- **Rust (core/):** محرك الأداء والخدمات الأساسية (HTTP/axum).
- **Node.js + TypeScript (services/api/):** بوابة API، مصادقة، توحيد المزوّدات.
- **Python (adapters/python/lexhub/):** وصلات الذكاء الاصطناعي والبيانات (OpenAI/Anthropic/HF/Kaggle...).

## التشغيل السريع
```bash
cp .env.example .env
docker compose up --build
```
- Rust Core على `http://localhost:8080`
- API Gateway على `http://localhost:3000`


## استخدام /v1/ai/infer (OpenAI)
ضع مفتاحك في `.env`:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # اختياري
OPENAI_BASE_URL=https://api.openai.com/v1  # اختياري
```
اختبر:
```bash
curl -X POST http://localhost:3000/v1/ai/infer \  -H "Content-Type: application/json" \  -d '{ "messages": [ { "role": "user", "content": "عرّف LexCode في جملة واحدة." } ] }'
```

## 🎨 Frontend Options

This project includes multiple frontend options to interact with the AI chatbot:

### 1. Next.js (React)
Modern React framework with TypeScript support.
```bash
cd frontend/nextjs
npm install
npm run dev
```
Open http://localhost:3000

**Note:** Next.js dev server uses port 3000 by default. If the main API Gateway is running on port 3000, either stop it or configure Next.js to use a different port with `npm run dev -- -p 3001`

### 2. Vue.js
Vue 3 with Composition API and Vite.
```bash
cd frontend/vue
npm install
npm run dev
```
Open http://localhost:5173

### 3. Vanilla HTML
Pure HTML/CSS/JavaScript - no build process required!
```bash
# Simply open in browser
open frontend/html/index.html
```
Or deploy to any static hosting service (Railway, GitHub Pages, Netlify, Vercel, etc.)

### 4. Telegram Bot
Python-based Telegram bot integration.
```bash
cd frontend/telegram-bot
pip install -r requirements.txt
python bot.py
```

**Setup Telegram Bot:**
1. Create a bot with @BotFather on Telegram
2. Copy token to `.env` file
3. Run the bot

All frontends connect to the Railway-deployed API: `https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer`
