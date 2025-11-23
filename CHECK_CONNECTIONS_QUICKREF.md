# 🚀 دليل سريع: check_connections.sh

## أوامر سريعة (نسخ ولصق)

### ⚡ الإعداد في 30 ثانية

```bash
# 1. جعل السكربت قابلاً للتنفيذ
chmod +x scripts/check_connections.sh

# 2. تشغيل فحص سريع
API_PORT=3000 bash scripts/check_connections.sh

# 3. عرض النتيجة
python3 -m json.tool < reports/check_connections.json
```

### 🔑 إضافة الأسرار (نسخ الكل دفعة واحدة)

```bash
# الأساسيات فقط
gh secret set TELEGRAM_BOT_TOKEN --body "YOUR_TOKEN"
gh secret set TELEGRAM_CHAT_ID --body "6090738107"
gh secret set OPENAI_API_KEY --body "sk-proj-..."
gh secret set API_PORT --body "3000"

# الكل (اختياري)
gh secret set TELEGRAM_ALLOWLIST --body "8256840669,6090738107"
gh secret set GROQ_API_KEY --body "gsk_..."
gh secret set ANTHROPIC_API_KEY --body "sk-ant-..."
gh secret set DB_URL --body "postgres://user:pass@localhost:5432/db"
gh secret set REDIS_URL --body "redis://localhost:6379/0"
gh secret set NEO4J_URI --body "bolt://localhost:7687"
gh secret set NEO4J_AUTH --body "neo4j/password"
```

### 🧪 اختبار Telegram

```bash
# اختبار التوكن
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq .

# إرسال رسالة تجريبية
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "text=✅ Test from $(hostname)"
```

### 🎯 إنشاء PR

```bash
# طريقة واحدة - سكربت آلي
bash scripts/create_pr_for_check_connections.sh
```

### 📊 تحليل التقرير

```bash
# عرض الأسرار المفقودة فقط
jq '.env | to_entries | map(select(.value == "missing"))' reports/check_connections.json

# حالة Telegram
jq '.telegram_test' reports/check_connections.json

# الخدمات المتاحة
jq '.docker_compose.services' reports/check_connections.json
```

## 📁 الملفات

| الملف | الغرض |
|------|-------|
| `scripts/check_connections.sh` | السكربت الرئيسي |
| `docs/CHECK_CONNECTIONS_GUIDE.md` | دليل شامل |
| `docs/QUICK_START_COMMANDS.md` | أوامر تفصيلية |
| `CHECK_CONNECTIONS_README.md` | README رئيسي |

## 🆘 مشاكل شائعة

**المشكلة:** `permission denied`  
**الحل:** `chmod +x scripts/check_connections.sh`

**المشكلة:** `jq: command not found`  
**الحل:** `sudo apt install -y jq` أو استخدم `python3 -m json.tool`

**المشكلة:** Telegram لا يرسل  
**الحل:** تحقق من التوكن: `curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"`

## 🔗 روابط

- [الدليل الكامل](docs/CHECK_CONNECTIONS_GUIDE.md)
- [أوامر مفصّلة](docs/QUICK_START_COMMANDS.md)
- [ملخص التنفيذ](IMPLEMENTATION_SUMMARY.md)

---
**آخر تحديث:** 2025-11-23
