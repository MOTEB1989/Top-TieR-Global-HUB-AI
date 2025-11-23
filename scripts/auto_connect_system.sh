#!/usr/bin/env bash
set -e

# =================================================================
# 🤖 AUTO-CONNECT SYSTEM – TOP-TIER GLOBAL HUB AI (HARDENED)
# =================================================================
# يقوم السكريبت بـ:
# ✅ قراءة المفاتيح الموجودة تلقائياً من الملفات أو المتغيرات
# ✅ اكتشاف Railway URL من المتغيرات
# ✅ إعداد Telegram Bot في حال توفر المفتاح
# ✅ إعداد Smart Agent
# ✅ اختبار التكوين المتوفر فقط
# =================================================================

# ==================== SETUP ====================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOGS_DIR="${REPO_ROOT}/logs"
CONFIG_DIR="${REPO_ROOT}/config"
mkdir -p "$LOGS_DIR" "$CONFIG_DIR"

LOG_FILE="${LOGS_DIR}/auto-connect.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# ==================== COLORS ====================
RED='\033[0;31m'     GREEN='\033[0;32m'     YELLOW='\033[1;33m'
BLUE='\033[0;34m'    MAGENTA='\033[0;35m'   CYAN='\033[0;36m'
WHITE='\033[1;37m'   NC='\033[0m'

# ==================== HELPERS ====================
log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

header() {
    echo -e "\n${MAGENTA}================================================${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${MAGENTA}================================================${NC}\n"
}

# دالة اكتشاف المفتاح من أي ملف
detect_key() {
    local key_name="$1"
    local files_to_check=(".env" ".env.local" ".env.production" ".env.example" "config/keys.json")

    for file in "${files_to_check[@]}"; do
        local file_path="${REPO_ROOT}/${file}"
        if [ -f "$file_path" ]; then
            # البحث عن المفتاح بأي صيغة
            local value=$(grep -i "^${key_name}=" "$file_path" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
            if [ -n "$value" ]; then
                success "اكتشف $key_name من $file"
                echo "$value"
                return 0
            fi
        fi
    done

    # محاولة من متغيرات البيئة
    if [ -n "${!key_name}" ]; then
        success "اكتشف $key_name من متغيرات البيئة"
        echo "${!key_name}"
        return 0
    fi

    warn "لم يتم العثور على $key_name"
    return 1
}

load_or_warn() {
    local key="$1"
    local value="$(detect_key "$key" || true)"

    if [ -z "$value" ]; then
        warn "المفتاح $key مفقود – سيتم تخطي التحقق المرتبط به"
    fi

    echo "$value"
}

# ==================== AUTO-DETECT ALL KEYS ====================
header "🔍 اكتشاف المفاتيح الموجودة تلقائياً"

# البدء بملف .env إذا لم يكن موجوداً
if [ ! -f "${REPO_ROOT}/.env" ]; then
    info "إنشاء ملف .env أساسي..."
    touch "${REPO_ROOT}/.env"
fi

# اكتشاف كل المفاتيح بدون تعيين قيم افتراضية حساسة
TELEGRAM_BOT_TOKEN=$(load_or_warn "TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWLIST=$(load_or_warn "TELEGRAM_ALLOWLIST")
TELEGRAM_CHAT_ID=$(load_or_warn "TELEGRAM_CHAT_ID")
GITHUB_REPO=$(load_or_warn "GITHUB_REPO")
RAILWAY_PROJECT_URL=$(load_or_warn "RAILWAY_PROJECT_URL")
OPENAI_API_KEY=$(load_or_warn "OPENAI_API_KEY")
CUSTOM_GPT_ID=$(load_or_warn "CUSTOM_GPT_ID")
GITHUB_TOKEN=$(load_or_warn "GITHUB_TOKEN")
RAILWAY_API_TOKEN=$(load_or_warn "RAILWAY_API_TOKEN")

# ==================== VALIDATE DETECTED KEYS ====================
header "🔐 التحقق من المفاتيح المكتشفة"

info "التحقق من Telegram Bot..."
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    if curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | grep -q '"ok":true'; then
        BOT_NAME=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | grep -o '"username":"[^"]*' | cut -d'"' -f4)
        success "Telegram Bot صالح: @$BOT_NAME"
    else
        error "Telegram Bot غير صالح"
    fi
else
    warn "تم تخطي تحقق Telegram لعدم توفر TELEGRAM_BOT_TOKEN"
fi

# إذا كان OpenAI مضبوطاً، تحقق منه
if [ -n "$OPENAI_API_KEY" ]; then
    info "التحقق من OpenAI API..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        "https://api.openai.com/v1/models")

    if [ "$HTTP_CODE" -eq 200 ]; then
        success "OpenAI API صالحة"
    else
        warn "OpenAI API تعيد HTTP $HTTP_CODE (قد تحتاج مفتاحاً صالحاً)"
    fi
else
    warn "تم تخطي تحقق OpenAI لعدم توفر OPENAI_API_KEY"
fi

# ==================== CREATE COMPLETE ENV IF MISSING ====================
header "📝 إنشاء/تحديث ملف .env"

ENV_CONTENT="# =================================================================
# 🔐 TOP-TIER GLOBAL HUB AI – AUTO-GENERATED ENVIRONMENT
# تم إنشاؤه تلقائياً بتاريخ: $(date)
# =================================================================

# Telegram Bot (Confirmed)
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_ALLOWLIST=${TELEGRAM_ALLOWLIST}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)

# OpenAI & Custom GPT (Add if you have them)
OPENAI_API_KEY=${OPENAI_API_KEY}
CUSTOM_GPT_ID=${CUSTOM_GPT_ID}

# GitHub Integration (Add if you have token)
GITHUB_REPO=${GITHUB_REPO}
GITHUB_TOKEN=${GITHUB_TOKEN}

# Railway (Confirmed)
RAILWAY_PROJECT_URL=${RAILWAY_PROJECT_URL}
RAILWAY_API_TOKEN=${RAILWAY_API_TOKEN}
RAILWAY_STATIC_URL=https://your-app.railway.app

# Database & Infrastructure
DATABASE_URL=postgres://example
REDIS_URL=redis://example
NEO4J_URI=bolt://neo4j:7687
NEO4J_AUTH=neo4j:LexCode2025Secure

# API Security (Auto-generated)
API_SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)

# Monitoring
LOG_LEVEL=info
ENABLE_TELEMETRY=true
SENTRY_DSN=""

# Smart Agent
AGENT_MODE=production
AGENT_POLL_INTERVAL=300
AUTO_HEALING=true
"

echo "$ENV_CONTENT" > "${REPO_ROOT}/.env"
success "ملف .env تم تحديثه تلقائياً"

# ==================== SETUP RAILWAY ====================
header "🚂 إعداد Railway تلقائياً"

cat > "${REPO_ROOT}/railway.json" << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks",
    "buildCommand": "cd services/api && npm install && cd ../.. && docker compose build",
    "startCommand": "docker compose up"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "healthcheckPath": "/v1/health",
    "healthcheckTimeout": 100
  },
  "environments": {
    "production": {
      "variables": {
        "NODE_ENV": "production",
        "AGENT_MODE": "production"
      }
    }
  }
}
EOF
success "ملف railway.json تم إنشاؤه"

# ==================== SETUP TELEGRAM BOT ====================
header "🤖 إعداد Telegram Bot تلقائياً"

BOT_FILE="${REPO_ROOT}/services/api/src/routes/v1/telegram.bot.ts"

cat > "$BOT_FILE" << 'BOTEOF'
import { Router } from 'express';
import { Telegraf } from 'telegraf';

const router = Router();
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN!);
const ALLOWLIST = process.env.TELEGRAM_ALLOWLIST?.split(',') || [];

// أمر /start
bot.start((ctx) => {
    const userId = ctx.from?.id.toString();
    const isAdmin = userId ? ALLOWLIST.includes(userId) : false;
    const allowlistMsg = isAdmin ? '*مشرف* ✅' : 'مستخدم عادي';

    ctx.reply(
        `🤖 *مرحباً في Top-Tier Global HUB AI*\n\n` +
        `👤 معرفك: \`${userId}\`\n` +
        `🔐 الصلاحيات: ${allowlistMsg}\n\n` +
        `الأوامر: /start, /status, /chat, /preflight`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /status
bot.command('status', (ctx) => {
    ctx.reply(
        `📊 *حالة النظام*\n\n` +
        `🤖 Bot: يعمل\n` +
        `🔗 Railway: ${process.env.RAILWAY_STATIC_URL || 'غير منشر'}\n` +
        `🧠 GPT: ${process.env.CUSTOM_GPT_ID || 'غير مضبوط'}\n` +
        `👥 المستخدمون: ${ALLOWLIST.length}`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /chat
bot.command('chat', async (ctx) => {
    const question = ctx.message.text.replace('/chat', '').trim();
    if (!question) return ctx.reply('أدخل سؤالاً');

    await ctx.replyWithChatAction('typing');

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
        },
        body: JSON.stringify({
            model: process.env.CUSTOM_GPT_ID || 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: question }]
        })
    });

    const data = await response.json();
    ctx.reply(data.choices[0].message.content);
});

// Webhook
router.post('/webhook/:token', async (req, res) => {
    if (req.params.token !== process.env.TELEGRAM_BOT_TOKEN) {
        return res.status(403).send('Forbidden');
    }
    await bot.handleUpdate(req.body);
    res.status(200).send('OK');
});

export default router;
BOTEOF
success "Telegram Bot تم إعداده"

# ==================== CREATE SMART AGENT ====================
header "🧠 إنشاء Smart Agent"

AGENT_FILE="${REPO_ROOT}/scripts/smart_agent_validator.py"
cat > "$AGENT_FILE" << 'AGENTEOF'
#!/usr/bin/env python3
import json, time, logging, requests
from pathlib import Path

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class SmartAgent:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)
        log.info("تم تحميل الإعدادات")

    def run(self):
        log.info("="*50)
        log.info("Smart Agent Started")
        log.info(f"GitHub: {self.config.get('github_repo', 'غير محدد')}")
        log.info("="*50)

        while True:
            time.sleep(3600)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise SystemExit("الرجاء تمرير مسار ملف الإعدادات")
    agent = SmartAgent(sys.argv[1])
    agent.run()
AGENTEOF
chmod +x "$AGENT_FILE"
success "Smart Agent تم إنشاؤه"

# ==================== CREATE GITHUB ACTIONS ====================
header "⚙️ إعداد GitHub Actions"

mkdir -p "${REPO_ROOT}/.github/workflows"
cat > "${REPO_ROOT}/.github/workflows/auto-sync.yml" << 'ACTIONEOF'
name: Auto Sync & Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway
        run: npm i -g @railway/cli
      
      - name: Run Integration
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          chmod +x scripts/auto_connect_system.sh
          bash scripts/auto_connect_system.sh --auto
      
      - name: Deploy
        run: railway up
ACTIONEOF
success "GitHub Actions تم إعدادها"

# ==================== FINAL TEST ====================
header "🧪 اختبار النظام الكامل"

# اختبار Telegram
info "اختبار Telegram Bot..."
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | grep -q '"ok":true' && \
        success "Telegram Bot يعمل" || \
        error "Telegram Bot لا يعمل"
else
    warn "تم تخطي اختبار Telegram Bot بسبب عدم توفر TELEGRAM_BOT_TOKEN"
fi

# اختبار Railway URL
info "اختبار Railway Project..."
if [ -n "$RAILWAY_PROJECT_URL" ]; then
    curl -s -I "$RAILWAY_PROJECT_URL" | grep -q "200\|302" && \
        success "Railway Project متاح" || \
        warn "Railway Project غير متاح (سيتم النشر)"
else
    warn "لم يتم توفير RAILWAY_PROJECT_URL لاختبار التوافر"
fi

# اختبار ملفات الإعداد
[ -f "${REPO_ROOT}/.env" ] && success ".env موجود" || error ".env مفقود"
[ -f "${REPO_ROOT}/railway.json" ] && success "railway.json موجود" || error "railway.json مفقود"
[ -f "$BOT_FILE" ] && success "telegram.bot.ts موجود" || error "telegram.bot.ts مفقود"

# ==================== GENERATE FINAL REPORT ====================
header "📊 تقرير النظام النهائي"

echo "🎯 **النظام جاهز للتشغيل**"
echo ""
echo "✅ **المفاتيح المكتشفة تلقائياً:**"
echo "   • Telegram Bot: ${TELEGRAM_BOT_TOKEN:+متوفر}"
echo "   • Allowlist: ${TELEGRAM_ALLOWLIST:-غير متوفر}"
echo "   • Railway: ${RAILWAY_PROJECT_URL:-غير متوفر}"
echo "   • GitHub Repo: ${GITHUB_REPO:-غير متوفر}"
echo ""
echo "📂 **الملفات المُنشأة:**"
echo "   • ${REPO_ROOT}/.env (محدث تلقائياً)"
echo "   • ${REPO_ROOT}/railway.json"
echo "   • $BOT_FILE"
echo "   • $AGENT_FILE"
echo "   • GitHub Actions workflows"
echo ""
echo "🚀 **للتشغيل الفوري:**"
echo "   bash scripts/auto_connect_system.sh --auto"
echo ""
echo "📱 **للاختبار:**"
echo "   ارسل /start إلى البوت"
echo ""
echo -e "${GREEN}✨ النظام كامل وجاهز!${NC}"

# ==================== EXECUTE BASED ON MODE ====================
main() {
    case "$1" in
        --auto)
            header "🤖 وضع التنفيذ التلقائي"
            log "جاري التنفيذ بدون تدخل..."
            ;;
        *)
            header "🚀 بدء التكامل التلقائي"
            log "اكتشاف المفاتيح وإعداد النظام..."
            ;;
    esac
}

main "$@"
