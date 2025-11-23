FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app app

COPY services/phi3/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/phi3 /app

USER app

EXPOSE 8082

CMD ["uvicorn", "phi_server:app", "--host", "0.0.0.0", "--port", "8082"]
