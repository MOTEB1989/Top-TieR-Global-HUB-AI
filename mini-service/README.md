# Mini Service (Isolated Safe Health Endpoint)

خدمة تجريبية صغيرة ومعزولة داخل المستودع:
- لا تعتمد على بقية مكوّنات المشروع.
- لا تستخدم قواعد بيانات أو Redis أو مفاتيح API.
- تعمل داخل Docker بمستخدم غير الجذر (appuser).
- تستجيب فقط على المسار `/health`.
- الهدف: اختبار النشر الآمن دون التأثير على الخدمات الأساسية (Gateway / Bot / Core).

## الاستخدام المحلي
```bash
cd mini-service
bash run_local.sh
curl http://localhost:8085/health
```
متوقع:
```json
{"status":"ok","service":"mini-safe","version":"1.0.0","uptime":"1.234567s"}
```

## بناء يدوي
```bash
cd mini-service
docker build -t mini-safe .
docker run -p 8085:8080 -e PORT=8080 mini-safe
```

## على Railway / Render
- أضف الخدمة كـ New Service.
- استخدم Dockerfile الموجود.
- لا حاجة لمتغيرات بيئة إضافية (PORT يُمرَّر تلقائياً). يمكن override محلياً.

## الأمان
- تشغيل بمستخدم غير الجذر يقلل المخاطر.
- لا يوجد أسرار أو مفاتيح.
- لا كتابة خارج مجلد العمل `/app`.
- سطح هجوم صغير (مسار واحد، لا مُدخلات ديناميكية معقّدة).

## التوسعة المحتملة لاحقاً
- إضافة `/ready` أو `/metrics`.
- دعم OpenAI بخيار env.
- إضافة عداد طلبات بسيط.

---
English Summary:
A minimal, isolated health-only microservice under `mini-service/` for safe deployment testing. Non-root, no secrets, no external dependencies.
