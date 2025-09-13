# Kubernetes Deployments

This directory contains Kubernetes manifests for deploying the Top-TieR-Global-HUB-AI system.

## Prerequisites

1. Kubernetes cluster (1.20+)
2. kubectl configured to connect to your cluster
3. Container images built and pushed to a registry

## Deployment Steps

### 1. Create Secrets

#### Neo4j Authentication Secret

The Neo4j deployment now uses the `veritas-neo4j-secrets` secret for improved security:

```bash
# Option 1: Create secret directly (recommended for production)
kubectl create secret generic veritas-neo4j-secrets \
  --from-literal=NEO4J_USER=neo4j \
  --from-literal=NEO4J_PASSWORD=your-secure-password-here

# Option 2: Use the example file
cp veritas-neo4j-secrets.yaml.example veritas-neo4j-secrets.yaml
# Edit veritas-neo4j-secrets.yaml with your actual credentials
kubectl apply -f veritas-neo4j-secrets.yaml
# Remove the file for security
rm veritas-neo4j-secrets.yaml
```

#### Application Secrets

Copy the example secrets file and update with your credentials:

```bash
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your actual credentials
kubectl apply -f secrets.yaml
```

### 2. Deploy Services

Deploy the services in the following order:

```bash
# Deploy Neo4j database (StatefulSet)
kubectl apply -f neo4j.yaml

# Wait for Neo4j to be ready
kubectl wait --for=condition=ready pod -l app=neo4j --timeout=300s

# Deploy core API service
kubectl apply -f core-deployment.yaml

# Deploy OSINT service
kubectl apply -f osint-deployment.yaml
```

### 3. Verify Deployment

Check that all pods are running:

```bash
kubectl get pods -l app=neo4j
kubectl get pods -l app=core
kubectl get pods -l app=osint
```

Check service endpoints:

```bash
kubectl get services
```

## Health Probes

Each service includes health probes for monitoring:

### Core Service (port 8080)
- **Liveness**: `/health` - Checks if the service is alive
- **Readiness**: `/ready` - Checks if the service is ready to accept requests

### OSINT Service (port 8081)
- **Liveness**: `/osint/health` - Checks if the OSINT service is alive
- **Readiness**: `/osint/ready` - Checks if the OSINT service is ready

### Neo4j (ports 7474/7687)
- **Liveness**: Cypher-shell query execution check
- **Readiness**: Cypher-shell query execution check
- **Authentication**: Uses `veritas-neo4j-secrets` secret with separate user/password fields

## Security Configuration

### Neo4j Authentication

The Neo4j deployment uses Kubernetes secrets for authentication:

- Secret name: `veritas-neo4j-secrets`
- Required keys: `NEO4J_USER`, `NEO4J_PASSWORD`
- Uses StatefulSet for better data persistence and ordered deployment
- Health checks use cypher-shell for more accurate database status validation

### Application Secrets

Core and OSINT services use separate secrets:

- `app-secrets`: Database and Redis URLs
- `osint-secrets`: API keys for OSINT data sources

## Scaling

To scale the services:

```bash
# Scale core service
kubectl scale deployment core --replicas=3

# Scale OSINT service
kubectl scale deployment osint --replicas=2
```

## Monitoring

Monitor the health of your deployments:

```bash
# Check pod status
kubectl get pods

# View logs
kubectl logs -l app=core
kubectl logs -l app=osint
kubectl logs -l app=neo4j

# Check health endpoints
kubectl port-forward svc/core 8080:8080
curl http://localhost:8080/health

kubectl port-forward svc/osint 8081:8081
curl http://localhost:8081/osint/health
```

## Troubleshooting

### Common Issues

1. **Neo4j connection failures**: Check that the `veritas-neo4j-secrets` secret is properly configured
2. **Image pull errors**: Ensure container images are accessible from your cluster
3. **Resource limits**: Adjust resource requests/limits based on your cluster capacity

### Debug Commands

```bash
# Describe problematic pods
kubectl describe pod <pod-name>

# Check secret contents (base64 encoded)
kubectl get secret veritas-neo4j-secrets -o yaml

# Test Neo4j connectivity and health
kubectl exec -it <neo4j-pod> -- cypher-shell -u neo4j -p your-password "RETURN 1"
```