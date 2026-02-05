#!/bin/bash
#
# setup.sh - Master setup script for ArgoCD Project
#
# This script performs a complete setup of the development environment including:
# - Prerequisites validation
# - Environment configuration
# - Infrastructure deployment
# - Service initialization
# - Initial configuration
#
# Usage: ./setup.sh [OPTIONS]
#
# Options:
#   --skip-checks          Skip prerequisite checks
#   --no-init             Skip service initialization
#   --env-file FILE       Use custom environment file
#   -h, --help            Show this help message
#

set -e
set -u
set -o pipefail

# ==============================================================================
# INITIALIZATION
# ==============================================================================

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Source common functions
source "${SCRIPT_DIR}/common.sh"

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Default values
SKIP_CHECKS=false
NO_INIT=false
ENV_FILE="${INFRASTRUCTURE_DIR}/.env"
CREDENTIALS_FILE="${PROJECT_ROOT}/credentials.txt"

# Service health check configuration
POSTGRES_MAX_RETRIES=30
POSTGRES_RETRY_INTERVAL=5
NEXUS_MAX_RETRIES=60
NEXUS_RETRY_INTERVAL=10
GITLAB_MAX_RETRIES=60
GITLAB_RETRY_INTERVAL=10
ARGOCD_MAX_RETRIES=30
ARGOCD_RETRY_INTERVAL=10

# ==============================================================================
# USAGE INFORMATION
# ==============================================================================

show_usage() {
    cat << EOF
ArgoCD Project - Master Setup Script

Usage: $(basename "$0") [OPTIONS]

This script performs a complete setup of the development environment.

Options:
    --skip-checks         Skip prerequisite checks
    --no-init            Skip service initialization
    --env-file FILE      Use custom environment file
    -h, --help           Show this help message

Example:
    $(basename "$0")                    # Full setup
    $(basename "$0") --skip-checks      # Skip prerequisite checks
    $(basename "$0") --no-init          # Setup without initialization

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --no-init)
                NO_INIT=true
                shift
                ;;
            --env-file)
                ENV_FILE="$2"
                shift 2
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
}

# ==============================================================================
# PREREQUISITE CHECKS
# ==============================================================================

check_prerequisites() {
    print_header "Checking Prerequisites"

    log_info "Checking required commands..."

    local required_commands=(
        "podman"
        "podman-compose"
        "git"
        "jq"
        "curl"
        "openssl"
        "sed"
        "awk"
    )

    if ! check_prerequisites "${required_commands[@]}"; then
        die "Missing required dependencies. Please install them and try again."
    fi

    log_info "Checking system resources..."

    # Check memory (minimum 4GB recommended)
    check_memory 4 || log_warning "Low memory detected. Performance may be impacted."

    # Check disk space (minimum 10GB recommended)
    check_disk_space "$PROJECT_ROOT" 10 || log_warning "Low disk space. You may need to free up space."

    log_success "All prerequisite checks passed"
}

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

setup_environment() {
    print_header "Setting Up Environment"

    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_info "Creating .env file from template..."

        local env_template="${INFRASTRUCTURE_DIR}/.env.example"

        if [ ! -f "$env_template" ]; then
            die "Environment template not found: $env_template"
        fi

        # Copy template
        cp "$env_template" "$ENV_FILE"

        # Generate secure passwords
        log_info "Generating secure passwords..."

        local postgres_password=$(generate_password 24)
        local pgadmin_password=$(generate_password 24)
        local nexus_password=$(generate_password 24)
        local gitlab_password=$(generate_password 24)
        local argocd_password=$(generate_password 24)

        # Update passwords in .env file
        sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${postgres_password}/" "$ENV_FILE"
        sed -i "s/PGADMIN_DEFAULT_PASSWORD=.*/PGADMIN_DEFAULT_PASSWORD=${pgadmin_password}/" "$ENV_FILE"
        sed -i "s/NEXUS_ADMIN_PASSWORD=.*/NEXUS_ADMIN_PASSWORD=${nexus_password}/" "$ENV_FILE"
        sed -i "s/GITLAB_ROOT_PASSWORD=.*/GITLAB_ROOT_PASSWORD=${gitlab_password}/" "$ENV_FILE"
        sed -i "s/ARGOCD_ADMIN_PASSWORD=.*/ARGOCD_ADMIN_PASSWORD=${argocd_password}/" "$ENV_FILE"

        log_success "Created .env file with secure passwords"
    else
        log_info ".env file already exists, using existing configuration"
    fi

    # Load environment variables
    load_env_file "$ENV_FILE"

    log_success "Environment configuration ready"
}

# ==============================================================================
# INFRASTRUCTURE DEPLOYMENT
# ==============================================================================

start_infrastructure() {
    print_header "Starting Infrastructure"

    log_info "Starting services with podman-compose..."

    cd "$INFRASTRUCTURE_DIR" || die "Failed to change to infrastructure directory"

    # Start services in detached mode
    podman-compose up -d

    if [ $? -eq 0 ]; then
        log_success "Infrastructure services started"
    else
        die "Failed to start infrastructure services"
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# SERVICE HEALTH CHECKS
# ==============================================================================

wait_for_services() {
    print_header "Waiting for Services to be Ready"

    # PostgreSQL
    print_step 1 "Waiting for PostgreSQL..."
    if wait_for_service "PostgreSQL" "check_postgres" "$POSTGRES_MAX_RETRIES" "$POSTGRES_RETRY_INTERVAL"; then
        log_success "PostgreSQL is ready"
    else
        die "PostgreSQL failed to start"
    fi

    # Nexus
    print_step 2 "Waiting for Nexus Repository..."
    if wait_for_service "Nexus" "check_nexus" "$NEXUS_MAX_RETRIES" "$NEXUS_RETRY_INTERVAL"; then
        log_success "Nexus is ready"
    else
        die "Nexus failed to start"
    fi

    # GitLab
    print_step 3 "Waiting for GitLab..."
    if wait_for_service "GitLab" "check_gitlab" "$GITLAB_MAX_RETRIES" "$GITLAB_RETRY_INTERVAL"; then
        log_success "GitLab is ready"
    else
        die "GitLab failed to start"
    fi

    # ArgoCD
    print_step 4 "Waiting for ArgoCD..."
    if wait_for_service "ArgoCD" "check_argocd" "$ARGOCD_MAX_RETRIES" "$ARGOCD_RETRY_INTERVAL"; then
        log_success "ArgoCD is ready"
    else
        die "ArgoCD failed to start"
    fi

    log_success "All services are ready"
}

# ==============================================================================
# RETRIEVE INITIAL CREDENTIALS
# ==============================================================================

retrieve_credentials() {
    print_header "Retrieving Initial Credentials"

    # ArgoCD initial password
    log_info "Retrieving ArgoCD initial password..."
    local argocd_initial_password=""

    # Try multiple methods to get ArgoCD password
    if [ -n "$ARGOCD_ADMIN_PASSWORD" ]; then
        argocd_initial_password="$ARGOCD_ADMIN_PASSWORD"
        log_success "Using ArgoCD password from environment"
    else
        # Try to get from container
        argocd_initial_password=$(podman exec argocd-server argocd admin initial-password 2>/dev/null | head -1 || echo "")

        if [ -n "$argocd_initial_password" ]; then
            log_success "Retrieved ArgoCD initial password from container"
        else
            log_warning "Could not retrieve ArgoCD password automatically"
            argocd_initial_password="admin"
        fi
    fi

    export ARGOCD_PASSWORD="$argocd_initial_password"

    # Nexus initial password
    log_info "Retrieving Nexus initial password..."
    local nexus_initial_password=""

    if [ -n "$NEXUS_ADMIN_PASSWORD" ]; then
        nexus_initial_password="$NEXUS_ADMIN_PASSWORD"
        log_success "Using Nexus password from environment"
    else
        # Try to get from container
        nexus_initial_password=$(podman exec orgmgmt-nexus cat /nexus-data/admin.password 2>/dev/null || echo "")

        if [ -n "$nexus_initial_password" ]; then
            log_success "Retrieved Nexus initial password from container"
        else
            log_warning "Could not retrieve Nexus password automatically"
            nexus_initial_password="admin123"
        fi
    fi

    export NEXUS_PASSWORD="$nexus_initial_password"

    log_success "Credentials retrieved"
}

# ==============================================================================
# SAVE CREDENTIALS
# ==============================================================================

save_credentials() {
    print_header "Saving Credentials"

    log_info "Saving credentials to ${CREDENTIALS_FILE}..."

    cat > "$CREDENTIALS_FILE" << EOF
========================================
  ArgoCD Project - Access Credentials
========================================
Generated: $(date)

PostgreSQL Database
-------------------
Host:     localhost
Port:     ${POSTGRES_PORT:-5432}
Database: ${POSTGRES_DB:-orgmgmt}
User:     ${POSTGRES_USER:-orgmgmt_user}
Password: ${POSTGRES_PASSWORD}

pgAdmin
-------
URL:      http://localhost:${PGADMIN_PORT:-5050}
Email:    ${PGADMIN_DEFAULT_EMAIL:-admin@orgmgmt.local}
Password: ${PGADMIN_DEFAULT_PASSWORD}

Nexus Repository
----------------
URL:      http://localhost:${NEXUS_HTTP_PORT:-8081}
Username: admin
Password: ${NEXUS_PASSWORD}

GitLab
------
URL:      http://localhost:${GITLAB_HTTP_PORT:-5003}
Username: root
Password: ${GITLAB_ROOT_PASSWORD}

ArgoCD
------
URL:      http://localhost:${ARGOCD_SERVER_PORT:-5010}
Username: admin
Password: ${ARGOCD_PASSWORD}

Application Frontend
--------------------
URL:      http://localhost:${APP_FRONTEND_PORT:-5006}

Application Backend
-------------------
URL:      http://localhost:${APP_BACKEND_PORT:-8080}
Health:   http://localhost:${APP_BACKEND_PORT:-8080}/actuator/health

========================================
  IMPORTANT SECURITY NOTES
========================================
1. Change all default passwords before deploying to production
2. This file contains sensitive information - keep it secure
3. Add credentials.txt to .gitignore if not already present
4. Use environment-specific passwords for different environments

EOF

    chmod 600 "$CREDENTIALS_FILE"
    log_success "Credentials saved to: ${CREDENTIALS_FILE}"
}

# ==============================================================================
# SERVICE INITIALIZATION
# ==============================================================================

initialize_services() {
    if [ "$NO_INIT" = true ]; then
        log_info "Skipping service initialization (--no-init flag)"
        return 0
    fi

    print_header "Initializing Services"

    # Note: Detailed initialization would go here
    # This includes:
    # - Creating GitLab projects
    # - Configuring Nexus repositories
    # - Setting up ArgoCD applications
    # - Running database migrations

    log_info "Service initialization can be done manually or with additional scripts"
    log_info "Run individual setup scripts for GitLab, Nexus, and ArgoCD as needed"

    log_success "Service initialization phase complete"
}

# ==============================================================================
# DISPLAY SUMMARY
# ==============================================================================

display_summary() {
    print_summary \
        "PostgreSQL:http://localhost:${POSTGRES_PORT:-5432}" \
        "pgAdmin:http://localhost:${PGADMIN_PORT:-5050}" \
        "Nexus:http://localhost:${NEXUS_HTTP_PORT:-8081}" \
        "GitLab:http://localhost:${GITLAB_HTTP_PORT:-5003}" \
        "ArgoCD:http://localhost:${ARGOCD_SERVER_PORT:-5010}" \
        "Frontend:http://localhost:${APP_FRONTEND_PORT:-5006}" \
        "Backend:http://localhost:${APP_BACKEND_PORT:-8080}"

    echo -e "${GREEN}✓ Setup completed successfully!${NC}"
    echo ""
    echo -e "Credentials saved to: ${CYAN}${CREDENTIALS_FILE}${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Review credentials: ${CYAN}cat ${CREDENTIALS_FILE}${NC}"
    echo -e "  2. Check service status: ${CYAN}./scripts/status.sh${NC}"
    echo -e "  3. View logs: ${CYAN}./scripts/logs.sh${NC}"
    echo -e "  4. Build and deploy: ${CYAN}./scripts/build-and-deploy.sh${NC}"
    echo ""
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "ArgoCD Project - Master Setup"

    log_info "Project root: ${PROJECT_ROOT}"
    log_info "Infrastructure directory: ${INFRASTRUCTURE_DIR}"
    log_info "Environment file: ${ENV_FILE}"

    # Run prerequisite checks
    if [ "$SKIP_CHECKS" = false ]; then
        check_prerequisites
    else
        log_warning "Skipping prerequisite checks (--skip-checks flag)"
    fi

    # Setup environment
    setup_environment

    # Start infrastructure
    start_infrastructure

    # Wait for services
    wait_for_services

    # Retrieve credentials
    retrieve_credentials

    # Initialize services
    initialize_services

    # Save credentials
    save_credentials

    # Display summary
    display_summary
}

# Run main function
main "$@"
