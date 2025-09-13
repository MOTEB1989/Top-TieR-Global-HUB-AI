# Kubernetes Deployment for Top-TieR Global HUB AI

This directory contains Kubernetes manifests for deploying the Top-TieR Global HUB AI application with enhanced security and health monitoring.

## Files Overview

- `neo4j-secret.yaml` - Kubernetes secret for Neo4j credentials
- `neo4j.yaml` - Neo4j database deployment with health probes and persistent storage
- `core-deployment.yaml` - Core API service deployment with health probes
- `osint-deployment.yaml` - OSINT engine deployment with health probes and API key management

## Security Features

### 1. Secure Credential Management
- Neo4j credentials are stored in Kubernetes secrets
- OSINT API keys are stored in separate secrets
- No hardcoded passwords in deployment files

### 2. Health Probes
All deployments include:
- **Liveness Probe**: Detects if the container is running and restarts if not
- **Readiness Probe**: Determines if the container is ready to serve traffic
- **Startup Probe**: Gives containers time to start before other probes begin

## Deployment Instructions

### Prerequisites
- Kubernetes cluster (v1.20+)
- kubectl configured to access your cluster
- Persistent volume support for Neo4j data

### 1. Deploy Neo4j Secret (IMPORTANT: Update credentials first!)

```bash
# Edit the secret file and update the credentials
kubectl apply -f k8s/neo4j-secret.yaml
```

**⚠️ Security Warning**: The default credentials in `neo4j-secret.yaml` are for demonstration only. Update them before deployment!

### 2. Deploy Neo4j Database

```bash
kubectl apply -f k8s/neo4j.yaml
```

This creates:
- Neo4j deployment with health probes
- ClusterIP service for internal access
- Persistent volume claims for data and logs

### 3. Deploy Core API Service

```bash
kubectl apply -f k8s/core-deployment.yaml
```

### 4. Deploy OSINT Engine

```bash
# First, update OSINT API keys in the secret
kubectl apply -f k8s/osint-deployment.yaml
```

### 5. Verify Deployments

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get services

# Check persistent volumes
kubectl get pvc

# View logs for troubleshooting
kubectl logs -l app=neo4j
kubectl logs -l app=top-tier-core
kubectl logs -l app=top-tier-osint
```

## Health Monitoring

### Check Pod Health
```bash
# Get pod status with health information
kubectl get pods -o wide

# Describe a pod to see health probe details
kubectl describe pod <pod-name>
```

### Health Probe Endpoints
- **Core API**: `http://core-service:8000/health` (liveness), `http://core-service:8000/ready` (readiness)
- **OSINT Engine**: `http://osint-service:8001/health` (liveness), `http://osint-service:8001/ready` (readiness)
- **Neo4j**: TCP check on port 7687

## Configuration

### Environment Variables
All sensitive configuration is managed through Kubernetes secrets and configmaps:

- `neo4j-secret`: Contains Neo4j authentication credentials
- `osint-secrets`: Contains OSINT service API keys

### Resource Limits
Each deployment includes resource requests and limits:
- **Neo4j**: 512Mi-2Gi memory, 250m-1000m CPU
- **Core API**: 256Mi-1Gi memory, 100m-500m CPU  
- **OSINT Engine**: 512Mi-2Gi memory, 200m-1000m CPU

## Scaling

### Scale deployments
```bash
# Scale core API to 5 replicas
kubectl scale deployment core-deployment --replicas=5

# Scale OSINT engine to 3 replicas
kubectl scale deployment osint-deployment --replicas=3
```

### Auto-scaling (Optional)
```bash
# Enable horizontal pod autoscaler for core API
kubectl autoscale deployment core-deployment --cpu-percent=70 --min=3 --max=10

# Enable horizontal pod autoscaler for OSINT engine
kubectl autoscale deployment osint-deployment --cpu-percent=80 --min=2 --max=8
```

## Security Best Practices

### 1. Update Default Credentials
```bash
# Generate new Neo4j password
NEO4J_PASSWORD=$(openssl rand -base64 32)

# Update the secret
kubectl create secret generic neo4j-secret \
  --from-literal=NEO4J_USER=neo4j \
  --from-literal=NEO4J_PASSWORD=$NEO4J_PASSWORD \
  --from-literal=NEO4J_AUTH="neo4j:$NEO4J_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Update OSINT API Keys
```bash
# Update OSINT secrets with real API keys
kubectl create secret generic osint-secrets \
  --from-literal=SHODAN_API_KEY=your-actual-shodan-key \
  --from-literal=VIRUSTOTAL_API_KEY=your-actual-virustotal-key \
  --from-literal=HUNTER_API_KEY=your-actual-hunter-key \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Network Policies (Recommended)
Consider implementing Kubernetes network policies to restrict pod-to-pod communication.

## Troubleshooting

### Common Issues

1. **Pods not starting**: Check resource availability and image availability
2. **Health probes failing**: Verify the application is listening on expected ports
3. **PVC pending**: Ensure your cluster has persistent volume support
4. **Neo4j connection issues**: Check if secret credentials match application configuration

### Debug Commands
```bash
# Check pod events
kubectl describe pod <pod-name>

# View container logs
kubectl logs <pod-name> -c <container-name>

# Execute into a running pod
kubectl exec -it <pod-name> -- /bin/bash

# Port forward for local testing
kubectl port-forward service/neo4j-service 7474:7474
kubectl port-forward service/core-service 8000:8000
```

## Monitoring Integration

These manifests are compatible with:
- Prometheus (for metrics collection)
- Grafana (for visualization)
- Jaeger (for distributed tracing)
- ELK Stack (for log aggregation)

Health probes provide essential monitoring data for observability platforms.