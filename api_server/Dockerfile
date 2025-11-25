# API server container
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api_server ./api_server
COPY gpt_client.py ./gpt_client.py
COPY review_engine ./review_engine
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "api_server.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
