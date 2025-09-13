# Kubernetes Deployments

This directory contains Kubernetes manifests for deploying the Top-TieR-Global-HUB-AI system.

## Prerequisites

1. Kubernetes cluster (1.20+)
2. kubectl configured to connect to your cluster
3. Container images built and pushed to a registry

## Deployment Steps

### 1. Create Secrets

Copy the example secrets file and update with your credentials:

```bash
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with your actual credentials
kubectl apply -f secrets.yaml
```

### 2. Deploy Services

Deploy the services in the following order:

```bash
# Deploy Neo4j database
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
- **Liveness**: TCP check on port 7687 (bolt)
- **Readiness**: HTTP check on port 7474 (browser)

## Security Configuration

### Neo4j Authentication

The Neo4j deployment uses Kubernetes secrets for authentication:

- Secret name: `neo4j-auth`
- Required keys: `auth`, `url`, `username`, `password`

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

1. **Neo4j connection failures**: Check that the `neo4j-auth` secret is properly configured
2. **Image pull errors**: Ensure container images are accessible from your cluster
3. **Resource limits**: Adjust resource requests/limits based on your cluster capacity

### Debug Commands

```bash
# Describe problematic pods
kubectl describe pod <pod-name>

# Check secret contents (base64 encoded)
kubectl get secret neo4j-auth -o yaml

# Test connectivity between services
kubectl exec -it <core-pod> -- curl http://neo4j:7474
```