# Bot Environment Validation Guide

## Overview
The `scripts/verify_env.py` script validates that all required environment variables are set before the bot starts. This prevents runtime errors and ensures consistent behavior across deployments.

## Required Environment Variables

All of the following environment variables **must** be set and **non-empty**:

### 1. TELEGRAM_BOT_TOKEN
- **Purpose**: Authentication token for your Telegram bot
- **How to get**: Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
- **Example**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Security**: This is a secret - keep it secure and never commit to version control

### 2. OPENAI_API_KEY
- **Purpose**: Authentication for OpenAI API calls
- **How to get**: Generate from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Example**: `sk-proj-abc123...`
- **Security**: This is a secret - keep it secure and never commit to version control

### 3. GITHUB_REPO
- **Purpose**: Repository identifier for bot operations
- **Format**: `owner/repository-name`
- **Example**: `MOTEB1989/Top-TieR-Global-HUB-AI`
- **Security**: Not secret, but must be accurate

### 4. OPENAI_MODEL (NEW - REQUIRED)
- **Purpose**: Explicitly specify which OpenAI model to use
- **Why required**: Ensures consistent behavior and quality across deployments
- **Common values**:
  - `gpt-4o-mini` (recommended for most use cases)
  - `gpt-4o` (higher quality, higher cost)
  - `gpt-4-turbo`
  - `gpt-3.5-turbo` (fastest, lowest cost)
- **Example**: `gpt-4o-mini`
- **Security**: Not secret - this value is displayed in validation output

## Optional Environment Variables

These variables can be set for additional functionality but are not required:

### TELEGRAM_ALLOWLIST
- **Purpose**: Comma-separated list of allowed Telegram user IDs
- **Example**: `8256840669,6090738107`
- **Default behavior**: If not set, all users can interact with the bot (you may want to restrict this in production)

### OPENAI_BASE_URL
- **Purpose**: Override the default OpenAI API endpoint
- **Example**: `https://api.openai.com/v1`
- **Default**: `https://api.openai.com/v1`
- **Use case**: For using OpenAI-compatible APIs or proxies

## Running Validation

### Manual Validation
```bash
python scripts/verify_env.py
```

### Expected Output (Success)
```
✅ جميع المتغيرات الحرجة موجودة وليست فارغة.
عرض آمن (مقنع) للقيم:
TELEGRAM_BOT_TOKEN = ***MASKED***
OPENAI_API_KEY = sk-pro...
GITHUB_REPO = MOTEB1989/Top-TieR-Global-HUB-AI
OPENAI_MODEL = gpt-4o-mini
TELEGRAM_ALLOWLIST = 8256840669,6090738107
OPENAI_BASE_URL = https://api.openai.com/v1
====================================
```

### Expected Output (Failure)
```
====================================
❌ فشل فحص المتغيرات:
 - مفقود: OPENAI_MODEL
سيتم إنهاء التشغيل لحماية البوت.
====================================
```

## Integration with Bot Startup

The validation script is automatically run before the bot starts:

### Railway Deployment
In `railway.json`:
```json
{
  "deploy": {
    "startCommand": "python scripts/verify_env.py && python scripts/telegram_chatgpt_mode.py"
  }
}
```

This ensures:
1. Validation runs first
2. Bot only starts if all variables are valid
3. Fast failure with clear error messages
4. No silent fallbacks that could cause unexpected behavior

## Troubleshooting

### Error: "مفقود: OPENAI_MODEL"
**Problem**: The `OPENAI_MODEL` environment variable is not set.

**Solution**: Set the variable in your environment:
```bash
export OPENAI_MODEL=gpt-4o-mini
```

Or in your `.env` file:
```
OPENAI_MODEL=gpt-4o-mini
```

### Error: "فارغ: OPENAI_MODEL"
**Problem**: The `OPENAI_MODEL` variable is set but empty.

**Solution**: Provide a valid model name:
```bash
export OPENAI_MODEL=gpt-4o-mini
```

### Validation passes but bot fails to start
**Problem**: Other issues beyond environment variables.

**Solution**: Check the bot logs for specific error messages. Common issues:
- Network connectivity to OpenAI API
- Invalid API key (wrong or expired)
- Rate limits or quota issues
- Invalid Telegram token

## Security Best Practices

1. **Never commit secrets**: Use `.env` files (gitignored) or secret management systems
2. **Rotate keys regularly**: Especially after team changes
3. **Use least privilege**: Telegram tokens should be bot-specific, not user accounts
4. **Monitor usage**: Set up alerts for unusual API consumption
5. **Use allowlists**: Restrict bot access to known users with `TELEGRAM_ALLOWLIST`

## Why OPENAI_MODEL is Now Required

Previously, `OPENAI_MODEL` had a default fallback value. This approach had several issues:

1. **Inconsistent deployments**: Different environments might use different models without realizing it
2. **Cost surprises**: Silent fallback to default could lead to unexpected costs
3. **Quality variations**: Model changes affect response quality; explicit is better
4. **Debugging difficulty**: Hard to troubleshoot issues when model selection is implicit

Making it required ensures:
- ✅ Explicit model selection
- ✅ Consistent behavior across environments
- ✅ Better cost management
- ✅ Easier debugging and troubleshooting
- ✅ No silent degradation of quality

## Related Documentation

- [SCRIPTS_OVERVIEW.md](./SCRIPTS_OVERVIEW.md) - Complete script documentation
- [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) - Railway deployment guide
- [README.md](./README.md) - General project setup
- [.env.example](./.env.example) - Environment variable template
