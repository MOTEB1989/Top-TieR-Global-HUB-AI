#!/bin/bash
set -e

# ============ إعدادات الألوان ============
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============ دوال مساعدة ============
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============ دوال التحقق ============
check_file_exists() {
    if [ -f "$1" ]; then
        log_success "✓ $1 موجود"
        return 0
    else
        log_error "✗ $1 مفقود"
        return 1
    fi
}

load_env() {
    if [ -f ".env" ]; then
        log_info "تحميل متغيرات البيئة..."
        set -a
        source .env
        set +a
    else
        log_warn "ملف .env غير موجود، سيتم استخدام .env.example"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "يرجى تحرير ملف .env وإضافة المفاتيح الحقيقية"
            exit 1
        else
            log_error "ملف .env.example غير موجود"
            exit 1
        fi
    fi
}

check_docker_service() {
    local service=$1
    local port=$2
    
    if docker compose ps 2>/dev/null | grep -q "$service.*Up"; then
        log_success "✓ خدمة $service تعمل"
        
        # التحقق من المنفذ
        if command -v nc &> /dev/null && nc -z localhost $port 2>/dev/null; then
            log_success "✓ المنفذ $port مفتوح"
        elif command -v ss &> /dev/null && ss -ltn | grep -q ":$port "; then
            log_success "✓ المنفذ $port مفتوح"
        else
            log_warn "⚠ لا يمكن التحقق من المنفذ $port"
        fi
    else
        log_error "✗ خدمة $service متوقفة"
        return 1
    fi
}

# ============ التحقق من المستودع ============
validate_repository() {
    log_info "جاري التحقق من مستودع GitHub..."
    
    REPO_URL="https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI"
    
    if curl -s --head --max-time 10 $REPO_URL | head -n 1 | grep -q "200\|302"; then
        log_success "✓ المستودع متاح على GitHub"
    else
        log_warn "⚠ لا يمكن الوصول إلى المستودع (قد تكون مشكلة اتصال)"
    fi
}

# ============ التحقق من ملفات المشروع ============
validate_project_files() {
    log_info "التحقق من ملفات المشروع..."
    
    required_files=(
        "docker-compose.yml"
        ".env.example"
        "scripts/check_connections.sh"
    )
    
    optional_files=(
        "Cargo.toml"
        "package.json"
    )
    
    for file in "${required_files[@]}"; do
        check_file_exists "$file" || exit 1
    done
    
    for file in "${optional_files[@]}"; do
        check_file_exists "$file" || log_warn "⚠ $file غير موجود (اختياري)"
    done
}

# ============ التحقق من متغيرات البيئة ============
validate_env_variables() {
    log_info "التحقق من متغيرات البيئة..."
    
    # المتغيرات الأساسية
    required_vars=(
        "TELEGRAM_BOT_TOKEN"
        "TELEGRAM_CHAT_ID"
    )
    
    optional_vars=(
        "OPENAI_API_KEY"
        "GROQ_API_KEY"
        "ANTHROPIC_API_KEY"
        "TELEGRAM_ALLOWLIST"
        "GITHUB_TOKEN"
        "DB_URL"
        "REDIS_URL"
        "NEO4J_URI"
        "NEO4J_AUTH"
    )
    
    missing_required=0
    
    for var in "${required_vars[@]}"; do
        val="${!var}"
        if [ -n "$val" ]; then
            len=${#val}
            log_success "✓ $var موجود ($len حرف)"
        else
            log_error "✗ $var غير موجود (مطلوب)"
            ((missing_required++))
        fi
    done
    
    for var in "${optional_vars[@]}"; do
        val="${!var}"
        if [ -n "$val" ]; then
            len=${#val}
            log_success "✓ $var موجود ($len حرف)"
        else
            log_warn "⚠ $var غير موجود (اختياري)"
        fi
    done
    
    if [ $missing_required -gt 0 ]; then
        log_error "يرجى إضافة المتغيرات المطلوبة في ملف .env"
        exit 1
    fi
    
    # التحقق الخاص من TELEGRAM_BOT_TOKEN
    if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
        log_info "التحقق من صحة توكن Telegram..."
        response=$(curl -s --max-time 10 https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe)
        if echo "$response" | grep -q '"ok":true'; then
            bot_name=$(echo "$response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
            log_success "✓ توكن Telegram صالح (@$bot_name)"
        else
            log_error "✗ توكن Telegram غير صالح"
            echo "$response"
            exit 1
        fi
    fi
}

# ============ التحقق من Docker Compose ============
validate_docker_setup() {
    log_info "التحقق من إعداد Docker..."
    
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version)
        log_success "✓ Docker مثبت: $docker_version"
    else
        log_error "✗ Docker غير مثبت"
        exit 1
    fi
    
    if docker compose version &> /dev/null; then
        compose_version=$(docker compose version)
        log_success "✓ Docker Compose متاح: $compose_version"
    else
        log_error "✗ Docker Compose غير متاح"
        exit 1
    fi
    
    # التحقق من تشغيل Docker daemon
    if ! docker info &> /dev/null; then
        log_error "✗ Docker daemon لا يعمل"
        exit 1
    fi
}

# ============ تشغيل الخدمات ============
start_services() {
    log_info "بناء وتشغيل الخدمات..."
    
    if docker compose up -d --build 2>&1; then
        log_success "✓ تم بناء وتشغيل الخدمات"
    else
        log_error "✗ فشل تشغيل الخدمات"
        docker compose logs --tail=50
        exit 1
    fi
    
    log_info "انتظار بدء الخدمات (30 ثانية)..."
    sleep 30
    
    # التحقق من الخدمات
    log_info "التحقق من حالة الخدمات..."
    docker compose ps
}

# ============ اختبار بسيط من Telegram ============
send_test_message() {
    log_info "إرسال رسالة اختبار إلى Telegram..."
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
        log_warn "⚠ لا يمكن إرسال رسالة اختبار: TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID مفقود"
        return 1
    fi
    
    message="🎉 اختبار شامل من سكربت comprehensive_setup_and_test.sh

✅ المستودع: MOTEB1989/Top-TieR-Global-HUB-AI
⏰ الوقت: $(date -u +'%Y-%m-%d %H:%M:%S UTC')
🖥️ المضيف: $(hostname)

📊 الحالة: جميع الفحوصات نجحت!"
    
    response=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${message}")
    
    if echo "$response" | grep -q '"ok":true'; then
        log_success "✓ تم إرسال رسالة الاختبار بنجاح"
    else
        log_error "✗ فشل إرسال رسالة الاختبار"
        echo "$response"
    fi
}

# ============ عرض ملخص نهائي ============
show_summary() {
    echo ""
    echo "=========================================="
    echo "📊 ملخص الإعداد والاختبار"
    echo "=========================================="
    echo ""
    
    # حالة Docker
    echo "🐳 خدمات Docker:"
    docker compose ps 2>/dev/null || log_warn "لا يمكن عرض حالة Docker"
    echo ""
    
    # المتغيرات البيئية
    echo "🔑 المتغيرات البيئية:"
    for var in TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID OPENAI_API_KEY GROQ_API_KEY; do
        if [ -n "${!var}" ]; then
            echo "  ✅ $var"
        else
            echo "  ❌ $var"
        fi
    done
    echo ""
    
    # التعليمات
    echo "📋 الخطوات التالية:"
    echo "  1. راجع السجلات: docker compose logs -f"
    echo "  2. اختبر check_connections: bash scripts/check_connections.sh"
    echo "  3. عرض التقرير: cat reports/check_connections.json"
    echo ""
    echo "=========================================="
}

# ============ تنظيف الموارد ============
cleanup() {
    log_info "تنظيف الموارد..."
    # يمكن إضافة عمليات تنظيف إضافية هنا
}

# ============ سكريبت رئيسي ============
main() {
    log_info "🚀 بدء سكريبت التحقق والإعداد الشامل..."
    echo ""
    
    # التحقق من المستودع
    validate_repository
    echo ""
    
    # التحقق من ملفات المشروع
    validate_project_files
    echo ""
    
    # التحقق من Docker
    validate_docker_setup
    echo ""
    
    # تحميل البيئة
    load_env
    echo ""
    
    # التحقق من المتغيرات
    validate_env_variables
    echo ""
    
    # سؤال المستخدم قبل تشغيل Docker
    echo "هل تريد بناء وتشغيل خدمات Docker؟ (y/n)"
    read -r start_docker
    
    if [ "$start_docker" = "y" ] || [ "$start_docker" = "Y" ]; then
        start_services
        echo ""
    else
        log_info "تم تخطي تشغيل Docker"
        echo ""
    fi
    
    # إرسال رسالة اختبار
    send_test_message
    echo ""
    
    # عرض الملخص
    show_summary
    
    log_success "🎉 اكتملت جميع الإجراءات!"
}

# التقاط الإشارات لضمان التنظيف
trap cleanup EXIT INT TERM

# تشغيل السكريبت
main "$@"
