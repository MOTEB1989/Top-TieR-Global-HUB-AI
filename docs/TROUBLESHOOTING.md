# Troubleshooting Guide

## Common Issues and Solutions

### 1. Bot Not Starting

#### Issue: "TELEGRAM_BOT_TOKEN غير مُعدّ بشكل صحيح"
**Cause**: Bot token not configured or invalid

**Solution**:
```bash
# Check .env file
cat .env | grep TELEGRAM_BOT_TOKEN

# Ensure token format is correct (should be: 1234567890:ABCdef...)
# Get new token from @BotFather if needed

# Test token manually
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

#### Issue: "Module 'telegram' not found"
**Cause**: Dependencies not installed

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import telegram; print(telegram.__version__)"
```

### 2. OpenAI Integration Issues

#### Issue: "OpenAI API error: 401 Unauthorized"
**Cause**: Invalid or expired API key

**Solution**:
```bash
# Check API key format (should start with sk-)
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Get new key from https://platform.openai.com/api-keys
```

#### Issue: "Rate limit exceeded"
**Cause**: Too many requests to OpenAI API

**Solution**:
```python
# Implement exponential backoff
import time
import openai

def call_openai_with_retry(max_retries=3):
    for i in range(max_retries):
        try:
            return openai.ChatCompletion.create(...)
        except openai.error.RateLimitError:
            wait_time = (2 ** i) * 1
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

### 3. Database Connection Issues

#### Issue: "Could not connect to PostgreSQL"
**Cause**: Database not running or wrong credentials

**Solution**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql postgresql://postgres:password@localhost:5432/motebai

# Check connection string in .env
echo $DB_URL

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Issue: "Redis connection refused"
**Cause**: Redis server not running

**Solution**:
```bash
# Check Redis status
sudo systemctl status redis

# Start Redis
sudo systemctl start redis

# Test connection
redis-cli ping
# Should return: PONG
```

#### Issue: "Neo4j authentication failed"
**Cause**: Wrong username/password

**Solution**:
```bash
# Reset Neo4j password
docker exec -it neo4j cypher-shell
# Or change in NEO4J_AUTH environment variable

# Test connection
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
driver.verify_connectivity()
```

### 4. GitHub Integration Issues

#### Issue: "GitHub API rate limit exceeded"
**Cause**: Too many API calls

**Solution**:
```bash
# Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit

# Implement caching
# Use conditional requests with ETag headers
# Increase polling interval
```

#### Issue: "GitHub token invalid"
**Cause**: Token expired or revoked

**Solution**:
```bash
# Test token
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Generate new token at https://github.com/settings/tokens
# Update .env file with new token
```

### 5. Performance Issues

#### Issue: "Bot responding slowly"
**Cause**: High load or resource constraints

**Solution**:
```bash
# Check system resources
htop  # or top

# Check memory usage
free -h

# Check disk space
df -h

# Monitor bot performance
python scripts/monitoring/metrics.py

# Scale horizontally
docker-compose up -d --scale telegram-bot=3
```

#### Issue: "Database queries slow"
**Cause**: Missing indexes or inefficient queries

**Solution**:
```sql
-- Add indexes
CREATE INDEX idx_user_id ON messages(user_id);
CREATE INDEX idx_created_at ON messages(created_at);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM messages WHERE user_id = 123;

-- Vacuum database
VACUUM ANALYZE;
```

### 6. Docker Issues

#### Issue: "Container keeps restarting"
**Cause**: Application crash or configuration error

**Solution**:
```bash
# Check logs
docker logs telegram-bot --tail 100

# Check container status
docker ps -a

# Inspect container
docker inspect telegram-bot

# Restart with fresh state
docker-compose down
docker-compose up --build
```

#### Issue: "Cannot connect to Docker daemon"
**Cause**: Docker not running or permission issue

**Solution**:
```bash
# Start Docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker run hello-world
```

### 7. Security Issues

#### Issue: "Rate limiter not working"
**Cause**: Configuration error

**Solution**:
```python
# Verify rate limiter is enabled
from scripts.security.rate_limiter import TokenBucketRateLimiter

limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)

# Test
for i in range(15):
    print(f"Request {i+1}: {limiter.is_allowed('test_user')}")
```

#### Issue: "Security headers not applied"
**Cause**: Middleware not configured

**Solution**:
```python
# Ensure middleware is added
from scripts.security.security_headers import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=True
)
```

### 8. Testing Issues

#### Issue: "Tests failing with 'Module not found'"
**Cause**: Import path issues

**Solution**:
```bash
# Run tests from project root
cd /path/to/Top-TieR-Global-HUB-AI

# Set PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Run tests
pytest tests/ -v
```

#### Issue: "Integration tests skipped"
**Cause**: API keys not configured

**Solution**:
```bash
# Set environment variables for testing
export OPENAI_API_KEY=sk-test-key
export TELEGRAM_BOT_TOKEN=test-token

# Run integration tests
pytest tests/integration/ -v -m integration
```

### 9. Logging Issues

#### Issue: "Logs not appearing"
**Cause**: Log level too high or wrong configuration

**Solution**:
```python
# Set log level to DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in .env
LOG_LEVEL=DEBUG

# Check log file location
tail -f /var/log/telegram-bot/app.log
```

#### Issue: "Log file too large"
**Cause**: No log rotation

**Solution**:
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/telegram-bot

# Add:
# /var/log/telegram-bot/*.log {
#     daily
#     rotate 7
#     compress
#     delaycompress
#     notifempty
# }
```

### 10. Health Check Failures

#### Issue: "Health check endpoint returns 500"
**Cause**: Service dependency failure

**Solution**:
```bash
# Check individual services
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/status

# Check service dependencies
python -c "
import asyncio
from scripts.monitoring.health_check import HealthCheck

async def test():
    health = HealthCheck()
    report = await health.run_all_checks()
    print(report)

asyncio.run(test())
"
```

## Debugging Tools

### 1. Enable Debug Mode
```python
# In run_telegram_bot.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Interactive Debugging
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### 3. Performance Profiling
```bash
# Profile with cProfile
python -m cProfile -o profile.stats scripts/run_telegram_bot.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

### 4. Memory Profiling
```bash
# Install memory_profiler
pip install memory_profiler

# Profile memory
python -m memory_profiler scripts/run_telegram_bot.py
```

## Emergency Procedures

### Service Down
```bash
# 1. Check status
systemctl status telegram-bot

# 2. Check logs
journalctl -u telegram-bot -n 100

# 3. Restart service
systemctl restart telegram-bot

# 4. If persistent, rollback
git checkout <previous-working-commit>
systemctl restart telegram-bot
```

### Database Corruption
```bash
# 1. Stop all services
systemctl stop telegram-bot

# 2. Backup current state
pg_dump $DB_URL > backup_$(date +%Y%m%d).sql

# 3. Restore from backup
psql $DB_URL < backup_latest.sql

# 4. Restart services
systemctl start telegram-bot
```

## Getting Help

### Collect Diagnostic Information
```bash
# System info
uname -a
python --version
docker --version

# Service status
systemctl status telegram-bot

# Recent logs
journalctl -u telegram-bot --since "1 hour ago"

# Configuration
cat .env | grep -v PASSWORD | grep -v TOKEN

# Resource usage
df -h
free -h
docker stats --no-stream
```

### Report Issues
1. Check existing issues: https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/issues
2. Create new issue with:
   - Problem description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Relevant logs
   - Configuration (sanitized)

## Additional Resources

- [Configuration Guide](CONFIGURATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Security Guide](SECURITY.md)
