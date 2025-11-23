FROM python:3.11-slim

WORKDIR /app
COPY app.py /app/app.py
RUN pip install --no-cache-dir fastapi==0.110.0 uvicorn[standard]==0.29.0

ENV PORT=8003
EXPOSE 8003

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
