import os
import requests
import streamlit as st

st.set_page_config(page_title="Top-TieR Chat", layout="centered")

# ===== إعدادات =====
DEFAULT_API_BASE = "http://localhost:3000"
API_BASE = os.getenv("GATEWAY_URL", DEFAULT_API_BASE)
API_URL = f"{API_BASE}/v1/ai/infer"

st.title("💬 Top-TieR Global HUB AI")
st.caption("واجهة محادثة خفيفة متوافقة مع الجوال (Safari / Chrome)")

if "messages" not in st.session_state:
    # تنسيق مشابه لواجهة واتساب: role + content
    st.session_state.messages = []

def call_gateway(user_message: str) -> str:
    payload = {
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # نتوقع إرجاع content كنص
        # عدّل هذا حسب شكل استجابة الـ API عندك
        if isinstance(data, dict):
            return data.get("content") or data.get("answer") or str(data)
        return str(data)
    except Exception as e:
        return f"[خطأ أثناء الاتصال بالـ Gateway] {e}"

# ===== عرض المحادثة =====
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        text = msg.get("content", "")
        if role == "user":
            st.markdown(f"🧑 **أنت:** {text}")
        else:
            st.markdown(f"🤖 **المساعد:** {text}")

st.markdown("---")

# ===== مربع الإدخال (مهيأ للجوال) =====
with st.form("chat-form", clear_on_submit=True):
    user_input = st.text_area(
        "اكتب رسالتك هنا",
        placeholder="اسأل عن أي شيء في المشروع، التقنيات، أو النصوص...",
        height=80,
    )
    submitted = st.form_submit_button("إرسال", use_container_width=True)

if submitted and user_input.strip():
    user_message = user_input.strip()
    # أضف رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_message})
    # نطلب الرد من الـ Gateway
    assistant_reply = call_gateway(user_message)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()

st.markdown("---")
st.caption(f"Gateway URL: {API_URL}")
