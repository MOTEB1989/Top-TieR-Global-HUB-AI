# Local RAG Engine Overview

This repository now includes a lightweight, local Retrieval-Augmented Generation (RAG) stack that stores embeddings in SQLite and can be queried via CLI, FastAPI, or Streamlit.

## Ingest documents

Use the ingestion CLI to chunk and embed `.txt` or `.md` files under a root directory:

```bash
python -m rag.ingest ./my_docs
```

Embeddings rely on `OPENAI_API_KEY` being set and the optional `RAG_*` environment variables in `rag/config.py` for tuning chunk size and overlap.

## Query via Python/CLI

You can query the store directly from Python for ad-hoc testing:

```python
from rag.query import rag_answer

print(rag_answer("سؤال عن المستندات").get("answer"))
```

## Run the API server

Start the FastAPI server (with hot reload for local development):

```bash
uvicorn api_server:app --reload --port 8000
```

The new endpoint `/rag/query` accepts a JSON payload with `question`, `top_k`, `provider`, and `model` fields and returns the composed answer plus contexts.

## Streamlit control panel

A Streamlit UI is available for interactive review and RAG queries:

```bash
streamlit run ui/streamlit_app.py
```

Use the sidebar to switch between the Review Engine and RAG Query modes and to select the provider/model.
