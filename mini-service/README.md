# Mini Service (Isolated Safe Health Endpoint)

خدمة تجريبية صغيرة ومعزولة:
- لا تعتمد على بقية مكوّنات المشروع.
- لا تستخدم قواعد بيانات أو Redis أو مفاتيح.
- تعمل داخل Docker بمستخدم غير الجذر (appuser).
- تستجيب فقط على `/health`.
- الهدف: اختبار النشر الآمن دون التأثير على الخدمات الأساسية.

## Usage (Local)
```bash
cd mini-service
bash run_local.sh
curl http://localhost:8085/health
```
متوقع:
```json
{"status":"ok","service":"mini-safe","version":"1.0.0","uptime":"1.234567s"}
```

## Docker Manual
```bash
cd mini-service
docker build -t mini-safe .
docker run -p 8085:8080 -e PORT=8080 mini-safe
```

## Railway / Render
- أضف الخدمة كخدمة مستقلة (New Service)، استخدم Dockerfile الموجود.
- لا تحتاج متغيرات بيئة خاصة (PORT يُمرَّر تلقائياً).

## Security / أمان
- تشغيل بمستخدم غير الجذر.
- عدم تضمين أي أسرار أو مفاتيح.
- لا كتابة خارج مجلد العمل.

## Extensibility
- لاحقاً يمكن إضافة `/ready` أو `/metrics` أو دعم OpenAI بشكل معزول.

---
English Summary:
A minimal, isolated health-only micro service under `mini-service/` for safe deployment testing. No external deps, non-root runtime, simple JSON uptime reporting.
