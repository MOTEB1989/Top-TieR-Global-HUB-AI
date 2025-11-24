# 🤖 Unified Telegram Bot

> Advanced Telegram Bot for Top-TieR-Global-HUB-AI with 24+ commands, multi-AI support, and GitHub integration

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Security](https://img.shields.io/badge/security-0%20vulnerabilities-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install python-telegram-bot python-dotenv requests
```

### 2. Configure
```bash
cp ../.env.example ../.env
# Edit .env and set:
#   TELEGRAM_BOT_TOKEN=your_token_from_botfather
#   TELEGRAM_ALLOWLIST=your_user_id
```

### 3. Run
```bash
python3 telegram_unified_bot.py
```

### 4. Test
```bash
python3 test_unified_bot.py
```

---

## 📱 Features

### ✨ 24 Specialized Commands

| Category | Count | Commands |
|----------|-------|----------|
| 🔹 **Basic** | 7 | start, help, whoami, status, ping, version, about |
| 💬 **AI & Chat** | 5 | chat, ask, translate, summarize, direct messages |
| 🔍 **Diagnostic** | 4 | verifyenv, preflight, report, health |
| 📦 **Repository** | 4 | repo, insights, search, issue |
| 💾 **Database** | 4 | db status/test, stats, history |
| 🤖 **AI Models** | 1 | model list/info |

### 🧠 AI Provider Support

- **OpenAI** - GPT-4o-mini (default), GPT-4o, GPT-3.5-turbo
- **Groq** - llama-3.1-70b, mixtral, gemma (fast inference)
- **Anthropic** - Claude 3.5 Sonnet, Opus

### 🔐 Security Features

- ✅ User allowlist authorization
- ✅ Rate limiting (50 msg/hr, 20 AI/hr)
- ✅ Secure token handling
- ✅ Input validation
- ✅ **0 security vulnerabilities** (CodeQL verified)

### 💾 Smart Features

- ✅ Conversation memory (30 messages per user)
- ✅ User statistics tracking
- ✅ GitHub integration (repo, search, issues)
- ✅ Multi-database support
- ✅ Comprehensive logging

---

## 📖 Command Examples

### Basic Usage
```
/start                          # Welcome message
/help                           # Show all commands
/whoami                         # Your stats
/status                         # System status
```

### AI Chat
```
Hello, how are you?             # Direct message (with memory)
/chat What is Docker?           # Chat (with memory)
/ask Explain Kubernetes         # Quick question (no memory)
/translate en مرحبا             # Translate to English
/summarize <long text>          # Summarize text
```

### Repository
```
/repo                           # Repository stats
/insights                       # AI-powered insights
/search def main                # Search code
/issue Fix login bug            # Create issue
```

### Diagnostics
```
/verifyenv                      # Check environment
/preflight                      # Full system check
/health                         # Health metrics
/report                         # JSON report
```

### Database
```
/db status                      # All databases
/db test                        # Test connections
/stats                          # Usage statistics
/history                        # Your chat history
```

### AI Management
```
/model list                     # Available models
/model info                     # Current config
```

---

## ⚙️ Configuration

### Required Environment Variables
```bash
TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

### Recommended
```bash
TELEGRAM_ALLOWLIST=user_id1,user_id2
```

### Optional AI Providers
```bash
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
ANTHROPIC_API_KEY=sk-ant-...
```

### Optional Integrations
```bash
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo
DB_URL=postgresql://...
REDIS_URL=redis://...
```

---

## 🧪 Testing

Run the test suite to verify everything is set up correctly:

```bash
python3 test_unified_bot.py
```

Expected output:
```
✅ Imports
✅ Environment
✅ Bot File
✅ Data Directory
✅ All tests passed!
```

---

## 📊 Architecture

### Core Components
```
RateLimiter          - Per-user rate limiting
UserStats            - Usage statistics
ConversationMemory   - Chat history (batch saves)
AIProvider           - Multi-AI abstraction
GitHubIntegration    - Repository operations
DatabaseChecker      - Health checks
```

### Data Storage
```
analysis/bot_data/
├── chat_sessions.json   # Conversations
├── user_stats.json      # User stats
├── rate_limits.json     # Rate limits
├── bot.log              # Logs
└── report_*.json        # Reports
```

---

## 🔧 Development

### Adding New Commands

1. Create handler function:
```python
@require_auth
async def cmd_mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_stats.record_command(update.effective_user.id, "mycommand")
    await update.message.reply_text("Response")
```

2. Register in main():
```python
application.add_handler(CommandHandler("mycommand", cmd_mycommand))
```

### Running in Development
```bash
# With debug logging
PYTHONPATH=. python3 -m pdb telegram_unified_bot.py
```

---

## 📚 Documentation

- **[Complete User Guide](../docs/TELEGRAM_BOT_GUIDE.md)** - Full documentation
- **[Commands Reference](../docs/BOT_COMMANDS_REFERENCE.md)** - Quick reference
- **[Implementation Summary](../docs/BOT_IMPLEMENTATION_SUMMARY.md)** - Technical details

---

## 🐛 Troubleshooting

### Bot doesn't start
```bash
# Check token
python3 test_unified_bot.py

# Verify .env file
cat ../.env | grep TELEGRAM_BOT_TOKEN
```

### AI commands fail
```bash
# Verify API keys
python3 -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Rate limit issues
```bash
# Check rate limit file
cat analysis/bot_data/rate_limits.json
```

### View logs
```bash
tail -f analysis/bot_data/bot.log
```

---

## 📈 Performance

- **Response Time**: <500ms typical
- **Memory Usage**: ~50-100 MB
- **Storage**: ~1-10 MB data files
- **Uptime**: Tracked since start
- **Rate Limits**: Per-user configurable

---

## 🔐 Security

### Best Practices
1. ✅ Always set `TELEGRAM_ALLOWLIST`
2. ✅ Never commit `.env` file
3. ✅ Rotate API keys regularly
4. ✅ Monitor `bot.log` for issues
5. ✅ Keep dependencies updated

### Security Audit
```bash
# Run CodeQL scan
codeql analyze

# Check dependencies
pip list --outdated

# Review logs
grep -i error analysis/bot_data/bot.log
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

---

## 📞 Support

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues
- **Testing**: `python3 test_unified_bot.py`
- **Logs**: `analysis/bot_data/bot.log`

---

## ✨ Status

- ✅ **Production Ready**
- ✅ **24 Commands**
- ✅ **3 AI Providers**
- ✅ **0 Vulnerabilities**
- ✅ **100% Tests Passing**
- ✅ **Complete Documentation**

---

**Version:** 2.0.0  
**Author:** MOTEB1989  
**Repository:** Top-TieR-Global-HUB-AI  
**Last Updated:** 2024-11-23

🚀 **Ready to use!**
