# Architecture Overview

## Components
- **Streamlit Web UI**: Provides RAG querying, review workflows, provider selection, and PDF uploads.
- **Review Engine**: Uses the shared gateway to route review prompts to configured LLM providers.
- **RAG Engine**: Handles ingestion, chunking, embedding, and retrieval using Qdrant (preferred) or FAISS (optional fallback).
- **Gateway (gateway/)**: Central abstraction that routes to OpenAI, Groq, Azure-compatible endpoints, mock, or the local Phi-3 runner.
- **Providers**: OpenAI, Groq, Azure-compatible endpoints, and the local Phi-3 mini model via llama.cpp wrapper.
- **Vector Stores**: Qdrant primary, FAISS optional local index.

## Flows
### RAG Query Flow
1. User submits a question in the Web UI.
2. UI calls the RAG engine query logic.
3. RAG builds embeddings, queries Qdrant/FAISS, and assembles context.
4. Gateway invokes the selected provider (including local Phi-3) to craft an answer bound to the provided context.
5. UI displays the answer and optional context snippets.

### Review Flow
1. User selects review type (code/security/document) and submits content.
2. Gateway routes the prompt to the chosen provider.
3. Response is returned to UI for display.

### Local vs Remote Providers
- Remote providers (OpenAI, Groq, Azure-compatible) require API keys.
- Local provider uses the Phi-3 runner exposed via HTTP or direct function calls for offline scenarios.

### Docker-only Deployment
- `docker-compose.rag.yml` orchestrates Qdrant, local Phi runner, API/RAG services, and the Streamlit Web UI for turnkey deployment.

```mermaid
flowchart TD
  User[👤 User] --> UI[🖥️ Streamlit Web UI]

  UI --> RAG[RAG Engine]
  RAG --> Qdrant[(Qdrant DB)]
  RAG --> FAISS[(FAISS Index)]
  RAG --> PDFLoader[📄 PDF Loader]

  UI --> Gateway[🔗 LLM Gateway (gateway/)]
  Gateway -->|Phi-3 Local| Phi[🤖 Phi-3 Runner]
  Gateway -->|Groq API| Groq[☁️ Groq Service]
  Gateway -->|OpenAI API| OpenAI[☁️ OpenAI Service]

  Gateway --> UI
```

## Environment Variables
- `RAG_EMBEDDING_PROVIDER` / `RAG_EMBEDDING_MODEL`
- `RAG_QDRANT_URL`, `RAG_QDRANT_API_KEY`, `RAG_COLLECTION_NAME`, `RAG_TOP_K`, `RAG_MAX_PDF_MB`
- `RAG_CACHE_ENABLED`, `RAG_CHUNK_SIZE`, `RAG_CHUNK_OVERLAP`
- `LLM_PROVIDER`, `LLM_MODEL`, `OPENAI_API_KEY`, `GROQ_API_KEY`, Azure OpenAI variables
- `LOCAL_PHI_BASE_URL`

## Assumptions & Manual Review
- FAISS usage is optional; install `faiss-cpu` when needed.
- PyMuPDF is required for PDF ingestion; ensure availability in runtime images.
- Embedding and LLM calls should be mocked in CI to avoid heavy downloads.
- Docker Compose stack assumes `models/` directory hosts the Phi-3 GGUF file.
