#!/bin/bash
# =============================================================================
# Container Push Script - Push Docker images to container registry
# =============================================================================
# This script pushes backend and frontend container images to a container
# registry with proper authentication and tagging.
#
# Usage:
#   ./push-to-registry.sh
#
# Environment Variables:
#   VERSION         - Image version tag (required if not in git repo)
#   REGISTRY_URL    - Container registry URL (default: localhost:5005)
#   REGISTRY_USER   - Registry username (optional, for authentication)
#   REGISTRY_PASS   - Registry password (optional, for authentication)
#   SKIP_LOGIN      - Skip registry login if set to "true"
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# =============================================================================
# Configuration
# =============================================================================

# Determine version from environment or git
if [ -z "${VERSION:-}" ]; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        VERSION=$(git rev-parse --short HEAD)
        log_info "Using git SHA as version: ${VERSION}"
    else
        log_error "VERSION environment variable is required when not in a git repository"
        exit 1
    fi
fi

# Container registry URL
REGISTRY_URL="${REGISTRY_URL:-localhost:5005}"

# Registry authentication (optional)
REGISTRY_USER="${REGISTRY_USER:-}"
REGISTRY_PASS="${REGISTRY_PASS:-}"
SKIP_LOGIN="${SKIP_LOGIN:-false}"

# Image names
BACKEND_IMAGE="${REGISTRY_URL}/orgmgmt/backend"
FRONTEND_IMAGE="${REGISTRY_URL}/orgmgmt/frontend"

log_info "Starting container push process..."
log_info "Version: ${VERSION}"
log_info "Registry URL: ${REGISTRY_URL}"

# =============================================================================
# Validate prerequisites
# =============================================================================

log_info "Validating prerequisites..."

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    log_error "podman is not installed. Please install podman first."
    exit 1
fi

# Verify images exist locally
log_info "Checking if images exist locally..."

if ! podman image exists "${BACKEND_IMAGE}:${VERSION}"; then
    log_error "Backend image ${BACKEND_IMAGE}:${VERSION} not found locally"
    log_error "Please run ./scripts/build-from-nexus.sh first"
    exit 1
fi

if ! podman image exists "${FRONTEND_IMAGE}:${VERSION}"; then
    log_error "Frontend image ${FRONTEND_IMAGE}:${VERSION} not found locally"
    log_error "Please run ./scripts/build-from-nexus.sh first"
    exit 1
fi

log_success "All images found locally"

# =============================================================================
# Registry Authentication
# =============================================================================

if [ "${SKIP_LOGIN}" != "true" ]; then
    log_info "Authenticating with container registry..."

    if [ -n "${REGISTRY_USER}" ] && [ -n "${REGISTRY_PASS}" ]; then
        # Login with provided credentials
        log_info "Logging in as user: ${REGISTRY_USER}"
        echo "${REGISTRY_PASS}" | podman login \
            --username "${REGISTRY_USER}" \
            --password-stdin \
            "${REGISTRY_URL}"

        if [ $? -eq 0 ]; then
            log_success "Successfully authenticated with registry"
        else
            log_error "Failed to authenticate with registry"
            exit 1
        fi
    else
        # Attempt login without credentials (may use cached credentials)
        log_warning "No credentials provided, attempting login with cached credentials..."
        if podman login "${REGISTRY_URL}" 2>/dev/null; then
            log_success "Using cached credentials"
        else
            log_warning "No cached credentials found. Continuing without authentication..."
            log_warning "This may fail if the registry requires authentication."
        fi
    fi
else
    log_info "Skipping registry login (SKIP_LOGIN=true)"
fi

# =============================================================================
# Push Backend Image
# =============================================================================

log_info "Pushing backend image..."

# Push versioned tag
log_info "Pushing ${BACKEND_IMAGE}:${VERSION}"
podman push "${BACKEND_IMAGE}:${VERSION}"

if [ $? -eq 0 ]; then
    log_success "Backend image (${VERSION}) pushed successfully"
else
    log_error "Failed to push backend image (${VERSION})"
    exit 1
fi

# Push latest tag
log_info "Pushing ${BACKEND_IMAGE}:latest"
podman push "${BACKEND_IMAGE}:latest"

if [ $? -eq 0 ]; then
    log_success "Backend image (latest) pushed successfully"
else
    log_error "Failed to push backend image (latest)"
    exit 1
fi

# =============================================================================
# Push Frontend Image
# =============================================================================

log_info "Pushing frontend image..."

# Push versioned tag
log_info "Pushing ${FRONTEND_IMAGE}:${VERSION}"
podman push "${FRONTEND_IMAGE}:${VERSION}"

if [ $? -eq 0 ]; then
    log_success "Frontend image (${VERSION}) pushed successfully"
else
    log_error "Failed to push frontend image (${VERSION})"
    exit 1
fi

# Push latest tag
log_info "Pushing ${FRONTEND_IMAGE}:latest"
podman push "${FRONTEND_IMAGE}:latest"

if [ $? -eq 0 ]; then
    log_success "Frontend image (latest) pushed successfully"
else
    log_error "Failed to push frontend image (latest)"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
log_success "=============================================="
log_success "Container push completed successfully!"
log_success "=============================================="
echo ""
log_info "Pushed images:"
log_info "  Backend:"
log_info "    - ${BACKEND_IMAGE}:${VERSION}"
log_info "    - ${BACKEND_IMAGE}:latest"
log_info "  Frontend:"
log_info "    - ${FRONTEND_IMAGE}:${VERSION}"
log_info "    - ${FRONTEND_IMAGE}:latest"
echo ""
log_info "Registry: ${REGISTRY_URL}"
echo ""
log_info "Next steps:"
log_info "  1. Update GitOps repository: ./scripts/update-gitops.sh"
log_info "  2. Verify images in registry: podman search ${REGISTRY_URL}/orgmgmt"
log_info "  3. Deploy to environment using ArgoCD or kubectl"
echo ""

exit 0
