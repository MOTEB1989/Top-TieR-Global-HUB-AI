# Top-TieR-Global-HUB-AI Development Instructions

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Repository Overview

Top-TieR-Global-HUB-AI is a Python-based FastAPI OSINT (Open Source Intelligence) platform. It provides REST API endpoints for data analysis and includes containerized deployment options.

**Core Technologies:**
- Python 3.11+ (works with 3.12)
- FastAPI for REST API
- Docker for containerization
- PostgreSQL/Neo4j for databases (optional)
- GitHub Actions for CI/CD

## Quick Setup and Validation

### Bootstrap Dependencies and Environment
```bash
# Verify Python version (3.11+ required, 3.12 confirmed working)
python --version

# Install core dependencies - takes ~11 seconds, NEVER CANCEL
pip install -r requirements.txt

# Install testing dependencies - takes ~5 seconds  
pip install pytest pytest-asyncio httpx

# Install code quality tools - takes ~8 seconds
pip install black isort flake8 ruff
```

### Build and Test Process
```bash
# Test API server import (instant validation)
python -c "import api_server; print('✅ API server imports successfully')"

# Run all tests - takes <1 second, NEVER CANCEL. Set timeout to 30+ seconds.
pytest -v

# Run comprehensive API functionality test
python -c "
from api_server import app
from fastapi.testclient import TestClient
client = TestClient(app)
assert client.get('/').status_code == 200
assert client.get('/health').status_code == 200
assert client.get('/api').status_code == 200
assert client.get('/docs').status_code == 200
print('✅ All API endpoints working')
"
```

### Run the Application
```bash
# Method 1: Direct Python execution
python api_server.py

# Method 2: Via uvicorn (recommended for development)
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# Method 3: Production mode
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

**Application URLs:**
- API Root: http://localhost:8000/
- Health Check: http://localhost:8000/health
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Code Quality and CI Validation

**ALWAYS run these before committing changes:**

```bash
# Code formatting - takes <1 second
black --check --diff .
black .  # Auto-fix formatting

# Import sorting - takes <1 second
isort --check-only --diff .
isort .  # Auto-fix imports

# Linting with flake8 - takes <1 second
flake8 .  # Reports 2 minor style issues (acceptable)

# Fast linting with ruff - takes <1 second
ruff check .
```

**Known acceptable linting issues:**
- `api_server.py:71:80: E501 line too long (93 > 79 characters)` - Single line, acceptable
- `utils/graph_ingestor.py:1:1: W391 blank line at end of file` - Minor formatting issue

## Container Deployment

**Docker build validation:**
```bash
# Note: Docker build fails in restricted environments due to SSL/network issues
# This is expected behavior in sandboxed/corporate environments
docker build -t top-tier-hub-ai .
```

**Expected Docker behavior:**
- ✅ In normal environments: Build succeeds in ~2-3 minutes
- ❌ In restricted environments: Fails with SSL certificate errors
- This is NOT a code issue - it's environmental

**Docker runtime (when build succeeds):**
```bash
# Run container
docker run -p 8000:8000 --env-file .env top-tier-hub-ai

# Health check available at: http://localhost:8000/health
```

## Environment Configuration

```bash
# Copy and customize environment file
cp .env.example .env
# Edit .env with your preferred settings
```

**Critical environment variables:**
- `API_HOST=0.0.0.0` (for container deployment)
- `API_PORT=8000` (default port)
- `DEBUG=false` (production) / `DEBUG=true` (development)
- `ENVIRONMENT=production|development|staging`

## Validation Scenarios

**After making changes, ALWAYS test these scenarios:**

1. **API Import Test**: `python -c "import api_server; print('OK')"`
2. **Health Check**: `curl http://localhost:8000/health`
3. **API Documentation**: Verify `/docs` endpoint loads (may show blank in restricted environments due to CDN blocking - this is expected)
4. **Full Test Suite**: `pytest -v` - all tests must pass
5. **Code Quality**: Run `black .`, `isort .`, and `flake8 .`

## Timing Expectations and Timeouts

**NEVER CANCEL these operations - they complete quickly:**

| Operation | Time | Timeout Setting |
|-----------|------|-----------------|
| `pip install -r requirements.txt` | ~11 seconds | 60+ seconds |
| `pip install pytest pytest-asyncio httpx` | ~5 seconds | 30+ seconds |
| `pip install black isort flake8 ruff` | ~8 seconds | 30+ seconds |
| `pytest -v` | <1 second | 30+ seconds |
| `black --check .` | <1 second | 30+ seconds |
| `isort --check .` | <1 second | 30+ seconds |
| `flake8 .` | <1 second | 30+ seconds |
| `ruff check .` | <1 second | 30+ seconds |
| API server startup | 1-2 seconds | 30+ seconds |

## File Structure

```
/
├── api_server.py          # Main FastAPI application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── .env.example          # Environment template
├── tests/                # Test directory
│   └── test_policy_load.py  # Policy validation tests
├── .github/workflows/    # CI/CD pipelines
│   ├── CI.yml           # Main CI pipeline
│   └── auto-assign-reviewer.yml
├── utils/               # Utility modules
│   └── graph_ingestor.py
├── scripts/             # Setup and utility scripts
├── policies/            # Policy configurations
└── docs/               # Documentation
```

## CI/CD Integration

**GitHub Actions workflow validates:**
- Python 3.11 and 3.12 compatibility
- Dependency installation
- Code quality (ruff, black, isort, flake8)
- API server functionality
- PostgreSQL integration (when DATABASE_URL provided)

**The CI workflow runs these key steps:**
1. Install dependencies
2. Run linting and formatting checks
3. Test API server imports and basic functionality
4. Database connection tests (when configured)

## Common Tasks

### Adding New Dependencies
```bash
# Add to requirements.txt, then:
pip install -r requirements.txt
# Test that API still imports:
python -c "import api_server; print('OK')"
```

### Running Development Server
```bash
# Auto-reload on changes:
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Testing New Endpoints
```bash
# Use FastAPI TestClient for programmatic testing:
python -c "
from fastapi.testclient import TestClient
from api_server import app
client = TestClient(app)
# Test your new endpoint here
response = client.get('/your-endpoint')
print(response.status_code, response.json())
"
```

## Troubleshooting

**Common issues and solutions:**

1. **Import errors**: Run `pip install -r requirements.txt`
2. **Port already in use**: Kill existing uvicorn processes with `pkill -f uvicorn`
3. **Docker build fails**: Expected in restricted environments - deploy in normal environment
4. **API docs show blank**: CDN resources blocked - functionality still works, use `/redoc` or test via `curl`
5. **SSL certificate errors**: Expected in sandboxed environments - not a code issue

## Security and Best Practices

- Always use environment variables for sensitive configuration
- Run with non-root user in production (Docker handles this)
- Enable CORS settings via environment variables
- Use proper rate limiting settings in production
- Keep dependencies updated via `pip install -r requirements.txt`

---

**Remember: These instructions are exhaustively tested. If something doesn't work as described, check your environment configuration first.**