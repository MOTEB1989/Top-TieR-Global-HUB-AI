# Bot Validation Guide - Top-TieR-Global-HUB-AI

Complete end-to-end testing procedure for Telegram bot functionality.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Pre-Deployment Validation](#pre-deployment-validation)
- [Local Testing](#local-testing)
- [Deployment Testing](#deployment-testing)
- [Command Testing](#command-testing)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- Python 3.9 or higher
- pip (Python package manager)
- Git
- A Telegram account
- (Optional) Docker for containerized testing

### Required Credentials

1. **Telegram Bot Token**
   - Create via [@BotFather](https://t.me/BotFather)
   - Command: `/newbot`
   - Save the token securely

2. **OpenAI API Key**
   - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Must start with `sk-`

3. **Telegram User ID**
   - Get your ID from [@userinfobot](https://t.me/userinfobot)
   - Or use `/whoami` command with the bot

4. **GitHub Token** (Optional)
   - For GitHub integration features
   - Create at [GitHub Settings > Tokens](https://github.com/settings/tokens)

---

## Environment Setup

### 1. Clone Repository

````bash
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
cd Top-TieR-Global-HUB-AI
````

### 2. Install Dependencies

````bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import telegram; print('✅ python-telegram-bot installed')"
python3 -c "import openai; print('✅ openai installed')"
python3 -c "import requests; print('✅ requests installed')"
````

### 3. Configure Environment

Create `.env` file from example:

````bash
cp .env.example .env
````

Edit `.env` with your credentials:

````env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=sk-your_openai_key_here
GITHUB_REPO=MOTEB1989/Top-TieR-Global-HUB-AI

# Optional
OPENAI_MODEL=gpt-4o-mini
TELEGRAM_ALLOWLIST=your_telegram_user_id
TELEGRAM_CHAT_ID=your_chat_id
GITHUB_TOKEN=your_github_token_here
````

**Security Notes**:
- Never commit `.env` to version control
- Keep tokens secure and rotate them regularly
- Use allowlist to restrict bot access

---

## Pre-Deployment Validation

### Step 1: Verify Environment Variables

Run the environment verification script:

````bash
python scripts/verify_env.py
````

**Expected Output**:
```
✅ جميع المتغيرات الحرجة موجودة وليست فارغة.
عرض آمن (مقنع) للقيم:
TELEGRAM_BOT_TOKEN = 123456...
OPENAI_API_KEY = sk-abc...
GITHUB_REPO = MOTEB1989/Top-TieR-Global-HUB-AI
====================================
```

**Strict Mode** (validates optional vars):

````bash
python scripts/verify_env.py --strict
````

### Step 2: Check All API Keys

````bash
python scripts/check_all_keys.py
````

**Expected Output**:
```
🔑 فحص جميع مفاتيح API والإعدادات
====================================

📂 مفاتيح AI/LLM
  ✅ صالح OPENAI_API_KEY
     موجود (51 حرف)
...
📊 الملخص
  إجمالي المفاتيح: 14
  ✅ صالحة: 10
  ❌ مفقودة: 0
  ⚠️  قيم افتراضية: 4
  نسبة الاكتمال: 71.4%
```

### Step 3: Test Telegram Connection

````bash
python scripts/test_telegram_bot.py
````

**Expected Output**:
```
🤖 اختبار بوت Telegram
==================================================
✅ تم العثور على المفتاح: 123456789:...
🔍 اختبار الاتصال...
✅ البوت متصل بنجاح!
   - الاسم: YourBotName
   - Username: @YourBotUsername
   - ID: 123456789
==================================================
✅ جميع الاختبارات نجحت!
==================================================
```

---

## Local Testing

### Dry-Run Mode

Test bot initialization without starting the polling loop:

````bash
python scripts/telegram_chatgpt_mode.py --dry-run
````

**Expected Output**:
```
✅ Dry-run mode: Bot initialized successfully, skipping polling
All handlers registered and configuration validated
```

This validates:
- ✅ Bot token is valid
- ✅ All handlers are registered
- ✅ Environment is configured correctly
- ✅ Dependencies are available

### Interactive Mode (Local)

Start the bot locally for testing:

````bash
python scripts/telegram_chatgpt_mode.py
````

**Expected Output**:
```
بدء تشغيل Telegram ChatGPT Mode Bot ...
المستودع: MOTEB1989/Top-TieR-Global-HUB-AI
Allowlist مفعّل للمستخدمين: {123456789}
✅ Starting bot polling loop...
```

Leave it running and test commands from Telegram.

### Refactored Mode (Enhanced Logging)

````bash
python scripts/telegram_chatgpt_mode.py --mode=refactored
````

**Expected Output**:
```
============================================================
🚀 RUNNING IN REFACTORED MODE 🚀
  Enhanced logging, error handling, and validation enabled
============================================================
بدء تشغيل Telegram ChatGPT Mode Bot ...
```

---

## Deployment Testing

### Railway Deployment

1. **Verify railway.json**:

````bash
cat railway.json
````

Should contain:
```json
{
  "deploy": {
    "startCommand": "python scripts/verify_env.py && python scripts/telegram_chatgpt_mode.py --mode=refactored",
    ...
  }
}
```

2. **Deploy to Railway**:

````bash
# Ensure all environment variables are set in Railway dashboard
# Push changes to trigger deployment
git push origin main
````

3. **Monitor Deployment Logs**:

Check Railway dashboard for:
- ✅ Environment verification passed
- ✅ Bot starting in refactored mode
- ✅ Polling loop started

---

## Command Testing

### Basic Commands

Test each command in order:

#### 1. /start Command

**Send**: `/start`

**Expected Response**:
```
🤖 أهلاً بك في وضع ChatGPT المتقدم داخل مستودع Top-TieR-Global-HUB-AI.
استخدم /help لاستعراض الأوامر المتاحة.
```

**Validates**:
- ✅ Bot is responding
- ✅ Basic connectivity working

---

#### 2. /whoami Command

**Send**: `/whoami`

**Expected Response**:
```
🆔 معرفك في تيليجرام: `123456789`
👤 اسم المستخدم: @yourusername

أضف هذا المعرف في TELEGRAM_ALLOWLIST (كمثال):
TELEGRAM_ALLOWLIST=123456789
```

**Validates**:
- ✅ User ID detection working
- ✅ Allowlist information provided

**Action**: Add your ID to `TELEGRAM_ALLOWLIST` if not already present.

---

#### 3. /help Command

**Send**: `/help`

**Expected Response**:
- List of all available commands
- Descriptions in Arabic
- Usage examples

**Validates**:
- ✅ Help text is properly formatted
- ✅ All commands documented

---

#### 4. /status Command

**Send**: `/status`

**Expected Response**:
```
📊 *حالة النظام – ChatGPT Mode*
- المستودع: `MOTEB1989/Top-TieR-Global-HUB-AI`
🧠 OpenAI: ✅ مضبوط (OPENAI_API_KEY موجود)
   • النموذج: `gpt-4o-mini`
🔐 Allowlist: ✅ مفعّل
   • المستخدمون المصرح لهم:
     - 123456789
📂 ملفات الهندسة/الأمن:
   • ✅ ARCHITECTURE.md (or ❌ if missing)
   • ✅ SECURITY_POSTURE.md (or ❌ if missing)
   ...
```

**Validates**:
- ✅ Environment configuration visible
- ✅ File presence checks working
- ✅ OpenAI integration confirmed

---

#### 5. /chat Command (AI Integration)

**Send**: `/chat ما هو Docker؟`

**Expected Response**:
- AI-generated explanation of Docker (in Arabic)
- Response within reasonable time (< 30 seconds)

**Validates**:
- ✅ OpenAI API integration working
- ✅ Chat memory initialized
- ✅ Arabic language support

**Follow-up Test**:

**Send**: `/chat وماذا عن Kubernetes؟`

**Expected**: Contextual response building on previous conversation

**Validates**:
- ✅ Conversation memory working
- ✅ Context preservation

---

#### 6. /repo Command (Repository Analysis)

**Send**: `/repo`

**Expected Response**:
- High-level repository summary
- Key risks identified
- Strengths highlighted
- 3 actionable recommendations

**Validates**:
- ✅ Repository context gathering working
- ✅ AI analysis functional
- ✅ Report files being read correctly

---

#### 7. /insights Command (Project Summary)

**Send**: `/insights`

**Expected Response**:
- Current state assessment
- Top 5 risks/gaps
- 3-phase implementation plan
- Important warnings

**Validates**:
- ✅ Advanced AI analysis working
- ✅ Strategic thinking enabled

---

### Advanced Testing

#### File Upload Test

1. **Prepare a test file**: Create `test.md` with sample content
2. **Send file to bot**
3. **Expected**: Bot analyzes content and provides summary

**Validates**:
- ✅ File handling working
- ✅ Content extraction working
- ✅ AI file analysis functional

#### Plain Text Message Test

**Send**: `Hello, how are you?` (without command)

**Expected**: AI response in conversational style

**Validates**:
- ✅ Fallback handler working
- ✅ Plain text processing enabled

---

## Troubleshooting

### Issue: Bot Not Responding

**Symptoms**: No response to any commands

**Diagnosis**:
1. Check bot is running: `ps aux | grep telegram_chatgpt_mode`
2. Check logs for errors
3. Verify token: `python scripts/test_telegram_bot.py`

**Solutions**:
- Restart bot
- Regenerate bot token from @BotFather
- Check network connectivity

---

### Issue: "غير مصرح لك" (Not Authorized)

**Symptoms**: Bot responds with authorization error

**Diagnosis**: User ID not in allowlist

**Solution**:
1. Use `/whoami` to get your user ID
2. Add ID to `.env`: `TELEGRAM_ALLOWLIST=your_user_id`
3. Restart bot

---

### Issue: OpenAI Errors

**Symptoms**: `/chat` command fails or times out

**Diagnosis**:
1. Verify API key: `echo $OPENAI_API_KEY`
2. Check OpenAI status: https://status.openai.com
3. Test API: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

**Solutions**:
- Verify API key is valid and has credits
- Check model name is correct
- Verify network can reach OpenAI API

---

### Issue: Dry-Run Mode Fails

**Symptoms**: `--dry-run` flag causes errors

**Diagnosis**:
````bash
python scripts/telegram_chatgpt_mode.py --dry-run 2>&1 | head -20
````

**Solutions**:
- Check Python version: `python3 --version` (must be 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify all imports work

---

### Issue: Environment Validation Fails

**Symptoms**: `verify_env.py` reports missing variables

**Diagnosis**:
````bash
python scripts/verify_env.py --strict
````

**Solutions**:
- Check `.env` file exists: `ls -la .env`
- Verify file format (no spaces around `=`)
- Ensure no placeholder values (e.g., `PASTE_YOUR_TOKEN_HERE`)

---

## Post-Refactor Validation

After deployment, run the comprehensive diagnostic:

````bash
./scripts/post_refactor_check.sh
````

**Expected Output**:
```
╔═══════════════════════════════════════════╗
║   Post-Refactor Diagnostic Check         ║
║   Top-TieR Global HUB AI                  ║
╚═══════════════════════════════════════════╝

========== Required Python Scripts ==========
✅ Present: scripts/telegram_chatgpt_mode.py
✅ Present: scripts/verify_env.py
...

========== Summary ==========
  Total Checks: 45
  Passed: 45
  Failed: 0

✅ All checks PASSED!
The refactoring is complete and successful.
```

---

## Validation Checklist

Use this checklist for complete validation:

### Pre-Deployment
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with valid credentials
- [ ] `verify_env.py` passes
- [ ] `check_all_keys.py` shows >80% completion
- [ ] `test_telegram_bot.py` connects successfully
- [ ] Dry-run mode works (`--dry-run`)

### Local Testing
- [ ] Bot starts without errors
- [ ] `/start` command works
- [ ] `/whoami` returns user ID
- [ ] `/help` displays all commands
- [ ] `/status` shows correct configuration
- [ ] `/chat` responds with AI
- [ ] Conversation memory persists
- [ ] File upload works
- [ ] Plain text messages handled

### Deployment
- [ ] `railway.json` updated with `--mode=refactored`
- [ ] Environment variables set in Railway
- [ ] Deployment logs show successful start
- [ ] Bot responds in production
- [ ] `/whoami` works after deployment
- [ ] All commands functional in production

### Post-Deployment
- [ ] `post_refactor_check.sh` passes all checks
- [ ] Logs show no errors
- [ ] Response times acceptable (< 30s for AI)
- [ ] Memory usage stable
- [ ] No unauthorized access attempts logged

---

## Performance Benchmarks

### Expected Response Times

| Command | Expected Time | Notes |
|---------|---------------|-------|
| `/start` | < 1s | Instant response |
| `/whoami` | < 1s | Instant response |
| `/help` | < 1s | Instant response |
| `/status` | < 2s | File system checks |
| `/chat` | 5-20s | AI processing time |
| `/repo` | 10-30s | File reading + AI |
| `/insights` | 15-40s | Complex AI analysis |
| File upload | 5-25s | Depends on file size |

### Resource Usage

- **Memory**: ~100-200 MB baseline
- **CPU**: Low (< 5%) when idle
- **Network**: Minimal, spikes during AI calls

---

## See Also

- [SCRIPTS_OVERVIEW.md](SCRIPTS_OVERVIEW.md) - Comprehensive script documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [README.md](README.md) - Main repository documentation

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs for error messages
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version)
   - Relevant log snippets

---

*Last Updated: 2025-11-23*
*Repository: MOTEB1989/Top-TieR-Global-HUB-AI*
