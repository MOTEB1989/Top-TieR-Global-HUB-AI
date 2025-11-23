FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAG_ENGINE_URL=http://rag_engine:8081 \
    GATEWAY_URL=http://gateway:3000

WORKDIR /app

COPY services/web_ui/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/web_ui /app

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
