#!/bin/bash

# Validation script for security and governance improvements
# This script validates all the changes made for the security implementation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Track validation results
PASSED=0
FAILED=0

validate() {
    local test_name="$1"
    local command="$2"
    
    log "Testing: $test_name"
    
    if eval "$command" >/dev/null 2>&1; then
        log_success "$test_name"
        ((PASSED++))
    else
        log_error "$test_name"
        ((FAILED++))
    fi
}

# Validation tests
echo "🔒 Security and Governance Validation"
echo "===================================="

# 1. Check governance files exist
validate "CODEOWNERS file exists" "test -f .github/CODEOWNERS"
validate "dependabot.yml exists" "test -f .github/dependabot.yml"
validate "CodeQL workflow exists" "test -f .github/workflows/codeql.yml"

# 2. Check Kubernetes files
validate "Neo4j K8s deployment exists" "test -f k8s/neo4j.yaml"
validate "Core K8s deployment exists" "test -f k8s/core-deployment.yaml"
validate "OSINT K8s deployment exists" "test -f k8s/osint-deployment.yaml"
validate "K8s secrets template exists" "test -f k8s/secrets.yaml.example"
validate "K8s README exists" "test -f k8s/README.md"

# 3. Check security files
validate "Neo4j env template exists" "test -f .env.neo4j.example"
validate "Setup script exists" "test -f setup_neo4j_security.sh"
validate "Setup script is executable" "test -x setup_neo4j_security.sh"
validate "Security documentation exists" "test -f SECURITY_GOVERNANCE.md"

# 4. Validate YAML syntax
validate "CodeQL YAML syntax" "python3 -c 'import yaml; yaml.safe_load(open(\".github/workflows/codeql.yml\"))'"
validate "Dependabot YAML syntax" "python3 -c 'import yaml; yaml.safe_load(open(\".github/dependabot.yml\"))'"
validate "Docker Compose YAML syntax" "python3 -c 'import yaml; yaml.safe_load(open(\"docker-compose.yml\"))'"

# 5. Validate Kubernetes YAML files
validate "Neo4j K8s YAML syntax" "python3 -c 'import yaml; list(yaml.safe_load_all(open(\"k8s/neo4j.yaml\")))'"
validate "Core K8s YAML syntax" "python3 -c 'import yaml; list(yaml.safe_load_all(open(\"k8s/core-deployment.yaml\")))'"
validate "OSINT K8s YAML syntax" "python3 -c 'import yaml; list(yaml.safe_load_all(open(\"k8s/osint-deployment.yaml\")))'"
validate "Secrets K8s YAML syntax" "python3 -c 'import yaml; list(yaml.safe_load_all(open(\"k8s/secrets.yaml.example\")))'"

# 6. Check script syntax
validate "Setup script bash syntax" "bash -n setup_neo4j_security.sh"

# 7. Check CodeQL focuses on Python only
validate "CodeQL Python-only configuration" "grep -q \"language: \\['python'\\]\" .github/workflows/codeql.yml"

# 8. Check dependabot includes dev dependency filtering
validate "Dependabot dev dependency filtering" "grep -q \"dependency-type.*development\" .github/dependabot.yml"

# 9. Check docker-compose uses env_file
validate "Docker Compose env_file configuration" "grep -q \"env_file:\" docker-compose.yml"

# 10. Check gitignore excludes secrets
validate "Gitignore excludes Neo4j secrets" "grep -q \".env.neo4j\" .gitignore"
validate "Gitignore excludes K8s secrets" "grep -q \"secrets.yaml\" .gitignore"

# 11. Check health probes in Kubernetes files
validate "Neo4j has liveness probe" "grep -q \"livenessProbe:\" k8s/neo4j.yaml"
validate "Neo4j has readiness probe" "grep -q \"readinessProbe:\" k8s/neo4j.yaml"
validate "Core has health endpoints" "grep -q \"/health\" k8s/core-deployment.yaml"
validate "OSINT has health endpoints" "grep -q \"/osint/health\" k8s/osint-deployment.yaml"

# 12. Check secret references in K8s
validate "Neo4j uses secret references" "grep -q \"secretKeyRef\" k8s/neo4j.yaml"
validate "Core uses secret references" "grep -q \"secretKeyRef\" k8s/core-deployment.yaml"
validate "OSINT uses secret references" "grep -q \"secretKeyRef\" k8s/osint-deployment.yaml"

# Summary
echo
echo "📊 Validation Summary"
echo "===================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo "📈 Success Rate: $(( PASSED * 100 / (PASSED + FAILED) ))%"

if [[ $FAILED -eq 0 ]]; then
    log_success "All validations passed! 🎉"
    echo
    echo "🚀 Ready for deployment:"
    echo "  1. Enable GitHub Security features (Settings → Security & analysis)"
    echo "  2. Run setup script: sudo ./setup_neo4j_security.sh"
    echo "  3. Deploy with Docker: docker compose up -d"
    echo "  4. Deploy to K8s: kubectl apply -f k8s/"
    exit 0
else
    log_error "Some validations failed. Please check the issues above."
    exit 1
fi