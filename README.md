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

## Mobile Chat Access (iPhone)

To run your personal RAG + Phi-3 + Chat UI stack on your laptop and access it from your iPhone:

```bash
./scripts/run_mobile_chat_stack.sh
```

When the script starts, it will print a line similar to:

```text
Open on your iPhone: http://192.168.X.X:8501
```

1. Make sure your iPhone is on the same Wi-Fi network as your laptop.
2. Open Safari (or Chrome) on the iPhone.
3. Type the printed URL exactly as shown.
4. You should see the Streamlit Chat UI connected to your local Gateway and RAG engine.

This stack is for **personal local development only**, not production.
