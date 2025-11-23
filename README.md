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

---

## 🌍 Bilingual Support & Dark Theme | الدعم ثنائي اللغة والسمة الداكنة

### English

This platform now includes full bilingual support for Arabic and English, with a default dark theme and seamless switching capabilities.

#### Features

- **🌐 Bilingual Interface**: Complete Arabic and English translation support
  - Automatic RTL (Right-to-Left) layout for Arabic
  - Locale persistence across sessions
  - Easy language toggle in navigation

- **🌙 Dark Theme by Default**: Modern dark mode interface
  - Default dark theme on first visit
  - Light/Dark theme toggle
  - Theme preference saved to browser storage
  - Smooth transitions between themes

- **💬 Replies Console**: Admin interface for message management
  - Located at `/admin/replies`
  - Send messages to backend API
  - Optional Telegram forwarding
  - Real-time delivery status
  - Unique message ID tracking

- **🤖 Telegram Bot Integration**: Multilingual bot support
  - Default Arabic responses (configurable)
  - Commands: `/start`, `/help`, `/health`
  - Message forwarding from web interface
  - Simple i18n system

#### Quick Start

##### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your backend API URL
npm run dev
```

Visit `http://localhost:3000` to see the interface.
Navigate to `/admin/replies` for the Replies Console.

##### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with optional Telegram credentials
python main.py
```

Backend runs on `http://localhost:8000`.
API docs available at `http://localhost:8000/docs`.

##### Bot (Telegram)

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
# Add your TELEGRAM_BOT_TOKEN
python main.py
```

#### API Documentation

**POST /api/v1/messages**

Send a message through the API:

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello from the Replies Console!",
    "locale": "en"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Hello from the Replies Console!",
  "locale": "en",
  "delivered": false
}
```

**GET /api/v1/messages/health**

Check messages service health:

```bash
curl http://localhost:8000/api/v1/messages/health
```

#### Configuration

**Frontend Environment Variables**

- `NEXT_PUBLIC_API_BASE`: Backend API URL (default: `http://localhost:8000`)

**Backend Environment Variables**

- `BACKEND_HOST`: Server host (default: `0.0.0.0`)
- `BACKEND_PORT`: Server port (default: `8000`)
- `CORS_ORIGINS`: Allowed CORS origins (default: `*`, **restrict in production**)
- `TELEGRAM_BOT_TOKEN`: Optional Telegram bot token for message forwarding
- `ADMIN_CHAT_ID`: Optional Telegram chat ID for receiving messages

**Bot Environment Variables**

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required)
- `BOT_DEFAULT_LOCALE`: Default response locale (`ar` or `en`, default: `ar`)

#### Security Notes

⚠️ **Important Security Considerations:**

1. **CORS Configuration**: The backend currently allows all origins (`*`). In production, restrict `CORS_ORIGINS` to your frontend domain(s).

2. **Message Persistence**: Messages are currently ephemeral (not saved to database). A future update will add persistent storage with proper data retention policies.

3. **Authentication**: The Replies Console currently has no authentication. In production, implement proper role-based access control for admin pages.

4. **Rate Limiting**: Consider adding rate limiting to the messages endpoint to prevent abuse.

5. **Environment Variables**: Never commit `.env` files. Always use `.env.example` as templates with placeholder values.

---

### العربية

تتضمن المنصة الآن دعمًا كاملاً للغتين العربية والإنجليزية، مع سمة داكنة افتراضية وإمكانيات تبديل سلسة.

#### الميزات

- **🌐 واجهة ثنائية اللغة**: دعم كامل للترجمة بين العربية والإنجليزية
  - تخطيط تلقائي من اليمين إلى اليسار للعربية
  - حفظ اللغة عبر الجلسات
  - تبديل سهل للغة في شريط التنقل

- **🌙 السمة الداكنة افتراضياً**: واجهة حديثة بوضع داكن
  - سمة داكنة افتراضية عند الزيارة الأولى
  - تبديل بين السمة الفاتحة والداكنة
  - حفظ تفضيلات السمة في المتصفح
  - انتقالات سلسة بين السمات

- **💬 وحدة الردود**: واجهة إدارة للرسائل
  - موجودة على `/admin/replies`
  - إرسال رسائل إلى واجهة برمجة التطبيقات
  - إعادة توجيه اختيارية إلى تيليجرام
  - حالة التسليم في الوقت الفعلي
  - تتبع معرّف الرسالة الفريد

- **🤖 تكامل بوت تيليجرام**: دعم متعدد اللغات للبوت
  - ردود عربية افتراضية (قابلة للتكوين)
  - أوامر: `/start`، `/help`، `/health`
  - إعادة توجيه الرسائل من واجهة الويب
  - نظام i18n بسيط

#### البدء السريع

##### الواجهة الأمامية (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local
# قم بتعديل .env.local بعنوان API الخاص بالخادم الخلفي
npm run dev
```

قم بزيارة `http://localhost:3000` لرؤية الواجهة.
انتقل إلى `/admin/replies` لوحدة الردود.

##### الخادم الخلفي (FastAPI)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# قم بتعديل .env ببيانات تيليجرام الاختيارية
python main.py
```

يعمل الخادم الخلفي على `http://localhost:8000`.
وثائق API متاحة على `http://localhost:8000/docs`.

##### البوت (تيليجرام)

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env
# أضف TELEGRAM_BOT_TOKEN الخاص بك
python main.py
```

#### توثيق API

**POST /api/v1/messages**

إرسال رسالة عبر API:

```bash
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "content": "مرحباً من وحدة الردود!",
    "locale": "ar"
  }'
```

الاستجابة:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "مرحباً من وحدة الردود!",
  "locale": "ar",
  "delivered": false
}
```

**GET /api/v1/messages/health**

التحقق من صحة خدمة الرسائل:

```bash
curl http://localhost:8000/api/v1/messages/health
```

#### التكوين

**متغيرات البيئة للواجهة الأمامية**

- `NEXT_PUBLIC_API_BASE`: عنوان API للخادم الخلفي (الافتراضي: `http://localhost:8000`)

**متغيرات البيئة للخادم الخلفي**

- `BACKEND_HOST`: مضيف الخادم (الافتراضي: `0.0.0.0`)
- `BACKEND_PORT`: منفذ الخادم (الافتراضي: `8000`)
- `CORS_ORIGINS`: أصول CORS المسموح بها (الافتراضي: `*`، **قيّد في الإنتاج**)
- `TELEGRAM_BOT_TOKEN`: رمز بوت تيليجرام الاختياري لإعادة توجيه الرسائل
- `ADMIN_CHAT_ID`: معرّف محادثة تيليجرام الاختياري لاستقبال الرسائل

**متغيرات البيئة للبوت**

- `TELEGRAM_BOT_TOKEN`: رمز بوت تيليجرام الخاص بك (مطلوب)
- `BOT_DEFAULT_LOCALE`: لغة الرد الافتراضية (`ar` أو `en`، الافتراضي: `ar`)

#### ملاحظات الأمان

⚠️ **اعتبارات الأمان المهمة:**

1. **تكوين CORS**: يسمح الخادم الخلفي حالياً بجميع الأصول (`*`). في الإنتاج، قيّد `CORS_ORIGINS` إلى نطاق(ات) الواجهة الأمامية الخاصة بك.

2. **استمرارية الرسائل**: الرسائل حالياً مؤقتة (غير محفوظة في قاعدة البيانات). سيضيف تحديث مستقبلي تخزيناً دائماً مع سياسات الاحتفاظ بالبيانات المناسبة.

3. **المصادقة**: لا تحتوي وحدة الردود حالياً على مصادقة. في الإنتاج، نفّذ التحكم في الوصول القائم على الأدوار لصفحات المسؤول.

4. **تحديد المعدل**: فكر في إضافة تحديد المعدل إلى نقطة نهاية الرسائل لمنع سوء الاستخدام.

5. **متغيرات البيئة**: لا تقم أبداً بالالتزام بملفات `.env`. استخدم دائماً `.env.example` كقوالب بقيم عنصر نائب.

---

## 📝 Future Enhancements | التحسينات المستقبلية

The following features are planned for future releases:

- Database persistence for messages with listing in console
- WebSocket support for real-time message streaming
- Advanced i18n library integration (react-intl or next-intl)
- Role-based access control for admin pages
- Message search and filtering
- Export messages functionality
- Enhanced Telegram bot commands

الميزات التالية مخططة للإصدارات المستقبلية:

- استمرارية قاعدة البيانات للرسائل مع القائمة في وحدة التحكم
- دعم WebSocket لبث الرسائل في الوقت الفعلي
- تكامل مكتبة i18n المتقدمة (react-intl أو next-intl)
- التحكم في الوصول القائم على الأدوار لصفحات المسؤول
- البحث والتصفية في الرسائل
- وظيفة تصدير الرسائل
- أوامر محسّنة لبوت تيليجرام
