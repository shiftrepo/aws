#!/bin/bash
################################################################################
# CA Environment Setup Script
#
# Purpose: Initial setup for CA infrastructure
# - Verify required tools (OpenSSL, Docker)
# - Create directory structure
# - Check file permissions
################################################################################

set -e

# Color logging functions
log_info() { echo -e "\033[34m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[32m[SUCCESS]\033[0m $1"; }
log_error() { echo -e "\033[31m[ERROR]\033[0m $1"; }
log_warning() { echo -e "\033[33m[WARNING]\033[0m $1"; }

echo "========================================"
echo "  CA Environment Setup"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CA_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "CA Root Directory: $CA_ROOT"
cd "$CA_ROOT"

# Check OpenSSL
log_info "Checking OpenSSL installation..."
if command -v openssl &> /dev/null; then
    OPENSSL_VERSION=$(openssl version)
    log_success "OpenSSL found: $OPENSSL_VERSION"
else
    log_error "OpenSSL not found. Please install OpenSSL first."
    exit 1
fi

# Check Docker
log_info "Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker found: $DOCKER_VERSION"
else
    log_error "Docker not found. Please install Docker first."
    exit 1
fi

# Check docker-compose
log_info "Checking docker-compose installation..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    log_success "docker-compose found: $COMPOSE_VERSION"
else
    log_error "docker-compose not found. Please install docker-compose first."
    exit 1
fi

# Create directory structure
log_info "Creating directory structure..."
mkdir -p scripts/utils
mkdir -p config/nginx
mkdir -p certs/{ca,server,export}
mkdir -p logs
log_success "Directory structure created"

# Check .env file
if [[ ! -f .env ]]; then
    log_warning ".env file not found"
    log_info "Please create .env file with required configuration"
else
    log_success ".env file exists"
fi

# Check .gitignore file
if [[ ! -f .gitignore ]]; then
    log_warning ".gitignore file not found"
    log_info "Creating basic .gitignore..."
    cat > .gitignore << 'EOF'
# Private keys
certs/ca/ca.key
certs/server/server.key
certs/server/*.csr
certs/ca/*.srl

# Export packages
certs/export/*.tar.gz

# Logs
logs/*.log
EOF
    log_success ".gitignore created"
else
    log_success ".gitignore file exists"
fi

# Set execute permissions for scripts
log_info "Setting execute permissions for scripts..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/utils/*.sh 2>/dev/null || true
log_success "Script permissions set"

echo ""
log_success "CA environment setup completed!"
echo ""
echo "Next steps:"
echo "  1. Review and update .env file if needed"
echo "  2. Run: ./scripts/create-ca.sh to generate certificates"
echo "  3. Run: sudo docker-compose up -d to start HTTPS test server"
echo ""
