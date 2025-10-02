FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY lexcode_runner.py runner_service.py ./

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "runner_service:app", "--host", "0.0.0.0", "--port", "8000"]
