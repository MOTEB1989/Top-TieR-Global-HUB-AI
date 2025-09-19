#!/usr/bin/env bash

echo "=== Stopping Local Services ==="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to stop service by PID
stop_service() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null; then
            echo "Stopping $name (PID: $pid)..."
            kill $pid
            # Wait a moment and force kill if necessary
            sleep 2
            if ps -p $pid > /dev/null; then
                echo "Force stopping $name..."
                kill -9 $pid
            fi
        else
            echo "$name process (PID: $pid) not found"
        fi
        rm -f "$pid_file"
    else
        echo "No PID file found for $name"
    fi
}

# Stop services by PID files
if [ -d "logs" ]; then
    stop_service "CORE_API" "logs/core_api.pid"
    stop_service "VERITAS_WEB" "logs/veritas_web.pid"
else
    echo "No logs directory found"
fi

# Kill any remaining uvicorn processes
echo "Cleaning up any remaining uvicorn processes..."
pkill -f "uvicorn" || true

# Kill any remaining python processes running our apps
pkill -f "api_server" || true
pkill -f "veritas-web/app.py" || true

echo -e "${GREEN}✅ Services stopped${NC}"
echo "You can now start services again with: ./scripts/start_services_local.sh"