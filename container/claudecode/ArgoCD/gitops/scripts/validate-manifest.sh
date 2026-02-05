#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "[INFO] $1"
}

# Check if required arguments are provided
if [ $# -lt 1 ]; then
    print_error "Usage: $0 <environment>"
    echo "Example: $0 dev"
    echo "Environments: dev, staging, prod"
    exit 1
fi

ENVIRONMENT=$1

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITOPS_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$GITOPS_DIR/$ENVIRONMENT/podman-compose.yml"
ENV_FILE="$GITOPS_DIR/$ENVIRONMENT/.env"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: dev, staging, prod"
    exit 1
fi

# Check if files exist
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Compose file not found: $COMPOSE_FILE"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    print_warning ".env file not found: $ENV_FILE"
fi

print_info "Validating $ENVIRONMENT environment manifest..."
echo ""

# Validation counter
VALIDATION_ERRORS=0

# 1. Validate YAML syntax with podman-compose
print_info "Checking YAML syntax..."
if podman-compose -f "$COMPOSE_FILE" config > /dev/null 2>&1; then
    print_success "YAML syntax is valid"
else
    print_error "YAML syntax validation failed"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# 2. Check for empty image tags
print_info "Checking image tags..."
if grep -q "image: localhost:5005/orgmgmt/.*:$" "$COMPOSE_FILE"; then
    print_error "Found empty image tags"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
else
    BACKEND_TAG=$(grep "image: localhost:5005/orgmgmt/backend:" "$COMPOSE_FILE" | sed 's/.*backend://' | tr -d ' ')
    FRONTEND_TAG=$(grep "image: localhost:5005/orgmgmt/frontend:" "$COMPOSE_FILE" | sed 's/.*frontend://' | tr -d ' ')
    print_success "Image tags are valid"
    print_info "  Backend:  localhost:5005/orgmgmt/backend:$BACKEND_TAG"
    print_info "  Frontend: localhost:5005/orgmgmt/frontend:$FRONTEND_TAG"
fi

# 3. Check required environment variables in .env file
if [ -f "$ENV_FILE" ]; then
    print_info "Checking required environment variables..."
    REQUIRED_VARS=("SPRING_PROFILES_ACTIVE" "LOG_LEVEL" "DEPLOYMENT_REPLICAS")

    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" "$ENV_FILE"; then
            VALUE=$(grep "^$var=" "$ENV_FILE" | cut -d'=' -f2)
            print_success "  $var=$VALUE"
        else
            print_error "  Missing required variable: $var"
            VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
        fi
    done

    # Check for sensitive variables (should be present but warn if using defaults)
    if grep -q "^POSTGRES_USER=" "$ENV_FILE"; then
        USER_VALUE=$(grep "^POSTGRES_USER=" "$ENV_FILE" | cut -d'=' -f2)
        print_success "  POSTGRES_USER is set"
    else
        print_warning "  POSTGRES_USER not found in .env"
    fi

    if grep -q "^POSTGRES_PASSWORD=" "$ENV_FILE"; then
        print_success "  POSTGRES_PASSWORD is set"
    else
        print_warning "  POSTGRES_PASSWORD not found in .env"
    fi
fi

# 4. Check network configuration
print_info "Checking network configuration..."
if grep -q "argocd-network:" "$COMPOSE_FILE" && grep -q "external: true" "$COMPOSE_FILE"; then
    print_success "External network 'argocd-network' is properly configured"
else
    print_error "External network 'argocd-network' is not properly configured"
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
fi

# 5. Check service dependencies
print_info "Checking service dependencies..."
if grep -q "depends_on:" "$COMPOSE_FILE"; then
    print_success "Service dependencies are defined"
else
    print_warning "No service dependencies found"
fi

# 6. Check healthchecks
print_info "Checking healthchecks..."
BACKEND_HEALTHCHECK=$(grep -A3 "orgmgmt-backend:" "$COMPOSE_FILE" | grep -c "healthcheck:" || true)
FRONTEND_HEALTHCHECK=$(grep -A3 "orgmgmt-frontend:" "$COMPOSE_FILE" | grep -c "healthcheck:" || true)

if [ "$BACKEND_HEALTHCHECK" -gt 0 ] && [ "$FRONTEND_HEALTHCHECK" -gt 0 ]; then
    print_success "Healthchecks are configured for all services"
else
    print_warning "Some services may be missing healthchecks"
fi

# 7. Validate restart policy
print_info "Checking restart policy..."
if grep -q "restart: unless-stopped" "$COMPOSE_FILE"; then
    print_success "Restart policy is set to 'unless-stopped'"
else
    print_warning "Restart policy not found or different from 'unless-stopped'"
fi

# Summary
echo ""
echo "=========================================="
if [ $VALIDATION_ERRORS -eq 0 ]; then
    print_success "All validations passed for $ENVIRONMENT environment!"
    echo "=========================================="
    exit 0
else
    print_error "Validation failed with $VALIDATION_ERRORS error(s) for $ENVIRONMENT environment"
    echo "=========================================="
    exit 1
fi
