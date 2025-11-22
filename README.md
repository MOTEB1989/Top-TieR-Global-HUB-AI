# Top-TieR Global HUB AI 🚀

**Enterprise-grade AI orchestration platform with hybrid architecture**

## 🏗️ Architecture

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| **Core Engine** | Rust (Axum) | 8080 | High-performance embedding & utilities |
| **API Gateway** | Node.js + TypeScript | 3000 | Unified API & provider routing |
| **AI Adapters** | Python (FastAPI) | 8000 | Multi-provider AI integration |

## ✨ Features

- 🤖 **Multi-Provider Support**: OpenAI, Anthropic, Hugging Face, local models
- ⚡ **High Performance**: Rust core for compute-intensive operations
- 🔐 **Secure**: Environment-based secrets, no hardcoded credentials
- 🐳 **Docker-Ready**: Full docker-compose orchestration
- ☸️ **Kubernetes-Ready**: Health & readiness probes included

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
cd Top-TieR-Global-HUB-AI

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
docker compose up --build

# 4. Test
curl http://localhost:3000/v1/health
```

## 📡 API Endpoints

### Health Checks
- `GET /health` - Service health status (Rust core)
- `GET /ready` - Readiness probe for Kubernetes (Rust core)
- `GET /v1/health` - Gateway health status (Node gateway)
- `GET /v1/ready` - Gateway readiness probe (Node gateway)

### AI Inference
```bash
curl -X POST http://localhost:3000/v1/ai/infer \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, AI!"}
    ],
    "model": "gpt-4o-mini"
  }'
```

### Embeddings
```bash
curl -X POST http://localhost:8080/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text for embedding"}'
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# AI Providers
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=sk-ant-...

# Database
NEO4J_PASSWORD=secure_password

# Service Ports
RUST_CORE_PORT=8080
NODE_GATEWAY_PORT=3000
PYTHON_ADAPTERS_PORT=8000
```

## 📁 Project Structure

```
Top-TieR-Global-HUB-AI/
├── backend/
│   ├── rust-core/          # High-performance core
│   │   ├── Cargo.toml
│   │   ├── main.rs
│   │   └── Dockerfile
│   ├── node-gateway/       # API Gateway
│   │   ├── package.json
│   │   ├── index.ts
│   │   ├── ai.ts
│   │   ├── openai.ts
│   │   ├── tsconfig.json
│   │   └── Dockerfile
│   └── python-adapters/    # AI Integrations
│       ├── providers.py
│       ├── gpt_client.py
│       ├── committee_service.py
│       ├── requirements.txt
│       └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🧪 Testing

```bash
# Test individual services
docker compose up rust-core
docker compose up node-gateway

# View logs
docker compose logs -f

# Run health checks
curl http://localhost:8080/health
curl http://localhost:8080/ready
curl http://localhost:3000/v1/health
curl http://localhost:3000/v1/ready
```

## 📊 Monitoring

All services include health and readiness probes:
- **Liveness**: `/health` - Is the service alive?
- **Readiness**: `/ready` - Can it handle traffic?

## 🛠️ Development

### Build Rust Core
```bash
cd backend/rust-core
cargo build --release
cargo run
```

### Build Node Gateway
```bash
cd backend/node-gateway
npm install
npm run dev
```

### Build Python Adapters
```bash
cd backend/python-adapters
pip install -r requirements.txt
uvicorn committee_service:app --reload
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ by MOTEB1989**
