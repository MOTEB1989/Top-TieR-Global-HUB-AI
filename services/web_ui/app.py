"""WhatsApp-style Streamlit chat UI for the local RAG stack.

Notes/assumptions:
- This UI is intended for local/dev use only; no authentication or rate limiting
  is applied.
- Health checks are assumed to use port availability for Streamlit. If an HTTP
  endpoint is required, consider adding a lightweight ``/health`` route via
  ``st.markdown`` with instructions instead of altering infrastructure files.
"""
from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any, Dict, List

import streamlit as st

from chat_client import ChatClient

st.set_page_config(page_title="Top-TieR AI Chat", layout="wide", page_icon="💬")

CUSTOM_CSS = """
<style>
body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
    background-color: #f5f5f5;
}

.chat-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem 0.25rem;
}

.chat-row {
    display: flex;
    width: 100%;
}

.chat-row.user { justify-content: flex-end; }
.chat-row.assistant { justify-content: flex-start; }

.chat-bubble {
    max-width: 90%;
    padding: 0.75rem;
    border-radius: 16px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    word-break: break-word;
    font-size: 0.95rem;
}

.chat-bubble.user {
    background-color: #DCF8C6;
    border: 1px solid #cde7b0;
}

.chat-bubble.assistant {
    background-color: #FFFFFF;
    border: 1px solid #e0e0e0;
}

.message-meta {
    font-size: 0.75rem;
    color: #555;
    margin-bottom: 0.25rem;
}

footer {display: none !important;}
</style>
"""


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Hi! I'm your Top-TieR AI assistant. Ask me anything.",
                "timestamp": datetime.utcnow().isoformat(),
                "context": None,
            }
        ]
    if "chat_input" not in st.session_state:
        st.session_state["chat_input"] = ""


def format_time(timestamp: str | None) -> str:
    if not timestamp:
        return ""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%H:%M")
    except ValueError:
        return ""


def render_message(message: Dict[str, Any]) -> None:
    role = message.get("role", "assistant")
    content = message.get("content", "")
    timestamp = format_time(message.get("timestamp"))

    label = "You" if role == "user" else "Assistant"
    meta = f"{label}"
    if timestamp:
        meta = f"{meta} · {timestamp}"

    safe_content = escape(str(content))
    bubble = f"""
    <div class="chat-row {role}">
        <div class="chat-bubble {role}">
            <div class="message-meta">{meta}</div>
            <div>{safe_content}</div>
        </div>
    </div>
    """
    st.markdown(bubble, unsafe_allow_html=True)

    # Optional RAG context display
    context = message.get("context")
    if role == "assistant" and context:
        with st.expander("Show context"):
            if isinstance(context, (list, tuple)):
                for idx, item in enumerate(context, start=1):
                    st.markdown(f"**Source {idx}:**\n\n{item}")
            elif isinstance(context, dict):
                st.json(context)
            else:
                st.markdown(str(context))


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_state()

    chat_client = ChatClient()
    gateway_url = chat_client.gateway_url

    st.title("Top-TieR AI Chat")
    st.caption("WhatsApp-style chat UI powered by the local RAG stack.")

    with st.sidebar:
        st.header("Settings")
        st.write("Backend URL:")
        st.code(gateway_url, language="text")
        mode = st.selectbox("Mode / Persona (optional)", ["default", "banking", "legal"], index=0)
        st.caption(
            "This UI is intended for personal/dev use only. No authentication or"
            " rate limits are applied."
        )

    st.write("")
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state["messages"]:
            render_message(msg)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    input_container = st.container()
    with input_container:
        st.text_input(
            "Type your message",
            key="chat_input",
            placeholder="Message...",
            label_visibility="collapsed",
        )
        col1, col2 = st.columns([4, 1])
        send_clicked = col1.button("Send", use_container_width=True)
        clear_clicked = col2.button("Clear chat", use_container_width=True)

        if clear_clicked:
            st.session_state["messages"] = st.session_state["messages"][:1]
            st.session_state["chat_input"] = ""
            st.experimental_rerun()

        user_text = st.session_state.get("chat_input", "").strip()
        if send_clicked and user_text:
            now = datetime.utcnow().isoformat()
            user_message = {
                "role": "user",
                "content": user_text,
                "timestamp": now,
                "context": None,
            }
            st.session_state["messages"].append(user_message)

            history: List[Dict[str, str]] = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state["messages"]
            ]
            response = chat_client.send_messages(history, mode=None if mode == "default" else mode)
            assistant_content = response.get("content", "(No response received)")
            assistant_message = {
                "role": "assistant",
                "content": assistant_content,
                "timestamp": datetime.utcnow().isoformat(),
                "context": response.get("context"),
            }
            st.session_state["messages"].append(assistant_message)
            st.session_state["chat_input"] = ""
            st.experimental_rerun()


if __name__ == "__main__":
    main()
