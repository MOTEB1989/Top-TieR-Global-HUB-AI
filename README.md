# Top-TieR Global HUB AI 🚀

**Stable Stack - Streamlit + SearXNG + Qdrant + Phi-3**

## Quick Start
```bash
./scripts/run_stable.sh
```

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
```
REDIS_URL=redis://redis:6379/1
PHI3_URL=http://phi3:8082
QDRANT_URL=http://qdrant:6333
SEARXNG_URL=http://searxng:8080
# Add API keys if needed
```

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
