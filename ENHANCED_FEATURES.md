# Enhanced Features Documentation

This document describes the new performance, cost optimization, and observability features added to Top-TieR Global HUB AI.

## 🚀 New Features

### 1. Redis Cache Middleware (`core/cache_middleware.py`)
- **Cache-aside pattern** with intelligent TTL management
- **OSINT queries**: 30 minutes TTL
- **General queries**: 10 minutes TTL
- **Cache keys**: Based on provider/model/normalized-text/scope
- **Graceful fallback** when Redis unavailable

```python
from core.cache_middleware import cache

# Cache automatically used in /query endpoint
# Manual usage:
cached = cache.get("openai", "gpt-3.5-turbo", "query text", "osint")
cache.set("openai", "gpt-3.5-turbo", "query text", response_data, "osint")
```

### 2. Smart Model Router (`core/model_router.py`)
- **Automatic model selection** based on task type and token count
- **3 model sizes**: Small (< 2k tokens), Medium (2k-6k), Large (> 6k)
- **7 task types**: extraction, classification, normalization, summary, report, osint_query, conversation
- **Cost optimization** with model downgrading for budget limits
- **Map-reduce detection** for large inputs (> 6k tokens)

```python
from core.model_router import model_router

routing = model_router.route_model(
    query="extract phone numbers",
    scope=["general"],
    cost_limit=5.0  # Optional cost ceiling
)
# Returns: model, task_type, estimated_tokens, estimated_cost, etc.
```

### 3. Comprehensive Metrics (`core/metrics.py`)
- **Request logging** with req_id, user, model, tokens, duration, cache_hit
- **Daily aggregation** and real-time counters
- **Prometheus-compatible** metrics endpoint
- **Dashboard data** for monitoring

```python
from core.metrics import metrics

# Automatic logging in API endpoints
metrics.log_request(
    req_id="abc123",
    model="gpt-3.5-turbo",
    tokens=150,
    duration=1.2,
    cache_hit=False
)
```

### 4. Rate Limiting (`core/rate_limiter.py`)
- **Redis sliding window**: 30 requests/minute per user/IP
- **Cost ceiling**: $10/hour protection
- **Client identification**: User ID or IP address
- **Graceful handling** with proper HTTP status codes

```python
from core.rate_limiter import rate_limit_middleware

# Automatic rate limiting in endpoints
rate_info = rate_limit_middleware(request, estimated_cost=0.05)
```

## 📡 New API Endpoints

### Enhanced Query Endpoint
```bash
POST /query
{
  "query": "extract phone numbers from this text",
  "scope": ["osint"],
  "trace": true,
  "model": null  # Auto-selected based on task
}
```

### Metrics Endpoints
```bash
# JSON format
GET /metrics

# Prometheus format
GET /metrics?format=prometheus

# Dashboard data
GET /metrics/dashboard

# Client rate limit stats
GET /stats
```

### Background Jobs
```bash
# Submit job
POST /job
{
  "job": "heavy-task",
  "parameters": {"param": "value"}
}

# Check status
GET /job/{job_id}
```

## 🐳 Docker Configuration

### Environment Variables
```yaml
environment:
  - REDIS_HOST=redis
  - CACHE_TTL_DEFAULT=600      # 10 minutes
  - CACHE_TTL_OSINT=1800       # 30 minutes
  - RATE_LIMIT_RPM=30          # 30 requests/minute
  - COST_CEILING=10.0          # $10/hour
```

### Redis Service
```yaml
redis:
  image: redis:7-alpine
  restart: unless-stopped
  ports:
    - "6379:6379"
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_cache_middleware.py -v
python -m pytest tests/test_model_router.py -v
python -m pytest tests/test_api_server.py -v
```

### Manual Testing
```bash
# Start services
docker compose up -d

# Test Redis cache
docker exec top-tier-global-hub-ai-redis-1 redis-cli PING

# Test model routing
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"test","model":null}'

# Test rate limiting (run 35 times)
for i in {1..35}; do curl http://localhost:8000/health; done

# Test metrics
curl http://localhost:8000/metrics
curl "http://localhost:8000/metrics?format=prometheus"

# Test jobs
curl -X POST http://localhost:8000/job \
  -H "Content-Type: application/json" \
  -d '{"job":"heavy-task"}'
```

## 📊 Performance Expectations

- **40-70% faster responses** for repeated queries (caching)
- **30-50% cost reduction** through optimized model routing
- **Complete observability** with request metrics and monitoring
- **Rate limiting protection** against abuse
- **Graceful degradation** when Redis unavailable

## 🔧 CI/CD Improvements

- **QEMU and Docker Buildx** setup for multi-platform builds
- **Python linting** with flake8 and black
- **YAML linting** with yamllint
- **Fixed Docker build** references and health checks

## 🛡️ Backward Compatibility

All enhancements are **non-breaking**:
- Existing endpoints continue to work
- New features gracefully degrade when dependencies unavailable
- Original `/gpt` endpoint unchanged
- Health checks enhanced but maintain compatibility

## 📝 Configuration Examples

### Production Setup
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  api:
    environment:
      - REDIS_HOST=redis-cluster.production.com
      - CACHE_TTL_OSINT=3600        # 1 hour for production
      - RATE_LIMIT_RPM=100          # Higher limits for production
      - COST_CEILING=50.0           # Higher ceiling for production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Development Setup
```bash
# .env file
REDIS_HOST=localhost
CACHE_TTL_DEFAULT=300
CACHE_TTL_OSINT=900
RATE_LIMIT_RPM=60
COST_CEILING=5.0
DEBUG=true
```

## 🚨 Monitoring

### Key Metrics to Monitor
- Cache hit rate (target: > 60%)
- Average response time (target: < 2s)
- Rate limit violations
- Cost per request
- Model distribution

### Alerts
- Cache hit rate < 40%
- Response time > 5s
- Error rate > 5%
- Cost ceiling breaches
- Redis connection failures

---

For questions or issues, please check the test suite or create an issue in the repository.