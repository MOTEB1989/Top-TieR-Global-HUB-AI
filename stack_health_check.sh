#!/bin/bash

# ============================================================================
# Stack Health Check Script for Top-TieR-Global-HUB-AI
# ============================================================================
# This script performs comprehensive health checks on the entire stack:
# - Git remote connectivity
# - CI badge status
# - Core health endpoints
# - JSON response validation
# - Neo4j database status
# - Docker services health
# - Dependencies verification

set -euo pipefail

# Configuration
SCRIPT_VERSION="2.0"
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
NEO4J_URL="${NEO4J_URL:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASS="${NEO4J_PASS:-password}"
TIMEOUT=${TIMEOUT:-30}
VERBOSE=${VERBOSE:-false}
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global status tracking
OVERALL_STATUS="HEALTHY"
FAILED_CHECKS=0
TOTAL_CHECKS=0

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[${timestamp}] INFO:${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[${timestamp}] WARN:${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] ERROR:${NC} $message"
            OVERALL_STATUS="UNHEALTHY"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] SUCCESS:${NC} $message"
            ;;
        "DEBUG")
            if [[ "$VERBOSE" == "true" ]]; then
                echo -e "${BLUE}[${timestamp}] DEBUG:${NC} $message"
            fi
            ;;
    esac
}

# Function to increment check counter
check_start() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check git remote connectivity
check_git_remote() {
    log "INFO" "Checking Git remote connectivity..."
    check_start
    
    if ! command_exists git; then
        log "ERROR" "Git command not found"
        return 1
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "ERROR" "Not in a Git repository"
        return 1
    fi
    
    # Check remote connectivity
    if git ls-remote --exit-code origin > /dev/null 2>&1; then
        log "SUCCESS" "Git remote is accessible"
        
        # Get additional git info
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        local commit=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        log "DEBUG" "Current branch: $branch, commit: $commit"
        
        return 0
    else
        log "ERROR" "Cannot connect to Git remote"
        return 1
    fi
}

# Function to check CI badge status
check_ci_badge() {
    log "INFO" "Checking CI badge status..."
    check_start
    
    local ci_url="https://github.com/MOTEB1989/Top-TieR-Global-HUB-AI/actions/workflows/CI.yml/badge.svg"
    
    if command_exists curl; then
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$ci_url")
        
        if [[ "$http_code" == "200" ]]; then
            log "SUCCESS" "CI badge is accessible (HTTP $http_code)"
            return 0
        else
            log "ERROR" "CI badge returned HTTP $http_code"
            return 1
        fi
    else
        log "WARN" "curl not available, skipping CI badge check"
        return 0
    fi
}

# Function to check core health endpoint
check_core_health() {
    log "INFO" "Checking core health endpoint..."
    check_start
    
    if command_exists curl; then
        local response=$(curl -s --max-time $TIMEOUT "$API_BASE_URL/health" 2>/dev/null || echo "")
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$API_BASE_URL/health" 2>/dev/null || echo "000")
        
        if [[ "$http_code" == "200" ]]; then
            log "SUCCESS" "Core health endpoint is accessible (HTTP $http_code)"
            log "DEBUG" "Health response: $response"
            return 0
        else
            log "ERROR" "Core health endpoint returned HTTP $http_code"
            return 1
        fi
    else
        log "WARN" "curl not available, skipping core health check"
        return 0
    fi
}

# Function to validate JSON response
check_json_response() {
    log "INFO" "Checking JSON response format..."
    check_start
    
    if ! command_exists curl || ! command_exists jq; then
        log "WARN" "curl or jq not available, skipping JSON validation"
        return 0
    fi
    
    local json_response=$(curl -s --max-time $TIMEOUT "$API_BASE_URL/health" 2>/dev/null || echo "{}")
    
    if echo "$json_response" | jq . > /dev/null 2>&1; then
        log "SUCCESS" "JSON response is valid"
        
        # Check for expected fields
        local status=$(echo "$json_response" | jq -r '.status // "unknown"' 2>/dev/null)
        local timestamp=$(echo "$json_response" | jq -r '.timestamp // "unknown"' 2>/dev/null)
        
        log "DEBUG" "Health status: $status, timestamp: $timestamp"
        return 0
    else
        log "ERROR" "Invalid JSON response from health endpoint"
        return 1
    fi
}

# Function to check Neo4j status
check_neo4j_status() {
    log "INFO" "Checking Neo4j database status..."
    check_start
    
    # Check if Neo4j container is running
    if command_exists docker; then
        local neo4j_container=$(docker ps --filter 'name=neo4j' --format '{{.Names}}' | head -n1)
        
        if [[ -n "$neo4j_container" ]]; then
            log "SUCCESS" "Neo4j container '$neo4j_container' is running"
            
            # Try to connect to Neo4j
            if command_exists cypher-shell; then
                if echo "RETURN 'connection test' as result;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" --non-interactive > /dev/null 2>&1; then
                    log "SUCCESS" "Neo4j database is accessible"
                    
                    # Get database info
                    local db_info=$(echo "CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version;" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" --non-interactive 2>/dev/null | grep -v "name\|----" | head -1 || echo "unknown")
                    log "DEBUG" "Neo4j info: $db_info"
                    
                    return 0
                else
                    log "ERROR" "Cannot connect to Neo4j database"
                    return 1
                fi
            else
                log "WARN" "cypher-shell not available, cannot test Neo4j connectivity"
                return 0
            fi
        else
            log "ERROR" "No Neo4j container found"
            return 1
        fi
    else
        log "WARN" "Docker not available, cannot check Neo4j container"
        return 0
    fi
}

# Function to check Docker services
check_docker_services() {
    log "INFO" "Checking Docker services status..."
    check_start
    
    if ! command_exists docker; then
        log "WARN" "Docker not available, skipping services check"
        return 0
    fi
    
    # Check if docker-compose.yml exists
    if [[ ! -f "docker-compose.yml" ]]; then
        log "WARN" "docker-compose.yml not found, skipping Docker services check"
        return 0
    fi
    
    # Get running services
    local running_services=$(docker compose ps --services --filter "status=running" 2>/dev/null || echo "")
    local total_services=$(docker compose config --services 2>/dev/null | wc -l || echo "0")
    local running_count=$(echo "$running_services" | grep -v '^$' | wc -l || echo "0")
    
    if [[ "$running_count" -gt 0 ]]; then
        log "SUCCESS" "Docker services: $running_count/$total_services running"
        log "DEBUG" "Running services: $(echo "$running_services" | tr '\n' ', ' | sed 's/,$//')"
        
        # Check health of individual services
        for service in $running_services; do
            local health=$(docker compose ps "$service" --format "{{.Health}}" 2>/dev/null || echo "unknown")
            if [[ "$health" == "healthy" ]] || [[ "$health" == "" ]]; then
                log "DEBUG" "Service '$service': OK"
            else
                log "WARN" "Service '$service': $health"
            fi
        done
        
        return 0
    else
        log "ERROR" "No Docker services are running"
        return 1
    fi
}

# Function to check system dependencies
check_dependencies() {
    log "INFO" "Checking system dependencies..."
    check_start
    
    local required_deps=("python3" "pip3")
    local optional_deps=("curl" "jq" "docker" "git")
    local missing_required=()
    local missing_optional=()
    
    # Check required dependencies
    for dep in "${required_deps[@]}"; do
        if ! command_exists "$dep"; then
            missing_required+=("$dep")
        fi
    done
    
    # Check optional dependencies
    for dep in "${optional_deps[@]}"; do
        if ! command_exists "$dep"; then
            missing_optional+=("$dep")
        fi
    done
    
    if [[ ${#missing_required[@]} -eq 0 ]]; then
        log "SUCCESS" "All required dependencies are available"
        
        if [[ ${#missing_optional[@]} -gt 0 ]]; then
            log "WARN" "Missing optional dependencies: ${missing_optional[*]}"
        else
            log "SUCCESS" "All optional dependencies are available"
        fi
        
        # Show Python version
        local python_version=$(python3 --version 2>/dev/null || echo "unknown")
        log "DEBUG" "Python version: $python_version"
        
        return 0
    else
        log "ERROR" "Missing required dependencies: ${missing_required[*]}"
        return 1
    fi
}

# Function to send notification (if webhook is configured)
send_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "$SLACK_WEBHOOK" ]] && command_exists curl; then
        local color="good"
        [[ "$status" == "UNHEALTHY" ]] && color="danger"
        
        local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$color",
            "title": "Stack Health Check - $status",
            "text": "$message",
            "footer": "Top-TieR-Global-HUB-AI Health Check",
            "ts": $(date +%s)
        }
    ]
}
EOF
)
        
        curl -s -X POST -H 'Content-type: application/json' \
             --data "$payload" "$SLACK_WEBHOOK" > /dev/null 2>&1 || true
    fi
}

# Function to generate health report
generate_report() {
    local contact_email="${1:-admin@example.com}"
    
    echo ""
    echo "============================================================================"
    echo "                    STACK HEALTH CHECK REPORT"
    echo "============================================================================"
    echo "Script Version: $SCRIPT_VERSION"
    echo "Check Time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Contact: $contact_email"
    echo ""
    echo "Overall Status: $OVERALL_STATUS"
    echo "Failed Checks: $FAILED_CHECKS/$TOTAL_CHECKS"
    echo ""
    echo "API Base URL: $API_BASE_URL"
    echo "Neo4j URL: $NEO4J_URL"
    echo ""
    
    if [[ "$OVERALL_STATUS" == "HEALTHY" ]]; then
        echo -e "${GREEN}✅ All critical systems are operational${NC}"
    else
        echo -e "${RED}❌ Some systems require attention${NC}"
        echo ""
        echo "Recommended Actions:"
        echo "1. Review the error messages above"
        echo "2. Check service logs: docker compose logs"
        echo "3. Verify configuration and environment variables"
        echo "4. Contact: $contact_email for assistance"
    fi
    
    echo ""
    echo "============================================================================"
}

# Main execution function
main() {
    local contact_email="${1:-admin@example.com}"
    
    echo "============================================================================"
    echo "          Top-TieR-Global-HUB-AI Stack Health Check v$SCRIPT_VERSION"
    echo "============================================================================"
    echo ""
    
    log "INFO" "Starting comprehensive health check..."
    
    # Run all health checks
    check_dependencies || true
    check_git_remote || true
    check_ci_badge || true
    check_core_health || true
    check_json_response || true
    check_neo4j_status || true
    check_docker_services || true
    
    # Generate report
    generate_report "$contact_email"
    
    # Send notification if configured
    local summary="Completed $TOTAL_CHECKS checks. Status: $OVERALL_STATUS"
    [[ "$FAILED_CHECKS" -gt 0 ]] && summary="$summary ($FAILED_CHECKS failed)"
    send_notification "$OVERALL_STATUS" "$summary"
    
    # Exit with appropriate code
    if [[ "$OVERALL_STATUS" == "HEALTHY" ]]; then
        exit 0
    else
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [CONTACT_EMAIL] [OPTIONS]

Stack health check script for Top-TieR-Global-HUB-AI

Arguments:
    CONTACT_EMAIL    Contact email for support (default: admin@example.com)

Environment Variables:
    API_BASE_URL     Base URL for API health checks (default: http://localhost:8000)
    NEO4J_URL        Neo4j connection URL (default: bolt://localhost:7687)
    NEO4J_USER       Neo4j username (default: neo4j)
    NEO4J_PASS       Neo4j password (default: password)
    TIMEOUT          Timeout for HTTP requests in seconds (default: 30)
    VERBOSE          Enable verbose output (default: false)
    SLACK_WEBHOOK_URL Slack webhook for notifications (optional)

Options:
    -h, --help       Show this help message
    -v, --verbose    Enable verbose output
    --version        Show script version

Examples:
    $0                                    # Basic health check
    $0 admin@company.com                  # With custom contact email
    VERBOSE=true $0                       # With verbose output
    API_BASE_URL=http://prod:8000 $0      # With custom API URL

Exit Codes:
    0    All checks passed (HEALTHY)
    1    One or more checks failed (UNHEALTHY)

EOF
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --version)
        echo "Stack Health Check Script v$SCRIPT_VERSION"
        exit 0
        ;;
    -v|--verbose)
        VERBOSE=true
        shift
        ;;
esac

# Set verbose mode if requested
if [[ "${1:-}" == "-v" ]] || [[ "${1:-}" == "--verbose" ]]; then
    VERBOSE=true
    shift
fi

# Run main function with contact email
main "${1:-admin@example.com}"