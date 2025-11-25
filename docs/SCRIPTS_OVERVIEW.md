# Scripts Overview

## Overview

This document provides a comprehensive overview of all scripts in the Top-TieR-Global-HUB-AI repository, their purposes, and how to use them.

## Environment Variables

### Required Variables

| Variable | Type | Description |
|----------|------|-------------|
| `TELEGRAM_BOT_TOKEN` | Secret | Your Telegram bot token from @BotFather |
| `OPENAI_API_KEY` | Secret | Your OpenAI API key for GPT models |
| `GITHUB_REPO` | String | GitHub repository name (format: owner/repo) |

### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_MODEL` | String | `gpt-4o-mini` | Primary OpenAI model to use |
| `OPENAI_FALLBACK_MODEL` | String | None | **Fallback model for auto-retry on failures** (rate limits, model unavailability) |
| `TELEGRAM_ALLOWLIST` | String | Empty | Comma-separated list of allowed Telegram user IDs |
| `OPENAI_BASE_URL` | String | `https://api.openai.com/v1` | Custom OpenAI API endpoint |
| `GITHUB_TOKEN` | Secret | None | GitHub personal access token |
| `TELEGRAM_CHAT_ID` | String | None | Your Telegram chat ID for notifications |
| `ULTRA_PREFLIGHT_PATH` | String | `scripts/ultra_preflight.sh` | Path to ultra preflight script |
| `FULL_SCAN_SCRIPT` | String | `scripts/execute_full_scan.sh` | Path to full scan script |
| `LOG_FILE_PATH` | String | `analysis/ULTRA_REPORT.md` | Path to analysis report |
| `CHAT_HISTORY_PATH` | String | `analysis/chat_sessions.json` | Path to chat history storage |

### New: Fallback Model Support

The `OPENAI_FALLBACK_MODEL` variable enables automatic model fallback for improved resilience:

- **Purpose**: Automatically retry failed requests with a secondary model
- **Triggers**: Rate limits (429), model unavailability, timeout errors, service outages (503)
- **Behavior**: Single retry only (no infinite loops)
- **Example**: Set `OPENAI_FALLBACK_MODEL=gpt-4o` to use as fallback when `gpt-4o-mini` fails
- **Documentation**: See [BOT_VALIDATION.md](BOT_VALIDATION.md#fallback-model-behavior) for details

## Core Scripts

### Bot Scripts

#### telegram_chatgpt_mode.py

Advanced Telegram bot with ChatGPT integration and repository analysis features.

**Location**: `scripts/telegram_chatgpt_mode.py`

**Usage**:
```bash
python scripts/telegram_chatgpt_mode.py [--force-fallback]
```

**Options**:
- `--force-fallback`: Force fallback model for testing (simulates primary failure)

**Features**:
- `/chat` - Interactive chat with memory per user
- `/repo` - Repository analysis using ULTRA reports
- `/insights` - Smart summary of project state
- `/file` - Analyze uploaded files
- `/status` - Bot and repository status
- `/help` - Command help
- `/whoami` - Get your Telegram ID

**Environment Dependencies**:
- Required: `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `GITHUB_REPO`
- Optional: `OPENAI_MODEL`, `OPENAI_FALLBACK_MODEL`, `TELEGRAM_ALLOWLIST`

**New Features**:
- Automatic fallback to secondary model on API errors
- Startup banner showing primary and fallback models
- Enhanced logging for fallback events
- Testing mode with `--force-fallback` flag

#### run_telegram_bot.py

Simple wrapper to run the Telegram bot.

**Location**: `scripts/run_telegram_bot.py`

**Usage**:
```bash
python scripts/run_telegram_bot.py
```

### Validation Scripts

#### verify_env.py

Validates environment variables and displays configuration safely.

**Location**: `scripts/verify_env.py`

**Usage**:
```bash
python scripts/verify_env.py
```

**Features**:
- Validates required variables are set and non-empty
- Masks sensitive values (tokens, keys)
- Shows unmasked non-sensitive values (model names, URLs)
- Displays fallback model configuration when present
- Exits with error if validation fails

**Updates**:
- Now checks and displays `OPENAI_FALLBACK_MODEL`
- Shows informational note when fallback is configured

#### post_refactor_check.sh

Post-refactoring validation checks.

**Location**: `scripts/post_refactor_check.sh`

**Usage**:
```bash
bash scripts/post_refactor_check.sh
```

**Features**:
- Validates required environment variables
- Shows optional configuration status
- Provides recommendations for fallback model
- Does not fail if optional variables are absent

### Testing Scripts

#### test_telegram_bot.py

Test script for Telegram bot functionality.

**Location**: `scripts/test_telegram_bot.py`

**Usage**:
```bash
python scripts/test_telegram_bot.py
```

#### quick_bot_test.py

Quick validation of bot connectivity.

**Location**: `scripts/quick_bot_test.py`

**Usage**:
```bash
python scripts/quick_bot_test.py
```

### Utility Scripts

#### lib/common.py

Shared utilities for bot scripts with model selection and fallback logic.

**Location**: `scripts/lib/common.py`

**Functions**:

- `select_model()` - Returns tuple of (primary_model, fallback_model) from environment
- `should_retry_with_fallback(exception)` - Determines if error warrants fallback retry
- `try_model_with_fallback(api_call, primary, fallback, operation)` - Executes API call with automatic fallback

**Example Usage**:
```python
from lib.common import select_model, try_model_with_fallback

# Get configured models
primary_model, fallback_model = select_model()

# Use with automatic fallback
def make_request(model):
    # Your API call here
    return api_client.chat(model=model, messages=messages)

result = try_model_with_fallback(
    api_call=make_request,
    primary_model=primary_model,
    fallback_model=fallback_model,
    operation_name="chat completion"
)
```

### Analysis Scripts

#### diagnose_external_apis.py

Diagnoses connectivity to external APIs.

**Location**: `scripts/diagnose_external_apis.py`

**Usage**:
```bash
python scripts/diagnose_external_apis.py
```

#### smart_agent_validator.py

Validates agent configurations.

**Location**: `scripts/smart_agent_validator.py`

**Usage**:
```bash
python scripts/smart_agent_validator.py
```

### Setup Scripts

#### generate_env_and_patch_workflows.py

Generates environment configuration and patches workflows.

**Location**: `scripts/generate_env_and_patch_workflows.py`

**Usage**:
```bash
python scripts/generate_env_and_patch_workflows.py
```

### Shell Scripts

#### check_all_keys.py

Validates all API keys and tokens.

**Location**: `scripts/check_all_keys.py`

**Usage**:
```bash
python scripts/check_all_keys.py
```

#### check_environment.sh

Quick environment check.

**Location**: `scripts/check_environment.sh`

**Usage**:
```bash
bash scripts/check_environment.sh
```

## Testing Fallback Behavior

### Standard Testing

1. Set up environment:
   ```bash
   export OPENAI_MODEL=gpt-4o-mini
   export OPENAI_FALLBACK_MODEL=gpt-4o
   ```

2. Run bot normally:
   ```bash
   python scripts/telegram_chatgpt_mode.py
   ```

3. Monitor logs for actual fallback events during rate limits

### Force Fallback Testing

To test fallback without waiting for real failures:

```bash
python scripts/telegram_chatgpt_mode.py --force-fallback
```

This simulates primary model failure and forces use of fallback for all requests.

### Validation Steps

1. **Verify Configuration**:
   ```bash
   python scripts/verify_env.py
   ```
   Should show both primary and fallback models

2. **Check Post-Refactor**:
   ```bash
   bash scripts/post_refactor_check.sh
   ```
   Should note fallback model configuration

3. **Test Bot Startup**:
   ```bash
   python scripts/telegram_chatgpt_mode.py
   ```
   Check logs for banner showing both models

4. **Test Fallback Logic**:
   ```bash
   python scripts/telegram_chatgpt_mode.py --force-fallback
   ```
   Verify fallback is used in logs

## Best Practices

### Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual values in `.env`

3. Never commit `.env` to version control

4. Use GitHub Secrets for CI/CD

### Running Scripts

1. Always validate environment first:
   ```bash
   python scripts/verify_env.py
   ```

2. Run scripts from repository root:
   ```bash
   cd /path/to/Top-TieR-Global-HUB-AI
   python scripts/telegram_chatgpt_mode.py
   ```

3. Monitor logs for errors and warnings

### Security

1. Never commit secrets or API keys
2. Use environment variables for all sensitive data
3. Rotate keys regularly
4. Use allowlist to restrict bot access
5. Review logs for unauthorized access attempts

## Troubleshooting

### Script Won't Start

1. Check Python version (requires 3.11+):
   ```bash
   python --version
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Validate environment:
   ```bash
   python scripts/verify_env.py
   ```

### Import Errors

If you see import errors from `lib.common`:

1. Ensure you're running from repository root
2. Check that `scripts/lib/` directory exists
3. Verify `scripts/lib/__init__.py` exists

### Fallback Not Working

1. Verify `OPENAI_FALLBACK_MODEL` is set:
   ```bash
   echo $OPENAI_FALLBACK_MODEL
   ```

2. Check model name is valid (see OpenAI docs)

3. Review logs for specific error messages

4. Test with `--force-fallback` flag

## Related Documentation

- [BOT_VALIDATION.md](BOT_VALIDATION.md) - Bot validation and fallback behavior
- [.env.example](../.env.example) - Environment variable template
- [README.md](../README.md) - Main project documentation

## Contributing

When adding new scripts:

1. Add documentation to this file
2. Include usage examples
3. Document environment dependencies
4. Add error handling
5. Include logging for debugging
6. Write tests if applicable
