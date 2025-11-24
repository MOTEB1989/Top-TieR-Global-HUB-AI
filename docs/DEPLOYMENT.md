# Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Development Deployment](#development-deployment)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Kubernetes Deployment](#kubernetes-deployment)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.11 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Memory**: Minimum 2GB RAM, Recommended 4GB+
- **Storage**: Minimum 10GB available space

### Required Accounts & Credentials
- Telegram Bot Token (from @BotFather)
- OpenAI API Key
- GitHub Personal Access Token
- Database credentials (if using external databases)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
cd Top-TieR-Global-HUB-AI
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# API Keys
OPENAI_API_KEY=sk-your-openai-key
TELEGRAM_BOT_TOKEN=your-bot-token
GITHUB_TOKEN=your-github-token
GITHUB_REPO=MOTEB1989/Top-TieR-Global-HUB-AI

# Telegram Configuration
TELEGRAM_ALLOWLIST=user_id_1,user_id_2

# Database URLs
DB_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_AUTH=neo4j/password
```

## Development Deployment

### Quick Start
```bash
# Activate virtual environment
source venv/bin/activate

# Run the bot
python scripts/run_telegram_bot.py
```

### With Auto-Reload
```bash
# Install watchdog for auto-reload
pip install watchdog

# Run with auto-reload
watchmedo auto-restart --patterns="*.py" --recursive python scripts/run_telegram_bot.py
```

### Development with Docker Compose
```bash
# Start all services (bot + databases)
docker-compose up -d

# View logs
docker-compose logs -f telegram-bot

# Stop services
docker-compose down
```

## Staging Deployment

### 1. Set Up Staging Environment
```bash
# Create staging configuration
cp .env .env.staging
# Edit .env.staging with staging credentials
```

### 2. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/integration/ -v  # Integration tests
pytest tests/e2e/ -v          # End-to-end tests
pytest tests/load/ -v         # Load tests
pytest tests/security/ -v     # Security tests
```

### 3. Deploy to Staging
```bash
# Using Docker Compose
docker-compose -f docker-compose.test.yml up -d

# Verify deployment
curl http://staging-server:8000/health
```

## Production Deployment

### Option 1: Direct Server Deployment

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip -y

# Create application user
sudo useradd -m -s /bin/bash telegram-bot
sudo su - telegram-bot
```

#### 2. Application Setup
```bash
# Clone and setup
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
cd Top-TieR-Global-HUB-AI
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production credentials (use secure editor)
```

#### 3. Create Systemd Service
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=telegram-bot
WorkingDirectory=/home/telegram-bot/Top-TieR-Global-HUB-AI
Environment="PATH=/home/telegram-bot/Top-TieR-Global-HUB-AI/venv/bin"
ExecStart=/home/telegram-bot/Top-TieR-Global-HUB-AI/venv/bin/python scripts/run_telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

### Option 2: Docker Deployment

#### 1. Build Docker Image
```bash
# Build image
docker build -t top-tier-telegram-bot:latest -f Dockerfile.telegram .

# Tag for registry (optional)
docker tag top-tier-telegram-bot:latest your-registry/top-tier-telegram-bot:v1.0.0
```

#### 2. Deploy with Docker Compose
```bash
# Create production docker-compose file
cat > docker-compose.prod.yml <<EOF
version: '3.8'
services:
  telegram-bot:
    image: top-tier-telegram-bot:latest
    restart: always
    env_file: .env
    depends_on:
      - postgres
      - redis
      - neo4j
    networks:
      - prod-network

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: \${DB_NAME}
      POSTGRES_USER: \${DB_USER}
      POSTGRES_PASSWORD: \${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - prod-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - prod-network

  neo4j:
    image: neo4j:5-community
    restart: always
    environment:
      NEO4J_AUTH: \${NEO4J_AUTH}
    volumes:
      - neo4j-data:/data
    networks:
      - prod-network

volumes:
  postgres-data:
  redis-data:
  neo4j-data:

networks:
  prod-network:
    driver: bridge
EOF

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Kubernetes Deployment

#### 1. Create Kubernetes Manifests
```bash
# Create namespace
kubectl create namespace telegram-bot

# Create secret for environment variables
kubectl create secret generic telegram-bot-secrets \
  --from-literal=OPENAI_API_KEY=your-key \
  --from-literal=TELEGRAM_BOT_TOKEN=your-token \
  --from-literal=GITHUB_TOKEN=your-token \
  -n telegram-bot

# Apply manifests (see k8s/ directory)
kubectl apply -f k8s/ -n telegram-bot
```

#### 2. Verify Deployment
```bash
# Check pods
kubectl get pods -n telegram-bot

# Check logs
kubectl logs -f deployment/telegram-bot -n telegram-bot

# Check service
kubectl get svc -n telegram-bot
```

## Verification

### 1. Health Checks
```bash
# Check bot is running
curl http://localhost:8000/health

# Check service health
curl http://localhost:8000/health/status
```

### 2. Test Bot Functionality
```bash
# Send test message to bot on Telegram
/start

# Check system status
/status

# Test AI integration (if configured)
/ai Hello, are you working?
```

### 3. Monitor Logs
```bash
# Docker
docker logs -f telegram-bot

# Systemd
sudo journalctl -u telegram-bot -f

# Kubernetes
kubectl logs -f deployment/telegram-bot -n telegram-bot
```

### 4. Check Metrics
```bash
# Prometheus metrics endpoint
curl http://localhost:9090/metrics
```

## Post-Deployment

### 1. Set Up Monitoring
```bash
# Configure Grafana dashboard
# Import dashboard from grafana/telegram-bot-dashboard.json

# Configure alerts
# Edit config/monitoring.yaml
```

### 2. Set Up Backups
```bash
# Database backup script
cat > /home/telegram-bot/backup.sh <<EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
pg_dump \$DB_URL > /backups/db_\$DATE.sql
gzip /backups/db_\$DATE.sql
# Keep only last 7 days
find /backups -name "db_*.sql.gz" -mtime +7 -delete
EOF

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/telegram-bot/backup.sh
```

### 3. Configure Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/telegram-bot
```

```
/var/log/telegram-bot/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 telegram-bot telegram-bot
    sharedscripts
    postrotate
        systemctl reload telegram-bot
    endscript
}
```

## Scaling

### Horizontal Scaling
```bash
# Docker Compose
docker-compose up -d --scale telegram-bot=3

# Kubernetes
kubectl scale deployment telegram-bot --replicas=3 -n telegram-bot
```

### Load Balancer Configuration
```nginx
# Nginx configuration
upstream telegram_bot {
    least_conn;
    server bot1:8000;
    server bot2:8000;
    server bot3:8000;
}

server {
    listen 80;
    server_name bot.example.com;

    location / {
        proxy_pass http://telegram_bot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Rollback Procedures

### Docker Deployment
```bash
# Tag current version
docker tag telegram-bot:latest telegram-bot:backup

# Rollback to previous version
docker-compose down
docker pull telegram-bot:previous-version
docker-compose up -d
```

### Kubernetes Deployment
```bash
# Rollback to previous revision
kubectl rollout undo deployment/telegram-bot -n telegram-bot

# Check rollout status
kubectl rollout status deployment/telegram-bot -n telegram-bot
```

## Security Hardening

### 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. SSL/TLS Configuration
```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d bot.example.com
```

### 3. Secure Secrets
```bash
# Use encrypted secrets
ansible-vault encrypt .env

# Or use cloud secret managers
# AWS Secrets Manager, Google Secret Manager, HashiCorp Vault
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Additional Resources

- [Configuration Guide](CONFIGURATION.md)
- [API Documentation](API.md)
- [Security Best Practices](SECURITY.md)
- [Architecture Overview](ARCHITECTURE.md)
