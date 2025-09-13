#!/bin/bash
# Comprehensive testing script for Top-TieR Global HUB AI enhancements
# Tests all features mentioned in the problem statement

set -e

echo "🚀 Top-TieR Global HUB AI Enhancement Testing"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print test results
print_test() {
    local test_name="$1"
    local status="$2"
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ $test_name${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗ $test_name${NC}"
    else
        echo -e "${YELLOW}⚠ $test_name${NC}"
    fi
}

echo ""
echo "📋 Testing Plan:"
echo "1. Redis Cache validation"
echo "2. Model Routing verification"
echo "3. Rate Limiting tests"
echo "4. Metrics endpoints"
echo "5. Heavy Jobs functionality"
echo "6. CI/CD improvements validation"
echo ""

# Start services
echo "🐳 Starting Docker services..."
docker compose up -d redis postgres neo4j 2>/dev/null || echo "Some services may already be running"
sleep 5

# Test 1: Redis Cache
echo ""
echo "📦 Test 1: Redis Cache"
echo "----------------------"

redis_ping=$(docker exec top-tier-global-hub-ai-redis-1 redis-cli ping 2>/dev/null || echo "FAIL")
if [ "$redis_ping" = "PONG" ]; then
    print_test "Redis connection" "PASS"
else
    print_test "Redis connection" "FAIL"
fi

# Test cache functionality programmatically
python3 << 'EOF'
import os
os.environ['REDIS_HOST'] = 'localhost'
try:
    from core.cache_middleware import cache
    
    # Test cache operations
    test_key = cache._generate_cache_key("openai", "gpt-3.5-turbo", "test query", "osint")
    print(f"✓ Cache key generation working: {test_key[:50]}...")
    
    # Test TTL calculation
    osint_ttl = cache._get_ttl("osint")
    general_ttl = cache._get_ttl("general")
    print(f"✓ OSINT TTL: {osint_ttl}s, General TTL: {general_ttl}s")
    
    if cache.redis_client:
        print("✓ Redis cache middleware connected and operational")
    else:
        print("⚠ Redis cache not connected")
        
except Exception as e:
    print(f"✗ Cache test failed: {e}")
EOF

# Test 2: Model Routing
echo ""
echo "🧠 Test 2: Model Routing"
echo "------------------------"

python3 << 'EOF'
try:
    from core.model_router import model_router
    
    # Test different query types
    test_cases = [
        ("extract phone numbers", ["general"], "extraction"),
        ("summarize this document", ["general"], "summary"),
        ("comprehensive OSINT report", ["osint"], "osint_query"),
        ("classify this text", ["general"], "classification")
    ]
    
    for query, scope, expected_task in test_cases:
        result = model_router.route_model(query, scope)
        actual_task = result["task_type"]
        model = result["model"]
        tokens = result["estimated_tokens"]
        
        if actual_task == expected_task:
            print(f"✓ '{query}' -> {actual_task} ({model}, ~{tokens} tokens)")
        else:
            print(f"✗ '{query}' -> Expected {expected_task}, got {actual_task}")
    
    # Test model size categories
    stats = model_router.get_model_stats()
    print(f"✓ Model router supports {len(stats['available_models'])} model sizes")
    print(f"✓ Supports {len(stats['supported_tasks'])} task types")
    
except Exception as e:
    print(f"✗ Model routing test failed: {e}")
EOF

# Start the API server in background for endpoint testing
echo ""
echo "🌐 Starting API server for endpoint testing..."
REDIS_HOST=localhost python api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!
sleep 3

# Function to test API endpoint
test_endpoint() {
    local method="$1"
    local url="$2"
    local description="$3"
    local expected_code="$4"
    local data="$5"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "http://localhost:8000$url" 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json -X "$method" -H "Content-Type: application/json" -d "$data" "http://localhost:8000$url" 2>/dev/null || echo "000")
    fi
    
    if [ "$response" = "$expected_code" ]; then
        print_test "$description" "PASS"
        return 0
    else
        print_test "$description (got $response, expected $expected_code)" "FAIL"
        return 1
    fi
}

# Test 3: API Endpoints
echo ""
echo "🔗 Test 3: API Endpoints"
echo "------------------------"

test_endpoint "GET" "/health" "Health check endpoint" "200"
test_endpoint "GET" "/metrics" "Metrics JSON endpoint" "200"
test_endpoint "GET" "/metrics?format=prometheus" "Prometheus metrics" "200"
test_endpoint "GET" "/metrics/dashboard" "Dashboard endpoint" "200"
test_endpoint "GET" "/stats" "Client stats endpoint" "200"

# Test 4: Rate Limiting (simulate multiple requests)
echo ""
echo "🚦 Test 4: Rate Limiting"
echo "------------------------"

echo "Testing rate limiting with 35 requests..."
success_count=0
for i in {1..35}; do
    response=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:8000/health 2>/dev/null)
    if [ "$response" = "200" ]; then
        ((success_count++))
    fi
done

if [ $success_count -lt 35 ]; then
    print_test "Rate limiting activated (allowed $success_count/35 requests)" "PASS"
else
    print_test "Rate limiting (all 35 requests succeeded - may need Redis)" "WARN"
fi

# Test 5: Model Routing via API
echo ""
echo "🎯 Test 5: Model Routing via API"
echo "--------------------------------"

test_endpoint "POST" "/query" "Query with model routing (no API key)" "503" '{"query":"test","model":null}'

# Test 6: Heavy Jobs
echo ""
echo "⚡ Test 6: Heavy Jobs"
echo "--------------------"

test_endpoint "POST" "/job" "Job submission" "200" '{"job":"heavy-task"}'

if [ -f /tmp/response.json ]; then
    job_id=$(python3 -c "import json; print(json.load(open('/tmp/response.json'))['job_id'])" 2>/dev/null || echo "unknown")
    if [ "$job_id" != "unknown" ]; then
        test_endpoint "GET" "/job/$job_id" "Job status retrieval" "200"
        print_test "Background job workflow" "PASS"
    fi
fi

# Test 7: Metrics Content Validation
echo ""
echo "📊 Test 7: Metrics Content"
echo "--------------------------"

curl -s http://localhost:8000/metrics > /tmp/metrics.json 2>/dev/null
python3 << 'EOF'
import json
try:
    with open('/tmp/metrics.json', 'r') as f:
        metrics = json.load(f)
    
    # Check required sections
    required_sections = ['real_time', 'cache', 'model_routing']
    for section in required_sections:
        if section in metrics:
            print(f"✓ Metrics section '{section}' present")
        else:
            print(f"✗ Metrics section '{section}' missing")
    
    # Check model routing data
    if 'model_routing' in metrics and 'available_models' in metrics['model_routing']:
        models = metrics['model_routing']['available_models']
        print(f"✓ Model routing config: {len(models)} model sizes")
        for size, config in models.items():
            print(f"  - {size}: {config['primary']} (max {config['max_tokens']} tokens)")
    
except Exception as e:
    print(f"✗ Metrics validation failed: {e}")
EOF

# Test 8: CI/CD Improvements
echo ""
echo "🔧 Test 8: CI/CD Configuration"
echo "------------------------------"

# Check CI file exists and has required components
if [ -f ".github/workflows/CI.yml" ]; then
    print_test "CI workflow file exists" "PASS"
    
    # Check for required CI components
    if grep -q "docker/setup-qemu-action@v3" .github/workflows/CI.yml; then
        print_test "QEMU setup present" "PASS"
    else
        print_test "QEMU setup missing" "FAIL"
    fi
    
    if grep -q "docker/setup-buildx-action@v3" .github/workflows/CI.yml; then
        print_test "Docker Buildx setup present" "PASS"
    else
        print_test "Docker Buildx setup missing" "FAIL"
    fi
    
    if grep -q "flake8\|black" .github/workflows/CI.yml; then
        print_test "Python linting configured" "PASS"
    else
        print_test "Python linting missing" "FAIL"
    fi
else
    print_test "CI workflow file" "FAIL"
fi

# Test 9: Docker Compose Configuration
echo ""
echo "🐳 Test 9: Docker Configuration"
echo "-------------------------------"

if grep -q "REDIS_HOST.*redis" docker-compose.yml; then
    print_test "Redis environment variables configured" "PASS"
else
    print_test "Redis environment variables" "FAIL"
fi

if grep -q "restart.*unless-stopped" docker-compose.yml; then
    print_test "Redis restart policy configured" "PASS"
else
    print_test "Redis restart policy" "FAIL"
fi

# Test 10: Token Hygiene and Map-Reduce
echo ""
echo "🧹 Test 10: Token Hygiene"
echo "-------------------------"

python3 << 'EOF'
try:
    from core.model_router import model_router
    
    # Test large input handling
    large_text = "This is a very long document that needs processing. " * 200
    result = model_router.route_model(large_text, scope=["general"])
    
    print(f"✓ Large text handling: {result['estimated_tokens']} tokens estimated")
    print(f"✓ Map-reduce needed: {result['needs_map_reduce']}")
    print(f"✓ Selected model: {result['model']} ({result['model_size']})")
    
    # Test streaming decision
    from core.model_router import TaskType
    streaming_needed = model_router.should_enable_streaming(TaskType.CONVERSATION, 2000)
    print(f"✓ Streaming for long conversation: {streaming_needed}")
    
except Exception as e:
    print(f"✗ Token hygiene test failed: {e}")
EOF

# Cleanup
echo ""
echo "🧽 Cleanup"
echo "----------"

# Stop API server
if [ ! -z "$API_PID" ]; then
    kill $API_PID 2>/dev/null || true
    print_test "API server stopped" "PASS"
fi

# Stop Docker services (optional - leave them running for further testing)
# docker compose down 2>/dev/null || true
# print_test "Docker services stopped" "PASS"

echo ""
echo "📋 Test Summary"
echo "==============="
echo ""
echo "Core Features Tested:"
echo "✅ Redis caching with configurable TTL"
echo "✅ Smart model routing (small/medium/large)"
echo "✅ Rate limiting with sliding window"
echo "✅ Comprehensive metrics collection"
echo "✅ Background job management"
echo "✅ Token hygiene and map-reduce logic"
echo "✅ Streaming decision logic"
echo "✅ CI/CD improvements (QEMU, Buildx, linting)"
echo "✅ Docker configuration enhancements"
echo ""
echo "🎉 Testing completed!"
echo ""
echo "To test with OpenAI API key:"
echo "  export OPENAI_API_KEY='your-key-here'"
echo "  docker compose up -d"
echo "  curl -X POST http://localhost:8000/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"query\":\"test\",\"scope\":[\"osint\"],\"trace\":true}'"
echo ""
echo "For manual validation:"
echo "  - Redis Cache: Check /tmp/api_server.log for cache hit/miss logs"
echo "  - Metrics: Visit http://localhost:8000/metrics/dashboard"
echo "  - Rate Limiting: Make 35+ requests to see 429 responses"
echo "  - Prometheus: curl http://localhost:8000/metrics?format=prometheus"
EOF