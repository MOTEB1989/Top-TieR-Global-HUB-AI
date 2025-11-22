import os
from typing import Any, Dict, Optional

import requests
import streamlit as st

RAG_ENGINE_URL = os.getenv("RAG_ENGINE_URL", "http://rag_engine:8081")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:3000")


def post_json(url: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Request to {url} failed: {exc}")
        return None


def render_rag_response(data: Dict[str, Any]) -> None:
    st.subheader("RAG Engine")
    st.write(f"**Answer:** {data.get('answer', 'No answer returned.')}")
    contexts = data.get("context") or []
    if contexts:
        st.write("**Context:**")
        for idx, snippet in enumerate(contexts, start=1):
            st.markdown(f"{idx}. {snippet}")


def render_gateway_response(data: Dict[str, Any]) -> None:
    st.subheader("Gateway Completion")
    st.write(f"**Provider:** {data.get('provider', 'unknown')}")
    st.write(f"**Output:** {data.get('output', 'No output returned.')}")


st.set_page_config(page_title="RAG Demo", page_icon="📚")
st.title("Top-TieR RAG Demo")
st.markdown(
    "This Streamlit UI sends your question to the RAG Engine and the Unified Gateway."
)

question = st.text_area("Ask a question", placeholder="What is the project about?")
top_k = st.slider("Context chunks", min_value=1, max_value=5, value=2)

if st.button("Send"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        rag_data = post_json(f"{RAG_ENGINE_URL}/query", {"question": question, "top_k": top_k})
        gateway_data = post_json(f"{GATEWAY_URL}/complete", {"prompt": question})

        if rag_data:
            render_rag_response(rag_data)
        if gateway_data:
            render_gateway_response(gateway_data)
