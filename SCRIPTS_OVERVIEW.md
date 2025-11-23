# Scripts Overview - نظرة عامة على السكربتات

## Core Bot Scripts - سكربتات البوت الأساسية

### telegram_chatgpt_mode.py
**الوصف**: بوت تيليجرام متقدم مع دعم ChatGPT والنموذج الاحتياطي

**الميزات الرئيسية**:
- نموذج OpenAI أساسي إلزامي (OPENAI_MODEL)
- نموذج احتياطي اختياري (OPENAI_FALLBACK_MODEL) مع محاولة واحدة
- تحديد معدل الرسائل (20 رسالة/مستخدم/دقيقة افتراضياً)
- تنقية أسماء الملفات والتحقق من حجم الملف (2MB كحد أقصى)
- دعم أعلام سطر الأوامر: `--dry-run`, `--mode=refactored`, `--force-fallback`

**الاستخدام**:
```bash
# Normal operation
python scripts/telegram_chatgpt_mode.py --mode=refactored

# Validate configuration without starting
python scripts/telegram_chatgpt_mode.py --dry-run

# Test fallback model
python scripts/telegram_chatgpt_mode.py --force-fallback --dry-run
```

**المتغيرات البيئية المطلوبة**:
- `TELEGRAM_BOT_TOKEN` (إلزامي)
- `OPENAI_API_KEY` (إلزامي)
- `OPENAI_MODEL` (إلزامي)
- `OPENAI_FALLBACK_MODEL` (اختياري)
- `TELEGRAM_RATE_LIMIT_PER_MIN` (اختياري، افتراضي 20)
- `TELEGRAM_ALLOWLIST` (اختياري)

**الأوامر المتاحة**:
- `/start` - رسالة ترحيب
- `/help` - عرض المساعدة
- `/whoami` - معرفة Telegram ID للمستخدم
- `/status` - حالة البوت والنظام
- `/chat <سؤال>` - دردشة تفاعلية مع ذاكرة
- `/repo` - تحليل المستودع
- `/insights` - ملخص ذكي عن حالة المشروع
- إرسال ملف - تحليل الملفات النصية

---

### run_telegram_bot.py
**الوصف**: سكربت بديل لتشغيل بوت تيليجرام مع ميزات متقدمة

**الاستخدام**:
```bash
python scripts/run_telegram_bot.py
```

---

### verify_env.py
**الوصف**: التحقق من صحة المتغيرات البيئية

**الميزات**:
- التحقق من المتغيرات الإلزامية
- إخفاء القيم الحساسة (_TOKEN, _KEY, _PASSWORD, _PASS, _AUTH)
- وضع صارم اختياري (--strict) يعامل التحذيرات كأخطاء
- كشف القيم المؤقتة (PASTE_YOUR_KEY_HERE)

**الاستخدام**:
```bash
# Normal mode
python scripts/verify_env.py

# Strict mode (warnings become errors)
python scripts/verify_env.py --strict
```

**المتغيرات المطلوبة**:
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (جديد - إلزامي)
- `GITHUB_REPO`

---

## Utility Library - مكتبة الأدوات المساعدة

### scripts/lib/common.py
**الوصف**: وحدة مشتركة توفر وظائف مساعدة لجميع السكربتات

**الوظائف الرئيسية**:

#### إخفاء الأسرار (Secret Masking)
```python
from scripts.lib.common import mask_secret, mask_env_dict

masked = mask_secret("sk-proj-1234567890", "OPENAI_API_KEY")
# Returns: "sk-pro...7890"
```

#### اختيار النموذج (Model Selection)
```python
from scripts.lib.common import get_openai_models, log_model_banner

primary, fallback = get_openai_models()
log_model_banner(primary, fallback)
```

#### تنقية أسماء الملفات (Filename Sanitization)
```python
from scripts.lib.common import sanitize_filename

safe_name = sanitize_filename("../../etc/passwd")
# Returns: "passwd"
```

#### التحقق من حجم الملف (File Size Validation)
```python
from scripts.lib.common import validate_file_size

is_valid, error_msg = validate_file_size(file_size_bytes, max_size_mb=2)
```

#### تحديد المعدل (Rate Limiting)
```python
from scripts.lib.common import RateLimiter

limiter = RateLimiter(messages_per_minute=20)
if limiter.is_allowed(user_id):
    # Process message
    pass
```

#### اشتقاق مفتاح التشفير (Encryption Key Derivation)
```python
from scripts.lib.common import derive_fernet_key

fernet_key = derive_fernet_key("my-secret-key")
```

---

## Validation Scripts - سكربتات التحقق

### post_refactor_check.sh
**الوصف**: سكربت تشخيصي شامل للتحقق من صحة الإصلاحات

**الفحوصات**:
1. التحقق من المتغيرات البيئية
2. التحقق من صحة الاستيراد (imports)
3. التشغيل التجريبي (dry-run)
4. محاكاة النموذج الاحتياطي
5. اختبار تنقية أسماء الملفات
6. اختبار تحديد المعدل
7. اختبار إخفاء الأسرار
8. اختبار اشتقاق مفتاح التشفير

**الاستخدام**:
```bash
bash scripts/post_refactor_check.sh
```

**المخرجات المتوقعة**:
```
✅ PASS: verify_env.py runs successfully
✅ PASS: scripts.lib.common imports successfully
✅ PASS: telegram_chatgpt_mode.py --dry-run succeeds
...
🎉 All checks PASSED! Refactor validated successfully.
```

---

## Testing the Bot - اختبار البوت

### خطوات الاختبار الوظيفي:

1. **اختبار الرسائل النصية**:
   ```
   أرسل رسالة نصية بدون أمر → يجب أن يرد البوت باستخدام النموذج الأساسي
   ```

2. **اختبار النموذج الاحتياطي**:
   ```bash
   # Set invalid primary model
   export OPENAI_MODEL=invalid-model-name
   export OPENAI_FALLBACK_MODEL=gpt-3.5-turbo
   
   # Bot should fallback automatically
   ```

3. **اختبار تحديد المعدل**:
   ```
   أرسل أكثر من 20 رسالة في دقيقة واحدة
   → يجب أن يرد البوت برسالة تحديد المعدل
   ```

4. **اختبار حجم الملف**:
   ```
   أرسل ملفاً أكبر من 2MB
   → يجب أن يرفض البوت الملف مع رسالة خطأ
   ```

5. **اختبار الأوامر**:
   ```
   /whoami  → عرض Telegram ID
   /status  → عرض حالة النظام
   /help    → عرض المساعدة
   ```

---

## Environment Variables Reference - مرجع المتغيرات البيئية

### Required (إلزامي)
| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather | `1234567890:ABC...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `OPENAI_MODEL` | Primary OpenAI model | `gpt-4o-mini` |
| `GITHUB_REPO` | Repository name | `MOTEB1989/Top-TieR-Global-HUB-AI` |

### Optional (اختياري)
| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENAI_FALLBACK_MODEL` | Fallback model for retry | None | `gpt-3.5-turbo` |
| `TELEGRAM_ALLOWLIST` | Comma-separated user IDs | Empty (all allowed) | `123456,789012` |
| `TELEGRAM_RATE_LIMIT_PER_MIN` | Messages per user per minute | `20` | `30` |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` | Custom endpoint |

---

## Security Best Practices - أفضل ممارسات الأمان

1. **Never commit secrets**:
   - Always use `.env` file (ignored by git)
   - Use GitHub Secrets for CI/CD
   - Use Railway/deployment platform secrets

2. **Strong passwords**:
   - Generate: `openssl rand -base64 32`
   - Avoid defaults like `password`, `motebai123`

3. **Allowlist configuration**:
   - Always set `TELEGRAM_ALLOWLIST` in production
   - Use `/whoami` to get user IDs
   - Regularly review authorized users

4. **File uploads**:
   - Maximum 2MB enforced automatically
   - Only text files analyzed
   - Filenames sanitized against path traversal

5. **Rate limiting**:
   - Prevents abuse and spam
   - Configurable per deployment
   - Per-user tracking

---

## Troubleshooting - استكشاف الأخطاء

### البوت لا يستجيب
```bash
# Check configuration
python scripts/verify_env.py

# Test dry-run
python scripts/telegram_chatgpt_mode.py --dry-run
```

### خطأ في النموذج (Model Error)
```bash
# Verify models are set correctly
echo $OPENAI_MODEL
echo $OPENAI_FALLBACK_MODEL

# Test with fallback
python scripts/telegram_chatgpt_mode.py --force-fallback --dry-run
```

### تجاوز تحديد المعدل
```bash
# Check rate limit setting
echo $TELEGRAM_RATE_LIMIT_PER_MIN

# Adjust if needed (higher for testing)
export TELEGRAM_RATE_LIMIT_PER_MIN=100
```

### خطأ في استيراد المكتبات
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify imports
python -c "from scripts.lib.common import RateLimiter"
```

---

## Quick Reference Commands - مرجع الأوامر السريع

```bash
# Validate environment
python scripts/verify_env.py

# Run full validation
bash scripts/post_refactor_check.sh

# Start bot in refactored mode
python scripts/telegram_chatgpt_mode.py --mode=refactored

# Test without starting
python scripts/telegram_chatgpt_mode.py --dry-run

# Force fallback model
python scripts/telegram_chatgpt_mode.py --force-fallback --dry-run
```

---

## Related Documentation - الوثائق ذات الصلة

- `BOT_VALIDATION.md` - خطوات التحقق من البوت (بالعربية)
- `SECURITY_ACTION_PLAN.md` - خطة الأمان لمدة 7 أيام
- `.env.example` - مثال على ملف البيئة
- `README.md` - الوثائق الرئيسية للمشروع
