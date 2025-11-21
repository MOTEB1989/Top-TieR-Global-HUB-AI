# AI Gateway V3 (CLI)

يوفر `gateway.py` طبقة أدوات CLI لمراجعة الملفات مع مخرجات Markdown جاهزة للدمج في تقارير المراجعة أو تعليقات Pull Requests.

- **مزودات متعددة:** OpenAI / Groq / Azure / Local (خادم داخلي)
- **مهام متعددة لكل ملف:** `code_review`، `legal`، `medical`، `tech`، `banking`، `document`
- **أنواع ملفات متعددة:** txt / md / py / rs / js / ts / yaml / yml / docx / pdf
- **المخرجات:** أقسام Markdown منظمة حسب المهمة مع ملخصات وتوصيات

## المتغيرات البيئية المطلوبة
- `PROVIDER` يحدد المزود (`openai`، `groq`، `azure`، `local`).
- `OPENAI_API_KEY` و `OPENAI_MODEL` (اختياري، الافتراضي `gpt-4o-mini`).
- `GROQ_API_KEY` و `GROQ_MODEL` (اختياري، الافتراضي `mixtral-8x7b-32768`).
- `AZURE_OPENAI_KEY` و `AZURE_OPENAI_ENDPOINT` و `AZURE_OPENAI_DEPLOYMENT` (ويمكن ضبط `AZURE_OPENAI_API_VERSION`).
- `LOCAL_MODEL_ENDPOINT` عند استخدام مزود محلي يدعم حمولة JSON `{ "system": ..., "input": ... }` ويرد `{ "output": ... }`.

## أمثلة الاستخدام
تشغيل تلقائي مع اكتشاف المهمة:
```bash
export PROVIDER=openai
export OPENAI_API_KEY=...
python gateway.py --task auto --file path/to/file.py > review.md
```

تحديد مهمة بعينها:
```bash
python gateway.py --task code_review --file src/module.py
```

للمراجعة ضمن CI انظر سير العمل `.github/workflows/ai-gateway-file-review.yml` الذي ينشئ تقريرًا ملحقًا كقطعة أثر.

## ملاحظات السلامة
- التحليلات القانونية/الطبية/المصرفية صادرة من نموذج ذكاء اصطناعي **ولا تُستخدم كأساس وحيد لاتخاذ القرارات**.
- يجب مراجعة النتائج من قبل خبير بشري قبل أي إجراء عملي.
