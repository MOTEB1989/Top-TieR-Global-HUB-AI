#!/usr/bin/env bash
set -euo pipefail

##############################################
# Ultra Preflight Check
# فحص شامل قبل تشغيل النظام
# يتحقق من جميع المتطلبات والإعدادات
##############################################

# ========== Colors ==========
C_RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_BLUE=$'\033[34m'
C_CYAN=$'\033[36m'
C_PURPLE=$'\033[35m'
C_BOLD=$'\033[1m'

# ========== Helper Functions ==========
log()   { printf "%s\n" "$*"; }
info()  { log "${C_BLUE}ℹ${C_RESET} $*"; }
ok()    { log "${C_GREEN}✅${C_RESET} $*"; }
warn()  { log "${C_YELLOW}⚠️${C_RESET} $*"; }
err()   { log "${C_RED}❌ $*${C_RESET}"; }
header() { log ""; log "${C_BOLD}${C_PURPLE}========== $* ==========${C_RESET}"; }

ERRORS=0
WARNINGS=0

check_pass() { ok "$1"; }
check_warn() { warn "$1"; ((WARNINGS++)); }
check_fail() { err "$1"; ((ERRORS++)); }

# ========== Detection Functions ==========
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "Windows"
    else
        echo "Unknown"
    fi
}

detect_ip() {
    local ip=""
    if command -v ipconfig >/dev/null 2>&1; then
        ip=$(ipconfig getifaddr en0 2>/dev/null || true)
    fi
    if [[ -z "$ip" ]] && command -v hostname >/dev/null 2>&1; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
    if [[ -z "$ip" ]]; then
        ip=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' || echo "")
    fi
    echo "${ip:-localhost}"
}

get_free_memory() {
    if command -v free >/dev/null 2>&1; then
        free -h | awk '/^Mem:/ {print $7}'
    elif command -v vm_stat >/dev/null 2>&1; then
        echo "$(vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\.//')KB"
    else
        echo "N/A"
    fi
}

get_disk_space() {
    df -h . | awk 'NR==2 {print $4}'
}

# ========== Main Checks ==========
echo "${C_BOLD}${C_CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════╗
║   Ultra Preflight Check                   ║
║   Top-TieR Global HUB AI                  ║
║   الفحص الشامل قبل التشغيل              ║
╚═══════════════════════════════════════════╝
EOF
echo "${C_RESET}"

# ========== System Information ==========
header "معلومات النظام"

OS_TYPE=$(detect_os)
LOCAL_IP=$(detect_ip)
FREE_MEM=$(get_free_memory)
DISK_SPACE=$(get_disk_space)

info "نظام التشغيل: ${C_CYAN}$OS_TYPE${C_RESET}"
info "العنوان المحلي: ${C_CYAN}$LOCAL_IP${C_RESET}"
info "الذاكرة المتاحة: ${C_CYAN}$FREE_MEM${C_RESET}"
info "المساحة المتاحة: ${C_CYAN}$DISK_SPACE${C_RESET}"

if [[ -n "${CODESPACE_NAME:-}" ]]; then
    info "البيئة: ${C_CYAN}GitHub Codespaces${C_RESET}"
fi

# ========== Repository Structure ==========
header "بنية المستودع"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
info "جذر المستودع: ${C_CYAN}$REPO_ROOT${C_RESET}"
cd "$REPO_ROOT"

REQUIRED_DIRS=("scripts" "core" "app" "data" "db" "k8s" "policies" "utils")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        check_pass "المجلد موجود: $dir"
    else
        check_warn "المجلد غير موجود: $dir"
    fi
done

# ========== Docker Checks ==========
header "فحص Docker"

if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    check_pass "Docker مُثبت: $DOCKER_VERSION"
    
    # Check Docker daemon
    if docker info >/dev/null 2>&1; then
        check_pass "Docker daemon يعمل"
        
        # Docker resources
        DOCKER_MEM=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo "N/A")
        info "ذاكرة Docker المتاحة: $(numfmt --to=iec ${DOCKER_MEM:-0} 2>/dev/null || echo $DOCKER_MEM)"
    else
        check_fail "Docker daemon لا يعمل"
    fi
else
    check_fail "Docker غير مُثبت"
fi

# Check Docker Compose
if docker compose version >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
    check_pass "Docker Compose مُثبت: $COMPOSE_VERSION"
else
    check_fail "Docker Compose غير متوفر"
fi

# ========== Configuration Files ==========
header "ملفات الإعدادات"

# Check docker-compose files
COMPOSE_FILES=("docker-compose.yml" "docker-compose.rag.yml")
for file in "${COMPOSE_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        check_pass "موجود: $file"
        
        # Validate syntax
        if docker compose -f "$file" config >/dev/null 2>&1; then
            check_pass "صحيح: $file"
        else
            check_fail "خطأ في بناء: $file"
        fi
    else
        check_warn "غير موجود: $file"
    fi
done

# Check .env file
if [[ -f ".env" ]]; then
    check_pass "ملف .env موجود"
    
    # Check for empty API keys
    EMPTY_KEYS=()
    for key in OPENAI_API_KEY GROQ_API_KEY ANTHROPIC_API_KEY; do
        if ! grep -q "^${key}=" .env; then
            EMPTY_KEYS+=("$key")
        elif grep -q "^${key}=$" .env; then
            EMPTY_KEYS+=("$key")
        fi
    done
    
    if [[ ${#EMPTY_KEYS[@]} -gt 0 ]]; then
        check_warn "مفاتيح API فارغة: ${EMPTY_KEYS[*]}"
    else
        check_pass "جميع مفاتيح API مُعرّفة"
    fi
else
    check_warn "ملف .env غير موجود (سيتم توليده)"
fi

# ========== Scripts Checks ==========
header "السكربتات"

SCRIPTS=(
    "scripts/run_everything.sh"
    "scripts/check_environment.sh"
    "scripts/test_all.sh"
    "scripts/ultra_preflight.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            check_pass "قابل للتنفيذ: $script"
        else
            check_warn "غير قابل للتنفيذ: $script (سيتم إصلاحه)"
            chmod +x "$script" 2>/dev/null && check_pass "تم إعطاء صلاحية التنفيذ" || check_fail "فشل في إعطاء الصلاحية"
        fi
        
        # Check bash syntax
        if bash -n "$script" 2>/dev/null; then
            check_pass "بناء صحيح: $script"
        else
            check_fail "خطأ في البناء: $script"
        fi
    else
        check_warn "غير موجود: $script"
    fi
done

# ========== Port Availability ==========
header "فحص المنافذ"

PORTS=(3000 8081 8082 6333 8501 7474 7687)
PORT_NAMES=(
    "3000:Gateway"
    "8081:RAG_Engine"
    "8082:Phi3"
    "6333:Qdrant"
    "8501:Web_UI"
    "7474:Neo4j_HTTP"
    "7687:Neo4j_Bolt"
)

for port_name in "${PORT_NAMES[@]}"; do
    port="${port_name%%:*}"
    name="${port_name##*:}"
    
    if command -v lsof >/dev/null 2>&1; then
        if lsof -iTCP -sTCP:LISTEN -n 2>/dev/null | grep -q ":$port "; then
            check_warn "المنفذ $port ($name) مستخدم"
        else
            check_pass "المنفذ $port ($name) متاح"
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            check_warn "المنفذ $port ($name) مستخدم"
        else
            check_pass "المنفذ $port ($name) متاح"
        fi
    else
        info "تخطي فحص المنفذ $port (أداة الفحص غير متوفرة)"
    fi
done

# ========== Python Environment ==========
header "بيئة Python"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    check_pass "Python مُثبت: $PYTHON_VERSION"
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        check_pass "pip مُثبت"
    else
        check_warn "pip غير مُثبت"
    fi
    
    # Check requirements.txt
    if [[ -f "requirements.txt" ]]; then
        check_pass "requirements.txt موجود"
    else
        check_warn "requirements.txt غير موجود"
    fi
else
    check_warn "Python غير مُثبت"
fi

# ========== Git Checks ==========
header "فحص Git"

if command -v git >/dev/null 2>&1; then
    check_pass "Git مُثبت: $(git --version | cut -d' ' -f3)"
    
    if git rev-parse --git-dir >/dev/null 2>&1; then
        check_pass "داخل مستودع Git"
        
        BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
        info "الفرع الحالي: ${C_CYAN}$BRANCH${C_RESET}"
        
        # Check for uncommitted changes
        if git diff-index --quiet HEAD -- 2>/dev/null; then
            check_pass "لا توجد تعديلات غير محفوظة"
        else
            check_warn "توجد تعديلات غير محفوظة"
        fi
    else
        check_warn "ليس مستودع Git"
    fi
else
    check_warn "Git غير مُثبت"
fi

# Check GitHub CLI
if command -v gh >/dev/null 2>&1; then
    check_pass "GitHub CLI مُثبت"
    
    if gh auth status >/dev/null 2>&1; then
        check_pass "مُسجل الدخول إلى GitHub"
    else
        check_warn "غير مُسجل الدخول إلى GitHub CLI"
    fi
else
    check_warn "GitHub CLI غير مُثبت"
fi

# ========== Network Connectivity ==========
header "الاتصال بالشبكة"

# Check internet connectivity
if curl -s --max-time 5 https://www.google.com >/dev/null 2>&1; then
    check_pass "الاتصال بالإنترنت متاح"
else
    check_warn "لا يوجد اتصال بالإنترنت"
fi

# Check Docker Hub
if curl -s --max-time 5 https://hub.docker.com >/dev/null 2>&1; then
    check_pass "يمكن الوصول إلى Docker Hub"
else
    check_warn "لا يمكن الوصول إلى Docker Hub"
fi

# Check GitHub
if curl -s --max-time 5 https://api.github.com >/dev/null 2>&1; then
    check_pass "يمكن الوصول إلى GitHub"
else
    check_warn "لا يمكن الوصول إلى GitHub"
fi

# ========== Running Containers ==========
header "الحاويات النشطة"

if docker ps >/dev/null 2>&1; then
    RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' | wc -l)
    if [[ $RUNNING_CONTAINERS -gt 0 ]]; then
        info "حاويات تعمل حالياً: ${C_CYAN}$RUNNING_CONTAINERS${C_RESET}"
        docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | while IFS= read -r line; do
            info "  $line"
        done
    else
        info "لا توجد حاويات تعمل حالياً"
    fi
fi

# ========== Final Summary ==========
echo ""
echo "${C_BOLD}${C_PURPLE}═══════════════════════════════════════════${C_RESET}"
echo "${C_BOLD}             ملخص النتائج${C_RESET}"
echo "${C_BOLD}${C_PURPLE}═══════════════════════════════════════════${C_RESET}"
echo ""

if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo "${C_GREEN}${C_BOLD}✅ جميع الفحوصات نجحت!${C_RESET}"
    echo "${C_GREEN}النظام جاهز للتشغيل${C_RESET}"
    EXIT_CODE=0
elif [[ $ERRORS -eq 0 ]]; then
    echo "${C_YELLOW}${C_BOLD}⚠️ التحذيرات: $WARNINGS${C_RESET}"
    echo "${C_YELLOW}يمكن المتابعة ولكن قد تواجه مشاكل${C_RESET}"
    EXIT_CODE=0
else
    echo "${C_RED}${C_BOLD}❌ الأخطاء: $ERRORS${C_RESET}"
    echo "${C_YELLOW}${C_BOLD}⚠️ التحذيرات: $WARNINGS${C_RESET}"
    echo ""
    echo "${C_RED}${C_BOLD}يُرجى إصلاح الأخطاء قبل المتابعة${C_RESET}"
    EXIT_CODE=1
fi

echo ""
echo "${C_PURPLE}═══════════════════════════════════════════${C_RESET}"
echo ""

# ========== Recommendations ==========
if [[ $ERRORS -gt 0 ]] || [[ $WARNINGS -gt 0 ]]; then
    echo "${C_BOLD}${C_CYAN}📋 التوصيات:${C_RESET}"
    echo ""
    
    if ! command -v docker >/dev/null 2>&1; then
        echo "  • قم بتثبيت Docker من: ${C_CYAN}https://docs.docker.com/get-docker/${C_RESET}"
    fi
    
    if ! command -v python3 >/dev/null 2>&1; then
        echo "  • قم بتثبيت Python 3 من: ${C_CYAN}https://www.python.org/downloads/${C_RESET}"
    fi
    
    if [[ ! -f ".env" ]]; then
        echo "  • أنشئ ملف .env بناءً على .env.example"
        echo "    ${C_CYAN}cp .env.example .env${C_RESET}"
    fi
    
    if ! gh auth status >/dev/null 2>&1; then
        echo "  • سجّل الدخول إلى GitHub CLI:"
        echo "    ${C_CYAN}gh auth login${C_RESET}"
    fi
    
    echo ""
fi

# ========== Next Steps ==========
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "${C_BOLD}${C_GREEN}🚀 الخطوات التالية:${C_RESET}"
    echo ""
    echo "  1️⃣  تشغيل جميع الخدمات:"
    echo "     ${C_CYAN}./scripts/run_everything.sh up${C_RESET}"
    echo ""
    echo "  2️⃣  تشغيل الاختبارات:"
    echo "     ${C_CYAN}./scripts/test_all.sh${C_RESET}"
    echo ""
    echo "  3️⃣  الوصول إلى واجهة الويب:"
    echo "     ${C_CYAN}http://$LOCAL_IP:8501${C_RESET}"
    echo ""
fi

exit $EXIT_CODE
