FROM python:3.11-slim

WORKDIR /app

# نظاميّات مطلوبة لـ psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الموديولات والرانر
COPY runner.py .
COPY modules ./modules
# نسمح بتمرير lexcode.yaml كـ Volume من الخارج
# الافتراضي: الملف داخل الصورة لو وُجد
COPY lexcode.yaml ./lexcode.yaml

ENV PYTHONUNBUFFERED=1
CMD ["python", "runner.py"]
