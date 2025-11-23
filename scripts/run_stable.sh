#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# run_stable.sh - Stable stack runner (Redis + SearXNG + Qdrant + Phi-3 + Streamlit)
#
# - Writes docker-compose.yml, .env, README.md, and src/web/app.py to the expected
#   stable templates (backing up existing files with a .bak suffix).
# - Starts the stack with docker compose and prints local/LAN access hints.
###############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $*${NC}"; }
log_ok()   { echo -e "${GREEN}✅ $*${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_error(){ echo -e "${RED}❌ $*${NC}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

log_info "Repository: $REPO_ROOT"
log_info "🚀 Preparing stable stack (Redis + SearXNG + Qdrant + Phi-3 + Streamlit)"

###############################################################################
# 0) Docker / docker compose availability
###############################################################################
if ! command -v docker >/dev/null 2>&1; then
  log_error "Docker is not installed. Please install Docker then re-run."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  log_error "Neither 'docker compose' nor 'docker-compose' is available."
  exit 1
fi
log_ok "Using compose command: ${COMPOSE_CMD[*]}"

###############################################################################
backup_if_exists() {
  local file="$1"
  if [[ -f "$file" ]]; then
    cp "$file" "$file.bak"
    log_warn "Backed up existing $file to $file.bak"
  fi
}

write_file() {
  local file="$1"
  local content="$2"
  backup_if_exists "$file"
  printf '%s\n' "$content" > "$file"
  log_ok "Wrote $file"
}

###############################################################################
# 1) docker-compose.yml (stable template)
###############################################################################
COMPOSE_TEMPLATE="version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports: ['6379:6379']
    volumes: [redis_data:/data]
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 3

  searxng:
    image: searxng/searxng:latest
    ports: ['8080:8080']
    environment: [SEARXNG_BASE_URL=http://localhost:8080]
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8080']
      interval: 30s
      timeout: 10s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports: ['6333:6333']
    volumes: [qdrant_data:/qdrant/storage]
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:6333/health']
      interval: 30s
      timeout: 10s
      retries: 5

  phi3:
    image: ghcr.io/ggerganov/llama.cpp:server
    ports: ['8082:8082']
    environment: [MODEL=phi-3-mini-4k.gguf]
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8082/health']
      interval: 60s
      timeout: 30s
      retries: 10

  streamlit-ui:
    image: python:3.11-slim
    ports: ['8501:8501']
    volumes:
      - ./src:/app/src
      - ./.env:/app/.env
    working_dir: /app
    command: bash -c "pip install --no-cache-dir streamlit redis requests && streamlit run src/web/app.py --server.address 0.0.0.0 --server.port 8501"
    depends_on:
      redis:
        condition: service_healthy
      phi3:
        condition: service_healthy
    restart: unless-stopped

volumes:
  redis_data:
  qdrant_data:
"

write_file "$REPO_ROOT/docker-compose.yml" "$COMPOSE_TEMPLATE"

###############################################################################
# 2) .env (stable defaults)
###############################################################################
ENV_TEMPLATE="# Stable Stack Config
REDIS_URL=redis://redis:6379/1
PHI3_URL=http://phi3:8082
QDRANT_URL=http://qdrant:6333
SEARXNG_URL=http://searxng:8080
"
write_file "$REPO_ROOT/.env" "$ENV_TEMPLATE"

###############################################################################
# 3) Streamlit app
###############################################################################
mkdir -p "$REPO_ROOT/src/web"
APP_TEMPLATE="import redis
import streamlit as st

redis_client = redis.Redis(host='redis', port=6379, db=1)

st.title('Top-TieR Global HUB AI')
st.write('Welcome to the Streamlit UI!')
"
write_file "$REPO_ROOT/src/web/app.py" "$APP_TEMPLATE"

###############################################################################
# 4) README (stable stack)
###############################################################################
README_TEMPLATE="# Top-TieR Global HUB AI 🚀

**Stable Stack - Streamlit + SearXNG + Qdrant + Phi-3**

## Quick Start
\`\`\`bash
./scripts/run_stable.sh
\`\`\`

### Access from iPhone / LAN
http://<YOUR-IP>:8501

## Services
Service | Port | Access
--- | --- | ---
Streamlit UI | 8501 | Main Interface
SearXNG | 8080 | Search Engine
Qdrant | 6333 | Vector DB
Phi-3 | 8082 | Local LLM
Redis | 6379 | Cache

## Configuration
Copy or edit `.env`:
\`\`\`
REDIS_URL=redis://redis:6379/1
PHI3_URL=http://phi3:8082
QDRANT_URL=http://qdrant:6333
SEARXNG_URL=http://searxng:8080
# Add API keys if needed
\`\`\`

## Troubleshooting
- **Streamlit not loading in Codespaces?**
  1. Go to Ports tab
  2. Add port 8501
  3. Set visibility to Public
  4. Open in browser
- **Phi-3 slow on first run?** Wait 60–90 seconds for the model to load.

## Stack Architecture
- Frontend: Streamlit (`src/web/app.py`)
- Backend: Docker Compose (Redis, SearXNG, Qdrant, Phi-3)
- AI: Local Phi-3 inference

License: MIT
"
write_file "$REPO_ROOT/README.md" "$README_TEMPLATE"

###############################################################################
# 5) Launch compose
###############################################################################
log_info "Starting docker compose (may take time on first run)..."
"${COMPOSE_CMD[@]}" -f "$REPO_ROOT/docker-compose.yml" up -d --build
log_ok "Containers started in the background."

###############################################################################
# 6) Wait for services
###############################################################################
log_info "⏳ Waiting 60 seconds for Phi-3 and dependencies..."
sleep 60 || true

###############################################################################
# 7) Print access URLs
###############################################################################
LOCAL_IP=""
if command -v hostname >/dev/null 2>&1; then
  LOCAL_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
log_ok "Stack is (hopefully) up. Access URLs:"
echo "═══════════════════════════════════════════════════════"
echo ""

echo "🖥️  Streamlit UI:"
echo "   - Localhost:  http://localhost:8501"
if [[ -n "$LOCAL_IP" ]]; then
  echo "   - iPhone/LAN: http://${LOCAL_IP}:8501"
fi
echo ""
echo "🌐 SearXNG:      http://localhost:8080"
echo "💾 Qdrant:       http://localhost:6333"
echo "🤖 Phi-3:        http://localhost:8082"
echo "🧠 Redis:        redis://localhost:6379/1"
echo ""
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  echo "📦 Codespaces hint:"
  echo "   - Use the Ports tab → ensure port 8501 is forwarded."
fi
echo ""
echo "═══════════════════════════════════════════════════════"
log_ok "Stable stack script completed."
echo "═══════════════════════════════════════════════════════"
