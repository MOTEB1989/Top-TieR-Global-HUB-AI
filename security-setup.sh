#!/bin/bash
echo "🔐 Generating security keys..."
openssl rand -hex 32 > .env.keys
echo "CODEX_ENCRYPTION_KEY=$(cat .env.keys)" >> .env
echo "✅ Security keys generated"
