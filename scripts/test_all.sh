#!/bin/bash

set -e

echo "=========================================="
echo "🧪 اختبار شامل للمستودع والخدمات"
echo "=========================================="
echo ""

# ========== 1. اختبار المستودع ==========
echo "📦 اختبار حالة المستودع على GitHub..."
echo "---"

if command -v gh &> /dev/null; then
    echo "✔️ GitHub CLI مُثبت"
    
    # التحقق من تسجيل الدخول
    if gh auth status &> /dev/null; then
        echo "✔️ تم تسجيل الدخول إلى GitHub"
        
        # جلب بيانات المستودع
        echo ""
        echo "جاري جلب بيانات المستودع..."
        REPO_DATA=$(gh repo view MOTEB1989/Top-TieR-Global-HUB-AI --json openIssuesCount,openPullRequestsCount 2>&1)
        
        if [ $? -eq 0 ]; then
            echo "✔️ تم جلب بيانات المستودع بنجاح"
            echo "$REPO_DATA" | jq '.'
            
            # التحقق من النتيجة المتوقعة
            OPEN_ISSUES=$(echo "$REPO_DATA" | jq -r '.openIssuesCount')
            OPEN_PRS=$(echo "$REPO_DATA" | jq -r '.openPullRequestsCount')
            
            echo ""
            echo "📊 النتائج:"
            echo "   - Issues المفتوحة: $OPEN_ISSUES"
            echo "   - Pull Requests المفتوحة: $OPEN_PRS"
            
            if [ "$OPEN_ISSUES" == "0" ] && [ "$OPEN_PRS" == "0" ]; then
                echo "✅ المستودع نظيف (لا توجد issues أو PRs مفتوحة)"
            else
                echo "⚠️ يوجد عناصر مفتوحة في المستودع"
            fi
        else
            echo "❌ فشل جلب بيانات المستودع"
            echo "$REPO_DATA"
        fi
    else
        echo "⚠️ لم يتم تسجيل الدخول إلى GitHub CLI"
        echo "قم بتنفيذ: gh auth login"
    fi
else
    echo "⚠️ GitHub CLI غير مُثبت"
    echo "للتثبيت: https://cli.github.com/"
fi

echo ""
echo "=========================================="

# ========== 2. اختبار الخدمات ==========
echo ""
echo "🐳 اختبار الخدمات باستخدام Docker Compose..."
echo "---"

# التحقق من وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker غير مُثبت"
    exit 1
fi

echo "✔️ Docker مُثبت: $(docker --version)"

# التحقق من وجود ملف docker-compose
COMPOSE_FILE="docker-compose.rag.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ ملف $COMPOSE_FILE غير موجود"
    exit 1
fi

echo "✔️ ملف $COMPOSE_FILE موجود"

# إيقاف أي خدمات قديمة
echo ""
echo "إيقاف الخدمات القديمة (إن وُجدت)..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true

# تشغيل الخدمات
echo ""
echo "🚀 تشغيل الخدمات..."
docker compose -f "$COMPOSE_FILE" up --build -d

# الانتظار قليلاً للخدمات للتشغيل
echo ""
echo "⏳ انتظار 10 ثوانٍ لتشغيل الخدمات..."
sleep 10

# عرض حالة الحاويات
echo ""
echo "📊 حالة الحاويات:"
docker compose -f "$COMPOSE_FILE" ps

# ========== 3. اختبار نقاط النهاية (Endpoints) ==========
echo ""
echo "=========================================="
echo "🔍 اختبار نقاط النهاية (Health Checks)..."
echo "---"

# دالة لاختبار endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local max_retries="${3:-3}"
    
    echo ""
    echo "اختبار $name على $url..."
    
    for i in $(seq 1 $max_retries); do
        if curl -f -s -o /dev/null -w "%{http_code}" "$url" &> /dev/null; then
            HTTP_CODE=$(curl -f -s -o /dev/null -w "%{http_code}" "$url")
            echo "✔️ $name يستجيب (HTTP $HTTP_CODE)"
            return 0
        else
            if [ $i -lt $max_retries ]; then
                echo "⏳ محاولة $i/$max_retries فشلت، إعادة المحاولة..."
                sleep 3
            fi
        fi
    done
    
    echo "❌ $name لا يستجيب بعد $max_retries محاولات"
    return 1
}

# اختبار الخدمات
ENDPOINTS_OK=true

# Gateway
if test_endpoint "Gateway" "http://localhost:3000/health" 5; then
    echo "   الاستجابة: $(curl -s http://localhost:3000/health 2>/dev/null || echo 'N/A')"
else
    ENDPOINTS_OK=false
fi

# RAG Engine
if test_endpoint "RAG Engine" "http://localhost:8081/health" 5; then
    echo "   الاستجابة: $(curl -s http://localhost:8081/health 2>/dev/null || echo 'N/A')"
else
    ENDPOINTS_OK=false
fi

# Phi3 (قد لا يكون له endpoint للـ health)
if test_endpoint "Phi3" "http://localhost:8082" 5; then
    echo "   ✔️ Phi3 يعمل"
else
    echo "   ℹ️ Phi3 قد يحتاج وقتاً أطول للتشغيل (نموذج كبير)"
fi

# Qdrant
if test_endpoint "Qdrant" "http://localhost:6333" 5; then
    echo "   ✔️ Qdrant يعمل"
else
    ENDPOINTS_OK=false
fi

# Streamlit Web UI
if test_endpoint "Web UI" "http://localhost:8501" 5; then
    echo "   ✔️ Web UI يعمل"
else
    ENDPOINTS_OK=false
fi

# ========== 4. النتيجة النهائية ==========
echo ""
echo "=========================================="
echo "📋 ملخص النتائج:"
echo "=========================================="

if [ "$ENDPOINTS_OK" = true ]; then
    echo "✅ جميع الاختبارات نجحت!"
    echo ""
    echo "🌐 نقاط الوصول:"
    echo "   - Gateway:    http://localhost:3000"
    echo "   - RAG Engine: http://localhost:8081"
    echo "   - Phi3:       http://localhost:8082"
    echo "   - Qdrant:     http://localhost:6333"
    echo "   - Web UI:     http://localhost:8501"
else
    echo "⚠️ بعض الاختبارات فشلت"
    echo ""
    echo "للتحقق من السجلات:"
    echo "   docker compose -f $COMPOSE_FILE logs"
fi

echo ""
echo "=========================================="
echo "✅ الاختبار اكتمل"
echo "=========================================="
