# Core Service

خدمة Core الأساسية لمشروع Top-TieR Global HUB AI

## الهيكل

```
core/
├── main.py           # تطبيق FastAPI الرئيسي
├── Dockerfile        # ملف Docker
└── requirements.txt  # متطلبات Python
```

## التشغيل

### باستخدام Docker Compose:

```bash
docker compose up -d --build core
```

### باستخدام السكريبت السريع:

```bash
chmod +x scripts/start_core.sh
./scripts/start_core.sh
```

### باستخدام Bot Run All:

```bash
./scripts/bot_run_all.sh
```

## نقاط النهاية (Endpoints)

- `GET /` - الصفحة الرئيسية
- `GET /health` - فحص الصحة

## الاختبار

```bash
# فحص الصحة
curl http://localhost:8000/health

# الصفحة الرئيسية
curl http://localhost:8000/
```

## المنفذ

- المنفذ الافتراضي: `8000`

## التكامل

خدمة Core جاهزة للتكامل مع:
- Gateway
- RAG Engine
- Phi3
- Qdrant
- باقي خدمات النظام
