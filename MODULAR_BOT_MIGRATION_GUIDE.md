# Modular Bot Migration Guide

## Overview

This guide helps you migrate from the legacy Telegram bot to the new modular ChatGPT-grade bot.

## What Changed?

### New Bot Features
- ✅ Multi-session management (create, switch, manage multiple conversations)
- ✅ Multiple AI providers (OpenAI, Anthropic Claude, Groq)
- ✅ Persona system (default, engineer, security, docs)
- ✅ Advanced commands (/summarize, /continue, /regen, /share)
- ✅ Rate limiting (30 msgs/hour, configurable)
- ✅ Safety filtering (automatic secret detection)
- ✅ Follow-up suggestions
- ✅ Session export (JSON/Markdown)

### What Stayed the Same?
- ✅ Legacy bot (`scripts/telegram_chatgpt_mode.py`) **completely unchanged**
- ✅ All existing commands still work
- ✅ Same Telegram bot token and authentication
- ✅ Same deployment method (Procfile worker)

## Migration Steps

### Step 1: Update Environment Variables

Add these to your `.env` file (see `.env.example` for details):

```bash
# New bot configuration
SESSION_BASE_PATH=analysis/sessions
BOT_MAX_MESSAGES_PER_SESSION=50
BOT_RATE_WINDOW_SECONDS=3600
BOT_RATE_MAX_MESSAGES=30
BOT_PERSONA=default
BOT_SILENT_SUGGESTIONS=false

# Migration control (0=legacy, 1=new bot)
USE_NEW_BOT=0
```

### Step 2: Test Locally (Optional but Recommended)

Before deploying, test the new bot locally:

```bash
# Install dependencies (already done if using same environment)
pip install -r requirements.txt

# Run new bot
USE_NEW_BOT=1 python bot/main.py
```

Test the following commands:
- `/start` - Welcome message
- `/help` - Command list
- `/status` - Bot status
- `/sessions` - List sessions
- `/new test` - Create session
- Send a text message - Chat functionality
- `/summarize` - Summarize conversation
- `/export md` - Export session

### Step 3: Deploy

#### Option A: Gradual Migration (Recommended)

1. **Keep legacy bot running** in production
2. **Deploy new bot** to a test/staging environment
3. **Test thoroughly** with real users
4. **Switch** when confident:
   ```bash
   USE_NEW_BOT=1
   ```

#### Option B: Direct Migration

1. **Update** `USE_NEW_BOT=1` in production environment
2. **Restart** the worker process
3. **Monitor** logs for any issues

#### Option C: Update Procfile

Edit `Procfile` to use new bot by default:

```procfile
# Old (legacy bot)
worker: python scripts/telegram_chatgpt_mode.py

# New (modular bot)
worker: python bot/main.py
```

### Step 4: Verify Deployment

After deployment, verify:
- [ ] Bot responds to `/start`
- [ ] `/help` shows all commands
- [ ] Chat messages work
- [ ] Sessions can be created and switched
- [ ] Rate limiting works (send 31 messages quickly)
- [ ] Safety filter blocks API keys (test with fake key pattern)

## Rollback Plan

If you encounter issues, rollback is simple:

### Method 1: Environment Variable
```bash
USE_NEW_BOT=0
# Restart worker
```

### Method 2: Revert Procfile (if changed)
```procfile
worker: python scripts/telegram_chatgpt_mode.py
```

### Method 3: Emergency Rollback
Stop the new bot process and start legacy:
```bash
pkill -f "python bot/main.py"
python scripts/telegram_chatgpt_mode.py
```

## Important Notes

### Data Compatibility
- **New bot sessions**: Stored in `analysis/sessions/<user_id>/`
- **Legacy bot history**: Stored in `analysis/chat_sessions.json`
- These are **separate** - sessions created in new bot won't appear in legacy

### Session Migration
The new bot and legacy bot use different session storage formats. If you need to migrate old conversations:

1. Legacy bot stores all users in one file: `analysis/chat_sessions.json`
2. New bot stores per-user in separate files: `analysis/sessions/<user_id>/default.json`

Manual migration is possible but not automated in this release.

### Provider API Keys
Ensure you have at least one provider configured:
- **OpenAI**: Required for basic functionality
- **Anthropic**: Optional (Claude models)
- **Groq**: Optional (fast inference)

Check with `/status` command to see which providers are available.

### Rate Limiting
The new bot has rate limiting enabled by default:
- 30 messages per hour per user
- Configurable via environment variables
- In-memory (resets on bot restart)

Adjust if needed:
```bash
BOT_RATE_MAX_MESSAGES=50
BOT_RATE_WINDOW_SECONDS=7200  # 2 hours
```

## Troubleshooting

### Bot Not Responding
**Problem**: Bot doesn't respond to commands

**Solutions**:
1. Check bot process is running: `ps aux | grep "python bot/main.py"`
2. Check logs for errors
3. Verify `TELEGRAM_BOT_TOKEN` is set
4. Check `TELEGRAM_ALLOWLIST` includes your user ID (use `/whoami`)

### Provider Unavailable
**Problem**: "الموفر غير مهيأ" or "Provider not configured"

**Solutions**:
1. Set the API key in `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GROQ_API_KEY=gsk_...
   ```
2. Restart the bot
3. Verify with `/status`

### Rate Limited
**Problem**: "تم تجاوز حد الرسائل"

**Solutions**:
1. Wait for the cooldown period (shown in message)
2. Increase limits in environment:
   ```bash
   BOT_RATE_MAX_MESSAGES=100
   ```
3. Restart bot to reset counters (temporary solution)

### Sessions Not Saving
**Problem**: Sessions disappear or don't persist

**Solutions**:
1. Check `SESSION_BASE_PATH` directory exists: `ls -la analysis/sessions/`
2. Check file permissions: `chmod -R 755 analysis/sessions/`
3. Check logs for write errors

## Command Reference

### New Commands
- `/sessions` - List all your sessions
- `/new <name>` - Create new session
- `/switch <name>` - Switch to session
- `/clear` - Clear current session
- `/export <md|json>` - Export session
- `/summarize` - Summarize conversation
- `/continue` - Extend last response
- `/regen` - Regenerate last response
- `/share` - Create shareable snippet
- `/model list` - List available models
- `/model <name>` - Switch model
- `/provider list` - List providers
- `/provider <name>` - Switch provider
- `/persona list` - List personas
- `/persona <name>` - Switch persona

### Existing Commands (Still Work)
- `/start` - Welcome
- `/help` - Help text
- `/whoami` - Your Telegram ID
- `/status` - Bot status
- `/chat <message>` - Chat (or just send text)

## Support & Feedback

### Getting Help
1. Check this guide
2. Check `bot/README.md` for detailed documentation
3. Review logs for specific error messages
4. Open an issue in the repository

### Reporting Issues
When reporting issues, include:
- Command that failed
- Error message (if any)
- Bot logs (relevant lines)
- Environment (local/production)
- Steps to reproduce

### Providing Feedback
We welcome feedback on:
- User experience
- Command usability
- Performance
- Feature requests
- Documentation clarity

## Security Notes

### Secrets Detection
The new bot automatically blocks messages containing:
- API keys (OpenAI, GitHub, AWS, etc.)
- OAuth tokens
- Private keys
- JWT tokens

If you accidentally try to send a secret, you'll get a warning instead.

### Authorization
The bot respects `TELEGRAM_ALLOWLIST`:
- If empty: All users allowed (dev/testing)
- If set: Only listed user IDs allowed (production)

Use `/whoami` to get your user ID.

## Future Enhancements

Planned for future releases:
- Redis-based session storage (scalability)
- Streaming responses (real-time output)
- Repository analysis tools integration
- Advanced conversation analytics
- Web dashboard
- Multi-language support

## Version History

- **v2.0.0** - Modular bot with multi-session support
- **v1.0.0** - Legacy bot (still available)

## Conclusion

The new modular bot provides significant improvements while maintaining full backward compatibility. The migration is low-risk with easy rollback options.

**Key Takeaway**: You can test the new bot risk-free using `USE_NEW_BOT=1` while keeping the legacy bot as fallback.

For questions or issues, refer to `bot/README.md` or open an issue.

---

**Happy Chatting! 🤖**
