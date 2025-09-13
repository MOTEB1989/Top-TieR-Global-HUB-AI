# Deployment Commands Summary

## Implementation Complete ✅

All security, governance, and reliability enhancements have been successfully implemented for the Top-TieR-Global-HUB-AI repository.

## Git Commands for Deployment

The changes are ready in the branch `copilot/fix-a6812835-7f28-4421-bf5f-2c32ac09fa34`. To deploy:

### 1. Merge Changes to Main Branch
```bash
# Switch to main branch
git checkout main

# Merge the enhancement branch
git merge copilot/fix-a6812835-7f28-4421-bf5f-2c32ac09fa34

# Push to remote
git push origin main
```

### 2. Deploy with Docker Compose
```bash
# Create Neo4j secrets directory
sudo mkdir -p /opt/veritas

# Copy the environment file (update passwords before production!)
sudo cp /tmp/veritas_config/.env.neo4j /opt/veritas/.env.neo4j

# Edit the passwords for production
sudo nano /opt/veritas/.env.neo4j

# Deploy the stack
docker-compose up -d

# Validate deployment
./scripts/validate_docker.sh
```

### 3. Deploy with Kubernetes
```bash
# Update secrets with production passwords first
# Edit k8s/neo4j-secret.yaml and k8s/postgres.yaml with base64 encoded passwords

# Deploy to Kubernetes
./k8s/deploy.sh

# Validate deployment
./scripts/validate_k8s.sh
```

## Verification Commands

### Check GitHub Actions
```bash
# View workflow status
gh workflow list
gh run list --workflow=codeql.yml
```

### Check Service Health
```bash
# Docker Compose
curl http://localhost:8000/health
curl http://localhost:8088/health  # if veritas-web is running

# Kubernetes
kubectl port-forward service/core-api-service 8000:8000 -n top-tier-hub &
curl http://localhost:8000/health
```

### Monitor Logs
```bash
# Docker Compose
docker-compose logs -f neo4j
docker-compose logs -f api

# Kubernetes
kubectl logs -f deployment/neo4j -n top-tier-hub
kubectl logs -f deployment/core-api -n top-tier-hub
```

## Security Notes

1. **Change Default Passwords**: Update all default passwords in secret files before production deployment
2. **Secret Rotation**: Implement regular password rotation using the provided scripts
3. **Access Control**: Ensure proper RBAC configuration for Kubernetes deployments
4. **Monitoring**: Set up alerts for health probe failures and resource exhaustion

## Files Changed

- `docker-compose.yml` - Secure Neo4j authentication
- `k8s/` - Complete Kubernetes infrastructure with health probes
- `scripts/` - Validation and deployment automation
- `docs/` - Comprehensive documentation
- `.github/` - Already had governance features (Dependabot, CodeQL, CODEOWNERS)

All changes maintain backward compatibility while significantly enhancing security and reliability.