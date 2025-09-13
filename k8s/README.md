# Kubernetes Deployment Files

This directory contains Kubernetes manifests for deploying Top-TieR-Global-HUB-AI with enhanced security and health monitoring.

## Quick Start

1. **Update secrets** (see [Security Enhancements Documentation](../docs/SECURITY_ENHANCEMENTS.md))
2. **Deploy**: `./deploy.sh`
3. **Validate**: `../scripts/validate_k8s.sh`

## Files

- `deploy.sh` - Automated deployment script
- `neo4j-secret.yaml` - Neo4j authentication secrets
- `neo4j.yaml` - Neo4j database with health probes
- `core-deployment.yaml` - Core API service with health probes
- `osint-deployment.yaml` - OSINT service with health probes
- `postgres.yaml` - PostgreSQL database with health probes
- `redis.yaml` - Redis cache with health probes

## Health Probes

All deployments include:
- **Liveness Probes**: Restart unhealthy containers
- **Readiness Probes**: Control traffic routing
- **Startup Probes**: Handle slow-starting services

## Security Features

- Secrets management for sensitive data
- Environment variable injection
- Resource limits and requests
- Network policies ready configuration

For detailed documentation, see [SECURITY_ENHANCEMENTS.md](../docs/SECURITY_ENHANCEMENTS.md).