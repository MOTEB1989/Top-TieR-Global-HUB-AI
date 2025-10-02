FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY lexcode_runner.py runner_service_full.py ./

CMD ["uvicorn", "runner_service_full:app", "--host", "0.0.0.0", "--port", "8000"]
