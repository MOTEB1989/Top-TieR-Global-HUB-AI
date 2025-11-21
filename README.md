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

## AI Gateway Layer

This repository now includes a unified AI gateway (OpenAI, Groq, Azure, local) under `gateway/`, and a validation workflow at `.github/workflows/ai-gateway-validation.yml`. Configure `LLM_PROVIDER`, `LLM_MODEL`, and provider API keys (e.g., `OPENAI_API_KEY`, `GROQ_API_KEY`) to switch providers without changing application code.
