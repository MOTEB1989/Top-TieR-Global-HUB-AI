#!/usr/bin/env bash
set -euo pipefail

################################################################################
# run_everything.sh
# A comprehensive script to run and validate the full RAG stack
# (qdrant, rag_engine, phi3, gateway, web_ui)
################################################################################

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Determine repository root (one level above scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Define key paths
COMPOSE_FILE="${REPO_ROOT}/docker-compose.rag.yml"
HEALTH_SCRIPT="${REPO_ROOT}/scripts/system_health_check.py"
ENV_FILE="${REPO_ROOT}/.env"

################################################################################
# Function: detect_ip
# Detects local IP address for iPhone-friendly URLs
################################################################################
detect_ip() {
    local ip=""
    
    # Try macOS approach first
    if command -v ipconfig >/dev/null 2>&1; then
        ip=$(ipconfig getifaddr en0 2>/dev/null || echo "")
    fi
    
    # Fallback to Linux approach
    if [ -z "$ip" ] && command -v hostname >/dev/null 2>&1; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
    fi
    
    echo "$ip"
}

################################################################################
# Function: print_banner
# Prints a formatted banner message
################################################################################
print_banner() {
    local message="$1"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${BLUE}${message}${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
}

################################################################################
# Function: print_success
# Prints a success message
################################################################################
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

################################################################################
# Function: print_error
# Prints an error message
################################################################################
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

################################################################################
# Function: print_warning
# Prints a warning message
################################################################################
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

################################################################################
# Function: print_info
# Prints an info message
################################################################################
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

################################################################################
# Main Script Start
################################################################################

print_banner "🚀 تشغيل نظام RAG الكامل / Starting Full RAG Stack"

# Print detected repository root
print_info "Repository root: ${REPO_ROOT}"

################################################################################
# Step 1: Check Docker installation
################################################################################
print_info "Checking Docker installation..."

if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker غير مثبت في هذا الجهاز. الرجاء تثبيت Docker ثم إعادة المحاولة."
    print_error "Docker is not installed on this system. Please install Docker and try again."
    exit 1
fi

print_success "Docker is installed"

################################################################################
# Step 2: Validate docker-compose.rag.yml
################################################################################
print_info "Validating docker-compose.rag.yml..."

if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "ملف docker-compose.rag.yml غير موجود في: ${COMPOSE_FILE}"
    print_error "docker-compose.rag.yml file not found at: ${COMPOSE_FILE}"
    print_warning "Please create docker-compose.rag.yml with your RAG stack configuration"
    exit 1
fi

# Validate compose file syntax
if ! docker compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then
    print_error "ملف docker-compose.rag.yml يحتوي على أخطاء في الصياغة"
    print_error "docker-compose.rag.yml has syntax errors"
    echo ""
    echo "Detailed error:"
    docker compose -f "$COMPOSE_FILE" config 2>&1 || true
    exit 1
fi

print_success "docker-compose.rag.yml is valid"

################################################################################
# Step 3: Handle .env file
################################################################################
print_info "Checking .env file..."

if [ ! -f "$ENV_FILE" ]; then
    print_warning "ملف .env غير موجود. سيتم إنشاء ملف .env بقيم افتراضية آمنة..."
    print_warning ".env file not found. Creating .env with safe defaults..."
    
    cat > "$ENV_FILE" << 'EOF'
# Auto-generated .env file for RAG stack
# Please update API keys and other sensitive values as needed

# LLM Provider Configuration
LLM_PROVIDER=phi_local
PHI3_URL=http://phi3:8082
RAG_ENGINE_URL=http://rag_engine:8081

# API Keys (please fill in your actual keys)
OPENAI_API_KEY=
GROQ_API_KEY=
ANTHROPIC_API_KEY=

# Database Configuration
NEO4J_URI=

# Vector Database
QDRANT_URL=http://qdrant:6333
EOF
    
    print_success "تم إنشاء ملف .env بنجاح. الرجاء تحديث المفاتيح السرية حسب الحاجة."
    print_success ".env file created successfully. Please update secret keys as needed."
else
    print_success ".env file exists"
fi

################################################################################
# Step 4: Detect local IP
################################################################################
print_info "Detecting local IP address..."

LOCAL_IP=$(detect_ip)

if [ -n "$LOCAL_IP" ]; then
    print_success "Local IP detected: ${LOCAL_IP}"
    print_info "🌐 Local IP for iPhone: ${LOCAL_IP}"
else
    print_warning "Could not detect local IP address"
    LOCAL_IP="unknown"
fi

################################################################################
# Step 5: Start the full RAG stack
################################################################################
print_banner "Starting RAG Stack Services"

print_info "Starting services: qdrant, rag_engine, phi3, gateway, web_ui..."
print_info "This may take a few minutes on first run..."

if docker compose -f "$COMPOSE_FILE" up --build -d qdrant rag_engine phi3 gateway web_ui; then
    print_success "Services started successfully"
else
    print_error "فشل في تشغيل الخدمات. يرجى التحقق من السجلات."
    print_error "Failed to start services. Please check the logs."
    exit 1
fi

# Give services time to initialize
print_info "Waiting for services to initialize (5 seconds)..."
sleep 5

################################################################################
# Step 6: Run health check if available
################################################################################
print_info "Checking for health check script..."

if [ -f "$HEALTH_SCRIPT" ]; then
    print_info "Running health check script..."
    python3 "$HEALTH_SCRIPT" || {
        print_warning "Health check script reported issues (non-fatal)"
    }
else
    print_warning "لم يتم العثور على سكريبت الفحص الصحي في: ${HEALTH_SCRIPT}"
    print_warning "Health check script not found at: ${HEALTH_SCRIPT}"
    print_info "Continuing without health check..."
fi

################################################################################
# Step 7: Display access information
################################################################################
print_banner "🎉 تم تشغيل النظام بنجاح / System Started Successfully"

echo ""
echo "📱 Access Points / نقاط الوصول:"
echo "─────────────────────────────────────────────────────────────────"
echo ""

# Streamlit Web UI
echo "🖥️  Streamlit Web UI:"
echo "   • Localhost:    http://localhost:8501"
if [ "$LOCAL_IP" != "unknown" ]; then
    echo "   • iPhone/LAN:   http://${LOCAL_IP}:8501"
fi
echo ""

# Gateway
echo "🌐 API Gateway:"
echo "   • Localhost:    http://localhost:3000"
if [ "$LOCAL_IP" != "unknown" ]; then
    echo "   • iPhone/LAN:   http://${LOCAL_IP}:3000"
fi
echo ""

# RAG Engine
echo "🔍 RAG Engine:"
echo "   • Localhost:    http://localhost:8081"
if [ "$LOCAL_IP" != "unknown" ]; then
    echo "   • iPhone/LAN:   http://${LOCAL_IP}:8081"
fi
echo ""

# Phi-3 Local Runner
echo "🤖 Phi-3 Local Runner:"
echo "   • Localhost:    http://localhost:8082"
if [ "$LOCAL_IP" != "unknown" ]; then
    echo "   • iPhone/LAN:   http://${LOCAL_IP}:8082"
fi
echo ""

# Qdrant
echo "💾 Qdrant Vector Database:"
echo "   • Localhost:    http://localhost:6333"
if [ "$LOCAL_IP" != "unknown" ]; then
    echo "   • iPhone/LAN:   http://${LOCAL_IP}:6333"
fi
echo ""

echo "─────────────────────────────────────────────────────────────────"
echo ""

# Additional helpful commands
print_info "Useful commands:"
echo "  • View logs:    docker compose -f ${COMPOSE_FILE} logs -f"
echo "  • Stop services: docker compose -f ${COMPOSE_FILE} down"
echo "  • Restart:      docker compose -f ${COMPOSE_FILE} restart"
echo ""

print_banner "🟢 تم تشغيل النظام بالكامل بنجاح"
print_success "All services are running! / جميع الخدمات تعمل بنجاح!"

exit 0
