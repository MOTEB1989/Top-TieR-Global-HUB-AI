# 🤖 Unified Telegram Bot Guide

## 📋 Overview

The **Unified Telegram Bot** is an advanced, feature-rich bot that provides:

- ✅ Multiple AI provider support (OpenAI, Groq, Anthropic)
- ✅ Bidirectional GitHub repository integration
- ✅ Multi-database connectivity
- ✅ Smart conversation with memory
- ✅ 30+ specialized commands
- ✅ Rate limiting and user quotas
- ✅ Comprehensive error handling and logging

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install python-telegram-bot python-dotenv requests psycopg2-binary redis
```

### 2. Configure Environment

Copy `.env.example` to `.env` and set your tokens:

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ALLOWLIST=your_user_id,another_user_id
OPENAI_API_KEY=your_openai_key  # For AI features
```

### 3. Run the Bot

```bash
python3 scripts/telegram_unified_bot.py
```

### 4. Test the Bot

```bash
python3 scripts/test_unified_bot.py
```

## 📱 Bot Commands

### 🔹 Basic Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Interactive welcome with command menu | `/start` |
| `/help` | Comprehensive guide by permissions | `/help` |
| `/whoami` | User info + statistics | `/whoami` |
| `/status` | Full system status (Bot, DB, APIs, Services) | `/status` |
| `/ping` | Response speed test | `/ping` |
| `/version` | Bot version + last update | `/version` |
| `/about` | Project information | `/about` |

### 🔹 AI & Chat Commands

| Command | Description | Example |
|---------|-------------|---------|
| Direct message | Smart auto-reply with memory | `Hello, how are you?` |
| `/chat <message>` | Chat with conversation memory | `/chat What is Docker?` |
| `/ask <question>` | Direct question without memory | `/ask Explain Kubernetes` |
| `/translate <lang> <text>` | Translate text | `/translate en مرحبا` |
| `/summarize <text>` | Summarize text | `/summarize <long text>` |

### 🔹 Diagnostic Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/verifyenv` | Check environment variables | `/verifyenv` |
| `/preflight` | Comprehensive connection checks | `/preflight` |
| `/report` | Full JSON system report | `/report` |
| `/health` | System health status | `/health` |

### 🔹 Repository Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/repo` | General repository analysis | `/repo` |
| `/insights` | Smart summary with risks/opportunities | `/insights` |
| `/file <path>` | Read file from repository | `/file README.md` |
| `/search <query>` | Search in code | `/search def main` |
| `/analyze <path>` | Analyze file/folder | `/analyze scripts/` |
| `/issue <title>` | Create GitHub Issue | `/issue Fix login bug` |
| `/pr <title>` | Create Pull Request | `/pr Add new feature` |

### 🔹 Database Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/db status` | All databases status | `/db status` |
| `/db test` | Test database connections | `/db test` |
| `/stats` | Usage statistics | `/stats` |
| `/history` | Last 20 conversations | `/history` |
| `/export` | Export user data | `/export` |

### 🔹 AI Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/model list` | List available AI models | `/model list` |
| `/model switch <model>` | Switch AI model | `/model switch gpt-4` |
| `/model info` | Current model information | `/model info` |

## ⚙️ Configuration

### Environment Variables

#### Required

- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
- `TELEGRAM_ALLOWLIST` - Comma-separated user IDs (leave empty to allow all)

#### Optional AI Providers

- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - Model name (default: `gpt-4o-mini`)
- `GROQ_API_KEY` - Groq API key for fast inference
- `ANTHROPIC_API_KEY` - Anthropic Claude API key

#### Optional Integrations

- `GITHUB_TOKEN` - GitHub personal access token
- `GITHUB_REPO` - Repository name (format: `owner/repo`)

#### Database URLs

- `DB_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `NEO4J_URI` - Neo4j bolt URI
- `NEO4J_AUTH` - Neo4j credentials (format: `user/password`)

### Rate Limiting

The bot implements automatic rate limiting to prevent abuse:

- **Messages**: 50 per hour per user
- **AI Calls**: 20 per hour per user

These limits automatically reset every hour.

## 🔐 Security Features

1. **User Authorization**: Only whitelisted users can access the bot (if TELEGRAM_ALLOWLIST is set)
2. **Rate Limiting**: Prevents spam and excessive API usage
3. **Input Validation**: All user inputs are validated before processing
4. **Secure Logging**: Sensitive data is not logged
5. **Error Handling**: Comprehensive error handling prevents crashes

## 📊 Data Storage

The bot stores data locally in `analysis/bot_data/`:

- `chat_sessions.json` - Conversation history
- `user_stats.json` - User statistics
- `rate_limits.json` - Rate limit tracking
- `bot.log` - Application logs

## 🐛 Troubleshooting

### Bot doesn't start

1. Check if `TELEGRAM_BOT_TOKEN` is set correctly
2. Verify dependencies are installed: `pip list | grep telegram`
3. Check logs in `analysis/bot_data/bot.log`

### AI commands don't work

1. Verify `OPENAI_API_KEY` is set and valid
2. Check API quota on OpenAI dashboard
3. Try alternative providers (Groq, Anthropic)

### Rate limit issues

1. Wait for the rate limit window to expire (1 hour)
2. Adjust limits in bot configuration if needed
3. Check `analysis/bot_data/rate_limits.json`

### Database connection errors

1. Verify database URLs are correct
2. Check if services are running: `docker ps`
3. Test connections: `/db test`

## 🔧 Development

### Adding New Commands

1. Create a new command handler function:

```python
@require_auth
async def cmd_mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mycommand."""
    user_stats.record_command(update.effective_user.id, "mycommand")
    # Your logic here
    await update.message.reply_text("Response")
```

2. Register the handler in `main()`:

```python
application.add_handler(CommandHandler("mycommand", cmd_mycommand))
```

### Testing

Run the test suite:

```bash
python3 scripts/test_unified_bot.py
```

### Logging

Logs are stored in `analysis/bot_data/bot.log` with the following levels:

- `INFO`: Normal operations
- `WARNING`: Suspicious activity (unauthorized access)
- `ERROR`: Command failures, API errors
- `CRITICAL`: System failures

## 📈 Performance Tips

1. **Use Groq for faster responses**: Set `GROQ_API_KEY` for quick AI inference
2. **Limit conversation history**: Adjust `max_messages` in `ConversationMemory`
3. **Monitor rate limits**: Use `/stats` to track usage
4. **Enable Redis**: For better performance with multiple users

## 🤝 Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `test_unified_bot.py`
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Email**: Contact repository owner

## 🔄 Updates

Check for updates:

```bash
git pull origin main
python3 scripts/telegram_unified_bot.py --version
```

---

**Made with ❤️ for Top-TieR-Global-HUB-AI**

Version: 2.0.0 | Last Updated: 2024-11-23
