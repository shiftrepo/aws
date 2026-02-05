#!/bin/bash
#
# build-and-deploy.sh - Build and Deploy Application
#
# This script handles the complete build and deployment workflow:
# - Environment validation
# - Backend build and test
# - Frontend build and test
# - Container image build
# - Artifact deployment to Nexus
# - GitOps manifest updates
# - ArgoCD synchronization
#
# Usage: ./build-and-deploy.sh [OPTIONS]
#
# Options:
#   --skip-tests          Skip test execution
#   --skip-backend        Skip backend build
#   --skip-frontend       Skip frontend build
#   --environment ENV     Target environment (dev/staging/prod, default: dev)
#   --version VERSION     Application version (default: auto-generated)
#   --no-sync            Don't trigger ArgoCD sync
#   -h, --help           Show this help message
#

set -e
set -u
set -o pipefail

# ==============================================================================
# INITIALIZATION
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "${SCRIPT_DIR}/common.sh"

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SKIP_TESTS=false
SKIP_BACKEND=false
SKIP_FRONTEND=false
ENVIRONMENT="dev"
VERSION=""
NO_SYNC=false

BACKEND_DIR="${APP_DIR}/backend"
FRONTEND_DIR="${APP_DIR}/frontend"
CONTAINER_BUILDER_DIR="${PROJECT_ROOT}/container-builder"

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Build and Deploy Application

Usage: $(basename "$0") [OPTIONS]

This script builds and deploys the application to the specified environment.

Options:
    --skip-tests         Skip test execution
    --skip-backend       Skip backend build
    --skip-frontend      Skip frontend build
    --environment ENV    Target environment (dev/staging/prod, default: dev)
    --version VERSION    Application version (default: auto-generated)
    --no-sync           Don't trigger ArgoCD sync
    -h, --help          Show this help message

Examples:
    $(basename "$0")                                    # Full build and deploy to dev
    $(basename "$0") --environment prod                 # Deploy to production
    $(basename "$0") --skip-tests --environment staging # Deploy to staging without tests
    $(basename "$0") --version 1.2.3                   # Deploy specific version

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --version)
                VERSION="$2"
                shift 2
                ;;
            --no-sync)
                NO_SYNC=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        die "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod."
    fi
}

# ==============================================================================
# ENVIRONMENT VALIDATION
# ==============================================================================

validate_environment() {
    print_header "Validating Environment"

    log_info "Checking infrastructure status..."

    # Check if required services are running
    local required_containers=(
        "orgmgmt-postgres"
        "orgmgmt-nexus"
        "argocd-server"
    )

    for container in "${required_containers[@]}"; do
        if ! is_container_running "$container"; then
            log_error "Required service not running: $container"
            die "Please start infrastructure first: cd ${INFRASTRUCTURE_DIR} && podman-compose up -d"
        fi
    done

    log_success "All required services are running"

    # Load environment
    load_env_file "${INFRASTRUCTURE_DIR}/.env"

    # Validate directories
    validate_directory "$BACKEND_DIR" "Backend directory not found"
    validate_directory "$FRONTEND_DIR" "Frontend directory not found"

    log_success "Environment validation complete"
}

# ==============================================================================
# VERSION GENERATION
# ==============================================================================

generate_version() {
    if [ -n "$VERSION" ]; then
        log_info "Using specified version: $VERSION"
        return
    fi

    print_header "Generating Version"

    # Try to get git commit SHA
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local commit_sha=$(git rev-parse --short HEAD)
        local branch=$(git rev-parse --abbrev-ref HEAD)
        local timestamp=$(date +%Y%m%d-%H%M%S)

        VERSION="${branch}-${commit_sha}-${timestamp}"
        log_success "Generated version: $VERSION"
    else
        VERSION="1.0.0-$(date +%Y%m%d-%H%M%S)"
        log_warning "Not a git repository, using timestamp-based version: $VERSION"
    fi
}

# ==============================================================================
# BACKEND BUILD
# ==============================================================================

build_backend() {
    if [ "$SKIP_BACKEND" = true ]; then
        log_info "Skipping backend build"
        return 0
    fi

    print_header "Building Backend"

    log_info "Building Spring Boot application..."

    cd "$BACKEND_DIR" || die "Failed to change to backend directory"

    # Clean and package
    print_step 1 "Running Maven clean package..."

    if [ "$SKIP_TESTS" = true ]; then
        mvn clean package -DskipTests
    else
        mvn clean package
    fi

    if [ $? -eq 0 ]; then
        log_success "Backend build successful"
    else
        die "Backend build failed"
    fi

    # Verify JAR file exists
    local jar_file=$(find target -name "*.jar" -not -name "*-sources.jar" | head -1)

    if [ -z "$jar_file" ]; then
        die "JAR file not found in target directory"
    fi

    log_success "Backend JAR: $jar_file"

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# BACKEND TESTS
# ==============================================================================

test_backend() {
    if [ "$SKIP_TESTS" = true ] || [ "$SKIP_BACKEND" = true ]; then
        log_info "Skipping backend tests"
        return 0
    fi

    print_header "Running Backend Tests"

    cd "$BACKEND_DIR" || die "Failed to change to backend directory"

    log_info "Executing test suite..."

    mvn test

    if [ $? -eq 0 ]; then
        log_success "All backend tests passed"

        # Generate coverage report
        if [ -d "target/site/jacoco" ]; then
            log_info "JaCoCo coverage report: ${BACKEND_DIR}/target/site/jacoco/index.html"
        fi
    else
        die "Backend tests failed"
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# FRONTEND BUILD
# ==============================================================================

build_frontend() {
    if [ "$SKIP_FRONTEND" = true ]; then
        log_info "Skipping frontend build"
        return 0
    fi

    print_header "Building Frontend"

    cd "$FRONTEND_DIR" || die "Failed to change to frontend directory"

    # Install dependencies
    print_step 1 "Installing dependencies..."

    if [ ! -d "node_modules" ]; then
        npm ci
    else
        log_info "Dependencies already installed"
    fi

    # Build application
    print_step 2 "Building React application..."

    npm run build

    if [ $? -eq 0 ]; then
        log_success "Frontend build successful"
    else
        die "Frontend build failed"
    fi

    # Verify dist directory
    if [ ! -d "dist" ]; then
        die "Build output directory not found"
    fi

    log_success "Frontend build: ${FRONTEND_DIR}/dist"

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# FRONTEND TESTS
# ==============================================================================

test_frontend() {
    if [ "$SKIP_TESTS" = true ] || [ "$SKIP_FRONTEND" = true ]; then
        log_info "Skipping frontend tests"
        return 0
    fi

    print_header "Running Frontend Tests"

    cd "$FRONTEND_DIR" || die "Failed to change to frontend directory"

    log_info "Executing test suite..."

    npm test -- --run

    if [ $? -eq 0 ]; then
        log_success "All frontend tests passed"

        # Check for coverage report
        if [ -d "coverage" ]; then
            log_info "Jest coverage report: ${FRONTEND_DIR}/coverage/index.html"
        fi
    else
        die "Frontend tests failed"
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# CONTAINER BUILD
# ==============================================================================

build_containers() {
    print_header "Building Container Images"

    cd "$CONTAINER_BUILDER_DIR" || die "Failed to change to container builder directory"

    # Build backend container
    if [ "$SKIP_BACKEND" = false ]; then
        print_step 1 "Building backend container..."

        podman build -t "localhost/orgmgmt-backend:${VERSION}" \
                     -t "localhost/orgmgmt-backend:latest" \
                     -f backend.Containerfile \
                     ../app/backend

        if [ $? -eq 0 ]; then
            log_success "Backend container built successfully"
        else
            die "Failed to build backend container"
        fi
    fi

    # Build frontend container
    if [ "$SKIP_FRONTEND" = false ]; then
        print_step 2 "Building frontend container..."

        podman build -t "localhost/orgmgmt-frontend:${VERSION}" \
                     -t "localhost/orgmgmt-frontend:latest" \
                     -f frontend.Containerfile \
                     ../app/frontend

        if [ $? -eq 0 ]; then
            log_success "Frontend container built successfully"
        else
            die "Failed to build frontend container"
        fi
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# PUSH TO REGISTRY
# ==============================================================================

push_to_registry() {
    print_header "Pushing Images to Registry"

    local registry="localhost:${NEXUS_DOCKER_PORT:-8082}"

    log_info "Using registry: $registry"

    # Tag and push backend
    if [ "$SKIP_BACKEND" = false ]; then
        print_step 1 "Pushing backend image..."

        podman tag "localhost/orgmgmt-backend:${VERSION}" "${registry}/orgmgmt-backend:${VERSION}"
        podman tag "localhost/orgmgmt-backend:${VERSION}" "${registry}/orgmgmt-backend:latest"

        podman push "${registry}/orgmgmt-backend:${VERSION}" --tls-verify=false
        podman push "${registry}/orgmgmt-backend:latest" --tls-verify=false

        log_success "Backend image pushed to registry"
    fi

    # Tag and push frontend
    if [ "$SKIP_FRONTEND" = false ]; then
        print_step 2 "Pushing frontend image..."

        podman tag "localhost/orgmgmt-frontend:${VERSION}" "${registry}/orgmgmt-frontend:${VERSION}"
        podman tag "localhost/orgmgmt-frontend:${VERSION}" "${registry}/orgmgmt-frontend:latest"

        podman push "${registry}/orgmgmt-frontend:${VERSION}" --tls-verify=false
        podman push "${registry}/orgmgmt-frontend:latest" --tls-verify=false

        log_success "Frontend image pushed to registry"
    fi
}

# ==============================================================================
# UPDATE GITOPS MANIFESTS
# ==============================================================================

update_gitops_manifests() {
    print_header "Updating GitOps Manifests"

    local manifest_dir="${GITOPS_DIR}/${ENVIRONMENT}"

    validate_directory "$manifest_dir" "GitOps manifests not found for environment: $ENVIRONMENT"

    log_info "Updating manifests in: $manifest_dir"

    # Update image tags in deployment files
    if [ -f "${manifest_dir}/backend-deployment.yaml" ]; then
        log_info "Updating backend deployment..."
        sed -i "s|image: localhost:8082/orgmgmt-backend:.*|image: localhost:8082/orgmgmt-backend:${VERSION}|g" \
            "${manifest_dir}/backend-deployment.yaml"
    fi

    if [ -f "${manifest_dir}/frontend-deployment.yaml" ]; then
        log_info "Updating frontend deployment..."
        sed -i "s|image: localhost:8082/orgmgmt-frontend:.*|image: localhost:8082/orgmgmt-frontend:${VERSION}|g" \
            "${manifest_dir}/frontend-deployment.yaml"
    fi

    log_success "GitOps manifests updated with version: $VERSION"
}

# ==============================================================================
# ARGOCD SYNC
# ==============================================================================

trigger_argocd_sync() {
    if [ "$NO_SYNC" = true ]; then
        log_info "Skipping ArgoCD sync (--no-sync flag)"
        return 0
    fi

    print_header "Triggering ArgoCD Sync"

    # Check if argocd CLI is available
    if ! check_command argocd; then
        log_warning "ArgoCD CLI not found, skipping sync"
        log_info "You can manually sync via: ./scripts/argocd-deploy.sh --environment $ENVIRONMENT"
        return 0
    fi

    log_info "Syncing application: orgmgmt-${ENVIRONMENT}"

    # Try to sync
    "${SCRIPT_DIR}/argocd-deploy.sh" --environment "$ENVIRONMENT" --wait

    if [ $? -eq 0 ]; then
        log_success "Application synced successfully"
    else
        log_warning "ArgoCD sync encountered issues. Check ArgoCD UI for details."
    fi
}

# ==============================================================================
# HEALTH CHECKS
# ==============================================================================

run_health_checks() {
    print_header "Running Health Checks"

    log_info "Checking deployment health..."

    # Get service ports based on environment
    local backend_port frontend_port

    case "$ENVIRONMENT" in
        dev)
            backend_port=8080
            frontend_port=5006
            ;;
        staging)
            backend_port=8081
            frontend_port=5007
            ;;
        prod)
            backend_port=8082
            frontend_port=5008
            ;;
    esac

    # Check backend health
    print_step 1 "Checking backend health..."

    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "http://localhost:${backend_port}/actuator/health" > /dev/null 2>&1; then
            log_success "Backend is healthy"
            break
        fi

        attempt=$((attempt + 1))
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        log_warning "Backend health check timed out"
    fi

    # Check frontend
    print_step 2 "Checking frontend..."

    if curl -sf "http://localhost:${frontend_port}" > /dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        log_warning "Frontend health check failed"
    fi
}

# ==============================================================================
# DISPLAY SUMMARY
# ==============================================================================

display_summary() {
    print_summary \
        "Environment:${ENVIRONMENT}" \
        "Version:${VERSION}" \
        "Backend:$([ "$SKIP_BACKEND" = false ] && echo "Built" || echo "Skipped")" \
        "Frontend:$([ "$SKIP_FRONTEND" = false ] && echo "Built" || echo "Skipped")" \
        "Tests:$([ "$SKIP_TESTS" = false ] && echo "Passed" || echo "Skipped")" \
        "ArgoCD Sync:$([ "$NO_SYNC" = false ] && echo "Triggered" || echo "Skipped")"

    echo -e "${GREEN}✓ Build and deployment completed!${NC}"
    echo ""
    echo -e "${YELLOW}Access URLs:${NC}"
    echo -e "  ArgoCD: ${CYAN}http://localhost:${ARGOCD_SERVER_PORT:-5010}${NC}"

    case "$ENVIRONMENT" in
        dev)
            echo -e "  Frontend: ${CYAN}http://localhost:5006${NC}"
            echo -e "  Backend: ${CYAN}http://localhost:8080${NC}"
            ;;
        staging)
            echo -e "  Frontend: ${CYAN}http://localhost:5007${NC}"
            echo -e "  Backend: ${CYAN}http://localhost:8081${NC}"
            ;;
        prod)
            echo -e "  Frontend: ${CYAN}http://localhost:5008${NC}"
            echo -e "  Backend: ${CYAN}http://localhost:8082${NC}"
            ;;
    esac

    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "Build and Deploy - Environment: $ENVIRONMENT"

    validate_environment
    generate_version
    build_backend
    test_backend
    build_frontend
    test_frontend
    build_containers
    push_to_registry
    update_gitops_manifests
    trigger_argocd_sync
    run_health_checks
    display_summary
}

main "$@"
