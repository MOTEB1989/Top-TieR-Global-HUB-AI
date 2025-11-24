# Modular ChatGPT-grade Telegram Bot

## Overview

This is a modular, ChatGPT-grade Telegram bot with advanced features including:

- ✅ Multi-session management
- ✅ Multiple AI providers (OpenAI, Anthropic, Groq)
- ✅ Persona system (default, engineer, security, docs)
- ✅ Advanced commands (summarize, continue, regen, share)
- ✅ Rate limiting and safety filtering
- ✅ Follow-up suggestions
- ✅ File-based persistence

## Architecture

```
bot/
├── core/                    # Core functionality
│   ├── session_store.py     # Multi-session CRUD & persistence
│   ├── rate_limiter.py      # Per-user rate limiting
│   ├── model_registry.py    # Model/provider registry
│   ├── persona_manager.py   # System prompt personas
│   └── tool_runner.py       # Tool execution (placeholder)
├── commands/                # Command handlers
│   ├── chat.py             # Chat and text message handling
│   ├── sessions.py         # Session management commands
│   ├── advanced.py         # Advanced commands
│   └── meta.py             # Meta commands (help, status, etc.)
├── adapters/               # AI provider adapters
│   ├── openai_client.py    # OpenAI wrapper
│   ├── anthropic_client.py # Anthropic (Claude) wrapper
│   └── groq_client.py      # Groq wrapper
├── utils/                  # Utilities
│   ├── response_builder.py # Follow-up suggestions
│   └── safety_filter.py    # Secret pattern detection
└── main.py                 # Entry point
```

## Installation & Setup

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_key

# Optional - additional providers
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Bot configuration
SESSION_BASE_PATH=analysis/sessions
BOT_MAX_MESSAGES_PER_SESSION=50
BOT_RATE_WINDOW_SECONDS=3600
BOT_RATE_MAX_MESSAGES=30
BOT_PERSONA=default
BOT_SILENT_SUGGESTIONS=false

# Use new bot (0=legacy, 1=new)
USE_NEW_BOT=1
```

### 2. Run the Bot

**Option A: Direct execution**
```bash
python bot/main.py
```

**Option B: With environment flag**
```bash
USE_NEW_BOT=1 python bot/main.py
```

**Option C: Update Procfile (production)**
```
worker: python bot/main.py
```

## Available Commands

### Basic Commands
- `/start` - Welcome message
- `/help` - Show all commands
- `/whoami` - Display your Telegram ID
- `/status` - Show bot status and configuration

### Session Management
- `/sessions` - List all your sessions
- `/new <name>` - Create a new session
- `/switch <name>` - Switch to a different session
- `/clear` - Clear current session messages
- `/export <md|json>` - Export current session

### Chat
- `/chat <message>` - Send a chat message
- Or simply send a text message directly!

### Advanced Commands
- `/summarize` - Summarize the current conversation
- `/continue` - Continue the last assistant response
- `/regen` - Regenerate the last assistant response
- `/share` - Create a shareable conversation snippet

### Configuration
- `/model list` - List available models
- `/model <name>` - Switch to a specific model
- `/provider list` - List available providers
- `/provider <openai|anthropic|groq>` - Switch provider
- `/persona list` - List available personas
- `/persona <name>` - Switch to a persona

## Personas

### default (الافتراضي)
General-purpose assistant focused on the repository

### engineer (المهندس)
Software engineer focused on architecture, code quality, and best practices

### security (الأمان)
Security expert focused on vulnerabilities, threats, and hardening

### docs (التوثيق)
Documentation specialist focused on clear, structured documentation

## Rate Limiting

By default:
- **30 messages** per **60 minutes** (1 hour)
- Configurable via `BOT_RATE_WINDOW_SECONDS` and `BOT_RATE_MAX_MESSAGES`

When rate limited, users receive a clear message with reset time.

## Safety Features

The bot automatically detects and blocks messages containing:
- API keys (OpenAI, GitHub, AWS, etc.)
- OAuth tokens
- Private keys
- JWT tokens

Users receive a warning instead of processing unsafe input.

## Session Persistence

Sessions are stored as JSON files under `analysis/sessions/<user_id>/<session_name>.json`

Each session contains:
- Messages (with timestamps)
- Metadata (model, provider, persona)
- Creation and update timestamps

Sessions are automatically trimmed to `BOT_MAX_MESSAGES_PER_SESSION` messages.

## Rollback Plan

If issues arise with the new bot:

### Option 1: Environment Variable
```bash
USE_NEW_BOT=0  # Use legacy bot
```

### Option 2: Revert Procfile
```
worker: python scripts/telegram_chatgpt_mode.py
```

### Option 3: Disable temporarily
Stop the worker process and restart with the legacy script.

**Note:** Session data is preserved during rollback. The legacy bot uses a different storage format (`analysis/chat_sessions.json`), so sessions created with the new bot won't be accessible in legacy mode.

## Migration from Legacy Bot

The new bot runs independently from the legacy bot. To migrate:

1. **Test the new bot** in a separate environment
2. **Set** `USE_NEW_BOT=1` when ready
3. **Update Procfile** if deploying to production
4. **Keep legacy bot** for at least one release cycle as backup

## Development

### Testing

```bash
# Test imports
python -c "from bot.main import main"

# Test components
python -c "from bot.core.session_store import SessionStore; print('OK')"

# Run with debug logging
LOG_LEVEL=DEBUG python bot/main.py
```

### Adding New Personas

Edit `bot/core/persona_manager.py` and add to `_register_default_personas()`:

```python
self.register_persona(Persona(
    name="my_persona",
    display_name="My Persona (العربي)",
    description="Description of the persona",
    system_prompt="System prompt text..."
))
```

### Adding New Models

Edit `bot/core/model_registry.py` and add to `_register_default_models()`:

```python
self.register_model(ModelInfo(
    name="model-name",
    provider="provider-name",
    display_name="Display Name",
    description="Model description",
    context_window=128000,
    supports_streaming=True
))
```

## Troubleshooting

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` is set correctly
- Verify bot has started without errors
- Check rate limiting isn't blocking you

### Provider not available
- Ensure API key is set in environment
- Check `/provider list` to see available providers
- Try `/provider openai` to switch to OpenAI

### Session not saving
- Check `SESSION_BASE_PATH` directory exists and is writable
- Verify no file permission issues
- Check logs for errors

### Rate limited incorrectly
- Adjust `BOT_RATE_MAX_MESSAGES` and `BOT_RATE_WINDOW_SECONDS`
- Rate limit state is in-memory (resets on bot restart)

## Future Enhancements

Planned features (not in this release):
- Redis-based session storage
- Streaming responses
- Repository deep analysis tools
- Metrics endpoint
- Advanced conversation analytics
- Multi-language support beyond Arabic/English

## Support

For issues or questions:
1. Check this README
2. Review logs for error messages
3. Test with legacy bot to isolate issues
4. Open an issue in the repository

## License

Part of Top-TieR-Global-HUB-AI project - MIT License
