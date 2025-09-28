#!/usr/bin/env bash

# ============================================================================
# Service Startup Script for Health Check
# ============================================================================
# This script starts both CORE_API and VERITAS_WEB services in the background
# for health check purposes. It ensures services are ready before running
# health checks and properly cleans up after.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
API_PID=""
WEB_PID=""
CLEANUP_REQUIRED=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] SUCCESS:${NC} $message"
            ;;
    esac
}

# Cleanup function
cleanup() {
    if [[ "$CLEANUP_REQUIRED" == "true" ]]; then
        log "INFO" "Cleaning up services..."
        
        if [[ -n "$API_PID" ]] && kill -0 "$API_PID" 2>/dev/null; then
            log "INFO" "Stopping CORE_API (PID: $API_PID)..."
            kill "$API_PID" 2>/dev/null || true
            wait "$API_PID" 2>/dev/null || true
        fi
        
        if [[ -n "$WEB_PID" ]] && kill -0 "$WEB_PID" 2>/dev/null; then
            log "INFO" "Stopping VERITAS_WEB (PID: $WEB_PID)..."
            kill "$WEB_PID" 2>/dev/null || true
            wait "$WEB_PID" 2>/dev/null || true
        fi
        
        log "SUCCESS" "Cleanup completed"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Function to wait for service to be ready
wait_for_service() {
    local name="$1"
    local url="$2"
    local max_attempts=30
    local attempt=1
    
    log "INFO" "Waiting for $name to be ready at $url..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            log "SUCCESS" "$name is ready (attempt $attempt/$max_attempts)"
            return 0
        fi
        
        log "INFO" "$name not ready yet (attempt $attempt/$max_attempts), waiting..."
        sleep 2
        ((attempt++))
    done
    
    log "ERROR" "$name failed to start after $max_attempts attempts"
    return 1
}

# Function to start CORE_API
start_core_api() {
    log "INFO" "Starting CORE_API on port 8000..."
    
    cd "$ROOT_DIR"
    export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"
    
    # Start the API server in background
    python3 api_server/__init__.py > /tmp/core_api.log 2>&1 &
    API_PID=$!
    CLEANUP_REQUIRED=true
    
    log "INFO" "CORE_API started with PID: $API_PID"
    
    # Wait for service to be ready
    if wait_for_service "CORE_API" "http://localhost:8000/health"; then
        return 0
    else
        log "ERROR" "CORE_API failed to start. Check logs at /tmp/core_api.log"
        return 1
    fi
}

# Function to start VERITAS_WEB
start_veritas_web() {
    log "INFO" "Starting VERITAS_WEB on port 8080..."
    
    cd "$ROOT_DIR/veritas-web"
    
    # Set environment variables for the service
    export MINI_WEB_PORT=8080
    export ENABLE_CACHE=false  # Disable Redis dependency for health check
    export ENABLE_MONITORING=true
    export ENABLE_ENCRYPTION=false
    export API_TOKEN=health-check-token
    
    # Start the web service in background
    python3 app.py > /tmp/veritas_web.log 2>&1 &
    WEB_PID=$!
    CLEANUP_REQUIRED=true
    
    log "INFO" "VERITAS_WEB started with PID: $WEB_PID"
    
    # Wait for service to be ready
    if wait_for_service "VERITAS_WEB" "http://localhost:8080/health"; then
        return 0
    else
        log "ERROR" "VERITAS_WEB failed to start. Check logs at /tmp/veritas_web.log"
        return 1
    fi
}

# Function to run health check
run_health_check() {
    log "INFO" "Running health check..."
    
    cd "$ROOT_DIR"
    if "$SCRIPT_DIR/veritas_health_check.sh"; then
        log "SUCCESS" "Health check passed!"
        return 0
    else
        log "ERROR" "Health check failed!"
        return 1
    fi
}

# Main execution
main() {
    log "INFO" "Starting services for health check..."
    
    # Start both services
    if start_core_api && start_veritas_web; then
        log "SUCCESS" "Both services started successfully"
        
        # Run health check
        if run_health_check; then
            log "SUCCESS" "Health check completed successfully"
            exit 0
        else
            log "ERROR" "Health check failed"
            exit 1
        fi
    else
        log "ERROR" "Failed to start services"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Start services for health check testing

Options:
    -h, --help       Show this help message
    --logs           Show service logs after completion

Examples:
    $0               # Start services and run health check
    $0 --logs        # Start services, run health check, and show logs

EOF
}

# Parse command line arguments
SHOW_LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main

# Show logs if requested
if [[ "$SHOW_LOGS" == "true" ]]; then
    echo ""
    echo "=== CORE_API Logs ==="
    cat /tmp/core_api.log 2>/dev/null || echo "No logs available"
    echo ""
    echo "=== VERITAS_WEB Logs ==="
    cat /tmp/veritas_web.log 2>/dev/null || echo "No logs available"
fi