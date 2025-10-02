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

## CI/CD Pipeline
- يتم تشغيل سير عمل GitHub Actions (`.github/workflows/ci-cd.yml`) على كل Push/PR.
- يبني كل من Gateway (Node.js)، الـ LLM API (FastAPI)، الـ Runner (Python) والـ Dashboard.
- يطلق اختبارات الوحدة / التكامل / E2E.
- يدعم نشر الـ Dashboard على Vercel ونشر صور Docker إلى Registry عند توافر الأسرار (`VERCEL_*` وبيانات السجل).

## الأمن (RBAC، Rate Limiting، Secrets)
- تمت إضافة RBAC للأدوار `admin`، `dev`، `viewer` عبر ترويسة `X-API-KEY`.
- تم دمج `fastapi-limiter` مع Redis (يعطل تلقائيًا عند عدم توافره).
- مدير أسرار موحد (`utils/secrets_manager.py`) يدعم HashiCorp Vault أو المتغيرات البيئية.
- كل المسارات الحساسة (GPT، مزامنة المصادر) تتطلب صلاحيات مناسبة، وتتوفر `/metrics` للمراقبة.

## المراقبة (Observability)
- مجلد `monitoring/` يحتوي على Docker Compose لتشغيل Prometheus + Grafana + OpenSearch + Fluent Bit.
- تم توفير Dashboard افتراضي في Grafana مع مصادر بيانات جاهزة.
- واجهة `/metrics` متاحة من خدمات FastAPI بعد التشغيل لربطها مع Prometheus.

## التوثيق + الواجهات النهائية
- `/docs/swagger` و`/docs/redoc` متاحان من خدمة الـ LLM API.
- لوحة التحكم (veritas-web) تعرض صفحة `GET /docs/api` توضّح كيفية استهلاك واجهات Gateway/LLM/Runner.
- نقاط النشر المقترحة:
  - Dashboard: `https://your-dashboard.vercel.app`
  - Gateway API: `https://your-domain.com:3000`
  - LLM API: `https://your-domain.com:5000/chat`
  - Runner API: `https://your-domain.com:8000/runner/run`

## تطبيق iOS (SwiftUI)
- عدّل `Services.swift` داخل مشروع iOS لتحديث المسارات:
  ```swift
  let runnerURL = "https://your-domain.com:8000/runner/run"
  let chatURL   = "https://your-domain.com:5000/chat"
  ```
- شغّل التطبيق عبر Xcode (Simulator أو جهاز حقيقي) بعد ضبط عنوان الخادم.


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
