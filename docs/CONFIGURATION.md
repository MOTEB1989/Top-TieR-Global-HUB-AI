# Configuration Guide

## Overview

This guide covers all configuration options for the Top-TieR-Global-HUB-AI Telegram bot system.

## Configuration Files

### 1. Environment Variables (`.env`)

```bash
# ============================================================================
# Core API Keys
# ============================================================================
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWLIST=123456789,987654321
TELEGRAM_CHAT_ID=123456789

GITHUB_TOKEN=ghp_your-token-here
GITHUB_REPO=MOTEB1989/Top-TieR-Global-HUB-AI

# ============================================================================
# Database Configuration
# ============================================================================
DB_URL=postgresql://postgres:password@localhost:5432/motebai
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_AUTH=neo4j/password

# ============================================================================
# Application Settings
# ============================================================================
API_PORT=3000
ENVIRONMENT=production  # development, staging, production
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================================================
# Security Settings
# ============================================================================
SECRET_ENCRYPTION_KEY=your-32-byte-base64-encoded-key
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# ============================================================================
# Monitoring & Alerts
# ============================================================================
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL_FROM=alerts@example.com
ALERT_EMAIL_TO=admin@example.com
GRAFANA_URL=http://localhost:3000
```

### 2. Security Configuration (`config/security.yaml`)

```yaml
# Rate Limiting
rate_limiting:
  enabled: true
  algorithm: "token_bucket"  # token_bucket, sliding_window, fixed_window
  token_bucket:
    capacity: 100
    refill_rate: 10.0
  endpoints:
    "/api/chat":
      capacity: 50
      refill_rate: 5.0

# Encryption
encryption:
  algorithm: "fernet"
  key_rotation_days: 90
  at_rest: true
  in_transit: true

# Input Validation
validation:
  max_input_length: 10000
  sanitize_html: true
  detect_sql_injection: true
  detect_xss: true

# Security Headers
security_headers:
  enabled: true
  content_security_policy: "default-src 'self'"
  strict_transport_security:
    enabled: true
    max_age: 31536000
    include_subdomains: true
```

### 3. Monitoring Configuration (`config/monitoring.yaml`)

```yaml
# Logging
logging:
  enabled: true
  format: "json"
  level: "INFO"
  outputs:
    console:
      enabled: true
    file:
      enabled: true
      path: "/var/log/telegram-bot/app.log"
      max_size_mb: 100
      backup_count: 5

# Health Checks
health_checks:
  enabled: true
  endpoints:
    liveness: "/health/live"
    readiness: "/health/ready"
    status: "/health/status"
  check_interval_seconds: 30

# Metrics
metrics:
  enabled: true
  namespace: "telegram_bot"
  prometheus:
    enabled: true
    endpoint: "/metrics"
    port: 9090

# Alerting
alerting:
  enabled: true
  channels:
    slack:
      enabled: true
      min_level: "warning"
    email:
      enabled: false
      min_level: "error"
  rules:
    - name: "high_error_rate"
      condition: "error_rate > 0.05"
      severity: "critical"
```

### 4. Testing Configuration (`config/testing.yaml`)

```yaml
# Integration Tests
integration_tests:
  enabled: true
  openai:
    enabled: true
    use_real_api: true
    test_model: "gpt-3.5-turbo"
  telegram:
    enabled: true
    use_real_api: true
  github:
    enabled: true
    use_real_api: true

# Load Tests
load_tests:
  enabled: true
  scenarios:
    light_load:
      duration_seconds: 60
      users: 10
      requests_per_second: 5
    normal_load:
      duration_seconds: 300
      users: 50
      requests_per_second: 20

# Security Tests
security_tests:
  enabled: true
  vulnerability_scan:
    enabled: true
    tools:
      - "bandit"
      - "safety"
```

## Configuration by Environment

### Development
```yaml
ENVIRONMENT=development
LOG_LEVEL=DEBUG
RATE_LIMIT_ENABLED=false
DB_URL=postgresql://postgres:dev@localhost:5432/dev_db
```

### Staging
```yaml
ENVIRONMENT=staging
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
DB_URL=postgresql://postgres:staging@staging-db:5432/staging_db
```

### Production
```yaml
ENVIRONMENT=production
LOG_LEVEL=WARNING
RATE_LIMIT_ENABLED=true
DB_URL=postgresql://postgres:prod@prod-db:5432/prod_db
SSL_ENABLED=true
HTTPS_ONLY=true
```

## Command-Line Options

### Bot Startup
```bash
# Basic startup
python scripts/run_telegram_bot.py

# With custom config
python scripts/run_telegram_bot.py --config config/custom.yaml

# With environment override
python scripts/run_telegram_bot.py --env production

# With debug logging
python scripts/run_telegram_bot.py --log-level DEBUG
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test category
pytest tests/integration/ -v -m integration

# Run with custom config
pytest tests/ -v --config config/testing.yaml
```

## Dynamic Configuration

### Runtime Configuration Updates
```python
from scripts.security.rate_limiter import TokenBucketRateLimiter

# Update rate limit at runtime
limiter = TokenBucketRateLimiter(capacity=200, refill_rate=20.0)
```

### Configuration Validation
```python
import yaml
from pathlib import Path

def validate_config(config_path: str):
    """Validate configuration file."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    required_keys = ['logging', 'health_checks', 'metrics']
    for key in required_keys:
        assert key in config, f"Missing required key: {key}"
```

## Best Practices

1. **Never commit secrets** to version control
2. **Use environment-specific configs** for different deployments
3. **Validate configurations** before deployment
4. **Document all custom settings**
5. **Keep backups** of production configurations
6. **Use encryption** for sensitive configuration files
7. **Review and rotate** API keys regularly
8. **Test configuration changes** in staging first

## Configuration Precedence

Configuration is loaded in the following order (later overrides earlier):

1. Default values (in code)
2. YAML configuration files
3. Environment variables
4. Command-line arguments

## Troubleshooting

### Configuration Not Loading
```bash
# Check file exists
ls -la config/

# Verify YAML syntax
python -c "import yaml; yaml.safe_load(open('config/security.yaml'))"

# Check environment variables
env | grep TELEGRAM
```

### Invalid Configuration Values
```bash
# Validate before starting
python scripts/verify_env.py

# Check specific values
python -c "import os; print(os.getenv('OPENAI_API_KEY', 'NOT SET'))"
```

## References

- [Security Configuration Details](SECURITY.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Architecture Overview](ARCHITECTURE.md)
