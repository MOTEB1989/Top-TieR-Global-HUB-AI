#!/usr/bin/env bash
set -euo pipefail

################################################################################
# run_everything.sh
# سكربت موحد لتشغيل نظام Top-TieR Global HUB AI في بيئة واحدة:
# - يشغّل كل الخدمات في docker-compose.yml (searxng, qdrant, embedder, phi3, tinydb, ...)
# - يتعامل مع ملف .env (إنشاء إذا مفقود)
# - يطبع عناوين الوصول (localhost + IP للجوال)
# - يشغّل واجهة Streamlit: src/web/app.py
################################################################################

# ألوان للـ output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# مجلد السكربت والجذر
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ملفات أساسية
COMPOSE_FILE="${REPO_ROOT}/docker-compose.yml"
ENV_FILE="${REPO_ROOT}/.env"
HEALTH_SCRIPT="${REPO_ROOT}/scripts/system_health_check.py"  # اختياري

# زمن الانتظار بعد تشغيل الخدمات
readonly STARTUP_WAIT_TIME=5

###############################################################################
# دوال طباعة
###############################################################################
print_banner() {
    local msg="$1"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${BLUE}${msg}${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
}

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error()   { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info()    { echo -e "${BLUE}ℹ️  $1${NC}"; }

###############################################################################
# اكتشاف IP محلي (للوصول من الجوال على نفس الشبكة)
###############################################################################
detect_ip() {
    local ip=""
    if command -v ipconfig >/dev/null 2>&1; then
        ip=$(ipconfig getifaddr en0 2>/dev/null || echo "")
        [[ -z "$ip" ]] && ip=$(ipconfig getifaddr en1 2>/dev/null || echo "")
    fi
    if [[ -z "$ip" ]] && command -v hostname >/dev/null 2>&1; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
    fi
    echo "$ip"
}

###############################################################################
# البداية
###############################################################################
print_banner "🚀 تشغيل نظام Top-TieR Global HUB AI الكامل"

print_info "Repository root: ${REPO_ROOT}"
print_info "Using compose file: ${COMPOSE_FILE}"

###############################################################################
# 1) التحقق من Docker
###############################################################################
print_info "Checking Docker installation..."

if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker غير مثبت على هذا النظام. الرجاء تثبيت Docker ثم إعادة المحاولة."
    exit 1
fi
print_success "Docker is installed."

###############################################################################
# 2) التحقق من ملف docker-compose.yml
###############################################################################
print_info "Validating docker-compose.yml..."

if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "لم يتم العثور على ${COMPOSE_FILE}"
    print_error "تأكد أن الملف موجود في جذر المستودع."
    exit 1
fi

if ! docker compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then
    print_error "هناك أخطاء في docker-compose.yml"
    echo ""
    docker compose -f "$COMPOSE_FILE" config 2>&1 || true
    exit 1
fi
print_success "docker-compose.yml is valid."

###############################################################################
# 3) التعامل مع ملف .env
###############################################################################
print_info "Checking .env file..."

if [[ ! -f "$ENV_FILE" ]]; then
    print_warning ".env غير موجود — سيتم إنشاء ملف افتراضي."
    cat > "$ENV_FILE" << 'EOF'
# Auto-generated .env for Top-TieR Global HUB AI

LLM_PROVIDER=phi_local
PHI3_URL=http://phi3:8082
RAG_ENGINE_URL=http://rag_engine:8081

OPENAI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=

NEO4J_URI=
QDRANT_URL=http://qdrant:6333
EOF
    print_success "تم إنشاء .env (تذكر تحديث المفاتيح الحقيقية عند الحاجة)."
else
    print_success ".env موجود."
fi

###############################################################################
# 4) اكتشاف IP محلي
###############################################################################
print_info "Detecting local IP..."
LOCAL_IP="$(detect_ip)"
if [[ -n "$LOCAL_IP" ]]; then
    print_success "Local IP: ${LOCAL_IP}"
else
    print_warning "تعذر اكتشاف IP محلي (لا بأس، يمكن استخدام localhost أو Codespaces)."
    LOCAL_IP="unknown"
fi

###############################################################################
# 5) تشغيل كل الخدمات في docker-compose.yml
###############################################################################
print_banner "تشغيل الحاويات (Docker Compose)"

# استخراج قائمة الخدمات ديناميكياً
SERVICES=$(docker compose -f "$COMPOSE_FILE" config --services | xargs)

print_info "Services detected: ${SERVICES}"

print_info "Starting services..."
docker compose -f "$COMPOSE_FILE" up --build -d ${SERVICES}

print_success "كل الخدمات في Docker Compose تم تشغيلها (بشكل خلفي)."

print_info "انتظار ${STARTUP_WAIT_TIME} ثواني لتهيئة الخدمات..."
sleep "${STARTUP_WAIT_TIME}"

###############################################################################
# 6) تشغيل سكربت الصحة (إن وجد)
###############################################################################
if [[ -f "$HEALTH_SCRIPT" ]]; then
    print_info "Running health check: ${HEALTH_SCRIPT}"
    if python3 "$HEALTH_SCRIPT"; then
        print_success "Health check script completed successfully."
    else
        print_warning "Health check script reported issues، افحص التقرير/اللوج."
    fi
else
    print_warning "لم يتم العثور على scripts/system_health_check.py – يتم التجاوز."
fi

###############################################################################
# 7) طباعة نقاط الوصول
###############################################################################
print_banner "📡 نقاط الوصول / Access Points"

echo "🖥️  Streamlit Web UI (src/web/app.py):"
echo "   • Localhost:    http://localhost:8501"
if [[ "$LOCAL_IP" != "unknown" ]]; then
    echo "   • iPhone/LAN:   http://${LOCAL_IP}:8501"
fi
if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "   • Codespaces:   https://${CODESPACE_NAME}-8501.app.github.dev"
fi
echo ""

echo "🔎 SearxNG meta-search (searxng):"
echo "   • http://localhost:8080"
if [[ "$LOCAL_IP" != "unknown" ]]; then
    echo "   • http://${LOCAL_IP}:8080"
fi
if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "   • https://${CODESPACE_NAME}-8080.app.github.dev"
fi
echo ""

echo "💾 Qdrant (vector DB):"
echo "   • http://localhost:6333"
if [[ "$LOCAL_IP" != "unknown" ]]; then
    echo "   • http://${LOCAL_IP}:6333"
fi
if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "   • https://${CODESPACE_NAME}-6333.app.github.dev"
fi
echo ""

echo "🤖 Phi-3 (llama.cpp):"
echo "   • http://localhost:8082"
if [[ "$LOCAL_IP" != "unknown" ]]; then
    echo "   • http://${LOCAL_IP}:8082"
fi
if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "   • https://${CODESPACE_NAME}-8082.app.github.dev"
fi
echo ""

echo "🔡 Embedder (sentence-transformers):"
echo "   • http://localhost:8081"
if [[ "$LOCAL_IP" != "unknown" ]]; then
    echo "   • http://${LOCAL_IP}:8081"
fi
if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "   • https://${CODESPACE_NAME}-8081.app.github.dev"
fi
echo ""

###############################################################################
# 8) تشغيل واجهة Streamlit
###############################################################################
print_banner "🚀 تشغيل واجهة المحادثة (Streamlit)"

print_info "سيتم الآن تشغيل: streamlit run src/web/app.py على المنفذ 8501"
print_info "اترك هذه العملية تعمل في التيرمنال (لا تغلقها)."

cd "${REPO_ROOT}"

# تشغيل Streamlit في الواجهة (ليظهر لك اللوج)
streamlit run src/web/app.py \
  --server.address 0.0.0.0 \
  --server.port 8501

# لن نصل إلى هنا عادة إلا عند إيقاف Streamlit
print_warning "تم إيقاف Streamlit. الخدمات في Docker ما زالت تعمل (استخدم docker compose down لإيقافها إن رغبت)."

exit 0
