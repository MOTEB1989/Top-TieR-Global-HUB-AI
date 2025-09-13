#!/bin/bash
# Kubernetes Validation Script for Top-TieR-Global-HUB-AI
# This script validates the health and security of Kubernetes deployment

set -e

echo "🔍 Validating Kubernetes deployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

NAMESPACE="top-tier-hub"

echo "✅ Kubernetes cluster connection verified"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "❌ Namespace $NAMESPACE does not exist"
    exit 1
fi

echo "✅ Namespace $NAMESPACE found"

# Check secrets
echo "🔐 Validating secrets..."
secrets=("neo4j-secret" "postgres-secret" "osint-secret")
for secret in "${secrets[@]}"; do
    if kubectl get secret "$secret" -n "$NAMESPACE" &>/dev/null; then
        echo "✅ Secret $secret exists"
    else
        echo "❌ Secret $secret not found"
    fi
done

# Check deployments
echo "🚀 Checking deployment status..."
deployments=("core-api" "osint-service" "neo4j" "postgres" "redis")
all_healthy=true

for deployment in "${deployments[@]}"; do
    if kubectl get deployment "$deployment" -n "$NAMESPACE" &>/dev/null; then
        ready_replicas=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
        desired_replicas=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')
        
        if [ "$ready_replicas" = "$desired_replicas" ]; then
            echo "✅ $deployment: $ready_replicas/$desired_replicas replicas ready"
        else
            echo "❌ $deployment: $ready_replicas/$desired_replicas replicas ready"
            all_healthy=false
        fi
    else
        echo "❌ Deployment $deployment not found"
        all_healthy=false
    fi
done

# Check services
echo "🌐 Checking services..."
services=("core-api-service" "osint-service" "neo4j-service" "postgres-service" "redis-service")
for service in "${services[@]}"; do
    if kubectl get service "$service" -n "$NAMESPACE" &>/dev/null; then
        echo "✅ Service $service exists"
    else
        echo "❌ Service $service not found"
        all_healthy=false
    fi
done

# Check persistent volume claims
echo "💾 Checking persistent volumes..."
pvcs=("neo4j-data-pvc" "neo4j-logs-pvc" "postgres-data-pvc" "redis-data-pvc")
for pvc in "${pvcs[@]}"; do
    if kubectl get pvc "$pvc" -n "$NAMESPACE" &>/dev/null; then
        status=$(kubectl get pvc "$pvc" -n "$NAMESPACE" -o jsonpath='{.status.phase}')
        if [ "$status" = "Bound" ]; then
            echo "✅ PVC $pvc: $status"
        else
            echo "⚠️  PVC $pvc: $status"
        fi
    else
        echo "❌ PVC $pvc not found"
        all_healthy=false
    fi
done

# Test health endpoints using port-forward
echo "🏥 Testing health endpoints..."

# Function to test endpoint with port-forward
test_endpoint() {
    local service=$1
    local port=$2
    local path=$3
    local local_port=$((port + 1000))  # Use different local port to avoid conflicts
    
    echo "Testing $service health endpoint..."
    
    # Start port-forward in background
    kubectl port-forward "service/$service" "$local_port:$port" -n "$NAMESPACE" &>/dev/null &
    local pf_pid=$!
    
    # Wait a moment for port-forward to establish
    sleep 3
    
    # Test the endpoint
    if curl -f "http://localhost:$local_port$path" &>/dev/null; then
        echo "✅ $service health endpoint responding"
        kill $pf_pid 2>/dev/null || true
        return 0
    else
        echo "❌ $service health endpoint not responding"
        kill $pf_pid 2>/dev/null || true
        return 1
    fi
}

# Test core API health
if ! test_endpoint "core-api-service" 8000 "/health"; then
    all_healthy=false
fi

# Test OSINT service health
if ! test_endpoint "osint-service" 8088 "/health"; then
    all_healthy=false
fi

# Show pod status
echo ""
echo "📊 Pod Status:"
kubectl get pods -n "$NAMESPACE"

# Show events
echo ""
echo "📝 Recent Events:"
kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10

# Show resource usage
echo ""
echo "📈 Resource Usage:"
kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "Metrics server not available"

if [ "$all_healthy" = true ]; then
    echo ""
    echo "🎉 All services are healthy and deployed successfully!"
    echo ""
    echo "🔧 To access services locally:"
    echo "  kubectl port-forward service/core-api-service 8000:8000 -n $NAMESPACE"
    echo "  kubectl port-forward service/osint-service 8088:8088 -n $NAMESPACE"
    echo "  kubectl port-forward service/neo4j-service 7474:7474 -n $NAMESPACE"
    exit 0
else
    echo ""
    echo "⚠️  Some services are not healthy. Check the status above for details."
    echo ""
    echo "🔍 To troubleshoot:"
    echo "  kubectl logs -f deployment/core-api -n $NAMESPACE"
    echo "  kubectl logs -f deployment/osint-service -n $NAMESPACE" 
    echo "  kubectl describe pods -n $NAMESPACE"
    exit 1
fi