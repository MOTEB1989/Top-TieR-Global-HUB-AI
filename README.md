# Top-TieR-Global-HUB-AI

**Veritas Nexus v2** — منصة OSINT مفتوحة المصدر للتجارب التعليمية: تجمع البيانات من مصادر متعددة، تخزنها في Neo4j، توفر REST API (FastAPI)، وكيل ذكي (LangChain Agent)، وواجهة بصرية (Cytoscape.js).

[![CI](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/CI.yml/badge.svg)](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/CI.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-modern-green.svg)](https://fastapi.tiangolo.com)

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- (Optional) Docker for containerized deployment

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
   cd Top-TieR-Global-HUB-AI
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the API server:**
   ```bash
   # Development mode with auto-reload
   python api_server.py
   
   # Or with uvicorn directly
   uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application:**
   - API: http://localhost:8000
   - Interactive API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Environment Variables

The application supports configuration through environment variables. Copy `.env.example` to `.env` and modify as needed:

### Core API Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Host to bind the API server |
| `API_PORT` | `8000` | Port for the API server |
| `DEBUG` | `false` | Enable debug mode with auto-reload |

### Application Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Top-TieR-Global-HUB-AI` | Application name |
| `APP_VERSION` | `2.0.0` | Application version |
| `ENVIRONMENT` | `production` | Environment (development/staging/production) |

### Database Configuration (Optional)
| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@localhost/db` | Primary database connection |
| `NEO4J_URL` | `bolt://localhost:7687` | Neo4j graph database URL |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |

### Security Settings
| Variable | Example | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `your-secret-key` | Application secret key |
| `JWT_SECRET` | `jwt-secret` | JWT token secret |

### External API Integration
| Variable | Example | Description |
|----------|---------|-------------|
| `OSINT_API_KEY` | `your-api-key` | OSINT data source API key |
| `SOCIAL_MEDIA_API_KEY` | `api-key` | Social media platforms API key |

### Performance & Scaling
| Variable | Default | Description |
|----------|---------|-------------|
| `WORKER_PROCESSES` | `4` | Number of worker processes |
| `WORKER_TIMEOUT` | `30` | Worker timeout in seconds |
| `RATE_LIMIT_REQUESTS` | `100` | Rate limit: requests per window |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for caching |
| `CACHE_TTL` | `300` | Cache time-to-live in seconds |

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run tests with coverage
pytest --cov=api_server
```

### Code Quality
```bash
# Install development dependencies
pip install black isort flake8

# Format code
black .
isort .

# Check code quality
flake8 .
```

### Docker Development
```bash
# Build container
docker build -t top-tier-hub-ai .

# Run container
docker run -p 8000:8000 --env-file .env top-tier-hub-ai

# Or use docker-compose (if available)
docker-compose up --build
```

## Architecture

### Components
- **API Server**: FastAPI-based REST API with automatic documentation
- **Veritas Console**: Advanced OSINT data collection and analysis engine
- **Graph Database**: Neo4j for relationship mapping and data storage
- **Web Interface**: Modern web UI for data visualization and interaction

### API Endpoints
- `GET /` - Root endpoint with application info
- `GET /api` - Legacy API endpoint for backward compatibility  
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Deployment

### Production Environment
1. Set `ENVIRONMENT=production` in your `.env` file
2. Configure proper database connections
3. Set up reverse proxy (nginx recommended)
4. Use process manager (systemd, supervisor, or docker)
5. Enable HTTPS/SSL certificates

### Container Deployment
The application includes a Dockerfile for containerized deployment:
```bash
docker build -t your-registry/top-tier-hub-ai .
docker push your-registry/top-tier-hub-ai
```

### CI/CD
The repository includes GitHub Actions workflows for:
- Continuous Integration testing
- Automated security scanning
- Container registry publishing
- Immutable release creation

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install dev dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

## Security

- All dependencies are regularly updated for security
- Environment variables are used for sensitive configuration
- Rate limiting is implemented to prevent abuse
- CORS settings can be configured for cross-origin requests
- Support for HTTPS/SSL in production environments

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 Documentation: Check the `/docs` endpoint when running the server
- 🐛 Issues: [GitHub Issues](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/discussions)

---

**Note**: This is an educational OSINT platform. Please use responsibly and in compliance with applicable laws and regulations.
