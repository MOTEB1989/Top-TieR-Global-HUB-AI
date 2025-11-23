#!/usr/bin/env bash
# 
# سكربت آلي لإنشاء PR للسكربت check_connections.sh
# 
# الاستخدام:
#   bash scripts/create_pr_for_check_connections.sh
#

set -euo pipefail

echo "🚀 إنشاء Pull Request لسكربت check_connections.sh"
echo "=================================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# التحقق من git
if ! command -v git >/dev/null 2>&1; then
    echo -e "${RED}❌ git غير مثبت${NC}"
    exit 1
fi

# التحقق من gh CLI
if ! command -v gh >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  gh CLI غير مثبت، سيتم استخدام git فقط${NC}"
    USE_GH=false
else
    USE_GH=true
fi

# التأكد من أننا في الريبو الصحيح
REPO_NAME=$(git config --get remote.origin.url | sed 's/.*\/\([^\/]*\)\.git/\1/' || echo "")
if [[ "$REPO_NAME" != "Top-TieR-Global-HUB-AI" ]]; then
    echo -e "${YELLOW}⚠️  تحذير: قد لا تكون في الريبو الصحيح${NC}"
    echo "الريبو الحالي: $REPO_NAME"
    read -p "هل تريد المتابعة؟ (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# اسم الفرع
BRANCH_NAME="feature/add-check-connections-preflight-script"

echo -e "${BLUE}1️⃣ التحقق من الحالة الحالية...${NC}"
git status --short

# التأكد من عدم وجود تغييرات غير محفوظة مهمة
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✅ لا توجد تغييرات غير محفوظة${NC}"
else
    echo -e "${YELLOW}⚠️  يوجد تغييرات غير محفوظة${NC}"
    git status --short
    echo
    read -p "هل تريد المتابعة وحفظ التغييرات؟ (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo
echo -e "${BLUE}2️⃣ إنشاء فرع جديد: $BRANCH_NAME${NC}"

# حذف الفرع إذا كان موجوداً
if git show-ref --verify --quiet refs/heads/$BRANCH_NAME; then
    echo -e "${YELLOW}⚠️  الفرع موجود بالفعل، سيتم حذفه${NC}"
    git branch -D $BRANCH_NAME || true
fi

# التأكد من أننا على main/master
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    echo -e "${YELLOW}⚠️  لست على الفرع الرئيسي، التبديل إلى main${NC}"
    git checkout main 2>/dev/null || git checkout master
fi

# سحب آخر التحديثات
echo "سحب آخر التحديثات..."
git pull origin $(git branch --show-current) || true

# إنشاء الفرع الجديد
git checkout -b $BRANCH_NAME

echo -e "${GREEN}✅ تم إنشاء الفرع: $BRANCH_NAME${NC}"
echo

echo -e "${BLUE}3️⃣ إضافة الملفات...${NC}"

# التحقق من وجود الملفات
FILES=(
    "scripts/check_connections.sh"
    "scripts/setup_check_connections.sh"
    "scripts/create_pr_for_check_connections.sh"
    ".env.example"
    "docs/CHECK_CONNECTIONS_GUIDE.md"
    "docs/QUICK_START_COMMANDS.md"
)

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        git add "$file"
        echo -e "  ${GREEN}✅ $file${NC}"
    else
        echo -e "  ${YELLOW}⚠️  $file (غير موجود)${NC}"
    fi
done

echo

echo -e "${BLUE}4️⃣ إنشاء الالتزام (commit)...${NC}"

COMMIT_MSG="feat: إضافة سكربت check_connections.sh شامل للتحقق من جاهزية المشروع

🎯 الهدف:
توفير أداة شاملة للتحقق من جاهزية المشروع قبل التشغيل، تفحص الخدمات،
المنافذ، المتغيرات البيئية، والاتصالات الخارجية.

✨ الميزات الجديدة:
- سكربت check_connections.sh شامل لفحص جميع الاتصالات
- فحص Docker Compose والخدمات المُعرّفة
- فحص المنافذ والاستماع على الشبكة
- فحص المتغيرات البيئية والأسرار المطلوبة
- اختبار اتصال Telegram Bot (getMe API)
- توليد تقرير JSON تفصيلي
- إرسال ملخص تلقائي إلى Telegram
- سكربت setup للإعداد الآلي
- توثيق شامل بالعربية مع أمثلة
- أوامر سريعة جاهزة للنسخ واللصق

📦 الملفات المضافة/المعدّلة:
- scripts/check_connections.sh - السكربت الرئيسي للفحص
- scripts/setup_check_connections.sh - سكربت الإعداد الآلي
- scripts/create_pr_for_check_connections.sh - هذا السكربت
- .env.example - محدّث بجميع الأسرار والتوثيق
- docs/CHECK_CONNECTIONS_GUIDE.md - دليل استخدام مفصّل
- docs/QUICK_START_COMMANDS.md - أوامر سريعة للبدء

🧪 الاختبار:
bash scripts/check_connections.sh
jq . reports/check_connections.json

📋 الأسرار المطلوبة:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- TELEGRAM_ALLOWLIST
- OPENAI_API_KEY
- GROQ_API_KEY
- ANTHROPIC_API_KEY
- DB_URL, REDIS_URL, NEO4J_URI, NEO4J_AUTH

🔗 Related:
Closes #preflight-check
Ref: GitHub Copilot guidelines compliance"

git commit -m "$COMMIT_MSG"

echo -e "${GREEN}✅ تم إنشاء الالتزام${NC}"
echo

echo -e "${BLUE}5️⃣ دفع الفرع إلى GitHub...${NC}"

git push -u origin $BRANCH_NAME

echo -e "${GREEN}✅ تم دفع الفرع بنجاح${NC}"
echo

if [[ "$USE_GH" == "true" ]]; then
    echo -e "${BLUE}6️⃣ إنشاء Pull Request...${NC}"
    
    PR_TITLE="feat: إضافة سكربت فحص الاتصالات الشامل check_connections.sh"
    
    PR_BODY="## 📝 الوصف

إضافة سكربت \`check_connections.sh\` شامل للتحقق من جاهزية المشروع قبل التشغيل.

## 🎯 المشكلة

كنا نحتاج أداة موحدة للتحقق من:
- توفر جميع الأسرار والمتغيرات البيئية
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

| الملف | الوصف |
|------|--------|
| \`scripts/check_connections.sh\` | السكربت الرئيسي للفحص الشامل |
| \`scripts/setup_check_connections.sh\` | سكربت الإعداد والاختبار الآلي |
| \`scripts/create_pr_for_check_connections.sh\` | سكربت إنشاء PR آلياً |
| \`.env.example\` | محدّث بجميع الأسرار المطلوبة + توثيق |
| \`docs/CHECK_CONNECTIONS_GUIDE.md\` | دليل استخدام شامل بالعربية |
| \`docs/QUICK_START_COMMANDS.md\` | أوامر جاهزة للنسخ واللصق |

## 🧪 الاختبار

### اختبار بسيط (بدون أسرار):
\`\`\`bash
API_PORT=3000 bash scripts/check_connections.sh
cat reports/check_connections.json | python3 -m json.tool
\`\`\`

### اختبار كامل (مع الأسرار):
\`\`\`bash
export TELEGRAM_BOT_TOKEN=\"your_token\"
export TELEGRAM_CHAT_ID=\"your_chat_id\"
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
gh secret set TELEGRAM_CHAT_ID --body \"your_chat_id\"
gh secret set TELEGRAM_ALLOWLIST --body \"8256840669,6090738107\"
gh secret set OPENAI_API_KEY --body \"sk-proj-...\"
gh secret set GROQ_API_KEY --body \"gsk_...\"
gh secret set ANTHROPIC_API_KEY --body \"sk-ant-...\"
gh secret set DB_URL --body \"postgres://...\"
gh secret set REDIS_URL --body \"redis://...\"
gh secret set NEO4J_URI --body \"bolt://...\"
gh secret set NEO4J_AUTH --body \"neo4j/password\"
\`\`\`

## 🔍 أمثلة من التقرير

<details>
<summary>مثال لتقرير JSON</summary>

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
  \"telegram_test\": \"ok\",
  \"env\": {
    \"TELEGRAM_BOT_TOKEN\": \"present\",
    \"TELEGRAM_CHAT_ID\": \"present\",
    \"OPENAI_API_KEY\": \"present\",
    \"GROQ_API_KEY\": \"missing\",
    \"DB_URL\": \"present\"
  }
}
\`\`\`
</details>

## ✅ Checklist

- [x] تم إنشاء السكربت الرئيسي
- [x] تم اختبار السكربت محلياً
- [x] توثيق شامل بالعربية
- [x] أمثلة استخدام واضحة
- [x] معالجة الأخطاء
- [x] دعم JSON output
- [x] دعم Telegram notifications
- [x] تحديث \`.env.example\`
- [x] إنشاء دليل الاستخدام
- [x] إنشاء أوامر سريعة
- [ ] مراجعة الكود من المشرفين
- [ ] اختبار في CI/CD
- [ ] دمج في \`main\`

## 🔗 Related Issues

Closes #preflight-check
Ref: GitHub Copilot usage guidelines

## 📸 Screenshots

سيتم إضافة لقطات شاشة للتقرير بعد الاختبار.

## 💬 ملاحظات إضافية

- السكربت آمن ولا يطبع الأسرار في الـ output
- يدعم التشغيل في Codespaces وlocal
- متوافق مع bash 4.0+
- يتطلب: \`curl\`, \`docker/docker-compose\` (اختياري), \`jq\` (اختياري)

---

**👨‍💻 المطور:** @MOTEB1989  
**📅 التاريخ:** $(date +'%Y-%m-%d')  
**🏷️ الإصدار:** v1.0.0"

    # إنشاء PR
    if gh pr create \
        --title "$PR_TITLE" \
        --body "$PR_BODY" \
        --assignee "@me" \
        --label "enhancement,documentation,preflight" \
        --base main; then
        
        echo -e "${GREEN}✅ تم إنشاء Pull Request بنجاح!${NC}"
        echo
        echo "عرض PR في المتصفح:"
        gh pr view --web
    else
        echo -e "${RED}❌ فشل إنشاء PR${NC}"
        echo "يمكنك إنشاؤه يدوياً من:"
        echo "https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/compare/$BRANCH_NAME"
    fi
else
    echo -e "${YELLOW}⚠️  gh CLI غير متاح${NC}"
    echo
    echo "يمكنك إنشاء PR يدوياً من:"
    echo "https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/compare/$BRANCH_NAME"
fi

echo
echo "=================================================="
echo -e "${GREEN}✅ العملية مكتملة!${NC}"
echo "=================================================="
echo
echo "الخطوات التالية:"
echo "1. راجع PR على GitHub"
echo "2. انتظر مراجعة المشرفين"
echo "3. دمج PR في main بعد الموافقة"
echo
