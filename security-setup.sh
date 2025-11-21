#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  echo "📄 Found existing .env file; values will be appended if missing." 
else
  echo "🆕 Creating .env file" > /dev/null
  touch .env
fi

if grep -q "^CODEX_ENCRYPTION_KEY=" .env; then
  echo "🔑 CODEX_ENCRYPTION_KEY already present; skipping generation."
else
  key=$(openssl rand -hex 32)
  echo "🔑 Generating CODEX_ENCRYPTION_KEY"
  echo "CODEX_ENCRYPTION_KEY=$key" >> .env
fi

echo "✅ Security environment prepared"
