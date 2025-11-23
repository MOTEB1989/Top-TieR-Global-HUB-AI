#!/usr/bin/env bash
# 
# ⚡ أوامر Git السريعة لإنشاء PR
# نسخ هذه الأوامر وألصقها مباشرة في Terminal
# 

# ========================================
# 🎯 الطريقة 1: استخدام السكربت الآلي
# ========================================

bash scripts/create_pr_for_check_connections.sh


# ========================================
# 🎯 الطريقة 2: أوامر يدوية (نسخ كل هذا الكود)
# ========================================

# 1. التأكد من أننا على الفرع الرئيسي
git checkout main && git pull origin main

# 2. إنشاء فرع جديد
git checkout -b feature/add-check-connections-preflight-script

# 3. جعل السكربتات قابلة للتنفيذ
chmod +x scripts/check_connections.sh \
         scripts/setup_check_connections.sh \
         scripts/create_pr_for_check_connections.sh

# 4. إضافة جميع الملفات
git add scripts/check_connections.sh \
        scripts/setup_check_connections.sh \
        scripts/create_pr_for_check_connections.sh \
        .env.example \
        docs/CHECK_CONNECTIONS_GUIDE.md \
        docs/QUICK_START_COMMANDS.md \
        IMPLEMENTATION_SUMMARY.md \
        scripts/GIT_READY_COMMANDS.sh

# 5. عرض التغييرات
git status

# 6. إنشاء commit
git commit -m "feat: إضافة سكربت check_connections.sh شامل للتحقق من جاهزية المشروع

🎯 الهدف:
توفير أداة شاملة للتحقق من جاهزية المشروع قبل التشغيل، تفحص الخدمات،
المنافذ، المتغيرات البيئية، والاتصالات الخارجية.

✨ الميزات الجديدة:
- سكربت check_connections.sh شامل لفحص جميع الاتصالات
- فحص Docker Compose والخدمات المُعرّفة
- فحص المنافذ والاستماع على الشبكة
- فحص المتغيرات البيئية والأسرار المطلوبة (11 سر)
- اختبار اتصال Telegram Bot (getMe API)
- توليد تقرير JSON تفصيلي في reports/check_connections.json
- إرسال ملخص تلقائي إلى Telegram
- سكربت setup للإعداد الآلي
- سكربت create_pr للأتمتة الكاملة
- توثيق شامل بالعربية مع أمثلة عملية
- أوامر سريعة جاهزة للنسخ واللصق

📦 الملفات المضافة/المعدّلة:
- scripts/check_connections.sh - السكربت الرئيسي (200+ سطر)
- scripts/setup_check_connections.sh - الإعداد الآلي
- scripts/create_pr_for_check_connections.sh - إنشاء PR آلياً
- scripts/GIT_READY_COMMANDS.sh - هذا الملف
- .env.example - محدّث بجميع الأسرار والتوثيق
- docs/CHECK_CONNECTIONS_GUIDE.md - دليل استخدام مفصّل (250+ سطر)
- docs/QUICK_START_COMMANDS.md - أوامر سريعة للبدء
- IMPLEMENTATION_SUMMARY.md - ملخص التنفيذ الكامل

🧪 الاختبار:
bash scripts/check_connections.sh
jq . reports/check_connections.json

📋 الأسرار المطلوبة (11):
1. TELEGRAM_BOT_TOKEN - مفتاح البوت من @BotFather
2. TELEGRAM_CHAT_ID - معرف المحادثة الرقمي
3. TELEGRAM_ALLOWLIST - قائمة User IDs المسموح لهم
4. GITHUB_TOKEN - توكن GitHub (للـ CI/CD)
5. OPENAI_API_KEY - مفتاح OpenAI
6. GROQ_API_KEY - مفتاح Groq
7. ANTHROPIC_API_KEY - مفتاح Anthropic
8. DB_URL - عنوان PostgreSQL
9. REDIS_URL - عنوان Redis
10. NEO4J_URI - عنوان Neo4j
11. NEO4J_AUTH - مصادقة Neo4j

🔗 Related:
Closes #preflight-check
Ref: GitHub Copilot usage guidelines
Ref: SECURITY.md compliance"

# 7. دفع الفرع إلى GitHub
git push -u origin feature/add-check-connections-preflight-script

# 8. إنشاء PR باستخدام GitHub CLI
gh pr create \
  --title "feat: إضافة سكربت فحص الاتصالات الشامل check_connections.sh" \
  --body "## 📝 الوصف

إضافة سكربت \`check_connections.sh\` شامل للتحقق من جاهزية المشروع قبل التشغيل.

## 🎯 المشكلة

كنا نحتاج أداة موحدة للتحقق من:
- توفر جميع الأسرار والمتغيرات البيئية (11 متغير)
- صحة خدمات Docker Compose
- استماع المنافذ المطلوبة
- صحة اتصالات Telegram Bot
- جاهزية البنية التحتية

## ✨ الحل

سكربت \`check_connections.sh\` يقوم بـ:

### الفحوصات الأساسية:
- ✅ فحص وجود \`docker-compose.yml\` والخدمات المُعرّفة
- ✅ فحص المنافذ المنشورة والاستماع المحلي
- ✅ فحص جميع المتغيرات البيئية المطلوبة (11 متغير)
- ✅ اختبار Telegram Bot API (getMe endpoint)
- ✅ البحث عن إعدادات النماذج (MODEL, PHI3, QDRANT_URL)

### المخرجات:
- 📊 تقرير JSON مفصّل في \`reports/check_connections.json\`
- 📱 ملخص تلقائي يُرسل إلى Telegram (اختياري)
- 🖥️ عرض موجز في Terminal

## 📦 الملفات المضافة

| الملف | الوصف | السطور |
|------|--------|--------|
| \`scripts/check_connections.sh\` | السكربت الرئيسي للفحص الشامل | 200+ |
| \`scripts/setup_check_connections.sh\` | سكربت الإعداد والاختبار الآلي | 80+ |
| \`scripts/create_pr_for_check_connections.sh\` | سكربت إنشاء PR آلياً | 300+ |
| \`scripts/GIT_READY_COMMANDS.sh\` | أوامر Git جاهزة | 150+ |
| \`.env.example\` | محدّث بجميع الأسرار + توثيق | 100+ |
| \`docs/CHECK_CONNECTIONS_GUIDE.md\` | دليل استخدام شامل بالعربية | 250+ |
| \`docs/QUICK_START_COMMANDS.md\` | أوامر جاهزة للنسخ | 300+ |
| \`IMPLEMENTATION_SUMMARY.md\` | ملخص التنفيذ الكامل | 305 |

**المجموع:** ~1500+ سطر من الكود والوثائق

## 🧪 الاختبار

### اختبار بسيط (بدون أسرار):
\`\`\`bash
API_PORT=3000 bash scripts/check_connections.sh
cat reports/check_connections.json | python3 -m json.tool
\`\`\`

### اختبار كامل (مع الأسرار):
\`\`\`bash
export TELEGRAM_BOT_TOKEN=\"your_token\"
export TELEGRAM_CHAT_ID=\"6090738107\"
export OPENAI_API_KEY=\"sk-proj-...\"
bash scripts/check_connections.sh
jq . reports/check_connections.json
\`\`\`

### الإعداد الآلي:
\`\`\`bash
bash scripts/setup_check_connections.sh
\`\`\`

## 📋 الأسرار المطلوبة

يجب إضافة هذه الأسرار في GitHub Settings → Secrets:

\`\`\`bash
gh secret set TELEGRAM_BOT_TOKEN --body \"your_token\"
gh secret set TELEGRAM_CHAT_ID --body \"6090738107\"
gh secret set TELEGRAM_ALLOWLIST --body \"8256840669,6090738107\"
gh secret set OPENAI_API_KEY --body \"sk-proj-...\"
gh secret set GROQ_API_KEY --body \"gsk_...\"
gh secret set ANTHROPIC_API_KEY --body \"sk-ant-...\"
gh secret set API_PORT --body \"3000\"
gh secret set DB_URL --body \"postgres://user:pass@host:5432/db\"
gh secret set REDIS_URL --body \"redis://redis:6379/0\"
gh secret set NEO4J_URI --body \"bolt://neo4j:7687\"
gh secret set NEO4J_AUTH --body \"neo4j/password\"
\`\`\`

## 🔍 مثال لتقرير JSON

<details>
<summary>انقر لعرض مثال التقرير</summary>

\`\`\`json
{
  \"repo\": \"MOTEB1989/Top-TieR-Global-HUB-AI\",
  \"scan_time\": \"2025-11-23T10:30:00Z\",
  \"docker_compose\": {
    \"present\": true,
    \"services\": \"api,postgres,redis,neo4j,qdrant\",
    \"ports\": \"3000:3000,5432:5432,6379:6379,7687:7687\"
  },
  \"api_port\": {
    \"port\": 3000,
    \"listening\": \"true\"
  },
  \"models_found_count\": 15,
  \"telegram_test\": \"ok\",
  \"env\": {
    \"TELEGRAM_BOT_TOKEN\": \"present\",
    \"TELEGRAM_CHAT_ID\": \"present\",
    \"TELEGRAM_ALLOWLIST\": \"present\",
    \"GITHUB_TOKEN\": \"present\",
    \"OPENAI_API_KEY\": \"present\",
    \"GROQ_API_KEY\": \"missing\",
    \"ANTHROPIC_API_KEY\": \"missing\",
    \"DB_URL\": \"present\",
    \"REDIS_URL\": \"present\",
    \"NEO4J_URI\": \"present\",
    \"NEO4J_AUTH\": \"present\"
  }
}
\`\`\`
</details>

## ✅ Checklist

- [x] تم إنشاء السكربت الرئيسي (200+ سطر)
- [x] تم اختبار السكربت محلياً
- [x] توثيق شامل بالعربية (800+ سطر)
- [x] أمثلة استخدام واضحة
- [x] معالجة الأخطاء الشاملة
- [x] دعم JSON output
- [x] دعم Telegram notifications
- [x] تحديث \`.env.example\` بالتوثيق
- [x] إنشاء دليل الاستخدام الكامل
- [x] إنشاء أوامر سريعة جاهزة
- [x] سكربت الإعداد الآلي
- [x] سكربت إنشاء PR الآلي
- [x] ملخص التنفيذ الشامل
- [ ] مراجعة الكود من المشرفين
- [ ] اختبار في CI/CD
- [ ] دمج في \`main\`

## 🔗 Related Issues

Closes #preflight-check  
Ref: GitHub Copilot usage guidelines  
Ref: SECURITY.md compliance

## 💬 ملاحظات إضافية

- ✅ السكربت آمن ولا يطبع الأسرار في الـ output
- ✅ يدعم التشغيل في Codespaces وlocal وCI/CD
- ✅ متوافق مع bash 4.0+
- ✅ يتطلب: \`curl\` (إلزامي), \`docker/docker-compose\` (اختياري), \`jq\` (اختياري)
- ✅ توثيق شامل بالعربية: 800+ سطر
- ✅ أمثلة عملية جاهزة للتنفيذ

## 📊 الإحصائيات

- **الملفات المُنشأة:** 8 ملفات
- **إجمالي السطور:** ~1500+ سطر
- **اللغات:** Bash, Markdown
- **الوثائق:** عربي كامل
- **الأسرار المدعومة:** 11 سر
- **وقت التطوير:** جلسة واحدة
- **الجودة:** إنتاج-جاهز

---

**👨‍💻 المطور:** @MOTEB1989  
**🤖 بمساعدة:** GitHub Copilot  
**📅 التاريخ:** 2025-11-23  
**🏷️ الإصدار:** v1.0.0" \
  --assignee "@me" \
  --label "enhancement,documentation,preflight,scripts" \
  --base main

# 9. عرض PR في المتصفح
gh pr view --web


# ========================================
# 🎯 الطريقة 3: إذا فشل gh CLI
# ========================================

# إذا فشل gh pr create، افتح هذا الرابط يدوياً:
echo ""
echo "=================================================="
echo "إذا فشل إنشاء PR آلياً، افتح هذا الرابط:"
echo "https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/compare/feature/add-check-connections-preflight-script"
echo "=================================================="
echo ""


# ========================================
# 📋 بعد إنشاء PR
# ========================================

# عرض حالة PR
gh pr status

# مراجعة التغييرات
gh pr diff

# إضافة مراجعين (اختياري)
# gh pr edit --add-reviewer REVIEWER_USERNAME


# ========================================
# ✅ تم! PR جاهز للمراجعة
# ========================================
