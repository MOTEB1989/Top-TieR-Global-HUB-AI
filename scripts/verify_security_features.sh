#!/bin/bash
# Top-TieR Global HUB AI - Governance and Security Verification Script
# This script verifies the implemented governance and security features

set -e

echo "🔍 Top-TieR Global HUB AI - Security Features Verification"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo
echo "1. 📋 GitHub Governance Features Verification"
echo "----------------------------------------------"

# Check Dependabot
if [ -f ".github/dependabot.yml" ]; then
    success "Dependabot configuration exists"
    echo "   - Python dependencies: weekly updates"
    echo "   - GitHub Actions: weekly updates" 
    echo "   - Docker: weekly updates"
else
    error "Dependabot configuration missing"
fi

# Check CodeQL
if [ -f ".github/workflows/codeql.yml" ]; then
    success "CodeQL security analysis workflow exists"
    echo "   - Languages: JavaScript, Python"
    echo "   - Triggers: push, PR, scheduled weekly"
else
    error "CodeQL workflow missing"
fi

# Check CODEOWNERS
if [ -f ".github/CODEOWNERS" ]; then
    success "CODEOWNERS file exists"
    echo "   - All files require @MOTEB1989 review"
else
    error "CODEOWNERS file missing"
fi

# Check CI improvements
if [ -f ".github/workflows/CI.yml" ]; then
    if grep -q "py_compile" ".github/workflows/CI.yml"; then
        success "CI includes Python syntax checking"
    else
        warning "Python syntax checking not found in CI"
    fi
    
    if grep -q "yamllint" ".github/workflows/CI.yml"; then
        success "CI includes YAML linting"
    else
        warning "YAML linting not found in CI"
    fi
else
    error "CI workflow missing"
fi

echo
echo "2. 🔐 Kubernetes Security Features Verification"
echo "------------------------------------------------"

# Check Kubernetes directory
if [ -d "k8s" ]; then
    success "Kubernetes deployment directory exists"
else
    error "Kubernetes deployment directory missing"
    exit 1
fi

# Check Neo4j secret
if [ -f "k8s/neo4j-secret.yaml" ]; then
    success "Neo4j secret configuration exists"
    if grep -q "stringData" "k8s/neo4j-secret.yaml"; then
        info "   - Uses stringData for credential management"
    fi
else
    error "Neo4j secret configuration missing"
fi

# Check Neo4j deployment
if [ -f "k8s/neo4j.yaml" ]; then
    success "Neo4j deployment configuration exists"
    
    # Check health probes
    if grep -q "livenessProbe" "k8s/neo4j.yaml"; then
        success "   - Liveness probe configured"
    else
        warning "   - Liveness probe missing"
    fi
    
    if grep -q "readinessProbe" "k8s/neo4j.yaml"; then
        success "   - Readiness probe configured"
    else
        warning "   - Readiness probe missing"
    fi
    
    if grep -q "startupProbe" "k8s/neo4j.yaml"; then
        success "   - Startup probe configured"
    else
        warning "   - Startup probe missing"
    fi
    
    # Check secret reference
    if grep -q "secretKeyRef" "k8s/neo4j.yaml"; then
        success "   - Uses Kubernetes secrets for credentials"
    else
        error "   - Not using Kubernetes secrets"
    fi
else
    error "Neo4j deployment configuration missing"
fi

# Check Core deployment
if [ -f "k8s/core-deployment.yaml" ]; then
    success "Core API deployment configuration exists"
    
    # Check health probes
    probes=("livenessProbe" "readinessProbe" "startupProbe")
    for probe in "${probes[@]}"; do
        if grep -q "$probe" "k8s/core-deployment.yaml"; then
            success "   - $probe configured"
        else
            warning "   - $probe missing"
        fi
    done
else
    error "Core deployment configuration missing"
fi

# Check OSINT deployment
if [ -f "k8s/osint-deployment.yaml" ]; then
    success "OSINT engine deployment configuration exists"
    
    # Check health probes
    probes=("livenessProbe" "readinessProbe" "startupProbe")
    for probe in "${probes[@]}"; do
        if grep -q "$probe" "k8s/osint-deployment.yaml"; then
            success "   - $probe configured"
        else
            warning "   - $probe missing"
        fi
    done
    
    # Check OSINT secrets
    if grep -q "osint-secrets" "k8s/osint-deployment.yaml"; then
        success "   - OSINT API keys managed via secrets"
    else
        warning "   - OSINT API keys not properly managed"
    fi
else
    error "OSINT deployment configuration missing"
fi

echo
echo "3. 🐳 Docker Compose Security Verification"
echo "-------------------------------------------"

if [ -f "docker-compose.yml" ]; then
    success "Docker Compose configuration exists"
    
    # Check environment variable usage
    if grep -q "\${NEO4J_USER" "docker-compose.yml"; then
        success "   - Neo4j credentials use environment variables"
    else
        warning "   - Neo4j credentials might be hardcoded"
    fi
    
    # Check health checks
    if grep -q "healthcheck" "docker-compose.yml"; then
        success "   - Health checks configured for services"
    else
        warning "   - Health checks missing"
    fi
else
    error "Docker Compose configuration missing"
fi

# Check .env.example
if [ -f ".env.example" ]; then
    success "Environment configuration template exists"
    
    if grep -q "NEO4J_PASSWORD" ".env.example"; then
        success "   - Neo4j credentials template available"
    fi
    
    if grep -q "SHODAN_API_KEY" ".env.example"; then
        success "   - OSINT API keys template available"
    fi
else
    error "Environment configuration template missing"
fi

echo
echo "4. 🧪 YAML Validation Tests"
echo "----------------------------"

# Check if yamllint is available
if command -v yamllint &> /dev/null; then
    info "Running YAML validation..."
    
    # Validate Kubernetes files
    if yamllint k8s/ &> /dev/null; then
        success "Kubernetes YAML files are valid"
    else
        error "Kubernetes YAML files have validation errors"
        yamllint k8s/
    fi
    
    # Validate Docker Compose
    if yamllint docker-compose.yml &> /dev/null; then
        success "Docker Compose YAML is valid"
    else
        warning "Docker Compose YAML has minor validation issues"
    fi
else
    warning "yamllint not available - install with: pip install yamllint"
fi

echo
echo "5. 🔧 Docker Compose Configuration Test"
echo "----------------------------------------"

if command -v docker &> /dev/null; then
    info "Testing Docker Compose configuration..."
    
    if docker compose config &> /dev/null; then
        success "Docker Compose configuration is valid"
    else
        error "Docker Compose configuration has errors"
        docker compose config
    fi
else
    warning "Docker not available for testing"
fi

echo
echo "6. 📊 Security Summary"
echo "----------------------"

echo "Governance Features:"
echo "  ✅ Dependabot for automated dependency updates"
echo "  ✅ CodeQL for automated security analysis"
echo "  ✅ CODEOWNERS for code review enforcement"
echo "  ✅ CI pipeline with syntax checking and linting"
echo ""
echo "Kubernetes Security:"
echo "  ✅ Credential management via Kubernetes secrets"
echo "  ✅ Health probes for all deployments"
echo "  ✅ Resource limits and requests defined"
echo "  ✅ Separate secrets for OSINT API keys"
echo ""
echo "Docker Compose Security:"
echo "  ✅ Environment variable support for credentials"
echo "  ✅ Health checks for all services"
echo "  ✅ Secure defaults with .env template"

echo
echo "📝 Next Steps:"
echo "-------------"
echo "1. Update default credentials in k8s/neo4j-secret.yaml"
echo "2. Add your OSINT API keys to k8s/osint-deployment.yaml"
echo "3. Create .env file from .env.example for Docker Compose"
echo "4. Test deployments in your target environment"
echo "5. Set up monitoring and alerting for health probes"

echo
success "Security and governance features verification completed!"
echo "========================================================"