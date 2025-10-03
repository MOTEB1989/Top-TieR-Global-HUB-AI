# Top TieR Global Hub – Multi-Agent Stack 🚀

منصة هجينة مصممة لتشغيل مجموعة وكلاء ذكاء اصطناعي متخصّصين ضمن بنية خدمات مصغّرة يمكن نشرها عبر Docker Compose بسهولة. التركيبة الحالية تشتمل على:

- **Core** (`core/`): خدمة Python / FastAPI مسؤولة عن واجهة الاستدلال الموحدة مع موفّري النماذج (تأتي مع رد افتراضي قابل للتوسعة).
- **Orchestrator** (`api/`): خدمة FastAPI تختار الوكيل الأنسب لكل مهمة وتنسّق مع خدمة الـCore.
- **Gateway** (`gateway/`): واجهة أمامية موحّدة لإكسبوز الخدمات داخلياً أو خارجياً.
- **AI Agents** (`ai_agents/`): مكتبة الوكلاء المتخصّصين (حوكمة، شرح كود، تحليل مالي، والمنسّق الأعلى).
- **PostgreSQL**: قاعدة بيانات جاهزة للتوسعة إن احتجت تخزيناً دائماً للأعمال.

## ⚙️ المتطلبات المسبقة
- Docker و Docker Compose
- Python 3.11+ (اختياري للتشغيل المحلي دون حاويات)

## 🚀 التشغيل السريع
```bash
cp .env.example .env
# عدّل القيم داخل .env بحسب مفاتيحك وبيئتك

docker compose up --build
```

بعد بدء الخدمات ستجد النقاط التالية:
- Core ⇒ `http://localhost:3000/v1/ai/infer`
- Orchestrator ⇒ `http://localhost:3100/v1/lex/run`
- Gateway ⇒ `http://localhost:8080/v1/...`
- PostgreSQL ⇒ `localhost:5432`

## 🧠 مثال على استدعاء المنسق الأعلى
```bash
curl -X POST http://localhost:8080/v1/lex/run \
  -H "Content-Type: application/json" \
  -d '{
        "task": "audit",
        "payload": {"scope": "security"}
      }'
```

يمكنك توجيه مهمة لوكيل محدد:
```bash
curl -X POST http://localhost:8080/v1/lex/run \
  -H "Content-Type: application/json" \
  -d '{
        "task": "explain",
        "agent": "mohsen_jj",
        "payload": {"file_path": "ai_agents/mohsen_jj/agent.py"}
      }'
```

ولطلب استدلال مباشر من خدمة الـCore:
```bash
curl -X POST http://localhost:8080/v1/ai/infer \
  -H "Content-Type: application/json" \
  -d '{
        "prompt": "Summarise the governance checklist",
        "options": {"temperature": 0.3}
      }'
```

## 🧱 بنية الحاويات
`docker-compose.yml` يهيئ الخدمات التالية:
- `core`: يبني من `core/Dockerfile` ويحمّل متطلبات FastAPI الأساسية.
- `orchestrator`: يبني من `api/Dockerfile` ويستورد مكتبة الوكلاء بالكامل.
- `gateway`: يبني من `gateway/Dockerfile` لتوفير نقطة الاتصال الموحدة.
- `db`: صورة رسمية لـPostgreSQL مع حجم دائم `db_data`.

يمكنك تخصيص المنافذ أو المفاتيح عبر متغيرات البيئة في `.env`.

## 🧩 التوسعة التالية
- ربط خدمة الـCore بموفّرين حقيقيين مثل OpenAI أو Anthropic.
- إضافة وكلاء جدد داخل `ai_agents/` وتسجيلهم في `ai_agents/registry.py`.
- بناء مهام مركّبة داخل `api/main.py` تستخدم `delegate_to_core` للدمج بين الوكلاء والاستدلال العام.

> هذه البنية تمنحك نقطة بداية منظمة ومرنة لتشغيل نظام وكلاء متكامل مع قابلية للنمو والتخصيص.
