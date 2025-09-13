#!/bin/bash
# Docker Compose Validation Script for Top-TieR-Global-HUB-AI
# This script validates the security enhancements and health of services

set -e

echo "🔍 Validating Docker Compose deployment..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ Docker or docker-compose is not installed"
    exit 1
fi

# Check if the Neo4j environment file exists
NEO4J_ENV_FILE="/opt/veritas/.env.neo4j"
if [ ! -f "$NEO4J_ENV_FILE" ]; then
    echo "⚠️  Neo4j environment file not found at $NEO4J_ENV_FILE"
    echo "📝 Creating example file for testing..."
    sudo mkdir -p /opt/veritas
    sudo cp /tmp/veritas_config/.env.neo4j "$NEO4J_ENV_FILE" 2>/dev/null || {
        echo "📝 Please create $NEO4J_ENV_FILE with the following content:"
        cat /tmp/veritas_config/.env.neo4j
        echo ""
        echo "Then run this script again."
        exit 1
    }
fi

echo "✅ Neo4j environment file found"

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

services=("api" "redis" "postgres" "neo4j")
all_healthy=true

for service in "${services[@]}"; do
    health_status=$(docker-compose ps --format json | jq -r ".[] | select(.Service == \"$service\") | .Health")
    if [ "$health_status" = "healthy" ] || [ "$health_status" = "null" ]; then
        echo "✅ $service: healthy"
    else
        echo "❌ $service: $health_status"
        all_healthy=false
    fi
done

# Test Neo4j connection with secure credentials
echo "🔐 Testing Neo4j secure connection..."
if docker-compose exec neo4j cypher-shell -u neo4j -p secure_neo4j_password_change_me "RETURN 'Connection successful' as status" &>/dev/null; then
    echo "✅ Neo4j secure authentication working"
else
    echo "❌ Neo4j secure authentication failed"
    all_healthy=false
fi

# Test API endpoints
echo "🌐 Testing API endpoints..."
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Core API health endpoint responding"
else
    echo "❌ Core API health endpoint not responding"
    all_healthy=false
fi

# Check if veritas-web is running (optional profile)
if docker-compose ps veritas-web &>/dev/null; then
    if curl -f http://localhost:8088/health &>/dev/null; then
        echo "✅ Veritas Web health endpoint responding"
    else
        echo "❌ Veritas Web health endpoint not responding"
        all_healthy=false
    fi
fi

# Show container status
echo ""
echo "📊 Container Status:"
docker-compose ps

# Show logs summary
echo ""
echo "📝 Recent logs (last 10 lines per service):"
for service in "${services[@]}"; do
    echo "--- $service ---"
    docker-compose logs --tail=10 "$service"
    echo ""
done

if [ "$all_healthy" = true ]; then
    echo "🎉 All services are healthy and secure!"
    exit 0
else
    echo "⚠️  Some services are not healthy. Check logs above for details."
    exit 1
fi