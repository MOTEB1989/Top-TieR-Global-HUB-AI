#!/usr/bin/env bash

echo "=== Starting Local Services for Development ==="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        echo -e "${YELLOW}Warning: Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $name failed to start within $max_attempts seconds${NC}"
    return 1
}

# Check dependencies
echo "Checking dependencies..."
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${RED}Error: FastAPI/Uvicorn not installed. Run: pip install -r requirements.txt${NC}"
    exit 1
fi

# Check if ports are available
echo "Checking ports..."
check_port 8000 || echo "CORE_API may conflict with existing service"
check_port 8080 || echo "VERITAS_WEB may conflict with existing service"

# Create log directory
mkdir -p logs

# Start CORE_API
echo "Starting CORE_API on port 8000..."
python3 -c "from api_server import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)" > logs/core_api.log 2>&1 &
CORE_PID=$!
echo "CORE_API PID: $CORE_PID"

# Start VERITAS_WEB
echo "Starting VERITAS_WEB on port 8080..."
cd veritas-web
MINI_WEB_PORT=8080 python3 app.py > ../logs/veritas_web.log 2>&1 &
VERITAS_PID=$!
echo "VERITAS_WEB PID: $VERITAS_PID"
cd ..

# Wait for services to be ready
echo ""
wait_for_service "CORE_API" "http://localhost:8000/health"
wait_for_service "VERITAS_WEB" "http://localhost:8080/health"

# Save PIDs for cleanup
echo "$CORE_PID" > logs/core_api.pid
echo "$VERITAS_PID" > logs/veritas_web.pid

echo ""
echo -e "${GREEN}=== Services Started Successfully ===${NC}"
echo "CORE_API: http://localhost:8000"
echo "  - Health: http://localhost:8000/health"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "VERITAS_WEB: http://localhost:8080"
echo "  - Health: http://localhost:8080/health"
echo "  - Docs: http://localhost:8080/docs"
echo ""
echo "Logs are saved in the logs/ directory"
echo "To stop services, run: ./scripts/stop_services_local.sh"
echo ""
echo "Running health check..."
sleep 2
./scripts/veritas_health_check.sh