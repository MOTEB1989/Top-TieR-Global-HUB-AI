FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LLM_PROVIDER=phi_local \
    PHI3_URL=http://phi3:8082

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app app

COPY services/gateway/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/gateway /app

USER app

EXPOSE 3000

CMD ["uvicorn", "gateway_server:app", "--host", "0.0.0.0", "--port", "3000"]
