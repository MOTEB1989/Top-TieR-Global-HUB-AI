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

## Runner Service (FastAPI)
يوفّر مجلّد `runner_service/` غلافًا بسيطًا حول `LexCodeRunner` عبر FastAPI.

### بناء وتشغيل الحاوية
```bash
docker build -t myorg/lexcode-runner ./runner_service
docker run -d -p 8000:8000 --name runner myorg/lexcode-runner
```

### نقاط النهاية
- `GET /health` — فحص الصحة.
- `POST /run` — تشغيل وصفة YAML مباشرة من الطلب.

مثال استخدام:
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "recipe": {
      "project": "demo",
      "tasks": [
        {
          "id": "t1",
          "name": "Hello World",
          "steps": [
            {"process": {"model": "gpt-3.5-turbo", "prompt": "اكتب حكمة قصيرة"}}
          ]
        }
      ]
    }
  }'
```
