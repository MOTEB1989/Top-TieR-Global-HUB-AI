# 🔧 دليل إعداد وتشغيل المشروع

## 📋 المتطلبات الأساسية

- Docker & Docker Compose
- Node.js 18+ (للتطوير المحلي)
- Python 3.11+ (للبوت)
- npm أو pnpm أو yarn

## 🚀 الإعداد السريع

### 1️⃣ نسخ ملف البيئة
```bash
cp .env.example .env
```

### 2️⃣ تعديل المفاتيح في .env
افتح `.env` وأضف:
- `TELEGRAM_BOT_TOKEN` - احصل عليه من [@BotFather](https://t.me/BotFather)
- `OPENAI_API_KEY` - من [OpenAI Platform](https://platform.openai.com/api-keys)
- `GITHUB_TOKEN` - من [GitHub Tokens](https://github.com/settings/tokens)

### 3️⃣ تنظيف الملفات المكررة
```bash
chmod +x clean-duplicates.sh
./clean-duplicates.sh
```

### 4️⃣ اختبار البناء
```bash
# بناء TypeScript
npm install
npm run build

# بناء Docker
docker build -t lexcode-api .
```

## 🎯 التشغيل

### خيار 1: Docker Compose (موصى به)
```bash
# تشغيل جميع الخدمات
docker-compose -f docker-compose.full.yml up -d

# مشاهدة السجلات
docker-compose -f docker-compose.full.yml logs -f

# إيقاف الخدمات
docker-compose -f docker-compose.full.yml down
```

### خيار 2: تشغيل محلي
```bash
# API Gateway
npm start

# Python AI Engine (في terminal آخر)
python api_server/main.py

# Telegram Bot (في terminal آخر)
python scripts/telegram_chatgpt_mode.py
```

## 🤖 استخدام Telegram Bot

### الأوامر المتاحة:
- `/start` - رسالة ترحيب
- `/help` - المساعدة
- `/whoami` - معرفة Telegram ID
- `/status` - حالة النظام
- `/chat <سؤال>` - دردشة مع AI
- `/repo` - تحليل المستودع
- `/insights` - ملخص ذكي

### إضافة مستخدمين مصرح لهم:
1. استخدم `/whoami` لمعرفة ID
2. أضف الـ ID في `.env`:
   ```
   TELEGRAM_ALLOWLIST=123456789,987654321
   ```

## 🧪 الاختبار

### اختبار شامل
```bash
chmod +x build-and-test.sh
./build-and-test.sh
```

### اختبار محدد
```bash
# TypeScript
npm run build

# Docker
docker build -t test .

# Telegram Bot
python scripts/test_telegram_bot.py

# الخدمات
./scripts/test_all.sh
```

## 🔍 فحص الصحة

### API Endpoints
```bash
# Gateway
curl http://localhost:3000/health

# AI Inference
curl -X POST http://localhost:3000/v1/ai/infer \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "مرحباً"}
    ]
  }'
```

### الخدمات
- Gateway: `http://localhost:3000`
- Qdrant: `http://localhost:6333`
- Neo4j: `http://localhost:7474` (browser)
- Redis: `localhost:6379`

## 🐛 حل المشاكل الشائعة

### خطأ: "No inputs were found in config file"
```bash
./clean-duplicates.sh
npm run build
```

### خطأ: "TELEGRAM_BOT_TOKEN غير موجود"
```bash
# تأكد من وجود المفتاح في .env
grep TELEGRAM_BOT_TOKEN .env

# أو أضفه:
echo "TELEGRAM_BOT_TOKEN=your_token_here" >> .env
```

### خطأ: "Port already in use"
```bash
# ابحث عن العملية
lsof -i :3000

# أو غيّر المنفذ في .env
echo "API_PORT=3001" >> .env
```

### خطأ: Docker build fails
```bash
# تنظيف الـ cache
docker system prune -a

# إعادة البناء
docker build --no-cache -t lexcode-api .
```

## 📊 المراقبة

### حالة الحاويات
```bash
docker-compose -f docker-compose.full.yml ps
```

### السجلات
```bash
# جميع الخدمات
docker-compose -f docker-compose.full.yml logs -f

# خدمة محددة
docker-compose -f docker-compose.full.yml logs -f python-ai
```

### استخدام الموارد
```bash
docker stats
```

## 🚢 النشر

### Railway
```bash
railway login
railway link
railway up
```

### Render
- Push إلى GitHub
- Render سينشر تلقائياً باستخدام `render.yaml`

## 📚 مصادر إضافية

- [Docker Documentation](./DOCKER_DEPLOY.md)
- [Railway Guide](./RAILWAY_DEPLOY.md)
- [Build Fix Guide](./DOCKER_FIX_README.md)
- [Security Guidelines](./.github/copilot-instructions.md)

## 💬 الدعم

- Issues: [GitHub Issues](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/issues)
- Discussions: [GitHub Discussions](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/discussions)

---

**Happy Coding! 🎉**
