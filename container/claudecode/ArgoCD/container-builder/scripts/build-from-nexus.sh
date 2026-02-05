#!/bin/bash
# =============================================================================
# Container Build Script - Build Docker images from Nexus artifacts
# =============================================================================
# This script builds backend and frontend container images by pulling
# artifacts from Nexus repository and building multi-stage Dockerfiles.
#
# Usage:
#   ./build-from-nexus.sh
#
# Environment Variables:
#   VERSION       - Artifact version (default: git SHA or 1.0.0-SNAPSHOT)
#   NEXUS_URL     - Nexus repository URL (default: http://localhost:8081)
#   REGISTRY_URL  - Container registry URL (default: localhost:5005)
#   GROUP_ID      - Maven group ID (default: com.example)
#   ARTIFACT_ID   - Maven artifact ID (default: orgmgmt-backend)
#   PACKAGE_NAME  - NPM package name (default: @orgmgmt/frontend)
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

# Determine version from environment, git, or default
if [ -z "${VERSION:-}" ]; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        VERSION=$(git rev-parse --short HEAD)
        log_info "Using git SHA as version: ${VERSION}"
    else
        VERSION="1.0.0-SNAPSHOT"
        log_warning "No VERSION set and not in git repo, using default: ${VERSION}"
    fi
fi

# Nexus repository URL
NEXUS_URL="${NEXUS_URL:-http://localhost:8081}"

# Container registry URL
REGISTRY_URL="${REGISTRY_URL:-localhost:5005}"

# Maven coordinates for backend
GROUP_ID="${GROUP_ID:-com.example}"
ARTIFACT_ID="${ARTIFACT_ID:-orgmgmt-backend}"

# NPM package name for frontend
PACKAGE_NAME="${PACKAGE_NAME:-@orgmgmt/frontend}"

# Image names
BACKEND_IMAGE="${REGISTRY_URL}/orgmgmt/backend"
FRONTEND_IMAGE="${REGISTRY_URL}/orgmgmt/frontend"

# Build timestamp
BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

log_info "Starting container build process..."
log_info "Version: ${VERSION}"
log_info "Nexus URL: ${NEXUS_URL}"
log_info "Registry URL: ${REGISTRY_URL}"
log_info "Project directory: ${PROJECT_DIR}"

# =============================================================================
# Validate prerequisites
# =============================================================================

log_info "Validating prerequisites..."

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    log_error "podman is not installed. Please install podman first."
    exit 1
fi

# Check if required files exist
if [ ! -f "${PROJECT_DIR}/Dockerfile.backend" ]; then
    log_error "Dockerfile.backend not found in ${PROJECT_DIR}"
    exit 1
fi

if [ ! -f "${PROJECT_DIR}/Dockerfile.frontend" ]; then
    log_error "Dockerfile.frontend not found in ${PROJECT_DIR}"
    exit 1
fi

if [ ! -f "${PROJECT_DIR}/nginx.conf" ]; then
    log_error "nginx.conf not found in ${PROJECT_DIR}"
    exit 1
fi

log_success "Prerequisites validated"

# =============================================================================
# Build Backend Image
# =============================================================================

log_info "Building backend image..."
log_info "Backend image: ${BACKEND_IMAGE}:${VERSION}"

cd "${PROJECT_DIR}"

podman build \
    --file Dockerfile.backend \
    --tag "${BACKEND_IMAGE}:${VERSION}" \
    --tag "${BACKEND_IMAGE}:latest" \
    --build-arg VERSION="${VERSION}" \
    --build-arg NEXUS_URL="${NEXUS_URL}" \
    --build-arg GROUP_ID="${GROUP_ID}" \
    --build-arg ARTIFACT_ID="${ARTIFACT_ID}" \
    --label "build.timestamp=${BUILD_TIMESTAMP}" \
    --label "build.version=${VERSION}" \
    --label "build.nexus.url=${NEXUS_URL}" \
    .

if [ $? -eq 0 ]; then
    log_success "Backend image built successfully"
    log_success "  - ${BACKEND_IMAGE}:${VERSION}"
    log_success "  - ${BACKEND_IMAGE}:latest"
else
    log_error "Backend image build failed"
    exit 1
fi

# =============================================================================
# Build Frontend Image
# =============================================================================

log_info "Building frontend image..."
log_info "Frontend image: ${FRONTEND_IMAGE}:${VERSION}"

podman build \
    --file Dockerfile.frontend \
    --tag "${FRONTEND_IMAGE}:${VERSION}" \
    --tag "${FRONTEND_IMAGE}:latest" \
    --build-arg VERSION="${VERSION}" \
    --build-arg NEXUS_URL="${NEXUS_URL}" \
    --build-arg PACKAGE_NAME="${PACKAGE_NAME}" \
    --label "build.timestamp=${BUILD_TIMESTAMP}" \
    --label "build.version=${VERSION}" \
    --label "build.nexus.url=${NEXUS_URL}" \
    .

if [ $? -eq 0 ]; then
    log_success "Frontend image built successfully"
    log_success "  - ${FRONTEND_IMAGE}:${VERSION}"
    log_success "  - ${FRONTEND_IMAGE}:latest"
else
    log_error "Frontend image build failed"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
log_success "=============================================="
log_success "Container build completed successfully!"
log_success "=============================================="
echo ""
log_info "Built images:"
log_info "  Backend:"
log_info "    - ${BACKEND_IMAGE}:${VERSION}"
log_info "    - ${BACKEND_IMAGE}:latest"
log_info "  Frontend:"
log_info "    - ${FRONTEND_IMAGE}:${VERSION}"
log_info "    - ${FRONTEND_IMAGE}:latest"
echo ""
log_info "Build timestamp: ${BUILD_TIMESTAMP}"
echo ""
log_info "Next steps:"
log_info "  1. Test images locally: podman run -p 8080:8080 ${BACKEND_IMAGE}:${VERSION}"
log_info "  2. Push to registry: ./scripts/push-to-registry.sh"
log_info "  3. Update GitOps: ./scripts/update-gitops.sh"
echo ""

# List images to verify
log_info "Verifying images..."
podman images | grep -E "(orgmgmt/backend|orgmgmt/frontend)" || true

exit 0
