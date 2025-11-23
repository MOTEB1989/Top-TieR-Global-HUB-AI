# 📋 أوامر الإعداد والتشغيل السريعة

## الإعداد الأولي (نسخ ولصق مباشرة)

```bash
# 1️⃣ جعل جميع السكربتات قابلة للتنفيذ
chmod +x scripts/check_connections.sh scripts/setup_check_connections.sh

# 2️⃣ إنشاء مجلد التقارير
mkdir -p reports

# 3️⃣ نسخ ملف البيئة (إن لم يكن موجوداً)
[ ! -f .env ] && cp .env.example .env && echo "✅ تم نسخ .env.example إلى .env"

# 4️⃣ عرض الأسرار المطلوبة
echo "🔑 المفاتيح المطلوبة:"
grep -E "^[A-Z_]+=" .env.example | cut -d= -f1
```

## اختبار سريع بدون مفاتيح

```bash
# تشغيل فحص بسيط (سيظهر missing للأسرار)
API_PORT=3000 bash scripts/check_connections.sh

# عرض التقرير
cat reports/check_connections.json | python3 -m json.tool
```

## إضافة المفاتيح محلياً (للاختبار)

```bash
# تصدير المفاتيح مؤقتاً في الجلسة الحالية
export TELEGRAM_BOT_TOKEN="ضع_التوكن_هنا"
export TELEGRAM_CHAT_ID="6090738107"
export TELEGRAM_ALLOWLIST="8256840669,6090738107"
export GITHUB_TOKEN="$(gh auth token 2>/dev/null || echo '')"
export OPENAI_API_KEY="sk-proj-..."
export GROQ_API_KEY="gsk_..."
export ANTHROPIC_API_KEY="sk-ant-..."
export API_PORT=3000

# تشغيل الفحص مع المفاتيح
bash scripts/check_connections.sh

# عرض التقرير مع jq
jq . reports/check_connections.json
```

## إضافة الأسرار إلى GitHub (يتطلب gh CLI)

```bash
# تسجيل الدخول إلى GitHub CLI (إن لم تكن مسجلاً)
gh auth login

# إضافة جميع الأسرار دفعة واحدة (انسخ كل هذا الكود)
gh secret set TELEGRAM_BOT_TOKEN --body "ضع_التوكن_هنا"
gh secret set TELEGRAM_CHAT_ID --body "6090738107"
gh secret set TELEGRAM_ALLOWLIST --body "8256840669,6090738107"
gh secret set OPENAI_API_KEY --body "sk-proj-..."
gh secret set GROQ_API_KEY --body "gsk_..."
gh secret set ANTHROPIC_API_KEY --body "sk-ant-..."
gh secret set API_PORT --body "3000"
gh secret set DB_URL --body "postgres://user:pass@db:5432/dbname"
gh secret set REDIS_URL --body "redis://redis:6379/0"
gh secret set NEO4J_URI --body "bolt://neo4j:7687"
gh secret set NEO4J_AUTH --body "neo4j/strongpassword"

# التحقق من الأسرار المُضافة
gh secret list
```

## اختبار اتصال Telegram

```bash
# اختبار 1: getMe (تحقق من صحة التوكن)
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq .

# اختبار 2: إرسال رسالة تجريبية
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=✅ اختبار من $(date -u +'%Y-%m-%d %H:%M:%S UTC')" | jq .

# اختبار 3: الحصول على آخر التحديثات (لمعرفة chat_id)
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates" | jq '.result[-1].message.chat.id'
```

## فحص المنافذ والخدمات

```bash
# فحص إذا كان المنفذ 3000 مفتوح ويستمع
ss -ltn | grep ":3000" || echo "❌ لا يوجد استماع على المنفذ 3000"

# عرض جميع المنافذ المفتوحة
ss -ltnp | grep LISTEN

# فحص خدمات Docker Compose
docker compose config --services 2>/dev/null || echo "⚠️ docker compose غير متاح"

# عرض الحاويات العاملة
docker compose ps 2>/dev/null || echo "⚠️ لا توجد حاويات عاملة"
```

## تشغيل الخدمات

```bash
# تشغيل Docker Compose في الخلفية
docker compose up -d

# عرض السجلات
docker compose logs -f --tail=50

# إيقاف الخدمات
docker compose down

# إعادة بناء وتشغيل
docker compose up -d --build
```

## تحليل التقرير

```bash
# عرض التقرير بالكامل
jq . reports/check_connections.json

# عرض فقط الأسرار المفقودة
jq '.env | to_entries | map(select(.value == "missing")) | .[].key' reports/check_connections.json

# عرض حالة Telegram
jq '.telegram_test' reports/check_connections.json

# عرض الخدمات المتاحة
jq '.docker_compose.services' reports/check_connections.json

# عرض المنافذ
jq '.docker_compose.ports' reports/check_connections.json

# عرض حالة المنفذ API
jq '.api_port' reports/check_connections.json

# حساب عدد الأسرار المفقودة
jq '.env | to_entries | map(select(.value == "missing")) | length' reports/check_connections.json
```

## إصلاح المشاكل الشائعة

### مشكلة: docker compose لا يعمل

```bash
# تحقق من تثبيت Docker
docker --version
docker compose version

# إعادة تشغيل Docker daemon
sudo systemctl restart docker

# أو في WSL/Codespaces
sudo service docker restart
```

### مشكلة: المنفذ محجوز

```bash
# معرفة العملية التي تحجز المنفذ
sudo lsof -i :3000

# إيقاف العملية
sudo kill -9 $(lsof -t -i:3000)

# أو تغيير المنفذ
export API_PORT=3001
```

### مشكلة: jq غير مثبت

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y jq

# macOS
brew install jq

# أو عرض JSON بدون jq
python3 -m json.tool < reports/check_connections.json
```

## سكربت الإعداد الآلي

```bash
# سكربت واحد يقوم بكل شيء
bash scripts/setup_check_connections.sh
```

## إنشاء PR (اختياري)

```bash
# إنشاء فرع جديد
git checkout -b feature/add-check-connections-script

# إضافة الملفات
git add scripts/check_connections.sh \
        scripts/setup_check_connections.sh \
        .env.example \
        docs/CHECK_CONNECTIONS_GUIDE.md \
        docs/QUICK_START_COMMANDS.md

# الالتزام
git commit -m "feat: إضافة سكربت check_connections.sh شامل

- سكربت فحص شامل قبل التشغيل
- توثيق كامل بالعربية
- أوامر سريعة للإعداد والاختبار
- دعم Telegram notifications
- تقرير JSON تفصيلي

Resolves: #preflight-check"

# دفع الفرع
git push -u origin feature/add-check-connections-script

# فتح PR (يتطلب gh CLI)
gh pr create \
  --title "feat: إضافة سكربت فحص الاتصالات الشامل" \
  --body "## 📝 الوصف

إضافة سكربت \`check_connections.sh\` شامل للتحقق من جاهزية المشروع قبل التشغيل.

## ✨ الميزات

- ✅ فحص Docker Compose والخدمات
- ✅ فحص المنافذ والاستماع
- ✅ فحص المتغيرات البيئية والأسرار
- ✅ اختبار اتصال Telegram Bot
- ✅ توليد تقرير JSON مفصل
- ✅ إرسال ملخص إلى Telegram
- ✅ توثيق شامل بالعربية

## 📦 الملفات المضافة

- \`scripts/check_connections.sh\` - السكربت الرئيسي
- \`scripts/setup_check_connections.sh\` - سكربت الإعداد الآلي
- \`docs/CHECK_CONNECTIONS_GUIDE.md\` - دليل الاستخدام الكامل
- \`docs/QUICK_START_COMMANDS.md\` - أوامر سريعة (هذا الملف)
- \`.env.example\` - محدّث بجميع الأسرار المطلوبة

## 🧪 الاختبار

\`\`\`bash
# تشغيل الفحص
bash scripts/check_connections.sh

# عرض التقرير
jq . reports/check_connections.json
\`\`\`

## 📋 Checklist

- [x] تم اختبار السكربت محلياً
- [x] توثيق كامل
- [x] أمثلة استخدام واضحة
- [x] معالجة الأخطاء
- [ ] مراجعة الكود
- [ ] اختبار في CI/CD

## 🔗 Related Issues

Closes #preflight-check" \
  --assignee "@me" \
  --label "enhancement,documentation"
```

## التحقق من صحة الإعداد

```bash
# سكربت التحقق الشامل (نسخ ولصق)
echo "🔍 التحقق من الإعداد..."
echo

# 1. التحقق من وجود الملفات
echo "1️⃣ فحص الملفات:"
for file in scripts/check_connections.sh scripts/setup_check_connections.sh .env.example; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (مفقود)"
    fi
done
echo

# 2. التحقق من الصلاحيات
echo "2️⃣ فحص الصلاحيات:"
for script in scripts/check_connections.sh scripts/setup_check_connections.sh; do
    if [[ -x "$script" ]]; then
        echo "  ✅ $script (قابل للتنفيذ)"
    else
        echo "  ⚠️  $script (غير قابل للتنفيذ - تشغيل chmod +x)"
        chmod +x "$script"
    fi
done
echo

# 3. التحقق من الأدوات
echo "3️⃣ فحص الأدوات المطلوبة:"
for cmd in docker jq curl gh; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $cmd ($($cmd --version 2>&1 | head -n1))"
    else
        echo "  ⚠️  $cmd (غير مثبت)"
    fi
done
echo

# 4. التحقق من المجلدات
echo "4️⃣ فحص المجلدات:"
for dir in reports analysis scripts docs; do
    if [[ -d "$dir" ]]; then
        echo "  ✅ $dir"
    else
        echo "  ⚠️  $dir (سيتم إنشاؤه)"
        mkdir -p "$dir"
    fi
done
echo

echo "✅ التحقق مكتمل!"
```

---

**💡 نصيحة:** احفظ هذا الملف للرجوع إليه، فيه جميع الأوامر التي تحتاجها!

**📞 للدعم:** افتح Issue مع وسم `preflight` أو `check-connections`
