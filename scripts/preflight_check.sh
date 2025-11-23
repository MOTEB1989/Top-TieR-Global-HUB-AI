#!/bin/bash
set -e

echo "=========================================================="
echo " 🔍 PRE-FLIGHT CHECK — Top-Tier Global HUB AI "
echo "=========================================================="
echo ""

fail() { echo "❌ $1"; exit 1; }
ok() { echo "✅ $1"; }

echo "📁 Checking directory structure..."
[[ -d core ]] && ok "core/ found" || fail "Missing core/"
[[ -d services/api ]] && ok "services/api/ found" || fail "Missing services/api/"
[[ -d adapters/python ]] && ok "adapters/python/ found" || fail "Missing adapters/python/"
[[ -f docker-compose.yml ]] && ok "docker-compose.yml found" || fail "Missing docker-compose.yml"

echo ""
echo "🐳 Checking Docker..."
command -v docker >/dev/null 2>&1 || fail "Docker not installed"
docker version >/dev/null 2>&1 && ok "Docker is working"
command -v docker compose >/dev/null 2>&1 || fail "Docker Compose v2 not installed"
docker compose version >/dev/null 2>&1 && ok "Docker Compose detected"

echo ""
echo "🧪 Validating docker-compose.yml..."
docker compose config >/dev/null 2>&1 && ok "docker-compose.yml valid" || fail "docker-compose.yml has syntax errors"

echo ""
echo "📦 Checking Node.js API..."
[[ -f services/api/package.json ]] && ok "package.json exists" || fail "package.json missing in services/api"
[[ -f services/api/index.js ]] && ok "index.js exists" || fail "Missing services/api/index.js"
echo "Testing Node dependencies..."
(cd services/api && npm install --silent >/dev/null 2>&1 && ok "Node dependencies install successfully") || fail "Node install failed"

echo ""
echo "🐍 Checking Python environment..."
command -v python3 >/dev/null 2>&1 && ok "Python3 detected" || fail "Python not installed"
[[ -f adapters/python/lexhub/requirements.txt ]] && ok "Python requirements found" || fail "Missing Python requirements"
pip install -r adapters/python/lexhub/requirements.txt --quiet && ok "Python packages OK" || fail "Python install failure"

echo ""
echo "🦀 Checking Rust core..."
command -v cargo >/dev/null 2>&1 && ok "Rust toolchain detected" || fail "Rust/Cargo not installed"
[[ -f core/Cargo.toml ]] && ok "Cargo.toml found" || fail "Missing core/Cargo.toml"
cargo check --manifest-path core/Cargo.toml && ok "Rust project compiles" || fail "Rust compilation error"

echo ""
echo "🌐 Checking ports in docker-compose..."
ports=(8080 3000 6379 6333 6334)
for p in "${ports[@]}"; do
    grep -R "$p:" docker-compose.yml >/dev/null && ok "Port $p declared" || echo "⚠️ Port $p not found (may be intentional)"
done

echo ""
echo "🧩 Checking ENV files..."
[[ -f .env ]] && ok ".env exists" || echo "⚠️ No .env file — using defaults"
[[ -f .env.example ]] && ok ".env.example exists" || echo "⚠️ Missing .env.example"

echo ""
echo "=========================================================="
echo " 🎉 PRE-FLIGHT CHECK COMPLETED"
echo "=========================================================="
echo ""

echo "If you see only green check marks, you may safely run:"
echo "   docker compose up --build"
echo ""
