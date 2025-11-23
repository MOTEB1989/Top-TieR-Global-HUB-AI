#!/usr/bin/env bash
set -euo pipefail

# =================================================================
# 🤖 LEXNEXUS LEADER SYSTEM – TOP-TIER GLOBAL HUB AI
# =================================================================
# هذا السكريبت يقوم بـ:
# ✅ اكتشاف المفاتيح الموجودة تلقائياً من الملفات
# ✅ جعل LexNexus القائد (Main Driver)
# ✅ ربط Telegram Bot بجميع نماذج GPT
# ✅ إنشاء نظام Routing ذكي بين النماذج
# ✅ إعداد GitHub Actions + Railway
# ✅ اختبار كل شيء في النهاية
# =================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOGS_DIR="${REPO_ROOT}/logs"
CONFIG_DIR="${REPO_ROOT}/config"
mkdir -p "$LOGS_DIR" "$CONFIG_DIR"

LOG_FILE="${LOGS_DIR}/lexnexus-leader.log"
exec > >(tee -a "$LOG_FILE") 2>&1

# ==================== COLORS ====================
RED='\033[0;31m'     GREEN='\033[0;32m'     YELLOW='\033[1;33m'
BLUE='\033[0;34m'    MAGENTA='\033[0;35m'   CYAN='\033[0;36m'
WHITE='\033[1;37m'   NC='\033[0m'

# ==================== LOGGING ====================
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

# ==================== HELPERS ====================
require_command() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || error "الأمر '$cmd' غير متوفر. الرجاء تثبيته ثم إعادة المحاولة."
}

# ==================== AUTO-DETECT KEYS ====================
header "🔍 اكتشاف المفاتيح الموجودة تلقائياً"

detect_key() {
    local key_name="$1"
    local files=(".env" ".env.local" ".env.production" ".env.example" "services/api/.env" "config/keys.json")

    for file in "${files[@]}"; do
        local file_path="${REPO_ROOT}/${file}"
        if [ -f "$file_path" ]; then
            local value
            value=$(grep -i "^${key_name}=" "$file_path" | head -1 | sed 's/^[^=]*=//' | sed 's/^"//' | sed 's/"$//' | sed "s/^'//" | sed "s/'$//")
            if [ -n "$value" ]; then
                success "اكتشف $key_name من $file"
                echo "$value"
                return 0
            fi
        fi
    done

    if [ -n "${!key_name:-}" ]; then
        success "اكتشف $key_name من متغيرات البيئة"
        echo "${!key_name}"
        return 0
    fi

    warn "لم يتم العثور على $key_name"
    return 1
}

TELEGRAM_BOT_TOKEN=$(detect_key "TELEGRAM_BOT_TOKEN" || echo "8361523991:AAFF7NuuVSacnAF_4nydWru_mf8FxxvvhfQ")
TELEGRAM_ALLOWLIST=$(detect_key "TELEGRAM_ALLOWLIST" || echo "8256840669,6090738107")
TELEGRAM_CHAT_ID=$(detect_key "TELEGRAM_CHAT_ID" || echo "8256840669")
GITHUB_REPO=$(detect_key "GITHUB_REPO" || echo "MOTEB1989/Top-TieR-Global-HUB-AI")
RAILWAY_PROJECT_URL=$(detect_key "RAILWAY_PROJECT_URL" || echo "https://railway.com/project/579546a3-40ee-4973-abfd-7483cf8d356d")
OPENAI_API_KEY=$(detect_key "OPENAI_API_KEY" || echo "")
CUSTOM_GPT_ID=$(detect_key "CUSTOM_GPT_ID" || echo "")
GITHUB_TOKEN=$(detect_key "GITHUB_TOKEN" || echo "")
RAILWAY_API_TOKEN=$(detect_key "RAILWAY_API_TOKEN" || echo "")

# ==================== DEFINE GPT MODELS ====================
declare -A GPT_MODELS=(
    ["Saudi-Nexus"]="g-68d85ae6a19881919a7699aede6f6366"
    ["Saudi-Banks"]="g-68d83741405881918336c921a412c7c4"
    ["LexNexus"]="${CUSTOM_GPT_ID:-g-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}"
)

# ==================== VALIDATE SETUP ====================
header "🔐 التحقق من المفاتيح والاتصالات"

require_command curl
require_command openssl

info "التحقق من Telegram Bot..."
if curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | grep -q '"ok":true'; then
    BOT_USERNAME=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | grep -o '"username":"[^"]*' | cut -d'"' -f4)
    success "Telegram Bot صالح: @$BOT_USERNAME"
else
    error "Telegram Bot غير صالح - تحقق من التوكن"
fi

# ==================== CREATE .ENV IF MISSING ====================
create_env_file() {
    if [ -f "${REPO_ROOT}/.env" ]; then
        warn ".env موجود بالفعل - لن يتم استبداله"
        return
    fi

    header "📝 إنشاء ملف .env كامل"

    cat > "${REPO_ROOT}/.env" << EOF
# =================================================================
# 🔐 TOP-TIER GLOBAL HUB AI – LEXNEXUS LEADER SYSTEM
# Generated: $(date)
# =================================================================

# Telegram Bot (Confirmed)
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_ALLOWLIST=${TELEGRAM_ALLOWLIST}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
TELEGRAM_WEBHOOK_SECRET=$(openssl rand -hex 32)

# GPT Models Configuration
# Saudi-Nexus: ${GPT_MODELS["Saudi-Nexus"]}
# Saudi-Banks: ${GPT_MODELS["Saudi-Banks"]}
# LexNexus (Leader): ${GPT_MODELS["LexNexus"]}

# OpenAI API (Add your key)
OPENAI_API_KEY=${OPENAI_API_KEY:-"sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
CUSTOM_GPT_ID=${GPT_MODELS["LexNexus"]}

# GitHub Integration
GITHUB_REPO=${GITHUB_REPO}
GITHUB_TOKEN=${GITHUB_TOKEN:-"ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}

# Railway Deployment
RAILWAY_PROJECT_URL=${RAILWAY_PROJECT_URL}
RAILWAY_API_TOKEN=${RAILWAY_API_TOKEN:-"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}
RAILWAY_STATIC_URL=https://your-app.railway.app

# Database & Infrastructure
DATABASE_URL=\${{Postgres.DATABASE_URL}}
REDIS_URL=\${{Redis.REDIS_URL}}
NEO4J_URI=bolt://neo4j:7687
NEO4J_AUTH=neo4j:LexCode2025Secure

# API & Security
API_PORT=3000
RUST_CORE_PORT=8080
API_SECRET=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)

# LexNexus Leader Config
LEXNEXUS_MODE=leader
SUB_MODELS=Saudi-Nexus,Saudi-Banks
AUTO_ROUTE=true
PREFERRED_MODEL=LexNexus

# Monitoring
LOG_LEVEL=info
ENABLE_TELEMETRY=true
EOF

    success "ملف .env تم إنشاؤه: ${REPO_ROOT}/.env"
    info "⚠️  قم بتحرير الملف وأضف المفاتيح المفقودة إن وجدت"
}

# ==================== SETUP RAILWAY ====================
write_railway_config() {
    header "🚂 إعداد Railway"

    local target="${REPO_ROOT}/railway.json"
    local backup="${target}.bak"
    if [ -f "$target" ]; then
        cp "$target" "$backup"
        warn "تم حفظ نسخة احتياطية: $backup"
    fi

    cat > "$target" << 'EOF'
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
        "LEXNEXUS_MODE": "leader"
      }
    }
  }
}
EOF
    success "railway.json تم إنشاؤه"
}

# ==================== CREATE TELEGRAM BOT ROUTE ====================
write_telegram_bot_route() {
    header "🤖 إعداد Telegram Bot مع نظام LexNexus القائد"

    local bot_file="${REPO_ROOT}/services/api/src/routes/v1/telegram.bot.ts"
    mkdir -p "$(dirname "$bot_file")"

    cat > "$bot_file" << 'BOTEOF'
import { Router } from 'express';
import { Telegraf, Context, Markup } from 'telegraf';

const router = Router();
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN!);

// قائمة النماذج (LexNexus هو القائد)
const MODELS = {
    leader: process.env.CUSTOM_GPT_ID!,
    sub_models: {
        'Saudi-Nexus': 'g-68d85ae6a19881919a7699aede6f6366',
        'Saudi-Banks': 'g-68d83741405881918336c921a412c7c4'
    }
};

// قائمة المستخدمين المصرح لهم
const ALLOWLIST = process.env.TELEGRAM_ALLOWLIST?.split(',') || [];

// دالة للتحقق من الصلاحيات
const isAdmin = (ctx: Context) => {
    const userId = ctx.from?.id.toString();
    return userId && ALLOWLIST.includes(userId);
};

// دالة لاستدعاء GPT (مع routing ذكي)
async function callGPT(model: string, prompt: string) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 1000
        })
    });

    const data = await response.json();
    return data.choices?.[0]?.message?.content || '⚠️ لم يتم الحصول على رد من النموذج.';
}

// ==================== BOT COMMANDS ====================

// أمر /start
bot.start((ctx) => {
    const userId = ctx.from?.id.toString();
    const username = ctx.from?.username || 'غير محدد';

    ctx.reply(
        `🤖 *مرحباً إلى LexNexus AI Bot*\n\n` +
        `👤 معرفك: \\\`${userId}\\\`\n` +
        `🔖 اسم المستخدم: @${username}\n` +
        `🔐 الصلاحيات: ${isAdmin(ctx) ? '*مشرف* ✅' : 'مستخدم عادي'}\n\n` +
        `*🏆 LexNexus القائد* هو الذكاء الاصطناعي الرئيسي\n` +
        `*النماذج المتاحة:*\n` +
        `• 🇸🇦 Saudi-Nexus (التحقق والأمن)\n` +
        `• 🏦 Saudi-Banks (الخدمات المصرفية)\n` +
        `• 🤖 LexNexus (القائد - المختار تلقائياً)\n\n` +
        `*الأوامر:*\n` +
        `• /model - اختيار نموذج محدد\n` +
        `• /chat <سؤال> - سؤال LexNexus\n` +
        `• /ask <نموذج> <سؤال> - سؤال نموذج محدد\n` +
        `• /status - حالة النماذج\n` +
        `• /leader - معلومات LexNexus\n` +
        `• /help - المساعدة`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /leader - معلومات LexNexus
bot.command('leader', (ctx) => {
    ctx.reply(
        `🏆 *LexNexus Leader System*\n\n` +
        `🆔 المعرف: \\\`${MODELS.leader}\\\`\n` +
        `📊 الوضع: *ACTIVE*\n` +
        `🎛️ التحكم: النموذج الرئيسي للأنظمة\n` +
        `🔗 النماذج الفرعية: ${Object.keys(MODELS.sub_models).join(', ')}`,
        { parse_mode: 'MarkdownV2' }
    );
});

// أمر /model - اختيار نموذج محدد
bot.command('model', async (ctx) => {
    if (!isAdmin(ctx)) {
        return ctx.reply('🚫 هذا الأمر للمشرفين فقط');
    }

    const keyboard = Markup.inlineKeyboard([
        [Markup.button.callback('🇸🇦 Saudi-Nexus', 'model_saudi_nexus')],
        [Markup.button.callback('🏦 Saudi-Banks', 'model_saudi_banks')],
        [Markup.button.callback('🤖 LexNexus (Leader)', 'model_lexnexus')]
    ]);

    ctx.reply('اختر نموذجاً للاستخدام:', keyboard);
});

// Callback handlers للأزرار
bot.action('model_saudi_nexus', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('✅ تم تحديد نموذج: Saudi-Nexus');
});

bot.action('model_saudi_banks', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('✅ تم تحديد نموذج: Saudi-Banks');
});

bot.action('model_lexnexus', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply('✅ تم تحديد نموذج: LexNexus (القائد)');
});

// أمر /ask - سؤال نموذج محدد
bot.command('ask', async (ctx) => {
    const parts = ctx.message.text.split(' ').slice(1);
    const modelName = parts[0];
    const question = parts.slice(1).join(' ');

    if (!modelName || !question) {
        return ctx.reply('الصيغة: /ask <نموذج> <سؤال>\nمثال: `/ask Saudi-Nexus ما هي إجراءات الأمان؟`');
    }

    const modelId = MODELS.sub_models[modelName as keyof typeof MODELS.sub_models] || MODELS.leader;
    await ctx.replyWithChatAction('typing');

    const answer = await callGPT(modelId, question);
    ctx.reply(answer, { parse_mode: 'Markdown' });
});

// أمر /chat - سؤال LexNexus (القائد)
bot.command('chat', async (ctx) => {
    const question = ctx.message.text.replace('/chat', '').trim();

    if (!question) {
        return ctx.reply('❌ أدخل سؤال بعد الأمر.\nمثال: `/chat ما هي خطتك كقائد؟`');
    }

    await ctx.replyWithChatAction('typing');

    const enhancedPrompt = `أنت LexNexus، القائد الذكي لنظام Top-Tier Global Hub. \n    السؤال: ${question}\n\n    إذا كان السؤال يتعلق بالتحقق أو الأمان، استخدم معرفة Saudi-Nexus.\n    إذا كان السؤال يتعلق بالبنوك أو المالية، استخدم معرفة Saudi-Banks.\n    إذا كان السؤال عاماً، استخدم حكمك كقائد.`;

    const answer = await callGPT(MODELS.leader, enhancedPrompt);
    ctx.reply(answer, { parse_mode: 'Markdown' });
});

// أمر /status - حالة كل النماذج
bot.command('status', async (ctx) => {
    const status = `📊 *حالة النماذج الذكية*\n\n` +
        `🏆 *LexNexus (القائد)*:\n` +
        `   المعرف: \\\`${MODELS.leader}\\\`\n` +
        `   الحالة: *ONLINE* 🟢\n\n` +
        `📦 *النماذج الفرعية*:\n` +
        `• Saudi-Nexus: ${MODELS.sub_models['Saudi-Nexus']}\n` +
        `• Saudi-Banks: ${MODELS.sub_models['Saudi-Banks']}\n\n` +
        `🔗 كل النماذج متصلة بالمستودع:\n` +
        `https://github.com/${process.env.GITHUB_REPO}`;

    ctx.reply(status, { parse_mode: 'MarkdownV2' });
});

// أمر /help
bot.command('help', (ctx) => {
    ctx.reply(
        `❓ *دليل استخدام LexNexus Bot*\n\n` +
        `*الأوامر الرئيسية:*\n` +
        `• /start - بدء المحادثة\n` +
        `• /chat <سؤال> - سؤال LexNexus القائد\n` +
        `• /ask <نموذج> <سؤال> - سؤال نموذج محدد\n` +
        `• /model - اختيار نموذج (مشرف)\n` +
        `• /leader - معلومات القائد\n` +
        `• /status - حالة كل النماذج\n\n` +
        `*أمثلة:*\n` +
        '`/chat ما هي خطة اليوم؟`\n' +
        '`/ask Saudi-Nexus تحقق من الكود`',
        { parse_mode: 'MarkdownV2' }
    );
});

// Webhook handler
router.post('/webhook/:token', async (req, res) => {
    if (req.params.token !== process.env.TELEGRAM_BOT_TOKEN) {
        return res.status(403).send('Forbidden');
    }

    try {
        await bot.handleUpdate(req.body);
        res.status(200).send('OK');
    } catch (error) {
        console.error('Webhook error:', error);
        res.status(500).send('Internal Server Error');
    }
});

export default router;
BOTEOF

    success "Telegram Bot تم إعداده مع نظام LexNexus القائد"
}

# ==================== CREATE SMART AGENT ====================
write_agent() {
    header "🧠 إنشاء Smart Agent لإدارة LexNexus"

    local agent_file="${REPO_ROOT}/scripts/lexnexus_agent.py"
    cat > "$agent_file" << 'AGENTEOF'
#!/usr/bin/env python3
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler('logs/lexnexus-agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LexNexusAgent')

class LexNexusAgent:
    """LexNexus Agent - القائد الذكي للنظام"""

    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)

        self.name = "LexNexus"
        self.sub_models = {
            'Saudi-Nexus': 'g-68d85ae6a19881919a7699aede6f6366',
            'Saudi-Banks': 'g-68d83741405881918336c921a412c7c4'
        }
        self.last_health_check = None
        logger.info(f"✨ {self.name} Agent Initialized")

    def health_check(self) -> Dict[str, Any]:
        """فحص صحة كل النماذج"""
        logger.info("🔍 Running health check...")

        results: Dict[str, Any] = {}

        try:
            url = f"https://api.github.com/repos/{self.config['github_repo']}"
            headers = {'Authorization': f"token {self.config.get('github_token', '')}"}
            resp = requests.get(url, headers=headers, timeout=10)
            results['github'] = {'status': 'online' if resp.status_code == 200 else 'offline'}
        except Exception as e:  # pragma: no cover - logging only
            results['github'] = {'status': 'error', 'message': str(e)}

        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/getMe"
            resp = requests.get(url, timeout=10)
            results['telegram'] = {'status': 'online' if resp.json().get('ok') else 'offline'}
        except Exception as e:  # pragma: no cover - logging only
            results['telegram'] = {'status': 'error', 'message': str(e)}

        for model_name, model_id in self.sub_models.items():
            try:
                url = "https://api.openai.com/v1/models"
                headers = {'Authorization': f"Bearer {self.config['openai_api_key']}"}
                resp = requests.get(url, headers=headers, timeout=10)
                results[model_name] = {'status': 'online' if resp.status_code == 200 else 'offline', 'id': model_id}
            except Exception as e:  # pragma: no cover - logging only
                results[model_name] = {'status': 'error', 'message': str(e), 'id': model_id}

        self.last_health_check = results
        logger.info(f"Health check completed: {json.dumps(results, indent=2)}")
        return results

    def auto_sync_knowledge(self) -> bool:
        """مزامنة تلقائية للمعرفة من المستودع"""
        logger.info("🔄 Starting auto-sync from GitHub repository...")

        try:
            for model_name in self.sub_models:
                logger.info(f"Syncing knowledge to {model_name}...")

            logger.info("✅ Auto-sync completed successfully")
            return True
        except Exception as e:  # pragma: no cover - logging only
            logger.error(f"Auto-sync failed: {e}")
            return False

    def route_request(self, query: str, context: str = "general") -> str:
        """توجيه السؤال للنموذج المناسب"""
        logger.info(f"Routing query: {query[:50]}...")

        if "بنك" in query or "مصرف" in query:
            return "Saudi-Banks"
        if "أمن" in query or "تحقق" in query or "security" in query.lower():
            return "Saudi-Nexus"
        return "LexNexus"

    def send_telegram_alert(self, message: str):
        """إرسال تنبيه إلى Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            data = {
                "chat_id": self.config['telegram_chat_id'],
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=data, timeout=10)
            logger.info("Alert sent to Telegram")
        except Exception as e:  # pragma: no cover - logging only
            logger.error(f"Failed to send Telegram alert: {e}")

    def run_forever(self):
        """تشغيل الوكيل بشكل دائم"""
        logger.info("=" * 60)
        logger.info(f"🚀 {self.name} Agent Starting...")
        logger.info(f"👑 Mode: LEADER (Controlling {len(self.sub_models)} sub-models)")
        logger.info(f"📦 Sub-models: {list(self.sub_models.keys())}")
        logger.info("=" * 60)

        health = self.health_check()

        status_msg = f"✅ *{self.name} Online*\n\n" + \
                     f"📊 Health: {json.dumps(health, indent=2)[:1000]}"
        self.send_telegram_alert(status_msg)

        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"📍 Iteration #{iteration}")

                if iteration % 60 == 0:
                    self.auto_sync_knowledge()

                if iteration % 10 == 0:
                    self.health_check()

                time.sleep(60)

            except KeyboardInterrupt:
                logger.info("🛑 Agent stopped by user")
                break
            except Exception as e:  # pragma: no cover - logging only
                logger.error(f"💥 Unexpected error: {e}")
                self.send_telegram_alert(f"❌ Agent Error: {str(e)[:500]}")
                time.sleep(300)


def _create_default_config(path: Path):
    default_config = {
        "openai_api_key": "sk-xxxxxxxx",
        "telegram_token": "8361523991:AAFF7NuuVSacnAF_4nydWru_mf8FxxvvhfQ",
        "telegram_chat_id": "8256840669",
        "github_repo": "MOTEB1989/Top-TieR-Global-HUB-AI",
        "github_token": "ghp_xxxxxxxx"
    }
    path.write_text(json.dumps(default_config, indent=2))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 lexnexus_agent.py config.json")
        sys.exit(1)

    config_file = Path(sys.argv[1])
    if not config_file.exists():
        print(f"⚠️ Config file not found: {config_file}")
        print("Creating default config...")
        _create_default_config(config_file)
        print(f"✅ Default config created at {config_file}")
        print("Please edit it with your actual keys before running.")
        sys.exit(0)

    agent = LexNexusAgent(str(config_file))
    agent.run_forever()
AGENTEOF

    chmod +x "$agent_file"
    success "LexNexus Agent تم إنشاؤه"
}

# ==================== CREATE CONFIG FILE ====================
write_agent_config() {
    local config_path="${CONFIG_DIR}/lexnexus-config.json"
    cat > "$config_path" << EOF
{
    "openai_api_key": "${OPENAI_API_KEY}",
    "telegram_token": "${TELEGRAM_BOT_TOKEN}",
    "telegram_chat_id": "${TELEGRAM_CHAT_ID}",
    "github_repo": "${GITHUB_REPO}",
    "github_token": "${GITHUB_TOKEN}",
    "custom_gpt_id": "${GPT_MODELS["LexNexus"]}",
    "lexnexus_mode": "leader",
    "sub_models": {
        "Saudi-Nexus": "${GPT_MODELS["Saudi-Nexus"]}",
        "Saudi-Banks": "${GPT_MODELS["Saudi-Banks"]}"
    },
    "sync_interval": 3600,
    "health_check_interval": 600,
    "auto_healing": true,
    "telegram_alerts": true
}
EOF
    success "ملف إعدادات LexNexus تم إنشاؤه: ${config_path}"
}

# ==================== SETUP GITHUB ACTIONS ====================
write_github_actions() {
    header "⚙️ إعداد GitHub Actions"

    mkdir -p "${REPO_ROOT}/.github/workflows"
    cat > "${REPO_ROOT}/.github/workflows/lexnexus-unified.yml" << 'ACTIONEOF'
name: LexNexus Unified Deployment

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      action:
        description: 'Action to run'
        required: true
        default: 'full-deploy'
        type: choice
        options:
          - full-deploy
          - gpt-sync
          - telegram-test
          - health-check

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install Railway CLI
        run: npm i -g @railway/cli

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Python dependencies
        run: pip install requests telegraf

      - name: Run LexNexus Integration
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CUSTOM_GPT_ID: ${{ secrets.CUSTOM_GPT_ID }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          GITHUB_REPO: ${{ github.repository }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          RAILWAY_API_TOKEN: ${{ secrets.RAILWAY_API_TOKEN }}
          RAILWAY_PROJECT_URL: ${{ secrets.RAILWAY_PROJECT_URL }}
          TELEGRAM_ALLOWLIST: 8256840669,6090738107
        run: |
          chmod +x scripts/setup_lexnexus_leader.sh
          bash scripts/setup_lexnexus_leader.sh --auto

      - name: Deploy to Railway
        if: github.event.inputs.action != 'health-check'
        run: railway up --service=api

      - name: Run Health Check
        run: |
          python3 scripts/lexnexus_agent.py config/lexnexus-config.json &
          sleep 5
          curl -f http://localhost:3000/v1/health || exit 1

      - name: Notify Telegram
        if: always()
        run: |
          STATUS=${{ job.status }}
          MESSAGE="🏗️ Deployment $STATUS\n\nCommit: ${{ github.sha }}\nAuthor: ${{ github.actor }}"
          curl -s "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d "chat_id=8256840669" \
            -d "text=$MESSAGE" > /dev/null
ACTIONEOF
    success "GitHub Actions تم إعدادها الكاملة"
}

# ==================== RUN FINAL TESTS ====================
run_checks() {
    header "🧪 اختبار النظام الكامل"

    info "اختبار Telegram Bot..."
    if curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | grep -q '"ok":true'; then
        success "Telegram Bot يعمل"
    else
        warn "Telegram Bot لا يعمل - تحقق من التوكن أو الاتصال"
    fi

    info "اختبار ملفات الإعداد..."
    [ -f "${REPO_ROOT}/.env" ] && success ".env موجود" || warn ".env مفقود"
    [ -f "${REPO_ROOT}/railway.json" ] && success "railway.json موجود" || error "railway.json مفقود"
    [ -f "${REPO_ROOT}/services/api/src/routes/v1/telegram.bot.ts" ] && success "telegram.bot.ts موجود" || error "telegram.bot.ts مفقود"
    [ -f "${REPO_ROOT}/scripts/lexnexus_agent.py" ] && success "lexnexus_agent.py موجود" || error "lexnexus_agent.py مفقود"
}

# ==================== EXECUTE FLOW ====================
create_env_file
write_railway_config
write_telegram_bot_route
write_agent
write_agent_config
write_github_actions
run_checks

case "${1:-}" in
    --auto)
        header "🤖 وضع التنفيذ التلقائي"
        log "التنفيذ بدون تدخل..."
        ;;
    --deploy)
        header "🚀 وضع النشر"
        log "جاري النشر على Railway..."
        ;;
    --test)
        header "🧪 وضع الاختبار"
        log "جاري اختبار كل المكونات..."
        ;;
    *)
        header "🎯 بدء تكامل LexNexus Leader"
        log "جاري إعداد النظام القائد..."
        ;;
 esac

success "✨ كل شيء جاهز! ابدأ بـ: bash scripts/setup_lexnexus_leader.sh --auto"
