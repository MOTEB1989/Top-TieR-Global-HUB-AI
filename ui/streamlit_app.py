import os

import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Top-TieR Global AI Console", layout="wide")

st.sidebar.title("LLM Provider")
provider = st.sidebar.selectbox("Provider", ["openai", "groq", "azure", "local"], index=0)
model = st.sidebar.text_input("Model override (optional)", "")

st.sidebar.markdown("---")
mode = st.sidebar.radio("Mode", ["Review Engine", "RAG Query"], index=0)

st.title("Top-TieR Global HUB AI — Control Panel")

if mode == "Review Engine":
    st.subheader("Unified Review Engine")
    review_type = st.selectbox("Review type", ["code", "security", "document"], index=0)
    content = st.text_area(
        "Content to review", height=300, placeholder="Paste code, config, or document text here..."
    )
    if st.button("Run Review", type="primary"):
        if not content.strip():
            st.warning("Please provide content to review.")
        else:
            payload = {
                "type": review_type,
                "content": content,
                "provider": provider,
                "model": model or None,
            }
            with st.spinner("Running review..."):
                resp = requests.post(f"{API_BASE}/review", json=payload, timeout=120)
                resp.raise_for_status()
                data = resp.json()
            st.success("Review completed.")
            st.json(data)

else:
    st.subheader("RAG Query")
    question = st.text_area("Question", height=150, placeholder="Ask about your ingested documents...")
    top_k = st.slider("Top-K context chunks", min_value=1, max_value=10, value=5)
    if st.button("Run RAG Query", type="primary"):
        if not question.strip():
            st.warning("Please provide a question.")
        else:
            payload = {
                "question": question,
                "top_k": top_k,
                "provider": provider,
                "model": model or None,
            }
            with st.spinner("Querying RAG engine..."):
                resp = requests.post(f"{API_BASE}/rag/query", json=payload, timeout=180)
                resp.raise_for_status()
                data = resp.json()
            st.success("RAG query completed.")
            st.write("### Answer")
            st.write(data.get("answer", ""))
            st.write("### Contexts")
            for c in data.get("contexts", []):
                st.markdown(f"**{c['path']} (chunk {c['chunk_index']}, score={c['score']:.3f})**")
                st.code(c["content"])
