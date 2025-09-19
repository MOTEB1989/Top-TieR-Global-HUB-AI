#!/usr/bin/env bash
set -e

PROJECT_DIR="/workspaces/Top-TieR-Global-HUB-AI"
APP_MODULE="api_server.main:app"
HOST="0.0.0.0"
PORT="8000"

echo "🚀 بدء تشغيل المشروع عبر CodeX..."

# 1️⃣ الانتقال لمجلد المشروع
cd "$PROJECT_DIR" || { echo "❌ لم أجد مجلد المشروع $PROJECT_DIR"; exit 1; }
echo "📂 الموقع الحالي: $(pwd)"

# 2️⃣ تشغيل docker-compose لو موجود
if [ -f "docker-compose.yml" ]; then
  echo "🐳 تشغيل docker-compose..."
  docker compose up -d
else
  echo "⚠️ لم أجد docker-compose.yml — سيتم التجاوز."
fi

# 3️⃣ التحقق من اتصال قاعدة البيانات (Postgres)
if command -v pg_isready >/dev/null 2>&1; then
  echo "🔎 التحقق من اتصال PostgreSQL..."
  if pg_isready -h localhost -p 5432 -q; then
    echo "✅ قاعدة البيانات متصلة"
  else
    echo "⚠️ لم أستطع الاتصال بـ Postgres على المنفذ 5432"
  fi
else
  echo "⚠️ pg_isready غير مثبت — تجاوز الفحص"
fi

# 4️⃣ التحقق من مفتاح API
if [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ المتغير OPENAI_API_KEY غير موجود. ضعه باستخدام:"
  echo "   export OPENAI_API_KEY=sk-xxxx"
  exit 1
else
  echo "🔑 OPENAI_API_KEY مضبوط ✅"
fi

# 5️⃣ تثبيت المتطلبات
if [ -f "poetry.lock" ]; then
  echo "📦 تثبيت الحزم عبر Poetry..."
  poetry install
  CMD="poetry run uvicorn $APP_MODULE --host $HOST --port $PORT --reload"
elif [ -f "requirements.txt" ]; then
  echo "📦 تثبيت الحزم عبر pip..."
  pip install -r requirements.txt
  CMD="uvicorn $APP_MODULE --host $HOST --port $PORT --reload"
else
  echo "⚠️ لا يوجد requirements.txt أو poetry.lock"
  CMD="uvicorn $APP_MODULE --host $HOST --port $PORT --reload"
fi

# 6️⃣ تشغيل التطبيق
echo "🚀 تشغيل Uvicorn على http://$HOST:$PORT ..."
exec $CMD
