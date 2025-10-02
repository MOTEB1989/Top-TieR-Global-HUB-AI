# التحقق من مساحات المعرفة الخاصة بالنماذج

يوضح هذا الدليل كيفية التأكد من أن مستودع `Top-TieR-Global-HUB-AI` مرتبط بخدمة Codex وأن كل نموذج يمتلك مساحة منفصلة في قاعدة المعرفة (Knowledge Base).

## 1. التأكد من حالة Codex

نفِّذ الأمر التالي للتأكد من أن خط أنابيب الإدخال (ingestion pipeline) يعمل وأن المستودع مربوط بخدمة Codex:

```bash
codex status github --repo MOTEB1989/Top-TieR-Global-HUB-AI
```

عندما تظهر أيقونة ✅ يكون الربط ناجحًا ويتم استيراد التعديلات تلقائيًا بعد كل commit.

## 2. استعراض الـ Namespaces في قاعدة المعرفة

يحتوي المشروع على سكربت `scripts/check_kb_namespaces.py` لفحص مجموعات ChromaDB.

```bash
python scripts/check_kb_namespaces.py --store-path .kb_store
```

سيعرض السكربت قائمة بالمساحات المكتشفة. مثال على المخرجات المتوقعة:

```
Detected namespaces:
- mohsen_gj
- saudi_banks
- saudi_nexus
```

إذا لم تظهر أي مساحات، تأكد من أن عملية المزامنة اكتملت وأن مسار التخزين (`--store-path`) يشير إلى قاعدة المعرفة الصحيحة.

