#!/bin/bash
# Kubernetes Deployment Script for Top-TieR-Global-HUB-AI
# This script deploys the complete stack with security enhancements

set -e

echo "🚀 Deploying Top-TieR-Global-HUB-AI to Kubernetes..."

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

echo "✅ Kubernetes cluster connection verified"

# Create namespace if it doesn't exist
kubectl create namespace top-tier-hub --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets first
echo "🔐 Applying secrets..."
kubectl apply -f k8s/neo4j-secret.yaml -n top-tier-hub
kubectl apply -f k8s/postgres.yaml -n top-tier-hub  # Contains postgres-secret
kubectl apply -f k8s/osint-deployment.yaml -n top-tier-hub  # Contains osint-secret

# Apply storage and database services
echo "💾 Deploying databases..."
kubectl apply -f k8s/postgres.yaml -n top-tier-hub
kubectl apply -f k8s/redis.yaml -n top-tier-hub
kubectl apply -f k8s/neo4j.yaml -n top-tier-hub

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres -n top-tier-hub
kubectl wait --for=condition=available --timeout=300s deployment/redis -n top-tier-hub
kubectl wait --for=condition=available --timeout=300s deployment/neo4j -n top-tier-hub

# Deploy application services
echo "🚀 Deploying application services..."
kubectl apply -f k8s/core-deployment.yaml -n top-tier-hub
kubectl apply -f k8s/osint-deployment.yaml -n top-tier-hub

# Wait for applications to be ready
echo "⏳ Waiting for applications to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/core-api -n top-tier-hub
kubectl wait --for=condition=available --timeout=300s deployment/osint-service -n top-tier-hub

echo "✅ Deployment completed successfully!"

# Show deployment status
echo ""
echo "📊 Deployment Status:"
kubectl get pods -n top-tier-hub
kubectl get services -n top-tier-hub

echo ""
echo "🔍 To check logs:"
echo "  kubectl logs -f deployment/core-api -n top-tier-hub"
echo "  kubectl logs -f deployment/osint-service -n top-tier-hub"
echo "  kubectl logs -f deployment/neo4j -n top-tier-hub"

echo ""
echo "🔧 To access services locally:"
echo "  kubectl port-forward service/core-api-service 8000:8000 -n top-tier-hub"
echo "  kubectl port-forward service/osint-service 8088:8088 -n top-tier-hub"
echo "  kubectl port-forward service/neo4j-service 7474:7474 -n top-tier-hub"