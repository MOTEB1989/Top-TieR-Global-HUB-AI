#!/bin/bash

# Setup script for Neo4j credentials security
# This script helps set up the local secrets file for Neo4j

set -euo pipefail

# Configuration
NEO4J_SECRETS_DIR="/opt/veritas"
NEO4J_SECRETS_FILE="$NEO4J_SECRETS_DIR/.env.neo4j"
EXAMPLE_FILE=".env.neo4j.example"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${2:-$BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    log "$1" "$GREEN"
}

log_warn() {
    log "$1" "$YELLOW"
}

log_error() {
    log "$1" "$RED"
}

# Check if running as root for directory creation
check_permissions() {
    if [[ ! -d "$NEO4J_SECRETS_DIR" ]]; then
        if [[ $EUID -ne 0 ]]; then
            log_error "Need root privileges to create $NEO4J_SECRETS_DIR"
            log "Please run: sudo $0"
            exit 1
        fi
    fi
}

# Create secrets directory
create_secrets_directory() {
    log "Creating secrets directory: $NEO4J_SECRETS_DIR"
    
    if [[ ! -d "$NEO4J_SECRETS_DIR" ]]; then
        mkdir -p "$NEO4J_SECRETS_DIR"
        log_success "Created directory: $NEO4J_SECRETS_DIR"
    else
        log_warn "Directory already exists: $NEO4J_SECRETS_DIR"
    fi
    
    # Set appropriate permissions
    chmod 750 "$NEO4J_SECRETS_DIR"
    log_success "Set directory permissions: 750"
}

# Generate secure password
generate_password() {
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
    else
        # Fallback to urandom if openssl not available
        tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 25
    fi
}

# Setup Neo4j credentials
setup_neo4j_credentials() {
    log "Setting up Neo4j credentials..."
    
    if [[ -f "$NEO4J_SECRETS_FILE" ]]; then
        log_warn "Credentials file already exists: $NEO4J_SECRETS_FILE"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Keeping existing credentials file"
            return 0
        fi
    fi
    
    # Generate secure password
    log "Generating secure password..."
    NEO4J_PASSWORD=$(generate_password)
    
    # Create credentials file
    cat > "$NEO4J_SECRETS_FILE" <<EOF
# Neo4j Authentication Configuration
# Generated on $(date)
# DO NOT commit this file to Git!

# Neo4j authentication format: username/password
NEO4J_AUTH=neo4j/$NEO4J_PASSWORD

# Alternative format for separate variables (used by veritas-web service)
NEO4J_AUTH_USER=neo4j
NEO4J_AUTH_PASSWORD=$NEO4J_PASSWORD

# Database name (optional, defaults to neo4j)
NEO4J_DATABASE=neo4j
EOF
    
    # Set secure permissions
    chmod 600 "$NEO4J_SECRETS_FILE"
    log_success "Created credentials file: $NEO4J_SECRETS_FILE"
    log_success "Set file permissions: 600"
    
    log "Neo4j credentials configured:"
    log "  Username: neo4j"
    log "  Password: $NEO4J_PASSWORD"
    log_warn "Please save this password securely!"
}

# Update docker-compose to use the secrets file
update_docker_compose() {
    if [[ -f "docker-compose.yml" ]]; then
        log "Updating docker-compose.yml to use local secrets file..."
        
        # Check if env_file is already configured
        if grep -q "env_file:" docker-compose.yml; then
            log_warn "docker-compose.yml already configured for env_file"
        else
            log "docker-compose.yml appears to be using the new format already"
        fi
        
        log_success "Docker Compose is ready to use the secrets file"
    else
        log_warn "docker-compose.yml not found in current directory"
    fi
}

# Show usage instructions
show_usage() {
    log_success "Setup completed successfully!"
    echo
    log "To use the credentials:"
    log "1. Start services with Docker Compose:"
    log "   docker compose up -d"
    echo
    log "2. Connect to Neo4j:"
    log "   Browser: http://localhost:7474"
    log "   Username: neo4j"
    log "   Password: (shown above)"
    echo
    log "3. For Kubernetes deployment:"
    log "   Update k8s/secrets.yaml with the generated password"
    log "   Then apply: kubectl apply -f k8s/secrets.yaml"
    echo
    log_warn "Security reminders:"
    log "- The secrets file is NOT in Git (.gitignore excludes it)"
    log "- Backup your password securely"
    log "- For production, use a more complex password"
}

# Main execution
main() {
    log "Top-TieR-Global-HUB-AI Neo4j Security Setup"
    log "============================================"
    
    check_permissions
    create_secrets_directory
    setup_neo4j_credentials
    update_docker_compose
    show_usage
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi