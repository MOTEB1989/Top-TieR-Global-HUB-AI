# WORKFLOW MAP – Top-TieR Global HUB AI

## مخطط تدفق العمل العام  

[User Request]
↓
[CLI / Telegram Bot]
↓
[run_everything.sh / railway runner]
↓
[validate_check_connections]
↓
[smart_agent_validator.py]
↓
[Providers / External APIs]
↓
[Data Fusion Layer]
↓
[Final Response]

## شرح المراحل

### المرحلة 1 – الإدخال
- Telegram
- الأوامر من الطرفية
- API لاحقاً

### المرحلة 2 – البوت/الواجهة
تشغيل:
- telegram_chatgpt_mode.py  
أو  
- Smart Agent CLI

### المرحلة 3 – الفحص المسبق
تشغيل:

validate_check_connections.sh

وهو مسؤول عن:
- التأكد من وجود المتغيرات  
- التأكد من توفر curl وجميع الأدوات  
- فحص نماذج OpenAI / Groq / Anthropic

### المرحلة 4 – الذكاء المركزي
الملف الرئيسي:

smart_agent_validator.py

### المرحلة 5 – مصادر البيانات
- WHO  
- WorldBank  
- Wikidata  
- GitHub API  
- Neo4j  
- Redis  

### المرحلة 6 – إخراج النتيجة
- رسالة Telegram  
- نتيجة نصية في CLI  
- ملف JSON (اختياري)
