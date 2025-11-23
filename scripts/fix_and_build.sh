#!/usr/bin/env bash
set -euo pipefail

# fix_and_build.sh
# إصلاح سريع لـ TS build error (TS18003) + إعادة بناء Docker image + تحقق.
#
# الاستخدام:
#   chmod +x scripts/fix_and_build.sh
#   ./scripts/fix_and_build.sh

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "📁 Working directory: $REPO_ROOT"
echo ""

# 1) نسخ احتياطي
echo "🛡️  عمل نسخ احتياطي من tsconfig.json و Dockerfile (إن وُجدا)..."
cp -v tsconfig.json tsconfig.json.bak 2>/dev/null || true
cp -v Dockerfile Dockerfile.bak 2>/dev/null || true
echo ""

# 2) استبدال/تحديث tsconfig.json ليشمل الجذر و src/
cat > tsconfig.json <<'JSON'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "outDir": "dist",
    "rootDir": ".",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true
  },
  "include": [
    "src",
    "index.ts",
    "*.ts",
    "**/*.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
JSON

echo "✅ تم تحديث tsconfig.json (نسخة احتياطية: tsconfig.json.bak)"
echo ""

# 3) تثبيت الاعتماديات Node (آمن: يستخدم npm ci إذا package-lock موجود، وإلا npm install)
if [ -f package-lock.json ]; then
  echo "📦 تثبيت الاعتماديات عبر npm ci..."
  npm ci --silent
else
  echo "📦 تثبيت الاعتماديات عبر npm install..."
  npm install --silent
fi
echo ""

# 4) اختبار بناء TypeScript محليًا
echo "🔬 اختبار npx tsc -p tsconfig.json ..."
if npx -y tsc -p tsconfig.json; then
  echo "✅ TypeScript build succeeded locally."
else
  echo "❌ TypeScript build فشل محليًا. تحقق من ملفات .ts ومسارات include في tsconfig.json"
  exit 1
fi
echo ""

# 5) بناء صورة Docker للخدمة (تفترض أن Dockerfile في الجذر أو في مسار خدمة محددة)
# حاول البناء للخدمة المسماة 'api' عبر docker compose إن وُجد، وإلا بناء الصورة من Dockerfile في الجذر.
if [ -f docker-compose.yml ]; then
  echo "🐳 Found docker-compose.yml — attempting docker compose build (service: api if present)..."
  if docker compose config >/dev/null 2>&1; then
    # if service named "api" exists in compose, build it; otherwise build all
    if docker compose config --services | grep -q '^api$'; then
      echo "🔧 Building 'api' service via docker compose..."
      docker compose build api
    else
      echo "🔧 Service 'api' not found in compose file — building all services..."
      docker compose build
    fi
  else
    echo "⚠️ docker compose config غير صالح — ستُحاول بناء Dockerfile مباشرةً."
    # fallthrough to direct build
    if [ -f Dockerfile ]; then
      docker build -t top-tier-api .
    fi
  fi
else
  echo "⚠️ لا يوجد docker-compose.yml في الجذر. سأحاول بناء Dockerfile إذا وُجد."
  if [ -f Dockerfile ]; then
    docker build -t top-tier-api .
  else
    echo "❌ لا يوجد Dockerfile ولا docker-compose.yml. توقف."
    exit 1
  fi
fi
echo ""

# 6) تشغيل الحاويات (اختياري) — نشغل فقط إذا يوجد docker-compose.yml
if [ -f docker-compose.yml ]; then
  echo "▶️ تشغيل docker compose up -d ..."
  docker compose up -d
  echo ""
  echo "📦 الحاويات الحالية:"
  docker compose ps
else
  echo "ℹ️ تخطّي تشغيل الحاويات (لا يوجد docker-compose.yml)"
fi
echo ""

# 7) تحقق المنفذ المفتوح (API_PORT) — تحقق محلياً
API_PORT=${API_PORT:-3000}
echo "🔎 تحقق ما إذا كان المنفذ المحلي ${API_PORT} قيد الاستماع (local)..."
# استخدام ss أو lsof أو netstat حسب التوفر
if command -v ss >/dev/null 2>&1; then
  ss -ltnp | grep ":${API_PORT}" || echo "لا يوجد استماع على ${API_PORT} حتى الآن."
elif command -v lsof >/dev/null 2>&1; then
  lsof -iTCP -sTCP:LISTEN -P | grep ":${API_PORT}" || echo "لا يوجد استماع على ${API_PORT} حتى الآن."
else
  echo "لا تتوفر أوامر ss/lsof. استخدم: docker compose ps أو curl للتحقق."
fi
echo ""

# 8) طباعة آخر 200 سطر من لوج الخدمة (إذا كانت موجودة كخدمة api في compose)
echo "📄 استخراج سجلات الخدمة (api) إن وُجدت..."
if docker compose ps --services | grep -q '^api$' 2>/dev/null; then
  docker compose logs --no-color api | tail -n 200 || true
else
  # حاول البحث عن container باسم يحتوي 'api' أو 'top-tier'
  CONTAINER_ID=$(docker ps --format '{{.ID}} {{.Names}}' | grep -E 'api|top-tier|lexcode|gateway' | awk '{print $1}' | head -n1 || true)
  if [ -n "$CONTAINER_ID" ]; then
    echo "📦 Found container: $CONTAINER_ID — printing last 200 lines"
    docker logs "$CONTAINER_ID" --tail 200 || true
  else
    echo "ℹ️ لا توجد حاوية تبدو كـ 'api' لتجلب سجلاتها."
  fi
fi
echo ""

echo "✅ انتهى السكربت. إذا فشل البناء مرة أخرى، انسخ آخر رسائل الخطأ وأرسلها لي لنحلّلها أعمق."
