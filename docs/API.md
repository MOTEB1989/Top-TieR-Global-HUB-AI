# API Documentation

## Telegram Bot Commands

### Public Commands

#### `/start`
**Description**: Welcome message and bot introduction

**Usage**:
```
/start
```

**Response**:
```
🤖 مرحباً User!

أنا @LexnexuxBot - مساعدك الذكي للمشروع Top-TieR Global HUB AI

📋 الأوامر المتاحة:
🔹 /start - رسالة الترحيب
🔹 /status - حالة النظام والخدمات
🔹 /help - المساعدة والتعليمات
...
```

#### `/help`
**Description**: Display help and available commands

**Usage**:
```
/help
```

**Response**: List of all available commands with descriptions

#### `/status`
**Description**: Check system status and service health

**Usage**:
```
/status
```

**Response**:
```
📊 حالة النظام

✓ Telegram Bot - يعمل
✓ OpenAI - مُعدّ
✓ GitHub - مُعدّ

⏰ الوقت: 2024-01-15 10:30:45
```

### Advanced Commands

#### `/ai <question>`
**Description**: Ask AI-powered question (requires OpenAI configuration)

**Usage**:
```
/ai What is Docker?
/ai كيف أحسن أداء Python؟
```

**Parameters**:
- `question` (required): Your question or prompt

**Response**: AI-generated answer from OpenAI GPT model

**Rate Limit**: 10 requests per minute per user

#### `/preflight`
**Description**: Run comprehensive system check

**Usage**:
```
/preflight
```

**Response**: Results of system diagnostics including:
- Service availability
- Configuration validation
- Dependency checks
- Performance metrics

#### `/keys`
**Description**: Verify API key configuration

**Usage**:
```
/keys
```

**Response**: Status of configured API keys (without exposing actual keys)

#### `/secrets`
**Description**: Check GitHub secrets configuration

**Usage**:
```
/secrets
```

**Response**: List of GitHub secrets and their configuration status

## REST API Endpoints

### Health & Status

#### GET `/health`
**Description**: Basic health check

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

**Status Codes**:
- `200`: Service healthy
- `503`: Service unavailable

#### GET `/health/live`
**Description**: Liveness probe (Kubernetes compatible)

**Response**:
```json
{
  "alive": true,
  "service": "telegram-bot",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "uptime_seconds": 3600
}
```

#### GET `/health/ready`
**Description**: Readiness probe (Kubernetes compatible)

**Response**:
```json
{
  "ready": true,
  "service": "telegram-bot",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

#### GET `/health/status`
**Description**: Detailed service health status

**Response**:
```json
{
  "service": "telegram-bot",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "uptime_seconds": 3600,
  "checks": {
    "openai": {
      "status": "healthy",
      "details": {
        "configured": true,
        "available": true,
        "response_time_ms": 234
      }
    },
    "telegram": {
      "status": "healthy",
      "details": {
        "configured": true,
        "available": true,
        "bot_username": "LexnexuxBot"
      }
    },
    "github": {
      "status": "healthy",
      "details": {
        "configured": true,
        "available": true,
        "repository": "MOTEB1989/Top-TieR-Global-HUB-AI"
      }
    },
    "database": {
      "status": "healthy",
      "details": {
        "connected": true,
        "response_time_ms": 12
      }
    }
  }
}
```

### Metrics

#### GET `/metrics`
**Description**: Prometheus-compatible metrics endpoint

**Response** (text/plain):
```
# TYPE telegram_bot_requests_total counter
telegram_bot_requests_total{method="POST",endpoint="/chat"} 1234

# TYPE telegram_bot_request_duration_seconds histogram
telegram_bot_request_duration_seconds_bucket{le="0.005"} 100
telegram_bot_request_duration_seconds_bucket{le="0.01"} 250
telegram_bot_request_duration_seconds_bucket{le="0.025"} 450
...

# TYPE telegram_bot_active_users gauge
telegram_bot_active_users 42

# TYPE telegram_bot_uptime_seconds gauge
telegram_bot_uptime_seconds 3600
```

## Authentication

### Telegram Bot
- **Method**: User ID allowlist
- **Configuration**: `TELEGRAM_ALLOWLIST` environment variable
- **Format**: Comma-separated user IDs
- **Example**: `TELEGRAM_ALLOWLIST=123456789,987654321`

### API Endpoints
- **Method**: API Key (if enabled)
- **Header**: `Authorization: Bearer <api_key>`
- **Configuration**: Set in environment or configuration file

## Rate Limiting

### Limits

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| `/api/chat` | 50 requests | 60 seconds |
| `/health` | 1000 requests | 60 seconds |
| `/metrics` | 100 requests | 60 seconds |
| Telegram commands (per user) | 10 requests | 60 seconds |

### Rate Limit Headers

**Response Headers**:
```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1673784045
```

**Rate Limit Exceeded Response**:
```json
{
  "error": "Rate limit exceeded",
  "detail": "Please try again later",
  "retry_after": 30
}
```

**Status Code**: `429 Too Many Requests`

## Error Responses

### Error Format
```json
{
  "error": "error_type",
  "detail": "Human-readable error message",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "trace_id": "abc123def456"
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "error": "invalid_input",
  "detail": "Invalid request parameters"
}
```

#### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "detail": "Authentication required"
}
```

#### 403 Forbidden
```json
{
  "error": "forbidden",
  "detail": "You are not authorized to use this bot"
}
```

#### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

#### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "detail": "An unexpected error occurred"
}
```

#### 503 Service Unavailable
```json
{
  "error": "service_unavailable",
  "detail": "Service temporarily unavailable"
}
```

## Webhooks (Optional)

### Telegram Webhook Setup

#### Set Webhook
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/webhook/telegram"}'
```

#### Webhook Endpoint
**POST** `/webhook/telegram`

**Headers**:
- `Content-Type: application/json`
- `X-Telegram-Bot-Api-Secret-Token`: (if configured)

**Request Body**:
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "User",
      "username": "username"
    },
    "chat": {
      "id": 123456789,
      "first_name": "User",
      "username": "username",
      "type": "private"
    },
    "date": 1673784045,
    "text": "/start"
  }
}
```

## SDK Examples

### Python
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Get metrics
response = requests.get("http://localhost:8000/metrics")
print(response.text)

# Telegram bot (python-telegram-bot)
from telegram import Bot

bot = Bot(token="YOUR_TOKEN")
bot.send_message(chat_id=123456789, text="Hello!")
```

### cURL
```bash
# Health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/health/status | jq

# Metrics
curl http://localhost:8000/metrics
```

### JavaScript/Node.js
```javascript
// Health check
const response = await fetch('http://localhost:8000/health');
const data = await response.json();
console.log(data);

// Telegram bot
const TelegramBot = require('node-telegram-bot-api');
const bot = new TelegramBot(TOKEN, {polling: true});

bot.on('message', (msg) => {
  console.log(msg);
});
```

## Monitoring Integration

### Prometheus
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'telegram-bot'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard
Import dashboard JSON from `grafana/telegram-bot-dashboard.json`

**Key Metrics**:
- Request rate
- Response time (P50, P95, P99)
- Error rate
- Active users
- Service health

## Versioning

**Current Version**: 2.0.0

**API Version**: v1

**Changelog**: See [CHANGELOG.md](../CHANGELOG.md)

## Support

- **Documentation**: https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/docs
- **Issues**: https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/issues
- **Discussions**: https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/discussions
