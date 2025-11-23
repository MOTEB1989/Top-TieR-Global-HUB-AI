#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOGS_DIR="${REPO_ROOT}/logs"
mkdir -p "$LOGS_DIR"
LOG_FILE="${LOGS_DIR}/all-in-one-integration.log"
exec > >(tee -a "$LOG_FILE") 2>&1

log(){ echo "[$(date '+%H:%M:%S')] $1"; }
error(){ echo "ERROR: $1"; exit 1; }
success(){ echo "OK: $1"; }
warn(){ echo "WARN: $1"; }

load_env_file(){
  local env_file="${REPO_ROOT}/.env"
  if [ -f "$env_file" ]; then
    log "Loading environment from $env_file"
    set -a; source "$env_file"; set +a
  fi
}

require_env(){
  local missing=()
  for var in "$@"; do
    if [ -z "${!var:-}" ]; then
      missing+=("$var")
    fi
  done
  [ ${#missing[@]} -eq 0 ] || error "Missing environment: ${missing[*]}"
}

validate_keys(){
  log "Validating connections"
  require_env TELEGRAM_BOT_TOKEN TELEGRAM_ALLOWLIST TELEGRAM_CHAT_ID RAILWAY_PROJECT_URL GITHUB_REPO

  if curl -s "https://api.github.com/repos/${GITHUB_REPO}" | grep -q '"full_name"'; then
    success "GitHub reachable"
  else
    error "GitHub not reachable"
  fi

  local telegram_check
  telegram_check=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
  echo "$telegram_check" | grep -q '"ok":true' || error "Telegram bot invalid"
  success "Telegram bot verified"

  if curl -s -I "$RAILWAY_PROJECT_URL" | grep -q "HTTP/2 200\|302"; then
    success "Railway reachable"
  else
    warn "Railway not reachable now"
  fi
}

create_complete_env(){
  log "Writing .env"
  cat > "${REPO_ROOT}/.env" <<ENV_FILE
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-<telegram-bot-token>}
TELEGRAM_ALLOWLIST=${TELEGRAM_ALLOWLIST:-<telegram-allowlist>}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-<telegram-chat-id>}
TELEGRAM_WEBHOOK_SECRET=${TELEGRAM_WEBHOOK_SECRET:-placeholder-webhook-secret}

OPENAI_API_KEY=${OPENAI_API_KEY:-<openai-api-key>}
CUSTOM_GPT_ID=${CUSTOM_GPT_ID:-<custom-gpt-id>}

GITHUB_REPO=${GITHUB_REPO:-<org/repo>}
GITHUB_TOKEN=${GITHUB_TOKEN:-<github-token>}

RAILWAY_PROJECT_URL=${RAILWAY_PROJECT_URL:-<railway-project-url>}
RAILWAY_API_TOKEN=${RAILWAY_API_TOKEN:-<railway-api-token>}
RAILWAY_STATIC_URL=${RAILWAY_STATIC_URL:-https://your-app.railway.app}

DATABASE_URL=${DATABASE_URL:-Postgres.DATABASE_URL}
REDIS_URL=${REDIS_URL:-Redis.REDIS_URL}
NEO4J_URI=${NEO4J_URI:-bolt://neo4j:7687}
NEO4J_AUTH=${NEO4J_AUTH:-neo4j:change-me}

API_PORT=${API_PORT:-3000}
RUST_CORE_PORT=${RUST_CORE_PORT:-8080}
API_SECRET=${API_SECRET:-replace-with-random-secret}
JWT_SECRET=${JWT_SECRET:-replace-with-random-jwt}

LOG_LEVEL=${LOG_LEVEL:-info}
ENABLE_TELEMETRY=${ENABLE_TELEMETRY:-true}
SENTRY_DSN=${SENTRY_DSN:-https://your-sentry-dsn}

AGENT_MODE=${AGENT_MODE:-production}
AGENT_POLL_INTERVAL=${AGENT_POLL_INTERVAL:-300}
AUTO_HEALING=${AUTO_HEALING:-true}
ENV_FILE
  success "Created .env"
}

setup_railway(){
  log "Writing railway templates"
  cat > "${REPO_ROOT}/railway.json" <<'RAILWAY_FILE'
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
RAILWAY_FILE

  cat > "${REPO_ROOT}/docker-compose.railway.yml" <<'DOCKER_FILE'
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: services/api/Dockerfile
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
      - TELEGRAM_ALLOWLIST=${TELEGRAM_ALLOWLIST:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CUSTOM_GPT_ID=${CUSTOM_GPT_ID}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - RAILWAY_STATIC_URL=${RAILWAY_STATIC_URL}
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis123}
    ports:
      - "6379:6379"
  neo4j:
    image: neo4j:5-community
    environment:
      - NEO4J_AUTH=${NEO4J_AUTH}
      - NEO4J_PLUGINS=["apoc"]
    ports:
      - "7474:7474"
      - "7687:7687"
DOCKER_FILE
  success "Updated Railway files"
}

setup_telegram_bot(){
  log "Writing Telegram route"
  local bot_file="${REPO_ROOT}/services/api/src/routes/v1/telegram.bot.ts"
  mkdir -p "$(dirname "$bot_file")"
  cat > "$bot_file" <<'BOT_FILE'
import { Router } from 'express'
import { Telegraf, Context } from 'telegraf'

const router = Router()
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN!)

const ALLOWLIST = process.env.TELEGRAM_ALLOWLIST?.split(',') || []
const CUSTOM_GPT_ID = process.env.CUSTOM_GPT_ID!

const adminOnly = (ctx: Context, next: () => Promise<void>) => {
  const userId = ctx.from?.id.toString()
  if (!userId || !ALLOWLIST.includes(userId)) {
    return ctx.reply('🚫 غير مصرح لك باستخدام هذا الأمر.')
  }
  return next()
}

bot.start((ctx) => {
  const userId = ctx.from?.id.toString()
  const isAdmin = userId ? ALLOWLIST.includes(userId) : false

  ctx.reply(`🤖 Top-Tier Global HUB AI\n\n👤 ${ctx.from?.id}\n🔐 ${isAdmin ? 'مشرف' : 'مستخدم عادي'}\n\n• /preflight\n• /chat <سؤال>\n• /status\n• /deploy`)
})

bot.command('preflight', adminOnly, async (ctx) => {
  await ctx.replyWithChatAction('typing')
  const checks = [
    { name: 'Railway Status', url: process.env.RAILWAY_STATIC_URL },
    { name: 'GitHub Repo', url: `https://github.com/${process.env.GITHUB_REPO}` },
    { name: 'Redis', url: process.env.REDIS_URL },
    { name: 'Neo4j', url: process.env.NEO4J_URI }
  ]
  const results = await Promise.all(checks.map(async ({ name, url }) => {
    try {
      await fetch(url!, { method: 'HEAD' })
      return `✅ ${name}: يعمل`
    } catch {
      return `❌ ${name}: متوقف`
    }
  }))
  await ctx.reply(results.join('\n'))
})

bot.command('chat', async (ctx) => {
  const question = ctx.message.text.replace('/chat', '').trim()
  if (!question) {
    return ctx.reply('❌ أدخل سؤال بعد الأمر.')
  }
  await ctx.replyWithChatAction('typing')
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: CUSTOM_GPT_ID,
        messages: [{ role: 'user', content: question }],
        max_tokens: 1000
      })
    })
    const data = await response.json()
    await ctx.reply(data.choices?.[0]?.message?.content ?? 'No response received')
  } catch (error) {
    console.error('Chat error:', error)
    await ctx.reply('❌ فشل الاتصال بـ GPT.')
  }
})

bot.command('status', (ctx) => {
  ctx.reply(`📊 الحالة\nBot: ✅\nRailway: ${process.env.RAILWAY_STATIC_URL || 'غير منشر'}\nGPT: ${CUSTOM_GPT_ID || 'غير مضبوط'}\nUsers: ${ALLOWLIST.length}`)
})

bot.command('deploy', adminOnly, async (ctx) => {
  await ctx.reply('🚀 جاري النشر على Railway...')
  const { exec } = require('child_process')
  exec('railway up', (error: unknown, stdout: string, stderr: string) => {
    if (error) {
      ctx.reply(`❌ فشل النشر:\n${stderr}`)
    } else {
      ctx.reply(`✅ نشر ناجح!\n${stdout}`)
    }
  })
})

router.post('/webhook/:token', async (req, res) => {
  if (req.params.token !== process.env.TELEGRAM_BOT_TOKEN) {
    return res.status(403).send('Forbidden')
  }
  try {
    await bot.handleUpdate(req.body)
    res.status(200).send('OK')
  } catch (error) {
    console.error('Webhook error:', error)
    res.status(500).send('Internal Server Error')
  }
})

export default router
BOT_FILE
  success "Updated Telegram bot route"
}

create_smart_agent(){
  log "Writing smart agent"
  local agent_script="${REPO_ROOT}/scripts/smart_agent_validator.py"
  cat > "$agent_script" <<'AGENT_FILE'
#!/usr/bin/env python3
import json
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SmartAgent:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
        self.log = logging.getLogger(__name__)
        self.last_sync = None

    def validate_github(self) -> bool:
        try:
            url = f"https://api.github.com/repos/{self.config['github_repo']}"
            headers = {'Authorization': f"token {self.config.get('github_token', '')}"}
            resp = requests.get(url, headers=headers, timeout=10)
            return resp.status_code == 200
        except Exception as exc:
            self.log.error("GitHub validation failed: %s", exc)
            return False

    def validate_gpt(self) -> bool:
        try:
            url = "https://api.openai.com/v1/models"
            headers = {'Authorization': f"Bearer {self.config['openai_api_key']}"}
            resp = requests.get(url, headers=headers, timeout=10)
            return resp.status_code == 200
        except Exception as exc:
            self.log.error("GPT validation failed: %s", exc)
            return False

    def validate_telegram(self) -> bool:
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/getMe"
            resp = requests.get(url, timeout=10)
            return resp.json().get('ok', False)
        except Exception as exc:
            self.log.error("Telegram validation failed: %s", exc)
            return False

    def sync_knowledge(self) -> bool:
        try:
            url = f"https://api.openai.com/v1/gpts/{self.config['custom_gpt_id']}/knowledge/sync"
            headers = {'Authorization': f"Bearer {self.config['openai_api_key']}"}
            data = {
                "repository": f"https://github.com/{self.config['github_repo']}",
                "branch": "main",
                "include": ["src/**", "scripts/**", "docs/**"]
            }
            resp = requests.post(url, json=data, headers=headers, timeout=30)
            if resp.status_code == 200:
                self.log.info("Knowledge synced successfully")
                self.last_sync = time.time()
                return True
            self.log.error("Sync failed: %s", resp.text)
            return False
        except Exception as exc:
            self.log.error("Sync error: %s", exc)
            return False

    def send_alert(self, message: str):
        try:
            url = f"https://api.telegram.org/bot{self.config['telegram_token']}/sendMessage"
            data = {"chat_id": self.config['telegram_chat_id'], "text": message, "parse_mode": "Markdown"}
            requests.post(url, json=data, timeout=10)
        except Exception as exc:
            self.log.error("Failed to send alert: %s", exc)

    def run(self):
        self.log.info("Smart Agent Starting...")
        checks = [
            ("GitHub", self.validate_github()),
            ("GPT", self.validate_gpt()),
            ("Telegram", self.validate_telegram())
        ]
        for name, status in checks:
            if status:
                self.log.info("✅ %s is online", name)
            else:
                self.log.error("❌ %s is offline", name)
        while True:
            try:
                if self.sync_knowledge():
                    self.log.info("Auto-sync completed")
                else:
                    self.send_alert("⚠️ Auto-sync failed")
                time.sleep(self.config.get('sync_interval', 3600))
            except KeyboardInterrupt:
                self.log.info("Agent stopped by user")
                break
            except Exception as exc:
                self.log.error("Unexpected error: %s", exc)
                time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 smart_agent_validator.py <config.json>")
        sys.exit(1)
    agent = SmartAgent(sys.argv[1])
    agent.run()
AGENT_FILE
  chmod +x "$agent_script"
  success "Updated smart agent"
}

setup_github_actions(){
  log "Writing GitHub Actions workflow"
  mkdir -p "${REPO_ROOT}/.github/workflows"
  cat > "${REPO_ROOT}/.github/workflows/unified-deploy.yml" <<'ACTIONS_FILE'
name: Unified Deploy & Sync
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
      - name: Login to Railway
        env:
          RAILWAY_API_TOKEN: ${{ secrets.RAILWAY_API_TOKEN }}
        run: railway login --token "$RAILWAY_API_TOKEN"
      - name: Run All-in-One Integration
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CUSTOM_GPT_ID: ${{ secrets.CUSTOM_GPT_ID }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          GITHUB_REPO: ${{ github.repository }}
          RAILWAY_PROJECT_URL: ${{ secrets.RAILWAY_PROJECT_URL }}
          TELEGRAM_ALLOWLIST: 8256840669,6090738107
        run: |
          chmod +x scripts/connect_all_in_one.sh
          bash scripts/connect_all_in_one.sh --auto
      - name: Deploy to Railway
        run: railway up --service=api
      - name: Test Telegram Bot
        if: github.event.inputs.action == 'telegram-test'
        run: |
          curl -s "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
            -d "chat_id=8256840669" \
            -d "text=✅ Deployment completed successfully!"
ACTIONS_FILE
  success "Updated workflow"
}

run_final_tests(){
  log "Running smoke tests"
  curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" -d "chat_id=${TELEGRAM_CHAT_ID}" -d "text=🚀 نظام Top-Tier AI جاهز للعمل!" >/dev/null
  [ -f "${REPO_ROOT}/.env" ] || error ".env missing"
  [ -f "${REPO_ROOT}/railway.json" ] || error "railway.json missing"
  [ -f "${REPO_ROOT}/docker-compose.railway.yml" ] || error "docker-compose.railway.yml missing"
  success "Smoke tests completed"
}

main(){
  load_env_file
  case "${1:-}" in
    --auto)
      validate_keys
      create_complete_env
      setup_telegram_bot
      setup_github_actions
      run_final_tests
      ;;
    --full-deploy)
      setup_railway
      ;;
    *)
      echo "This will validate keys, write env, set up Railway, Telegram, GitHub Actions, and run smoke tests."
      read -rp "Press Enter to continue or Ctrl+C to abort..."
      validate_keys
      create_complete_env
      setup_railway
      setup_telegram_bot
      create_smart_agent
      setup_github_actions
      run_final_tests
      ;;
  esac
  log "Mission complete"
}

main "$@"
