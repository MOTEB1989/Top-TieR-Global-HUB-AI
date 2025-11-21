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

## RAG Engine Usage
- Ingest text/PDF documents: `python services/rag_engine/rag.py ingest --path ./docs --type auto`
- Query with context retrieval: `python services/rag_engine/rag.py query "question here" --top-k 5`

## Web UI
- Launch Streamlit UI: `streamlit run services/web_ui/streamlit_app.py`
- Select provider (OpenAI, Groq, Azure, local Phi-3, or mock) from the sidebar and optionally upload PDFs (stored locally).

## Docker-only RAG Stack
- Start full stack: `make rag-up` (uses `docker-compose.rag.yml` for Qdrant, local Phi runner, RAG API placeholder, and Web UI).

## Fine-tuning Dataset Prep
- Validate JSONL training data: `python scripts/fine_tune.py validate data/fine_tune/sample_training.jsonl`
- Sample datasets live in `data/fine_tune/` and can be extended before calling provider-specific fine-tuning APIs.
