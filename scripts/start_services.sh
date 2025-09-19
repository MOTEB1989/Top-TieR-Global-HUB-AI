#!/bin/bash

# Script to start Veritas services for health checking
# This script starts the API server and Veritas web service in the background

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Function to check if a port is available
check_port() {
    local port=$1
    if command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep -q ":$port "; then
            return 1  # Port is in use
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln | grep -q ":$port "; then
            return 1  # Port is in use
        fi
    else
        # Fallback: try to connect to the port
        if timeout 1 bash -c "echo >/dev/tcp/localhost/$port" 2>/dev/null; then
            return 1  # Port is in use
        fi
    fi
    return 0  # Port is free
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    log "Waiting for $name to be ready at $url..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            log "$name is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    error "$name failed to become ready within $((max_attempts * 2)) seconds"
    return 1
}

# Main function
main() {
    log "Starting Veritas services..."
    
    cd "$PROJECT_ROOT"
    
    # Install Python dependencies if not already installed
    if ! python3 -c "import fastapi" >/dev/null 2>&1; then
        log "Installing Python dependencies..."
        python3 -m pip install --user -r requirements.txt
    fi
    
    # Install veritas-web dependencies
    if ! python3 -c "import httpx" >/dev/null 2>&1; then
        log "Installing Veritas-web dependencies..."
        python3 -m pip install --user -r veritas-web/requirements.txt
    fi
    
    # Check if API server port is available
    if ! check_port 8000; then
        warn "Port 8000 is already in use, attempting to continue..."
    else
        log "Starting API server on port 8000..."
        python3 api_server/__init__.py &
        API_PID=$!
        echo $API_PID > /tmp/api_server.pid
        log "API server started with PID $API_PID"
    fi
    
    # Check if veritas-web port is available
    if ! check_port 8080; then
        warn "Port 8080 is already in use, attempting to continue..."
    else
        log "Starting Veritas-web service on port 8080..."
        cd veritas-web
        MINI_WEB_PORT=8080 python3 app.py &
        VERITAS_PID=$!
        echo $VERITAS_PID > /tmp/veritas_web.pid
        log "Veritas-web service started with PID $VERITAS_PID"
        cd ..
    fi
    
    # Wait for services to be ready
    wait_for_service "http://localhost:8000/health" "API server"
    wait_for_service "http://localhost:8080/health" "Veritas-web service"
    
    log "All services are ready!"
    return 0
}

# Cleanup function
cleanup() {
    log "Cleaning up services..."
    
    # Kill API server if we started it
    if [ -f /tmp/api_server.pid ]; then
        local api_pid=$(cat /tmp/api_server.pid)
        if kill -0 $api_pid 2>/dev/null; then
            log "Stopping API server (PID $api_pid)..."
            kill $api_pid
            wait $api_pid 2>/dev/null || true
        fi
        rm -f /tmp/api_server.pid
    fi
    
    # Kill Veritas-web service if we started it
    if [ -f /tmp/veritas_web.pid ]; then
        local veritas_pid=$(cat /tmp/veritas_web.pid)
        if kill -0 $veritas_pid 2>/dev/null; then
            log "Stopping Veritas-web service (PID $veritas_pid)..."
            kill $veritas_pid
            wait $veritas_pid 2>/dev/null || true
        fi
        rm -f /tmp/veritas_web.pid
    fi
    
    log "Cleanup complete"
}

# Handle script termination
trap cleanup EXIT INT TERM

# Parse command line arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        cleanup
        exit 0
        ;;
    "restart")
        cleanup
        sleep 2
        main
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        echo "  start   - Start the services (default)"
        echo "  stop    - Stop the services"
        echo "  restart - Restart the services"
        exit 1
        ;;
esac