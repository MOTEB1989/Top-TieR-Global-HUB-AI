import os
from typing import Dict, List

import requests
import streamlit as st

st.set_page_config(page_title="Mobile Chat RAG", layout="wide")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:3000")
RAG_ENGINE_URL = os.getenv("RAG_ENGINE_URL", "http://localhost:8081")


def _call_gateway(message: str) -> Dict:
    try:
        response = requests.post(
            f"{GATEWAY_URL}/chat", json={"message": message}, timeout=20
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _render_header():
    st.title("Mobile Chat RAG Stack")
    st.caption(
        "Use mobile browser in portrait mode; for best experience, use Safari/Chrome."
    )
    st.write(
        "This chat UI connects to the local Gateway and RAG engine running on your laptop."
    )


if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []


_render_header()

with st.container(border=True):
    st.markdown("### Chat")
    chat_placeholder = st.container()
    with st.form("chat-form", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            placeholder="Ask anything...",
            height=80,
            label_visibility="hidden",
        )
        submitted = st.form_submit_button("Send", use_container_width=True)

    if submitted and user_input:
        st.session_state.messages.append({"role": "user", "text": user_input})
        response = _call_gateway(user_input)
        completion = response.get("completion") or response.get("error") or ""
        contexts = response.get("contexts", [])
        st.session_state.messages.append(
            {"role": "assistant", "text": completion, "contexts": contexts}
        )

    with chat_placeholder:
        for message in st.session_state.messages:
            role = message.get("role", "user").capitalize()
            st.markdown(f"**{role}:** {message.get('text', '')}")
            if message.get("contexts"):
                with st.expander("Context", expanded=False):
                    for ctx in message["contexts"]:
                        source = ctx.get("source", "unknown")
                        snippet = ctx.get("snippet", "")
                        st.markdown(f"- **{source}**: {snippet}")

with st.container(border=True):
    st.markdown("### Connection")
    st.text(f"Gateway: {GATEWAY_URL}")
    st.text(f"RAG Engine: {RAG_ENGINE_URL}")


if __name__ == "__main__":
    # Allows running with `python app.py` for quick smoke tests
    st.write("Start with: streamlit run app.py --server.port=8501 --server.address=0.0.0.0")
