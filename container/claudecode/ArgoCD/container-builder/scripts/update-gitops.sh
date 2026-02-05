#!/bin/bash
# =============================================================================
# GitOps Update Script - Update image tags in GitOps repository
# =============================================================================
# This script updates the image tags in GitOps configuration files to deploy
# new versions of the application.
#
# Usage:
#   ./update-gitops.sh
#
# Environment Variables:
#   VERSION         - Image version tag (required if not in git repo)
#   REGISTRY_URL    - Container registry URL (default: localhost:5005)
#   GITOPS_DIR      - GitOps directory path (default: auto-detect)
#   ENVIRONMENT     - Target environment (default: dev)
#   GIT_COMMIT      - Commit changes to git (default: true)
#   GIT_PUSH        - Push changes to remote (default: false)
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

# Environment to update (dev, staging, prod)
ENVIRONMENT="${ENVIRONMENT:-dev}"

# Git settings
GIT_COMMIT="${GIT_COMMIT:-true}"
GIT_PUSH="${GIT_PUSH:-false}"

# Get script directory and auto-detect GitOps directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

# Try to find GitOps directory
if [ -z "${GITOPS_DIR:-}" ]; then
    # Look for gitops directory relative to project
    if [ -d "${PROJECT_DIR}/../gitops" ]; then
        GITOPS_DIR="${PROJECT_DIR}/../gitops"
    elif [ -d "${PROJECT_DIR}/../../gitops" ]; then
        GITOPS_DIR="${PROJECT_DIR}/../../gitops"
    elif [ -d "/root/aws.git/container/claudecode/ArgoCD/gitops" ]; then
        GITOPS_DIR="/root/aws.git/container/claudecode/ArgoCD/gitops"
    else
        log_warning "GitOps directory not found, will create configurations locally"
        GITOPS_DIR="${PROJECT_DIR}/gitops"
    fi
fi

# Ensure GITOPS_DIR is absolute path
GITOPS_DIR="$(cd "${GITOPS_DIR}" 2>/dev/null && pwd || echo "${GITOPS_DIR}")"

# Configuration file paths
COMPOSE_FILE="${GITOPS_DIR}/${ENVIRONMENT}/podman-compose.yml"
KUSTOMIZE_FILE="${GITOPS_DIR}/${ENVIRONMENT}/kustomization.yaml"

log_info "Starting GitOps update process..."
log_info "Version: ${VERSION}"
log_info "Registry URL: ${REGISTRY_URL}"
log_info "Environment: ${ENVIRONMENT}"
log_info "GitOps directory: ${GITOPS_DIR}"

# =============================================================================
# Validate prerequisites
# =============================================================================

log_info "Validating prerequisites..."

# Check if GitOps directory exists
if [ ! -d "${GITOPS_DIR}" ]; then
    log_warning "GitOps directory not found: ${GITOPS_DIR}"
    log_info "Creating GitOps directory structure..."
    mkdir -p "${GITOPS_DIR}/${ENVIRONMENT}"
fi

# Check if git is installed (for commit operations)
if [ "${GIT_COMMIT}" = "true" ] && ! command -v git &> /dev/null; then
    log_warning "git is not installed. Will skip git commit."
    GIT_COMMIT="false"
fi

# Check if sed is available
if ! command -v sed &> /dev/null; then
    log_error "sed is not installed. This script requires sed."
    exit 1
fi

log_success "Prerequisites validated"

# =============================================================================
# Update Podman Compose File
# =============================================================================

if [ -f "${COMPOSE_FILE}" ]; then
    log_info "Updating podman-compose.yml..."

    # Backup original file
    cp "${COMPOSE_FILE}" "${COMPOSE_FILE}.backup"

    # Update backend image tag
    sed -i.tmp \
        "s|image: ${REGISTRY_URL}/orgmgmt/backend:.*|image: ${REGISTRY_URL}/orgmgmt/backend:${VERSION}|g" \
        "${COMPOSE_FILE}"

    # Update frontend image tag
    sed -i.tmp \
        "s|image: ${REGISTRY_URL}/orgmgmt/frontend:.*|image: ${REGISTRY_URL}/orgmgmt/frontend:${VERSION}|g" \
        "${COMPOSE_FILE}"

    # Remove temporary backup files
    rm -f "${COMPOSE_FILE}.tmp"

    # Verify changes
    if grep -q "${VERSION}" "${COMPOSE_FILE}"; then
        log_success "Successfully updated podman-compose.yml"
        log_info "Changes:"
        diff "${COMPOSE_FILE}.backup" "${COMPOSE_FILE}" || true
    else
        log_error "Failed to update podman-compose.yml"
        mv "${COMPOSE_FILE}.backup" "${COMPOSE_FILE}"
        exit 1
    fi

    rm -f "${COMPOSE_FILE}.backup"
else
    log_warning "Podman compose file not found: ${COMPOSE_FILE}"
    log_warning "Skipping podman-compose.yml update"
fi

# =============================================================================
# Update Kustomize File
# =============================================================================

if [ -f "${KUSTOMIZE_FILE}" ]; then
    log_info "Updating kustomization.yaml..."

    # Backup original file
    cp "${KUSTOMIZE_FILE}" "${KUSTOMIZE_FILE}.backup"

    # Update image tags in kustomization.yaml
    # This updates the images section in kustomize
    sed -i.tmp \
        "s|newTag: .*|newTag: ${VERSION}|g" \
        "${KUSTOMIZE_FILE}"

    # Remove temporary backup files
    rm -f "${KUSTOMIZE_FILE}.tmp"

    # Verify changes
    if grep -q "${VERSION}" "${KUSTOMIZE_FILE}"; then
        log_success "Successfully updated kustomization.yaml"
        log_info "Changes:"
        diff "${KUSTOMIZE_FILE}.backup" "${KUSTOMIZE_FILE}" || true
    else
        log_warning "Failed to update kustomization.yaml (may not contain version tag)"
    fi

    rm -f "${KUSTOMIZE_FILE}.backup"
else
    log_warning "Kustomize file not found: ${KUSTOMIZE_FILE}"
    log_warning "Skipping kustomization.yaml update"
fi

# =============================================================================
# Update Kubernetes Manifests (if present)
# =============================================================================

K8S_MANIFESTS_DIR="${GITOPS_DIR}/${ENVIRONMENT}/manifests"

if [ -d "${K8S_MANIFESTS_DIR}" ]; then
    log_info "Updating Kubernetes manifests..."

    # Find all YAML files with image references
    find "${K8S_MANIFESTS_DIR}" -type f -name "*.yaml" -o -name "*.yml" | while read -r manifest; do
        if grep -q "image:.*orgmgmt" "${manifest}"; then
            log_info "Updating ${manifest}"

            # Backup and update
            cp "${manifest}" "${manifest}.backup"

            sed -i.tmp \
                "s|image: ${REGISTRY_URL}/orgmgmt/backend:.*|image: ${REGISTRY_URL}/orgmgmt/backend:${VERSION}|g; \
                 s|image: ${REGISTRY_URL}/orgmgmt/frontend:.*|image: ${REGISTRY_URL}/orgmgmt/frontend:${VERSION}|g" \
                "${manifest}"

            rm -f "${manifest}.tmp" "${manifest}.backup"
        fi
    done

    log_success "Updated Kubernetes manifests"
fi

# =============================================================================
# Git Commit
# =============================================================================

if [ "${GIT_COMMIT}" = "true" ]; then
    log_info "Committing changes to git..."

    cd "${GITOPS_DIR}"

    # Check if we're in a git repository
    if git rev-parse --git-dir > /dev/null 2>&1; then
        # Check if there are changes to commit
        if [ -n "$(git status --porcelain)" ]; then
            # Stage changes
            git add "${ENVIRONMENT}/"

            # Create commit
            COMMIT_MSG="chore: Update ${ENVIRONMENT} images to version ${VERSION}

Updated images:
- Backend: ${REGISTRY_URL}/orgmgmt/backend:${VERSION}
- Frontend: ${REGISTRY_URL}/orgmgmt/frontend:${VERSION}

Generated by: update-gitops.sh"

            git commit -m "${COMMIT_MSG}"

            log_success "Changes committed to git"

            # Push if requested
            if [ "${GIT_PUSH}" = "true" ]; then
                log_info "Pushing changes to remote..."
                git push
                log_success "Changes pushed to remote"
            else
                log_info "Changes not pushed (set GIT_PUSH=true to push automatically)"
            fi
        else
            log_warning "No changes to commit"
        fi
    else
        log_warning "Not in a git repository, skipping git commit"
    fi

    cd - > /dev/null
else
    log_info "Skipping git commit (set GIT_COMMIT=true to commit automatically)"
fi

# =============================================================================
# Summary
# =============================================================================

echo ""
log_success "=============================================="
log_success "GitOps update completed successfully!"
log_success "=============================================="
echo ""
log_info "Updated configuration:"
log_info "  Environment: ${ENVIRONMENT}"
log_info "  Version: ${VERSION}"
log_info "  Backend image: ${REGISTRY_URL}/orgmgmt/backend:${VERSION}"
log_info "  Frontend image: ${REGISTRY_URL}/orgmgmt/frontend:${VERSION}"
echo ""
log_info "Updated files:"
[ -f "${COMPOSE_FILE}" ] && log_info "  - ${COMPOSE_FILE}"
[ -f "${KUSTOMIZE_FILE}" ] && log_info "  - ${KUSTOMIZE_FILE}"
[ -d "${K8S_MANIFESTS_DIR}" ] && log_info "  - ${K8S_MANIFESTS_DIR}/*.yaml"
echo ""
log_info "Next steps:"
if [ "${GIT_COMMIT}" = "true" ] && [ "${GIT_PUSH}" = "false" ]; then
    log_info "  1. Review changes: cd ${GITOPS_DIR} && git diff HEAD~1"
    log_info "  2. Push changes: cd ${GITOPS_DIR} && git push"
fi
log_info "  3. ArgoCD will automatically sync the changes (if configured)"
log_info "  4. Or manually apply: kubectl apply -k ${GITOPS_DIR}/${ENVIRONMENT}"
echo ""

exit 0
