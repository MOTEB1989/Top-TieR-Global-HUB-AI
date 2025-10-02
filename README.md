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

## مشاركة البوابة عبر ngrok

لتوفير بوابة الـ API للآخرين دون فتح المنافذ يدويًا، يمكنك استخدام `ngrok`:

```bash
ngrok http 3000
```

ستحصل على رابط عشوائي في كل مرة مثل:

```
Forwarding  https://7f8a-102-45-33-12.ngrok-free.app -> http://localhost:3000
```

- عنوان البوابة الخارجي: `https://7f8a-102-45-33-12.ngrok-free.app/`
- مسار الاستدلال الكامل: `https://7f8a-102-45-33-12.ngrok-free.app/v1/ai/infer`

> **ملاحظة:** الجزء قبل `.ngrok-free.app` يتغيّر مع كل تشغيل للحسابات المجانية. للحصول على نطاق مخصّص ثابت (مثل `https://myapi.ngrok-free.app`)، تحتاج إلى حساب ngrok مدفوع وتفعيل ميزة *Custom Subdomain*.
