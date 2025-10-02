# Docker Dev Workflow

هذه الملاحظات تساعدك على تشغيل الحزمة الهجينة محليًا باستخدام Docker وتأكيد جاهزية الخدمات قبل البدء بالتطوير.

## التحضير
1. انسخ ملف البيئة الافتراضي ثم حدّث المفاتيح عند الحاجة:
   ```bash
   cp .env.example .env
   ```
2. إذا كنت ستجرب التكامل مع OpenAI فاحفظ مفتاح `OPENAI_API_KEY` وأي إعدادات اختيارية في `.env`.

## تشغيل الخدمات
بناء الحاويات وتشغيلها يتم من خلال Docker Compose:
```bash
docker compose up --build
```
هذا الأمر ينشئ صور Rust Core و Gateway (Node.js) ويشغلهما في الحاويات نفسها المستخدمة في الإنتاج المصغّر.

## التأكد من الصحة (Health Checks)
بعد الإقلاع تأكد أن كل خدمة تعمل:

- **Core (Rust/Axum):** `http://localhost:8080/health`
- **API Gateway (Node.js):** `http://localhost:3000/v1/health`

يمكنك استخدام `curl` أو أي متصفح/أداة HTTP سريعة:
```bash
curl http://localhost:8080/health
curl http://localhost:3000/v1/health
```
ينبغي أن تحصل على استجابة JSON بسيطة (200 OK) تشير إلى أن الخدمة جاهزة.

## اختبار التكامل مع OpenAI
مع وجود مفتاح OpenAI في `.env` يمكن التأكد من المسار الرئيسي للاستدلال:
```bash
curl -X POST http://localhost:3000/v1/ai/infer \
  -H "Content-Type: application/json" \
  -d '{ "messages": [ { "role": "user", "content": "Hello from LexCode" } ] }'
```
يتوقع أن يعيد Gateway رد نموذج اللغة القادم من OpenAI. في حال وجود خطأ ستظهر رسالة واضحة في السجل.

## إيقاف الحاويات وتنظيفها
لإيقاف كل الخدمات اضغط `Ctrl+C` في الطرفية التي تشغّل Compose، ثم اختياريًا نظّف الصور/الحاويات:
```bash
docker compose down
```
يمكنك أيضًا إضافة `--volumes` إذا رغبت بإزالة مجلدات البيانات المؤقتة.

## نصائح أثناء التطوير
- راقب سجلات الحاويات عبر نافذة `docker compose` أو باستخدام `docker compose logs -f` عند الحاجة.
- عند تعديل الشيفرة أعد بناء الصور باستخدام `docker compose up --build` لضمان تحديث الاعتمادات.
- استخدم هذه الدورة قبل فتح Pull Request للتأكد من أن الخدمات الأساسية سليمة وأن الاستدلال يعمل.

