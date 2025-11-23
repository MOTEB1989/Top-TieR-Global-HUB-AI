# LexCode Hybrid Stack 🚀

هندسة هجينة متينة:
- **Rust (core/):** محرك الأداء والخدمات الأساسية (HTTP/axum).
- **Node.js + TypeScript (services/api/):** بوابة API، مصادقة، توحيد المزوّدات.
- **Python (adapters/python/lexhub/):** وصلات الذكاء الاصطناعي والبيانات (OpenAI/Anthropic/HF/Kaggle...).

## التشغيل السريع
```bash
cp .env.example .env
docker compose up --build
```
- Rust Core على `http://localhost:8080`
- API Gateway على `http://localhost:3000`


## استخدام /v1/ai/infer (OpenAI)
ضع مفتاحك في `.env`:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # اختياري
OPENAI_BASE_URL=https://api.openai.com/v1  # اختياري
```
اختبر:
```bash
curl -X POST http://localhost:3000/v1/ai/infer \  -H "Content-Type: application/json" \  -d '{ "messages": [ { "role": "user", "content": "عرّف LexCode في جملة واحدة." } ] }'
```

## 🔍 Telegram Bot with RAG (Retrieval-Augmented Generation)
### نظام الاسترجاع المعزز للتوليد

The Telegram bot now includes RAG capabilities for intelligent code search and context-aware responses.

**Features:**
- **Vector Search**: Search repository files using semantic similarity
- **Auto Context Injection**: Automatically inject relevant code context into chat responses
- **CLI Search Tool**: Query the embeddings index from command line

**Environment Variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENABLE_RAG` | `false` | Master switch for RAG context injection in `/chat` |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model name |
| `EMBEDDING_INDEX_PATH` | `analysis/embeddings/index.json` | Location of saved embeddings index |
| `EMBEDDING_CHUNK_SIZE` | `1200` | Characters per chunk |
| `EMBEDDING_CHUNK_OVERLAP` | `150` | Overlap characters between chunks |
| `FILE_EXT_ALLOWLIST` | `.py,.ts,.md,.sh,.yaml,.yml,.txt,.json` | Allowed file extensions |
| `EMBEDDING_MAX_FILES` | `0` | Optional limit (# of files); 0 = unlimited |
| `VECTOR_TOP_K` | `6` | Number of top chunks retrieved |

**Bot Commands:**
- `/search <query>` - Search repository files using vector similarity
- `/chat <message>` - Chat with automatic context injection (when `ENABLE_RAG=true`)
- `/status` - View RAG configuration status

**CLI Tools:**
```bash
# Build embeddings index (automatically run on Railway deploy)
python scripts/embed_index.py

# Search index from command line
python scripts/embed_search.py "authentication implementation"
```

**Example Configuration:**
```bash
# Enable RAG in .env
ENABLE_RAG=true
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_TOP_K=6
```

**Arabic / العربية:**

يتضمن بوت تيليجرام الآن إمكانيات RAG للبحث الذكي في الكود والإجابات الواعية بالسياق.

**الأوامر:**
- `/search <استعلام>` - البحث في ملفات المستودع باستخدام التشابه المتجه
- `/chat <رسالة>` - الدردشة مع حقن السياق التلقائي (عند تفعيل `ENABLE_RAG=true`)
- `/status` - عرض حالة تكوين RAG
