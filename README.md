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

## RAG Local Stack
This repository includes a lightweight, developer-focused RAG stack for local experiments (not for production).

- **Start the stack:**
  ```bash
  ./scripts/run_rag_stack.sh
  ```
- **Services exposed locally:**
  - Streamlit Web UI: http://localhost:8501
  - Gateway API
  - RAG engine
  - Qdrant vector store
  - Local Phi-3 runner
