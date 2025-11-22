# WhatsApp-style Chat UI (Streamlit)

This Streamlit app provides a mobile-friendly, WhatsApp-style interface for chatting with the local RAG stack.

## Running locally

Use Docker Compose for the RAG stack. The web UI will be available on port `8501`.

```bash
docker compose -f docker-compose.rag.yml up web_ui gateway rag_engine phi3 qdrant
```

> If you add or rename services, keep the `web_ui` service name and port `8501` to match this UI.

## Accessing from a phone on the same Wi-Fi

1. Find your laptop/desktop IP address on the local network (e.g., `192.168.x.x`).
2. On your phone (iPhone/Android) connected to the same Wi-Fi, open a browser and visit:
   ```
   http://<LAPTOP_IP>:8501
   ```
3. You should see the WhatsApp-like chat interface. Messages are green on the right for you and grey on the left for the assistant.

## Notes
- This UI is intended for personal/dev use only; no authentication or rate limiting is enabled.
- The app sends the full conversation history to the configured `GATEWAY_URL` on every message for context.
- If the gateway returns RAG context or sources, they are shown under each assistant reply in an expandable panel.
