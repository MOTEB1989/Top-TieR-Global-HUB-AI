# 🔍 دليل استخدام سكربت check_connections.sh

## نظرة عامة

سكربت `check_connections.sh` هو أداة شاملة للتحقق من جاهزية المشروع قبل التشغيل. يفحص:
- ✅ ملفات Docker Compose والخدمات
- ✅ المنافذ والاستماع على الشبكة
- ✅ المتغيرات البيئية والأسرار
- ✅ اتصال Telegram Bot
- ✅ نماذج الذكاء الاصطناعي المتاحة

## 🚀 التثبيت السريع

```bash
# 1. جعل السكربت قابلاً للتنفيذ
chmod +x scripts/check_connections.sh

# 2. نسخ ملف البيئة
cp .env.example .env

# 3. تحرير .env وإضافة المفاتيح
nano .env  # أو vi .env

# 4. تشغيل السكربت
./scripts/check_connections.sh
```

## 📋 المتغيرات البيئية المطلوبة

### أساسية (Essential)

| المتغير | الوصف | مثال | كيفية الحصول عليه |
|---------|--------|------|------------------|
| `TELEGRAM_BOT_TOKEN` | رمز البوت من BotFather | `123456:ABCdef...` | [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | معرف المحادثة الرقمي | `6090738107` | استخدم `/whoami` مع البوت |
| `OPENAI_API_KEY` | مفتاح OpenAI | `sk-proj-...` | [platform.openai.com](https://platform.openai.com/api-keys) |
| `API_PORT` | منفذ الـ API | `3000` | اختياري (افتراضي: 3000) |

### اختيارية (Optional)

| المتغير | الوصف | مثال |
|---------|--------|------|
| `TELEGRAM_ALLOWLIST` | قائمة المستخدمين المسموح لهم | `8256840669,6090738107` |
| `GROQ_API_KEY` | مفتاح Groq API | `gsk_...` |
| `ANTHROPIC_API_KEY` | مفتاح Anthropic | `sk-ant-...` |
| `DB_URL` | عنوان PostgreSQL | `postgres://user:pass@host:5432/db` |
| `REDIS_URL` | عنوان Redis | `redis://localhost:6379/0` |
| `NEO4J_URI` | عنوان Neo4j | `bolt://localhost:7687` |
| `NEO4J_AUTH` | مصادقة Neo4j | `neo4j/password` |

## 🔐 إضافة الأسرار إلى GitHub

### استخدام GitHub CLI

```bash
# تسجيل الدخول
gh auth login

# إضافة الأسرار (واحدًا تلو الآخر)
gh secret set TELEGRAM_BOT_TOKEN --body "YOUR_TOKEN_HERE"
gh secret set TELEGRAM_CHAT_ID --body "6090738107"
gh secret set TELEGRAM_ALLOWLIST --body "8256840669,6090738107"
gh secret set OPENAI_API_KEY --body "sk-proj-..."
gh secret set GROQ_API_KEY --body "gsk_..."
gh secret set ANTHROPIC_API_KEY --body "sk-ant-..."
gh secret set API_PORT --body "3000"

# أو من ملف
gh secret set TELEGRAM_BOT_TOKEN < token.txt
```

### عبر واجهة GitHub

1. اذهب إلى: `https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/settings/secrets/actions`
2. اضغط **New repository secret**
3. أضف كل سر على حدة

### أسماء الأسرار الموصى بها

**⚠️ ملاحظة مهمة:** لا تستخدم أسماء تبدأ بـ `GITHUB_` (محجوزة للنظام)

```
✅ مسموح:
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
TELEGRAM_ALLOWLIST
OPENAI_API_KEY
GROQ_API_KEY
ANTHROPIC_API_KEY
DB_URL
REDIS_URL
NEO4J_URI
NEO4J_AUTH
API_PORT

❌ ممنوع:
GITHUB_SECRET_KEY  (يبدأ بـ GITHUB_)
```

## 🧪 اختبار الاتصالات

### 1. اختبار Telegram Bot

```bash
# اختبار getMe
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq .

# إرسال رسالة تجريبية
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=✅ Test message from $(date -u)"
```

### 2. اختبار المنفذ API_PORT

```bash
# فحص الاستماع على المنفذ 3000
ss -ltn | grep ":3000"
# أو
lsof -iTCP -sTCP:LISTEN -P | grep ":3000"
```

### 3. اختبار Docker Compose

```bash
# عرض الخدمات المُعرّفة
docker compose config --services

# فحص المنافذ المنشورة
docker compose config | grep -A 2 "ports:"

# تشغيل الخدمات
docker compose up -d
docker compose ps
```

## 📊 فهم التقرير

السكربت ينتج ملف JSON في `reports/check_connections.json`:

```json
{
  "repo": "MOTEB1989/Top-TieR-Global-HUB-AI",
  "scan_time": "2025-11-23T10:30:00Z",
  "docker_compose": {
    "present": true,
    "services": "api,postgres,redis,neo4j",
    "ports": "3000:3000,5432:5432,6379:6379"
  },
  "api_port": {
    "port": 3000,
    "listening": "true"
  },
  "telegram_test": "ok",
  "env": {
    "TELEGRAM_BOT_TOKEN": "present",
    "TELEGRAM_CHAT_ID": "present",
    "OPENAI_API_KEY": "present",
    "GROQ_API_KEY": "missing",
    "DB_URL": "missing"
  }
}
```

### قراءة التقرير

```bash
# عرض التقرير بتنسيق جميل
jq . reports/check_connections.json

# فحص الأسرار المفقودة
jq '.env | to_entries | map(select(.value == "missing"))' reports/check_connections.json

# فحص حالة Telegram
jq '.telegram_test' reports/check_connections.json
```

## 🐛 استكشاف الأخطاء

### المشكلة: Telegram Bot لا يرسل رسائل

**الأسباب المحتملة:**
1. `TELEGRAM_BOT_TOKEN` خاطئ أو منتهي الصلاحية
2. `TELEGRAM_CHAT_ID` خاطئ
3. البوت غير مفعّل (تم إيقافه من BotFather)
4. `TELEGRAM_ALLOWLIST` يمنع المستخدم

**الحل:**
```bash
# تحقق من صحة التوكن
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# تحقق من Chat ID باستخدام getUpdates
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates" | jq .

# أرسل /start للبوت ثم شغّل getUpdates مرة أخرى
```

### المشكلة: API Port لا يستمع

**الأسباب:**
1. الخدمة لم تبدأ
2. المنفذ محجوز من عملية أخرى
3. خطأ في `docker-compose.yml`

**الحل:**
```bash
# فحص العمليات على المنفذ
sudo lsof -i :3000

# إيقاف العملية المحجوزة للمنفذ
sudo kill -9 $(lsof -t -i:3000)

# إعادة تشغيل الخدمات
docker compose down
docker compose up -d
```

### المشكلة: متغيرات البيئة مفقودة

**الحل:**
```bash
# تحقق من ملف .env
cat .env

# تحميل المتغيرات
set -a
source .env
set +a

# تحقق من المتغير
echo $TELEGRAM_BOT_TOKEN
```

## 🔄 سير العمل الموصى به

### في البيئة المحلية (Local/Codespace)

```bash
# 1. نسخ البيئة وتحريرها
cp .env.example .env
nano .env

# 2. تحميل المتغيرات
source .env

# 3. تشغيل الفحص
./scripts/check_connections.sh

# 4. فحص التقرير
jq . reports/check_connections.json

# 5. إصلاح الأخطاء وإعادة التشغيل
# ... أضف المفاتيح المفقودة ...
./scripts/check_connections.sh
```

### في GitHub Actions

```yaml
# .github/workflows/preflight.yml
name: Preflight Check

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run preflight check
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          TELEGRAM_ALLOWLIST: ${{ secrets.TELEGRAM_ALLOWLIST }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          API_PORT: 3000
        run: ./scripts/check_connections.sh
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: preflight-report
          path: reports/check_connections.json
```

## 📝 أمثلة استخدام

### مثال 1: فحص سريع بدون Telegram

```bash
API_PORT=3000 ./scripts/check_connections.sh
```

### مثال 2: فحص كامل مع إرسال لـ Telegram

```bash
export TELEGRAM_BOT_TOKEN="123456:ABCdef..."
export TELEGRAM_CHAT_ID="6090738107"
export TELEGRAM_ALLOWLIST="8256840669,6090738107"
export OPENAI_API_KEY="sk-proj-..."
export API_PORT=3000

./scripts/check_connections.sh
```

### مثال 3: فحص مع قواعد البيانات

```bash
export DB_URL="postgres://admin:pass@localhost:5432/toptier"
export REDIS_URL="redis://localhost:6379/0"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_AUTH="neo4j/strongpass"

./scripts/check_connections.sh
```

## 🔗 روابط مفيدة

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Groq Console](https://console.groq.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [GitHub CLI](https://cli.github.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## 💡 نصائح أمان

1. **لا تشارك المفاتيح:** لا تنسخ مفاتيح حقيقية في المحادثات أو Issues
2. **استخدم .gitignore:** تأكد أن `.env` مُضاف إلى `.gitignore`
3. **دوّر المفاتيح:** غيّر المفاتيح بشكل دوري
4. **استخدم Secrets Manager:** في الإنتاج، استخدم AWS Secrets Manager أو HashiCorp Vault
5. **احذر من Logs:** لا تطبع المفاتيح في السجلات

## 🤝 المساهمة

إذا وجدت مشكلة أو لديك اقتراح:
1. افتح Issue في [GitHub Issues](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/issues)
2. أو قدّم Pull Request

## 📞 الدعم

للمساعدة:
- افتح Issue مع وسم `preflight` أو `check-connections`
- تواصل مع @MOTEB1989

---

**آخر تحديث:** 2025-11-23  
**الإصدار:** 1.0.0
