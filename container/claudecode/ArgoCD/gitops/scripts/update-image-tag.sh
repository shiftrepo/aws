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
if [ $# -lt 2 ]; then
    print_error "Usage: $0 <environment> <version>"
    echo "Example: $0 dev v1.2.3"
    echo "Environments: dev, staging, prod"
    exit 1
fi

ENVIRONMENT=$1
VERSION=$2

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITOPS_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$GITOPS_DIR/$ENVIRONMENT/podman-compose.yml"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: dev, staging, prod"
    exit 1
fi

# Validate version format (should start with v or be 'latest')
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] && [[ "$VERSION" != "latest" ]] && [[ "$VERSION" != "staging" ]]; then
    print_warning "Version format should be 'vX.Y.Z', 'latest', or 'staging'. Got: $VERSION"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Compose file not found: $COMPOSE_FILE"
    exit 1
fi

print_info "Updating image tags in $ENVIRONMENT environment to version: $VERSION"

# Create backup
BACKUP_FILE="${COMPOSE_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$COMPOSE_FILE" "$BACKUP_FILE"
print_info "Backup created: $BACKUP_FILE"

# Update image tags using sed
# Update backend image tag
sed -i "s|image: localhost:5005/orgmgmt/backend:.*|image: localhost:5005/orgmgmt/backend:$VERSION|g" "$COMPOSE_FILE"

# Update frontend image tag
sed -i "s|image: localhost:5005/orgmgmt/frontend:.*|image: localhost:5005/orgmgmt/frontend:$VERSION|g" "$COMPOSE_FILE"

# Validate the updated file
print_info "Validating updated manifest..."
if bash "$SCRIPT_DIR/validate-manifest.sh" "$ENVIRONMENT" > /dev/null 2>&1; then
    print_success "Image tags updated successfully!"
    print_info "Updated services:"
    grep "image: localhost:5005" "$COMPOSE_FILE" | sed 's/^[ \t]*/  - /'

    # Remove backup if validation succeeds
    rm "$BACKUP_FILE"
    print_info "Backup removed (validation passed)"
else
    print_error "Validation failed! Restoring from backup..."
    mv "$BACKUP_FILE" "$COMPOSE_FILE"
    print_info "Original file restored"
    exit 1
fi

print_success "Update completed for $ENVIRONMENT environment"
echo ""
print_info "Next steps:"
echo "  1. Review the changes: git diff $COMPOSE_FILE"
echo "  2. Commit the changes: git add $COMPOSE_FILE && git commit -m 'chore: Update $ENVIRONMENT images to $VERSION'"
echo "  3. Push to trigger ArgoCD sync: git push"
