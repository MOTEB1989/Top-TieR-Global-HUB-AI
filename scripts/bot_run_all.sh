#!/usr/bin/env bash
set -euo pipefail

##############################################
# Top-Tier Global HUB AI – Bot Run All
# Full automation script for Codespaces
##############################################

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_FILE="${REPO_ROOT}/scripts/stack_report.json"
LOG_FILE="${REPO_ROOT}/scripts/bot_run_all.log"

# Colors
C_RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_BLUE=$'\033[34m'
C_CYAN=$'\033[36m'

log()   { printf "%s\n" "$*" | tee -a "$LOG_FILE"; }
info()  { log "${C_BLUE}ℹ${C_RESET} $*"; }
ok()    { log "${C_GREEN}✅${C_RESET} $*"; }
warn()  { log "${C_YELLOW}⚠️${C_RESET} $*"; }
err()   { log "${C_RED}❌ $*${C_RESET}"; }

# Initialize log
> "$LOG_FILE"
info "بدء التشغيل الآلي الكامل - $(date)"

##############################################
# Step 1: Prerequisites Check
##############################################
check_prerequisites() {
    info "فحص المتطلبات الأساسية..."
    
    local missing=()
    
    command -v docker &>/dev/null || missing+=("docker")
    command -v docker-compose &>/dev/null || missing+=("docker-compose")
    command -v python3 &>/dev/null || missing+=("python3")
    command -v node &>/dev/null || missing+=("node")
    command -v git &>/dev/null || missing+=("git")
    
    if [ ${#missing[@]} -gt 0 ]; then
        err "المتطلبات الناقصة: ${missing[*]}"
        return 1
    fi
    
    ok "جميع المتطلبات متوفرة"
}

##############################################
# Step 2: Environment Setup
##############################################
setup_environment() {
    info "إعداد البيئة..."
    
    cd "$REPO_ROOT"
    
    # Create .env if it doesn't exist
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            warn ".env غير موجود، نسخ من .env.example"
            cp .env.example .env
        else
            warn "إنشاء .env أساسي"
            cat > .env <<EOF
# Basic configuration
CORE_URL=http://localhost:8080
API_PORT=3000
NODE_ENV=development
EOF
        fi
    fi
    
    # Install Python dependencies
    if [ -f requirements.txt ]; then
        info "تثبيت مكتبات Python..."
        python3 -m pip install --quiet --upgrade pip || true
        python3 -m pip install --quiet -r requirements.txt || warn "بعض مكتبات Python فشلت"
    fi
    
    # Install Node dependencies
    if [ -f package.json ]; then
        info "تثبيت مكتبات Node.js..."
        npm install --silent 2>&1 | tail -n 5 || warn "بعض مكتبات Node فشلت"
    fi
    
    ok "تم إعداد البيئة"
}

##############################################
# Step 3: Start Services
##############################################
start_services() {
    info "بدء الخدمات..."
    
    cd "$REPO_ROOT"
    
    # Stop any running containers first
    docker-compose down 2>/dev/null || true
    
    # Start services
    info "تشغيل Docker Compose..."
    if docker-compose up -d --build 2>&1 | tee -a "$LOG_FILE"; then
        ok "تم بدء الخدمات"
    else
        warn "حدثت بعض المشاكل عند بدء الخدمات"
    fi
    
    # Wait for services to be ready
    info "انتظار جاهزية الخدمات (30 ثانية)..."
    sleep 30
}

##############################################
# Step 4: Health Check
##############################################
check_services_health() {
    info "فحص صحة الخدمات..."
    
    local services=()
    local failed_services=()
    
    # Check Docker containers
    while IFS= read -r container; do
        if [ -n "$container" ]; then
            local name=$(echo "$container" | awk '{print $1}')
            local status=$(echo "$container" | awk '{print $2}')
            services+=("$name:$status")
            
            if [[ "$status" != "Up"* ]]; then
                failed_services+=("$name")
                warn "الخدمة $name في حالة: $status"
            else
                ok "الخدمة $name تعمل"
            fi
        fi
    done < <(docker-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | tail -n +2)
    
    # Check common ports
    local ports=(3000 8080 8000 5000)
    for port in "${ports[@]}"; do
        if nc -z localhost "$port" 2>/dev/null; then
            ok "المنفذ $port مفتوح"
        else
            info "المنفذ $port غير مفتوح"
        fi
    done
    
    echo "${failed_services[@]}"
}

##############################################
# Step 5: Get Access URLs
##############################################
get_access_urls() {
    local urls=()
    
    # Localhost URLs
    urls+=("http://localhost:3000")
    urls+=("http://localhost:8080")
    urls+=("http://localhost:8000")
    
    # Codespaces URLs
    if [ -n "${CODESPACE_NAME:-}" ]; then
        local base_url="https://${CODESPACE_NAME}-"
        urls+=("${base_url}3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}")
        urls+=("${base_url}8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}")
        urls+=("${base_url}8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}")
    fi
    
    printf '%s\n' "${urls[@]}"
}

##############################################
# Step 6: Generate Report
##############################################
generate_report() {
    local failed_services="$1"
    
    info "إنشاء تقرير JSON..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local access_urls=$(get_access_urls | jq -R . | jq -s .)
    local container_status=$(docker-compose ps --format json 2>/dev/null | jq -s . || echo "[]")
    
    cat > "$REPORT_FILE" <<EOF
{
  "timestamp": "$timestamp",
  "status": "completed",
  "failed_services": $(echo "$failed_services" | jq -R . | jq -s . | jq 'map(select(length > 0))'),
  "access_urls": $access_urls,
  "services": $container_status,
  "environment": {
    "codespace": "${CODESPACE_NAME:-none}",
    "repo_root": "$REPO_ROOT"
  }
}
EOF
    
    ok "تم حفظ التقرير في: $REPORT_FILE"
}

##############################################
# Main Execution
##############################################
main() {
    info "═══════════════════════════════════════════"
    info "  Top-Tier Global HUB AI - Bot Run All"
    info "═══════════════════════════════════════════"
    echo ""
    
    # Execute all steps
    check_prerequisites || exit 1
    setup_environment
    start_services
    local failed_services=$(check_services_health)
    generate_report "$failed_services"
    
    # Display results
    echo ""
    info "═══════════════════════════════════════════"
    info "  نتائج التشغيل"
    info "═══════════════════════════════════════════"
    echo ""
    
    if [ -f "$REPORT_FILE" ]; then
        ok "تقرير JSON:"
        cat "$REPORT_FILE"
        echo ""
    fi
    
    info "روابط الوصول:"
    get_access_urls | while read -r url; do
        info "  → $url"
    done
    echo ""
    
    if [ -n "$failed_services" ]; then
        warn "الخدمات الفاشلة:"
        echo "$failed_services" | tr ' ' '\n' | while read -r svc; do
            [ -n "$svc" ] && err "  ✗ $svc"
        done
    else
        ok "جميع الخدمات تعمل بنجاح!"
    fi
    
    echo ""
    info "سجل التشغيل الكامل: $LOG_FILE"
    info "═══════════════════════════════════════════"
    
    # Display full log
    echo ""
    info "السجل الكامل:"
    echo "═══════════════════════════════════════════"
    cat "$LOG_FILE"
    echo "═══════════════════════════════════════════"
}

main "$@"
