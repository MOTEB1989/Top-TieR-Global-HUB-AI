# Bot Validation Guide

## Overview

This guide explains the validation processes for the Telegram bot in the Top-TieR-Global-HUB-AI project, including environment validation, runtime checks, and fallback model behavior.

## Environment Validation

### Required Variables

The bot requires the following environment variables to be set and non-empty:

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from @BotFather
- `OPENAI_API_KEY` - Your OpenAI API key for GPT models
- `GITHUB_REPO` - The GitHub repository name (format: owner/repo)

### Optional Variables

The following environment variables are optional but recommended:

- `OPENAI_MODEL` - Primary OpenAI model to use (default: `gpt-4o-mini`)
- `OPENAI_FALLBACK_MODEL` - Fallback model for resilience (see below)
- `TELEGRAM_ALLOWLIST` - Comma-separated list of allowed Telegram user IDs
- `OPENAI_BASE_URL` - Custom OpenAI API endpoint (default: https://api.openai.com/v1)

### Running Validation

To validate your environment configuration, run:

```bash
python scripts/verify_env.py
```

This will:
1. Check that all required variables are set and non-empty
2. Display masked values for secrets (tokens, keys)
3. Show unmasked values for non-sensitive variables (model names, URLs)
4. Indicate if fallback model is configured

## Fallback Model Behavior

### What is the Fallback Model?

The fallback model is an optional secondary OpenAI model that the bot automatically switches to when the primary model fails. This improves resilience and availability of the bot.

### When Does Fallback Trigger?

The bot automatically switches to the fallback model when it encounters:

- **Rate Limit Errors (HTTP 429)** - When you exceed your API rate limits
- **Model Not Found Errors** - When the requested model is unavailable or doesn't exist
- **Invalid Request Errors** - When the model rejects the request due to model-specific issues
- **Service Unavailable (HTTP 503)** - During temporary OpenAI service outages
- **Timeout Errors** - When requests to the primary model time out

### Configuration

To enable fallback model support:

1. Set the `OPENAI_FALLBACK_MODEL` environment variable:
   ```bash
   export OPENAI_FALLBACK_MODEL=gpt-4o
   ```

2. Or add it to your `.env` file:
   ```
   OPENAI_FALLBACK_MODEL=gpt-4o
   ```

### Example Configuration

```bash
# Primary model (fast and cost-effective)
OPENAI_MODEL=gpt-4o-mini

# Fallback model (more capable, used when primary fails)
OPENAI_FALLBACK_MODEL=gpt-4o
```

### Behavior Details

1. **Single Retry Only**: The bot only attempts the fallback model **once** per failed request. There are no infinite retry loops.

2. **Automatic Detection**: The bot automatically detects errors that warrant a fallback attempt.

3. **Logging**: All fallback attempts are logged:
   - Warning when switching to fallback
   - Success confirmation when fallback works
   - Error if both primary and fallback fail

4. **No Fallback Configured**: If no fallback model is set, the bot simply fails with the original error.

### Log Examples

**Successful Fallback:**
```
WARNING: ⚠️ Primary model 'gpt-4o-mini' failed: OpenAI error 429: Rate limit exceeded
         Attempting fallback to 'gpt-4o'...
INFO: ✅ Successfully completed request using fallback model 'gpt-4o'
```

**Both Models Fail:**
```
WARNING: ⚠️ Primary model 'gpt-4o-mini' failed: OpenAI error 429: Rate limit exceeded
         Attempting fallback to 'gpt-4o'...
ERROR: ❌ Fallback model 'gpt-4o' also failed: OpenAI error 429: Rate limit exceeded
```

### Testing Fallback Behavior

You can test the fallback mechanism using the `--force-fallback` flag:

```bash
python scripts/telegram_chatgpt_mode.py --force-fallback
```

This simulates a primary model failure, forcing the bot to use the fallback model for all requests. **Only use this flag for testing purposes.**

### Best Practices

1. **Choose Complementary Models**: Use a fast, cost-effective primary model (like `gpt-4o-mini`) with a more capable fallback (like `gpt-4o`).

2. **Monitor Fallback Usage**: Check your logs regularly to see how often fallback is triggered. Frequent fallbacks may indicate:
   - Rate limit issues (consider upgrading your API tier)
   - Model availability issues
   - Request patterns that need optimization

3. **Cost Considerations**: Fallback models may have different pricing. Monitor your API usage to ensure costs remain acceptable.

4. **Update Models**: Keep your model names up to date. OpenAI periodically deprecates older models.

## Validation Scripts

### verify_env.py

Validates environment variables and displays configuration:

```bash
python scripts/verify_env.py
```

### post_refactor_check.sh

Comprehensive post-refactoring validation:

```bash
bash scripts/post_refactor_check.sh
```

This checks:
- Required environment variables
- Optional configuration
- Provides recommendations for fallback model setup

## Security Considerations

1. **Never Commit Secrets**: Never commit `.env` files or hardcode API keys
2. **Use GitHub Secrets**: For CI/CD, use GitHub Secrets to store sensitive values
3. **Rotate Keys Regularly**: Periodically rotate your API keys and bot tokens
4. **Limit Bot Access**: Use `TELEGRAM_ALLOWLIST` to restrict bot access to authorized users
5. **Model Names Are Not Secrets**: Model names (like `gpt-4o`) are not considered secrets and are displayed in logs

## Troubleshooting

### Bot Fails to Start

1. Run `python scripts/verify_env.py` to check your configuration
2. Ensure all required variables are set
3. Check that your API keys are valid and not expired

### Fallback Not Working

1. Verify `OPENAI_FALLBACK_MODEL` is set correctly
2. Check that the fallback model name is valid
3. Review logs to see the specific error preventing fallback

### Too Many Fallbacks

If you see frequent fallback usage:

1. Check your OpenAI account rate limits
2. Consider upgrading your API tier
3. Optimize request frequency
4. Review error patterns in logs

## Related Documentation

- [Scripts Overview](SCRIPTS_OVERVIEW.md) - Detailed guide to all scripts
- [Environment Variables](.env.example) - Full list of configuration options
- [OpenAI API Documentation](https://platform.openai.com/docs) - OpenAI API reference
