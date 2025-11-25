# Scripts Overview

## Table of Contents
- [Environment Validation](#environment-validation)
- [Environment Variables Reference](#environment-variables-reference)
- [Bot Scripts](#bot-scripts)
- [Testing Scripts](#testing-scripts)
- [Utility Scripts](#utility-scripts)

## Environment Validation

### verify_env.py
**Location**: `scripts/verify_env.py`

**Purpose**: Validates that all required environment variables are set and non-empty before the bot starts.

**Usage**:
```bash
python scripts/verify_env.py
```

**Exit Codes**:
- `0`: All required variables are valid
- `1`: One or more required variables are missing or empty

**Features**:
- Fast-fail validation to prevent runtime errors
- Secure masking of sensitive values (API keys, tokens)
- Display of non-sensitive configuration values
- Clear error messages in Arabic and English

## Environment Variables Reference

### Required Variables

All of these variables **must** be set and non-empty:

| Variable | Description | Example | Status |
|----------|-------------|---------|--------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot authentication token | `1234567890:ABC...` | **Required** |
| `OPENAI_API_KEY` | OpenAI API authentication key | `sk-proj-abc...` | **Required** |
| `GITHUB_REPO` | Repository identifier (owner/repo) | `MOTEB1989/Top-TieR-Global-HUB-AI` | **Required** |
| `OPENAI_MODEL` | OpenAI model to use (explicit) | `gpt-4o-mini` | **Required** |

### Optional Variables

These variables enhance functionality but have defaults:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TELEGRAM_ALLOWLIST` | Comma-separated user IDs allowed to use bot | None (all users) | `8256840669,6090738107` |
| `OPENAI_BASE_URL` | OpenAI API endpoint URL | `https://api.openai.com/v1` | `https://api.openai.com/v1` |
| `CHAT_HISTORY_PATH` | Path to store chat session history | `analysis/chat_sessions.json` | `data/chats.json` |
| `ULTRA_PREFLIGHT_PATH` | Path to ultra preflight script | `scripts/ultra_preflight.sh` | Custom path |
| `FULL_SCAN_SCRIPT` | Path to full scan script | `scripts/execute_full_scan.sh` | Custom path |
| `LOG_FILE_PATH` | Path to log file | `analysis/ULTRA_REPORT.md` | Custom path |

### Database & Infrastructure (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_URL` | PostgreSQL connection string | None |
| `REDIS_URL` | Redis connection string | None |
| `NEO4J_URI` | Neo4j database URI | None |
| `NEO4J_AUTH` | Neo4j authentication | None |

## Bot Scripts

### telegram_chatgpt_mode.py
**Location**: `scripts/telegram_chatgpt_mode.py`

**Purpose**: Main Telegram bot with ChatGPT integration.

**Features**:
- `/chat` - Interactive chat with memory per user
- `/repo` - Repository analysis using reports
- `/insights` - Smart project status summary
- `/file` - Analyze uploaded files
- `/status` - Bot and repository status
- `/help` - Display help message
- `/whoami` - Get your Telegram ID for allowlist

**Usage**:
```bash
# Direct execution
python scripts/telegram_chatgpt_mode.py

# With validation (recommended)
python scripts/verify_env.py && python scripts/telegram_chatgpt_mode.py
```

**Required Environment Variables**:
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `GITHUB_REPO`

**Optional Environment Variables**:
- `TELEGRAM_ALLOWLIST` - Restrict access to specific users
- `OPENAI_BASE_URL` - Use custom OpenAI-compatible endpoint

### run_telegram_bot.py
**Location**: `scripts/run_telegram_bot.py`

**Purpose**: Alternative bot launcher with additional setup.

## Testing Scripts

### test_telegram_bot.py
**Location**: `scripts/test_telegram_bot.py`

**Purpose**: Test Telegram bot functionality.

**Usage**:
```bash
python scripts/test_telegram_bot.py
```

### quick_bot_test.py
**Location**: `scripts/quick_bot_test.py`

**Purpose**: Quick validation of bot configuration.

**Usage**:
```bash
python scripts/quick_bot_test.py
```

### test_gpt_connection.py
**Location**: `scripts/test_gpt_connection.py`

**Purpose**: Test OpenAI API connectivity and model access.

**Usage**:
```bash
python scripts/test_gpt_connection.py
```

## Utility Scripts

### check_connections.sh
**Location**: `scripts/check_connections.sh`

**Purpose**: Verify connectivity to external services.

### check_environment.sh
**Location**: `scripts/check_environment.sh`

**Purpose**: Check system environment and dependencies.

### diagnose_external_apis.py
**Location**: `scripts/diagnose_external_apis.py`

**Purpose**: Diagnose issues with external API connections.

### check_github_secrets.py
**Location**: `scripts/check_github_secrets.py`

**Purpose**: Validate GitHub secrets configuration.

## Railway Deployment

### Railway Configuration
The `railway.json` file configures deployment:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python scripts/verify_env.py && python scripts/telegram_chatgpt_mode.py",
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Key Points**:
- `verify_env.py` runs first to validate configuration
- Bot starts only if validation passes
- Automatic restarts on failure (up to 10 times)
- Uses NIXPACKS builder for Python environment

### Required Railway Environment Variables
When deploying to Railway, ensure these variables are set:

1. `TELEGRAM_BOT_TOKEN` - From @BotFather
2. `OPENAI_API_KEY` - From OpenAI Platform
3. `OPENAI_MODEL` - e.g., `gpt-4o-mini`
4. `GITHUB_REPO` - Your repository name
5. `TELEGRAM_ALLOWLIST` - (Optional) Restrict access

## Best Practices

### 1. Always Validate Before Running
```bash
# Good - validates first
python scripts/verify_env.py && python scripts/telegram_chatgpt_mode.py

# Bad - might fail at runtime
python scripts/telegram_chatgpt_mode.py
```

### 2. Use .env Files for Local Development
```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env

# Source it (if needed)
source .env
```

### 3. Never Commit Secrets
Ensure `.env` is in `.gitignore`:
```bash
# Check if .env is ignored
git check-ignore .env
```

### 4. Test Configuration Changes
```bash
# Validate environment
python scripts/verify_env.py

# Quick bot test
python scripts/quick_bot_test.py

# Test OpenAI connection
python scripts/test_gpt_connection.py
```

### 5. Monitor Bot Logs
```bash
# Railway logs
railway logs

# Local logs
python scripts/telegram_chatgpt_mode.py 2>&1 | tee bot.log
```

## Troubleshooting

### Bot Won't Start

**Check validation first**:
```bash
python scripts/verify_env.py
```

**Common issues**:
1. Missing `OPENAI_MODEL` (now required)
2. Empty environment variables
3. Invalid API keys
4. Network connectivity issues

### "مفقود: OPENAI_MODEL" Error

**Solution**: Set the variable:
```bash
export OPENAI_MODEL=gpt-4o-mini
```

Or in `.env`:
```
OPENAI_MODEL=gpt-4o-mini
```

### Validation Passes But Bot Fails

**Check API connectivity**:
```bash
python scripts/test_gpt_connection.py
```

**Verify Telegram token**:
```bash
# Should return bot information
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Permission Denied Errors

**Check script permissions**:
```bash
chmod +x scripts/*.sh
```

## Security Considerations

### Masking in Output
`verify_env.py` automatically masks sensitive values:
- `*_TOKEN` variables: Shows only first 6 chars + "..."
- `*_KEY` variables: Shows only first 6 chars + "..."
- `OPENAI_MODEL`: Not masked (not secret)
- `GITHUB_REPO`: Not masked (not secret)

### Allowlist Usage
Restrict bot access to specific users:
```bash
# Get your Telegram ID
/whoami

# Add to environment
export TELEGRAM_ALLOWLIST=123456789,987654321
```

### API Key Rotation
Regularly rotate sensitive credentials:
1. Generate new API key
2. Update environment variables
3. Test with `verify_env.py`
4. Remove old key from OpenAI dashboard

## Migration Notes

### OPENAI_MODEL Now Required

**Previous behavior**: Optional with fallback to `gpt-4o-mini`
```python
# Old (deprecated)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
```

**Current behavior**: Required, no fallback
```python
# New (current)
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
```

**Migration steps**:
1. Add `OPENAI_MODEL` to your environment
2. Set to desired model (e.g., `gpt-4o-mini`)
3. Run `python scripts/verify_env.py` to validate
4. Deploy changes

**Why this change?**
- Explicit model selection
- Consistent behavior across deployments
- Prevents silent quality degradation
- Better cost management
- Easier debugging

## Related Documentation

- [BOT_VALIDATION.md](./BOT_VALIDATION.md) - Detailed validation guide
- [RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md) - Railway deployment
- [README.md](./README.md) - General project documentation
- [.env.example](./.env.example) - Environment template

## Support

For issues or questions:
1. Check [BOT_VALIDATION.md](./BOT_VALIDATION.md) troubleshooting section
2. Review script logs for error messages
3. Verify environment with `verify_env.py`
4. Open an issue on GitHub with logs and configuration (sanitized!)
