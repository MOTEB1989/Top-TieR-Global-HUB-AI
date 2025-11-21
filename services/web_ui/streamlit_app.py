from __future__ import annotations

import os
from pathlib import Path
from typing import List

import streamlit as st

from gateway.router import simple_chat
from services.rag_engine.rag import query

UPLOAD_DIR = Path("var/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _available_providers() -> List[str]:
    providers = ["mock"]
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("GROQ_API_KEY"):
        providers.append("groq")
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        providers.append("azure")
    if os.getenv("LOCAL_PHI_BASE_URL"):
        providers.append("local_phi3")
    return providers


def render_sidebar() -> dict:
    st.sidebar.header("Settings")
    provider = st.sidebar.selectbox("Provider", _available_providers())
    model_override = st.sidebar.text_input("Model override", value="")
    show_context = st.sidebar.checkbox("Show context chunks", value=True)
    st.sidebar.info("Uploads are stored locally; do not upload sensitive data.")
    max_mb = int(os.getenv("RAG_MAX_PDF_MB", "10"))
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDFs for ingestion", type=["pdf"], accept_multiple_files=True
    )
    saved_paths = []
    for uploaded in uploaded_files or []:
        if uploaded.size > max_mb * 1024 * 1024:
            st.sidebar.warning(f"{uploaded.name} is too large (>{max_mb}MB)")
            continue
        sanitized = Path(uploaded.name).name
        dest = UPLOAD_DIR / sanitized
        dest.write_bytes(uploaded.getbuffer())
        saved_paths.append(dest)
    return {
        "provider": provider,
        "model": model_override,
        "show_context": show_context,
        "uploads": saved_paths,
    }


def render_rag_tab(show_context: bool):
    st.subheader("RAG Query")
    question = st.text_area("Question", height=120)
    top_k = st.slider("Top K", min_value=1, max_value=10, value=5)
    if st.button("Run RAG") and question:
        result = query(question, top_k=top_k)
        st.write(result.get("answer"))
        if show_context:
            st.markdown("### Context")
            for ctx in result.get("contexts", []):
                metadata = ctx.get("metadata", {})
                st.markdown(
                    f"- Score: {ctx.get('score')} | Source: {metadata.get('source')} | Page: {metadata.get('page_number', '?')}"
                )


def render_review_tab(provider: str, model: str):
    st.subheader("Review Engine")
    review_type = st.selectbox("Review type", ["code", "security", "document"])
    content = st.text_area("Content", height=200)
    if st.button("Run Review") and content:
        prompt = f"Review type: {review_type}\nContent:\n{content}\nProvide concise feedback."
        response = simple_chat(prompt, provider=provider, model=model or None)
        st.write(response)


def main():
    st.title("Top-Tier RAG & Review UI")
    settings = render_sidebar()
    tab = st.radio("Mode", ["RAG Query", "Review Engine"])
    if tab == "RAG Query":
        render_rag_tab(settings["show_context"])
    else:
        render_review_tab(settings["provider"], settings["model"])


if __name__ == "__main__":  # pragma: no cover - streamlit
    main()
