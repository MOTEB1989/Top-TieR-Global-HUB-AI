# 🤖 Bot Commands Quick Reference

## 📋 All Commands (24 Total)

### 🔹 Basic (7 commands)
```
/start          - Interactive welcome
/help           - Full command guide
/whoami         - Your info & stats
/status         - System status
/ping           - Test response time
/version        - Bot version info
/about          - Project details
```

### 💬 AI & Chat (5 commands)
```
/chat <msg>     - Chat with memory
/ask <question> - Quick question
/translate <lang> <text> - Translate
/summarize <text> - Summarize text
<direct msg>    - Auto smart reply
```

### 🔍 Diagnostic (4 commands)
```
/verifyenv      - Check env variables
/preflight      - Full system check
/report         - JSON report
/health         - Health metrics
```

### 📦 Repository (4 commands)
```
/repo           - Repo analysis
/insights       - AI insights
/search <query> - Search code
/issue <title>  - Create issue
```

### 💾 Database (4 commands)
```
/db status      - DB status
/db test        - Test connections
/stats          - Usage stats
/history        - Chat history
```

### 🤖 AI Models (1 command)
```
/model list     - List models
/model info     - Current model
```

## 🚀 Quick Start Examples

### Chat & AI
```
# Direct message (with memory)
Hello, tell me about Docker

# Chat (with memory)
/chat What are the best security practices?

# Quick question (no memory)
/ask What is Kubernetes?

# Translate
/translate en مرحبا بكم
/translate ar Hello world

# Summarize
/summarize [long text here]
```

### Repository
```
# Get repo info
/repo

# AI-powered insights
/insights

# Search code
/search def main
/search class User

# Create issue
/issue Fix login bug in auth.py
```

### Diagnostics
```
# Check environment
/verifyenv

# Full system check
/preflight

# Health status
/health

# Generate report
/report
```

### Database
```
# Check all databases
/db status

# Test connections
/db test

# View your stats
/stats

# Your chat history
/history
```

### AI Models
```
# See available models
/model list

# Current configuration
/model info
```

## ⚡ Tips

1. **Direct Messages**: Just type normally without `/` for smart chat
2. **Rate Limits**: 50 messages/hour, 20 AI calls/hour per user
3. **Memory**: `/chat` remembers context, `/ask` doesn't
4. **Authorization**: Configure TELEGRAM_ALLOWLIST for security

## 🔐 Security

- Only whitelisted users can access (if TELEGRAM_ALLOWLIST set)
- All commands require authorization
- Rate limiting prevents abuse
- Sensitive data not logged

## 📊 Features

✅ 3 AI providers (OpenAI, Groq, Anthropic)
✅ GitHub integration
✅ Multi-database support
✅ Conversation memory
✅ User statistics
✅ Comprehensive logging
✅ Error handling

---

**Version**: 2.0.0 | **Repository**: MOTEB1989/Top-TieR-Global-HUB-AI
