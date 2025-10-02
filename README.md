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


## مسارات ذكاء LexCode الموحدة

### 1. `POST /v1/ai/infer`
يوفّر هذا المسار الآن وضعين:

- **وضع OpenAI التقليدي:** ارسل مصفوفة رسائل (بنفس الصيغة القديمة) للاستفادة من مقدّم OpenAI.
  ```bash
  curl -X POST http://localhost:3000/v1/ai/infer \
    -H "Content-Type: application/json" \
    -d '{ "messages": [ { "role": "user", "content": "عرّف LexCode في جملة واحدة." } ] }'
  ```
- **الوضع الداخلي (Rust):** ارسل نصًا مباشرًا ليتم تحليله عبر الخدمة المكتوبة بـ Rust.
  ```bash
  curl -X POST http://localhost:3000/v1/ai/infer \
    -H "Content-Type: application/json" \
    -d '{ "input": "اختبار بسيط" }'
  ```

### 2. `POST /v1/ai/external`
واجهة مبسّطة للوصول إلى مزوّد OpenAI مباشرةً مع توليد Prompt نظامي افتراضي.
```bash
curl -X POST http://localhost:3000/v1/ai/external \
  -H "Content-Type: application/json" \
  -d '{ "message": "مرحبا من المسار الخارجي" }'
```

### 3. `POST /v1/ai/model`
مُدخل موحّد يتيح اختيار المزوّد (`internal` أو `openai`). في حال عدم وجود مفتاح OpenAI يتم استخدام استجابة محاكاة محلية لتسهيل التطوير.
```bash
curl -X POST http://localhost:3000/v1/ai/model \
  -H "Content-Type: application/json" \
  -d '{ "provider": "internal", "message": "مرحبا، أجبني كذكاء اصطناعي موحّد" }'
```

> **ملاحظة:** عند غياب `OPENAI_API_KEY` يعيد المزوّد رسالة توضح أن الاستجابة محاكاة محلية بدلًا من محاولة الاتصال بالشبكة.
