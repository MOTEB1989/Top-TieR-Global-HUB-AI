# Railway Deployment Guide
# دليل النشر على Railway

## خدمات المشروع على Railway:

### 1. Python AI Engine
**Type:** Web Service
**Start Command:** `python api_server/main.py`
**Environment Variables:**
```
OPENAI_API_KEY=<your-key>
GROQ_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
TELEGRAM_BOT_TOKEN=<your-token>
TELEGRAM_ALLOWLIST=8256840669,6090738107
GITHUB_TOKEN=<your-token>
GITHUB_REPO=MOTEB1989/Top-TieR-Global-HUB-AI
API_PORT=3000
PYTHON_VERSION=3.11
REDIS_URL=${{Redis.REDIS_URL}}
```

---

### 2. Node.js API Gateway
**Type:** Web Service
**Start Command:** `npm start`
**Root Directory:** `gateway/`
**Environment Variables:**
```
OPENAI_API_KEY=<your-key>
API_PORT=3001
PYTHON_AI_URL=${{python-ai-engine.Railway_STATIC_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

---

### 3. Telegram Bot (ChatGPT Mode)
**Type:** Worker
**Start Command:** `python scripts/telegram_chatgpt_mode.py`
**Environment Variables:**
```
TELEGRAM_BOT_TOKEN=<your-token>
TELEGRAM_ALLOWLIST=8256840669,6090738107
GITHUB_TOKEN=<your-token>
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini
GITHUB_REPO=MOTEB1989/Top-TieR-Global-HUB-AI
FULL_SCAN_SCRIPT=scripts/execute_full_scan.sh
ULTRA_PREFLIGHT_PATH=scripts/ultra_preflight.sh
LOG_FILE_PATH=analysis/ULTRA_REPORT.md
```

---

### 4. Redis Database
**Type:** Redis Plugin
من Railway Marketplace:
- ابحث عن "Redis"
- أضف Redis Plugin
- سيتم إنشاء `REDIS_URL` تلقائياً

---

### 5. PostgreSQL (Optional)
**Type:** PostgreSQL Plugin
من Railway Marketplace:
- ابحث عن "PostgreSQL"
- أضف PostgreSQL Plugin
- سيتم إنشاء `DATABASE_URL` تلقائياً

---

## خطوات النشر:

### 1. إنشاء مشروع جديد:
```bash
# من Railway Dashboard
1. New Project
2. Deploy from GitHub repo
3. اختر: MOTEB1989/Top-TieR-Global-HUB-AI
```

### 2. إضافة الخدمات:
```
1. في المشروع، اضغط "New Service"
2. أضف الخدمات واحدة تلو الأخرى:
   - Python AI Engine
   - Node.js Gateway
   - Telegram Bot
   - Redis
```

### 3. إعداد المتغيرات البيئية:
```
1. لكل خدمة، اذهب إلى "Variables"
2. أضف المتغيرات المطلوبة
3. استخدم Reference Variables للربط بين الخدمات
   مثال: ${{Redis.REDIS_URL}}
```

### 4. إعداد Start Commands:
```
Python AI Engine:
  python api_server/main.py

Node Gateway:
  npm start

Telegram Bot:
  python scripts/telegram_chatgpt_mode.py
```

### 5. Deploy:
```
1. اضغط "Deploy" لكل خدمة
2. راقب Logs للتأكد من التشغيل
```

---

## الميزات على Railway:

✅ **Auto-Deploy:** كل push إلى GitHub
✅ **Environment Variables:** آمنة ومشفرة
✅ **Custom Domains:** مجاناً
✅ **Metrics:** CPU, Memory, Network
✅ **Logs:** في الوقت الفعلي
✅ **Horizontal Scaling:** حسب الحاجة

---

## التكلفة المتوقعة:

**Free Tier:**
- $5 قيمة استخدام مجاني شهرياً
- يكفي للتطوير والاختبار

**Pro Plan:**
- $20/شهر
- يشمل $20 استخدام
- مناسب للإنتاج

---

## الروابط المهمة:

- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Community: https://discord.gg/railway

---

## Troubleshooting:

### مشكلة: الخدمة لا تبدأ
```bash
# تحقق من Logs
# تأكد من:
1. Start Command صحيح
2. Dependencies مثبتة
3. Environment Variables موجودة
```

### مشكلة: Cannot connect to Redis
```bash
# تأكد من:
1. Redis Plugin مُضاف
2. REDIS_URL في Environment Variables
3. استخدم: ${{Redis.REDIS_URL}}
```

### مشكلة: Port already in use
```bash
# Railway يوفر PORT تلقائياً
# استخدم:
PORT = os.environ.get("PORT") or 3000
```

---

## Best Practices:

1. **استخدم Railway CLI:**
```bash
npm i -g @railway/cli
railway login
railway link
railway run python api_server/main.py
```

2. **Monitor Resources:**
```
- راقب CPU/Memory في Dashboard
- ضع Alerts للاستخدام الزائد
```

3. **Use Healthchecks:**
```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

4. **Database Backups:**
```
- فعّل Auto Backups للـ PostgreSQL
- استخدم Railway's Backup feature
```

---

## الملفات المطلوبة:

✅ `railway.json` - إعدادات أساسية
✅ `requirements.txt` - Python dependencies
✅ `package.json` - Node.js dependencies
✅ `.gitignore` - تجنب رفع .env

---

**جاهز للنشر على Railway!** 🚂
