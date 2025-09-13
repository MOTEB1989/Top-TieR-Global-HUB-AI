# Deployment and Verification Guide

This guide provides step-by-step instructions for deploying and verifying the Top-TieR Global HUB AI governance and security features.

## 🔧 Quick Deployment Commands

### For Kubernetes Deployment:

```bash
# 1. Update Neo4j credentials (IMPORTANT!)
# Edit k8s/neo4j-secret.yaml and update the credentials

# 2. Deploy Neo4j with secrets
kubectl apply -f k8s/neo4j-secret.yaml
kubectl apply -f k8s/neo4j.yaml

# 3. Deploy application services
kubectl apply -f k8s/core-deployment.yaml
kubectl apply -f k8s/osint-deployment.yaml

# 4. Verify deployment
kubectl get pods
kubectl get services
kubectl get pvc
```

### For Docker Compose Deployment:

```bash
# 1. Create environment file
cp .env.example .env

# 2. Edit .env with your credentials
# Update NEO4J_PASSWORD, and any OSINT API keys

# 3. Start services
docker compose up -d

# 4. Verify health
docker compose ps
docker compose logs
```

## 🔍 Verification Commands

### Run Automated Verification:
```bash
./scripts/verify_security_features.sh
```

### Manual Verification:

#### GitHub Actions Status:
```bash
# Check if workflows are enabled (via GitHub UI or CLI)
gh workflow list
gh workflow view codeql.yml
```

#### Kubernetes Health:
```bash
# Check pod health
kubectl get pods -o wide

# Describe pods for detailed health info
kubectl describe pods

# Check health probe status
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### Docker Compose Health:
```bash
# Check service health
docker compose ps

# View health check logs
docker compose logs neo4j
curl http://localhost:8000/health
```

## 🔐 Security Checklist

### Before Production Deployment:

- [ ] **Update Neo4j Credentials**: Change default password in `k8s/neo4j-secret.yaml`
- [ ] **Add OSINT API Keys**: Update `k8s/osint-deployment.yaml` with real API keys
- [ ] **Review CODEOWNERS**: Ensure appropriate code reviewers are assigned
- [ ] **Test Health Probes**: Verify all health endpoints respond correctly
- [ ] **Validate YAML**: Run `yamllint k8s/` before deployment
- [ ] **Resource Limits**: Adjust CPU/memory limits based on your environment
- [ ] **Network Policies**: Consider implementing Kubernetes network policies
- [ ] **Monitoring**: Set up monitoring for health probe failures

### Post-Deployment Verification:

- [ ] **CodeQL Scans**: Verify CodeQL analysis completes successfully
- [ ] **Dependabot**: Check that dependency update PRs are created
- [ ] **Health Monitoring**: Confirm all services are healthy
- [ ] **Log Aggregation**: Ensure logs are being collected properly
- [ ] **Backup Strategy**: Implement backup for Neo4j persistent volumes
- [ ] **Disaster Recovery**: Test pod restart and failover scenarios

## 📊 Monitoring Health Probes

### Kubernetes Health Endpoints:
- **Neo4j**: TCP check on port 7687
- **Core API**: `http://core-service:8000/health` (liveness), `http://core-service:8000/ready` (readiness)
- **OSINT Engine**: `http://osint-service:8001/health` (liveness), `http://osint-service:8001/ready` (readiness)

### Docker Compose Health Endpoints:
- **Neo4j**: Cypher shell connection test
- **Core API**: `http://localhost:8000/health`
- **PostgreSQL**: `pg_isready` command
- **Redis**: `redis-cli ping`

## 🚨 Troubleshooting

### Common Issues:

1. **Pod stuck in Pending**: Check PVC availability and node resources
2. **Health probes failing**: Verify application starts on expected ports
3. **Secret not found**: Ensure secrets are created before deployments
4. **Image pull errors**: Check image names and registry access

### Debug Commands:
```bash
# Kubernetes debugging
kubectl logs <pod-name> -f
kubectl describe pod <pod-name>
kubectl exec -it <pod-name> -- /bin/bash

# Docker Compose debugging
docker compose logs <service-name>
docker compose exec <service-name> /bin/bash
```

## 🎯 Success Criteria

Your deployment is successful when:

✅ All GitHub Actions workflows pass  
✅ All Kubernetes pods are in `Running` state  
✅ All Docker Compose services are `healthy`  
✅ Health probes return successful responses  
✅ Neo4j is accessible with secure credentials  
✅ OSINT services can connect to external APIs  
✅ Dependabot creates update PRs automatically  
✅ CodeQL analysis completes without critical issues  

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review logs using the debug commands
- Run the verification script: `./scripts/verify_security_features.sh`
- Open an issue in the repository with the `security` label