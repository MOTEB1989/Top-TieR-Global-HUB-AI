# Stack Health Check Workflow

This document describes the GitHub Actions workflow for ensuring consistency and health of the stack defined in `.env`, `docker-compose.yml`, and `scripts/veritas_health_check.sh`.

## Overview

The Stack Health Check workflow validates that all services in the docker-compose stack can be properly started and are responding to health checks. It uses the `.env` file as the single source of truth for environment variables and runs daily to ensure ongoing consistency.

## Workflow Features

### 1. Environment Configuration
- **Source of Truth**: Uses `.env.example` as the base configuration
- **Secret Handling**: Safely loads sensitive values like `OPENAI_API_KEY` from GitHub Secrets
- **CI Compatibility**: Automatically fixes environment variables for CI environment compatibility
- **Neo4j Setup**: Creates required Neo4j configuration files for the stack

### 2. Docker Compose Integration
- **Service Startup**: Starts core services (Redis, PostgreSQL, Neo4j, API)
- **Health Monitoring**: Waits for services to be healthy using Docker health checks
- **Failure Tolerance**: Continues with health checks even if some services fail to start
- **Resource Management**: Properly cleans up containers and volumes after testing

### 3. Health Validation
- **Script Execution**: Runs the enhanced `scripts/veritas_health_check.sh`
- **Service Testing**: Tests both Core API (port 8000) and Veritas Web (port 8080)
- **Timeout Handling**: Uses 10-second timeouts for health check requests
- **Exit Codes**: Properly reports success/failure with appropriate exit codes

### 4. Scheduling and Triggers
- **Daily Execution**: Runs automatically at midnight UTC every day
- **Manual Triggers**: Can be triggered manually via `workflow_dispatch`
- **Change Detection**: Triggers on changes to key configuration files:
  - `.env.example`
  - `docker-compose.yml`
  - `scripts/veritas_health_check.sh`
  - The workflow file itself

## Workflow Steps

1. **Checkout**: Get the latest code from the repository
2. **Environment Setup**: Create and configure the `.env` file
3. **Docker Setup**: Install and configure Docker Buildx
4. **Service Startup**: Start Docker Compose services in stages
5. **Health Monitoring**: Wait for services to be healthy
6. **Health Testing**: Execute the Veritas health check script
7. **Log Collection**: Gather logs on failure for debugging
8. **Artifact Upload**: Save configuration and logs for review
9. **Cleanup**: Stop services and clean up resources

## Configuration

### Required Secrets
- `OPENAI_API_KEY`: OpenAI API key for services that require it
- Other API keys as needed based on your `.env.example` configuration

### Environment Variables
The workflow automatically configures:
- `ENVIRONMENT=ci`
- `DEBUG=false`
- `NEO4J_USER=neo4j`
- `NEO4J_PASSWORD=testpassword123` (for CI testing)

### Service Dependencies
The workflow handles these service dependencies:
- **Redis**: Basic caching service
- **PostgreSQL**: Primary database
- **Neo4j**: Graph database with authentication
- **API**: Main application service
- **Veritas Web**: Web interface (optional)

## Troubleshooting

### Common Issues

1. **Neo4j Authentication**: The workflow creates the required `/opt/veritas/.env.neo4j` file
2. **CORS Variables**: Array-style CORS variables are converted to comma-separated strings
3. **Service Timeouts**: Extended wait times for services to start and become healthy
4. **Build Failures**: Some services may fail to build in CI; health checks will catch this

### Debugging

- Check the workflow run logs for detailed output
- Review uploaded artifacts for configuration files and logs
- Use manual triggers to test changes before they're merged
- Monitor service startup logs in the "Collect service logs on failure" step

## Integration with Existing Workflows

This workflow complements the existing `veritas-health.yml` workflow by:
- Focusing specifically on Docker Compose stack health
- Using `.env` file as single source of truth
- Providing daily automated validation
- Testing the complete service stack rather than individual components

**Note:** The `veritas-health.yml` workflow has been configured for manual triggering only to prevent CI failures when services aren't available in the GitHub Actions environment.

## Maintenance

### Regular Tasks
- Review failed workflow runs and investigate root causes
- Update Neo4j password and other credentials as needed
- Adjust timeout values based on service startup performance
- Update service list as new services are added to docker-compose.yml

### Updates Required When:
- New services are added to `docker-compose.yml`
- Environment variables change in `.env.example`
- Health check endpoints change
- Service startup order requirements change

## Security Considerations

- Sensitive values are handled via GitHub Secrets
- Neo4j credentials are generated for CI and not stored in Git
- Artifacts contain sanitized logs (sensitive values filtered)
- Services are properly isolated in Docker network
- All containers and volumes are cleaned up after testing

---

For questions or issues with this workflow, please open an issue with the `health-check` and `automation` labels.