# Top-TieR Global HUB AI 🚀

<div dir="rtl">

## مركز Top-TieR العالمي للذكاء الاصطناعي

منصة استخبارات OSINT متقدمة مع بنية خدمات متعددة قابلة للنشر على Railway.

</div>

---

## 🌟 Overview | نظرة عامة

Top-TieR Global HUB AI is a professional OSINT (Open Source Intelligence) platform built with a modern monorepo architecture. The platform consists of three main services deployable independently to Railway.

**منصة استخبارات OSINT احترافية مبنية بهندسة monorepo حديثة. تتكون المنصة من ثلاث خدمات رئيسية قابلة للنشر بشكل مستقل على Railway.**

---

## 🏗️ Architecture | الهندسة المعمارية

```
Top-TieR-Global-HUB-AI/
├── backend/              # FastAPI Backend Service
│   ├── app/
│   │   ├── api/v1/      # API endpoints
│   │   ├── core/        # Configuration
│   │   └── main.py      # Application entry
│   ├── requirements.txt
│   ├── railway.json
│   └── .env.example
│
├── bot/                 # Telegram Bot Service (Aiogram)
│   ├── main.py
│   ├── requirements.txt
│   ├── railway.json
│   └── .env.example
│
├── frontend/            # Next.js Frontend (TypeScript + Tailwind)
│   ├── src/
│   │   ├── pages/      # Next.js pages
│   │   ├── components/ # React components
│   │   └── services/   # API services
│   ├── package.json
│   ├── railway.json
│   └── .env.example
│
├── shared/              # Shared utilities
│   ├── python/utils/   # Python utilities
│   └── js/helpers/     # JavaScript utilities
│
├── scripts/             # Utility scripts
│   ├── verify_env.py   # Environment validation
│   └── seed_db.py      # Database seeding
│
├── .github/workflows/   # CI/CD pipelines
│   ├── deploy-backend.yml
│   ├── deploy-bot.yml
│   └── deploy-frontend.yml
│
└── docker/              # Optional Docker configurations
```

---

## 🚀 Quick Start | البدء السريع

### Prerequisites | المتطلبات الأساسية

- **Python 3.11+** for backend and bot
- **Node.js 18+** for frontend
- **Railway Account** for deployment (optional)
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

### Local Development | التطوير المحلي

#### 1. Clone the repository | استنساخ المستودع

```bash
git clone https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI.git
cd Top-TieR-Global-HUB-AI
```

#### 2. Backend Setup | إعداد الخلفية

```bash
cd backend
cp .env.example .env
# Edit .env with your configuration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

#### 3. Bot Setup | إعداد البوت

```bash
cd bot
cp .env.example .env
# Edit .env with TELEGRAM_BOT_TOKEN and BACKEND_API_URL

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

#### 4. Frontend Setup | إعداد الواجهة الأمامية

```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_BASE

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## 🔐 Environment Variables | متغيرات البيئة

### Backend Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `ENV` | Environment name | No | `development` |
| `DATABASE_URL` | PostgreSQL connection | Yes* | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection | No | `redis://localhost:6379` |
| `JWT_SECRET` | Secret for JWT tokens | Yes* | `your-secret-key-min-32-chars` |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Yes | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `ADMIN_CHAT_ID` | Telegram admin user ID | Yes | `123456789` |
| `OPENAI_API_KEY` | OpenAI API key | No | `sk-...` |
| `GROQ_API_KEY` | Groq API key | No | `gsk_...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | No | `sk-ant-...` |

*Required for production deployment

### Bot Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Yes | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `BACKEND_API_URL` | Backend API endpoint | Yes | `http://localhost:8000` |
| `ADMIN_CHAT_ID` | Admin Telegram user ID | Yes | `123456789` |

### Frontend Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_BASE` | Backend API base URL | Yes | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL (future) | No | `ws://localhost:8000/ws` |
| `ENV` | Environment name | No | `development` |

### Verifying Environment Variables | التحقق من متغيرات البيئة

Use the verification script to check your environment:

```bash
# Check all services
python scripts/verify_env.py

# Check specific service
python scripts/verify_env.py --service backend
python scripts/verify_env.py --service bot
python scripts/verify_env.py --service frontend
```

---

## 🚢 Deployment to Railway | النشر على Railway

### Prerequisites

1. Create a [Railway](https://railway.app) account
2. Install Railway CLI: `npm i -g @railway/cli`
3. Login: `railway login`

### Deploy Services | نشر الخدمات

#### Backend Deployment

```bash
cd backend
railway up
```

Configure environment variables in Railway dashboard:
- `DATABASE_URL` - Railway provides PostgreSQL
- `REDIS_URL` - Railway provides Redis
- `JWT_SECRET` - Generate a secure secret
- `TELEGRAM_BOT_TOKEN` - Your bot token
- `ADMIN_CHAT_ID` - Your Telegram user ID

#### Bot Deployment

```bash
cd bot
railway up
```

Configure environment variables:
- `TELEGRAM_BOT_TOKEN` - Your bot token
- `BACKEND_API_URL` - Your deployed backend URL
- `ADMIN_CHAT_ID` - Your Telegram user ID

#### Frontend Deployment

```bash
cd frontend
railway up
```

Configure environment variables:
- `NEXT_PUBLIC_API_BASE` - Your deployed backend URL

### CI/CD with GitHub Actions

The repository includes GitHub Actions workflows for automated deployment:

1. Add `RAILWAY_TOKEN` to your GitHub repository secrets
2. Push changes to `main` branch
3. Workflows will automatically deploy changed services

---

## 🔒 Security | الأمان

### ⚠️ CRITICAL SECURITY NOTES

**DO NOT COMMIT SECRETS TO THE REPOSITORY**
**لا تقم بتضمين الأسرار في المستودع**

- ✅ Use `.env` files (already in `.gitignore`)
- ✅ Use environment variables in production
- ✅ Use Railway/GitHub secrets for CI/CD
- ❌ **NEVER** hardcode API keys, tokens, or passwords
- ❌ **NEVER** commit `.env` files

### Secret Management

1. **Local Development**: Use `.env` files (not committed)
2. **Railway Deployment**: Use Railway environment variables
3. **CI/CD**: Use GitHub Secrets

### Generating Secure Secrets

```bash
# Generate JWT secret (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

---

## 🧪 Testing | الاختبار

### Backend Testing

```bash
cd backend
pytest  # (tests to be implemented)
```

### Bot Testing

```bash
cd bot
python -m pytest  # (tests to be implemented)
```

### Frontend Testing

```bash
cd frontend
npm run test  # (tests to be implemented)
```

---

## 📚 API Documentation | توثيق API

### Backend API

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Available Endpoints

#### Health Check
```bash
GET /health
```

#### Root
```bash
GET /
```

#### Example Endpoints
```bash
GET    /api/v1/examples      # Get all examples
GET    /api/v1/examples/{id} # Get specific example
POST   /api/v1/examples      # Create example
```

---

## 🤖 Telegram Bot Commands | أوامر بوت تيليجرام

| Command | Description | الوصف |
|---------|-------------|--------|
| `/start` | Start the bot | بدء البوت |
| `/help` | Show help message | عرض رسالة المساعدة |
| `/health` | Check system health | فحص صحة النظام |

### Future Commands (To be implemented)

- `/stats` - View system statistics
- `/query` - Perform OSINT query
- `/admin` - Admin panel access

---

## 🌐 Internationalization | الترجمة

The platform supports bilingual content (Arabic + English):

- **Backend**: API responses include Arabic descriptions
- **Bot**: Commands and messages support both languages
- **Frontend**: UI components display dual language content

### Adding Translations

Future implementation will include proper i18n framework:
- `react-i18next` for frontend
- Bot message templates for multiple languages
- RTL (Right-to-Left) support for Arabic

---

## 🗂️ Database Schema | مخطط قاعدة البيانات

### Future Implementation

Database models and migrations will be implemented using:
- **SQLAlchemy** - ORM for Python
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database

Run migrations (future):
```bash
cd backend
alembic upgrade head
```

Seed database (placeholder):
```bash
python scripts/seed_db.py
```

---

## 🔧 Development Tools | أدوات التطوير

### Recommended VS Code Extensions

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- GitLens

### Code Formatting

```bash
# Python (backend/bot)
pip install black isort
black .
isort .

# TypeScript (frontend)
npm run lint
npm run format
```

---

## 📦 Technology Stack | التقنيات المستخدمة

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **httpx** - Async HTTP client

### Bot
- **Aiogram 3.x** - Telegram bot framework
- **httpx** - HTTP client for API calls

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS
- **Axios** - HTTP client

### Deployment
- **Railway** - Platform as a Service
- **GitHub Actions** - CI/CD automation

---

## 🛣️ Roadmap | خارطة الطريق

### Phase 1: Foundation ✅ (Current PR)
- [x] Monorepo structure
- [x] Backend service (FastAPI)
- [x] Bot service (Aiogram)
- [x] Frontend service (Next.js)
- [x] Railway deployment configuration
- [x] CI/CD workflows

### Phase 2: Core Features (Next)
- [ ] Database models (SQLAlchemy)
- [ ] Alembic migrations
- [ ] User authentication (JWT)
- [ ] Admin dashboard functionality
- [ ] WebSocket integration
- [ ] Rate limiting

### Phase 3: OSINT Features
- [ ] OSINT query engine
- [ ] Data source integrations
- [ ] Advanced Telegram commands
- [ ] Real-time notifications
- [ ] Report generation

### Phase 4: Production Ready
- [ ] Comprehensive testing
- [ ] Error monitoring (Sentry)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Documentation completion
- [ ] Deployment automation

---

## 🤝 Contributing | المساهمة

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 📄 License | الترخيص

This project is proprietary software. All rights reserved.

---

## 👥 Team | الفريق

- **Project Lead**: [@MOTEB1989](https://github.com/MOTEB1989)

---

## 📞 Support | الدعم

- **Issues**: [GitHub Issues](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/discussions)

---

## 🙏 Acknowledgments | شكر وتقدير

Built with modern open-source technologies:
- FastAPI
- Aiogram
- Next.js
- Railway
- And many more amazing tools

---

<div align="center" dir="rtl">

**مركز Top-TieR العالمي للذكاء الاصطناعي**

منصة استخبارات OSINT الاحترافية

</div>

<div align="center">

**Top-TieR Global HUB AI**

Professional OSINT Intelligence Platform

---

Made with ❤️ for the OSINT community

</div>
