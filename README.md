# Top-TieR-Global-HUB-AI

**Veritas Nexus v2** — منصة OSINT مفتوحة المصدر للتجارب التعليمية: تجمع البيانات من مصادر متعددة، تخزنها في Neo4j، توفر REST API (FastAPI)، وكيل ذكي (LangChain Agent)، وواجهة بصرية (Cytoscape.js).

[![CI](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/CI.yml/badge.svg)](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/CI.yml)
[![Post-merge Validation (Readonly)](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/post-merge-validation.yml/badge.svg?branch=main)](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/post-merge-validation.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-modern-green.svg)](https://fastapi.tiangolo.com)

## Project Objectives

Top-TieR-Global-HUB-AI is an educational OSINT (Open Source Intelligence) platform designed to:

🎯 **Primary Goals:**
- **Data Collection**: Aggregate information from multiple open sources for intelligence analysis
- **Graph Analysis**: Store and visualize relationships using Neo4j graph database
- **API Access**: Provide modern REST API endpoints for programmatic access
- **Intelligence Processing**: Utilize AI agents for automated analysis and insights
- **Educational Focus**: Serve as a learning platform for OSINT methodologies and techniques

🔧 **Technical Objectives:**
- Modern microservices architecture with Docker containerization
- Scalable data processing with async Python and FastAPI
- Real-time graph visualization with Cytoscape.js
- Comprehensive testing and CI/CD pipeline
- Security-first design with proper authentication and data handling

⚖️ **Ethical Considerations:**
- Educational and research purposes only
- Compliance with data protection regulations
- Respect for source terms of service
- Transparent data handling and retention policies

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Git
- Docker and Docker Compose (recommended for full system deployment)
- curl and jq (for OSINT query scripts)

### Method 1: Docker Compose Deployment (Recommended)

The fastest way to get the complete system running with all services:

```bash
# Clone the repository
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
cd Top-TieR-Global-HUB-AI

# Start all services with Docker Compose
docker compose up -d

# Check service health
docker compose ps

# Access the application
# API: http://localhost:8000
# Interactive Docs: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474 (user: neo4j, password: password)
```

Services included in Docker Compose:
- **API Server**: FastAPI application on port 8000
- **PostgreSQL**: Primary database on port 5432
- **Redis**: Caching layer on port 6379
- **Neo4j**: Graph database on ports 7474 (browser) and 7687 (bolt)

### Method 2: Local Development Setup

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
   python -m api_server
   
   # Or with uvicorn directly
   uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application:**
   - API: http://localhost:8000
   - Interactive API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## OSINT Query Scripts

The repository includes powerful command-line tools for OSINT data collection and analysis:

### snap_osint_query.sh

A comprehensive OSINT query tool that provides quick access to the platform's capabilities:

```bash
# Make script executable
chmod +x scripts/snap_osint_query.sh

# Check API server status
./scripts/snap_osint_query.sh status

# Search for domain information
./scripts/snap_osint_query.sh search "domain:example.com"

# Analyze an IP address
./scripts/snap_osint_query.sh analyze "192.168.1.1"

# Export results in different formats
./scripts/snap_osint_query.sh export json
./scripts/snap_osint_query.sh export csv

# Run comprehensive health check
./scripts/snap_osint_query.sh health

# Get help and see all options
./scripts/snap_osint_query.sh --help
```

### Script Features:
- **Multi-format output**: JSON, CSV, and graph exports
- **Comprehensive logging**: Detailed logs with timestamps and color coding
- **Error handling**: Robust error detection and recovery
- **Health monitoring**: Check status of all system components
- **Configurable**: Set API endpoints and output directories via environment variables

### Script Examples:

```bash
# Set custom API endpoint
export API_BASE_URL="https://your-api.example.com"
./scripts/snap_osint_query.sh status

# Use custom output directory
./scripts/snap_osint_query.sh --output ./my_results search "target:investigation"

# Enable verbose logging
./scripts/snap_osint_query.sh --verbose analyze "email@example.com"
```

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
| `NEO4J_AUTH_USER` | `neo4j` | Neo4j username (for Docker) |
| `NEO4J_AUTH_PASSWORD` | `password` | Neo4j password (for Docker) |

**Note**: For enhanced security, Neo4j credentials should be stored in `/opt/veritas/.env.neo4j` outside the Git repository. See `.env.neo4j.example` for the format.

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

#### Option 1: Docker Compose (Full Stack)
```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes (clean reset)
docker compose down -v
```

#### Option 2: Single Container
```bash
# Build container
docker build -t top-tier-hub-ai .

# Run container
docker run -p 8000:8000 --env-file .env top-tier-hub-ai

# Run with volume for development
docker run -p 8000:8000 -v $(pwd):/app top-tier-hub-ai
```

### Local Development with Docker Services

For local development with external databases:

```bash
# Start only the databases
docker compose up postgres redis neo4j -d

# Set environment variables to connect to Docker services
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/app_db"
export REDIS_URL="redis://localhost:6379/0"
export NEO4J_URL="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# Run the API server locally
python -m api_server
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
- Post-merge Validation (Readonly): Safe, read-only health checks post-merge and on-demand
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
