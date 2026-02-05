#!/bin/bash
#
# argocd-deploy.sh - ArgoCD Deployment Management
#
# This script manages application deployments via ArgoCD including:
# - Application synchronization
# - Deployment status monitoring
# - Health checks
#
# Usage: ./argocd-deploy.sh [OPTIONS]
#
# Options:
#   --environment ENV     Target environment (dev/staging/prod, required)
#   --wait               Wait for sync to complete
#   --timeout SECONDS    Sync timeout in seconds (default: 300)
#   --prune              Prune resources during sync
#   --force              Force sync even if app is up-to-date
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

ENVIRONMENT=""
WAIT=false
TIMEOUT=300
PRUNE=false
FORCE=false
ARGOCD_SERVER="localhost:5010"

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
ArgoCD Deployment Management

Usage: $(basename "$0") [OPTIONS]

Deploy applications via ArgoCD to specified environment.

Options:
    --environment ENV    Target environment (dev/staging/prod, required)
    --wait              Wait for sync to complete
    --timeout SECONDS   Sync timeout in seconds (default: 300)
    --prune             Prune resources during sync
    --force             Force sync even if app is up-to-date
    -h, --help          Show this help message

Examples:
    $(basename "$0") --environment dev                    # Deploy to dev
    $(basename "$0") --environment prod --wait            # Deploy to prod and wait
    $(basename "$0") --environment staging --force --prune # Force sync with prune

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --wait)
                WAIT=true
                shift
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            --prune)
                PRUNE=true
                shift
                ;;
            --force)
                FORCE=true
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
    if [ -z "$ENVIRONMENT" ]; then
        log_error "Environment is required"
        show_usage
        exit 1
    fi

    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        die "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod."
    fi
}

# ==============================================================================
# ARGOCD LOGIN
# ==============================================================================

login_to_argocd() {
    print_header "Logging in to ArgoCD"

    # Load environment
    if [ -f "${INFRASTRUCTURE_DIR}/.env" ]; then
        load_env_file "${INFRASTRUCTURE_DIR}/.env"
    fi

    # Check if ArgoCD is running
    if ! check_argocd; then
        die "ArgoCD is not accessible. Please ensure infrastructure is running."
    fi

    # Get password
    local password=""

    if [ -n "${ARGOCD_ADMIN_PASSWORD:-}" ]; then
        password="$ARGOCD_ADMIN_PASSWORD"
    else
        password=$(podman exec argocd-server argocd admin initial-password 2>/dev/null | head -1 || echo "admin")
    fi

    # Login
    log_info "Logging in to ArgoCD at ${ARGOCD_SERVER}..."

    argocd login "$ARGOCD_SERVER" \
        --username admin \
        --password "$password" \
        --insecure

    if [ $? -eq 0 ]; then
        log_success "Logged in to ArgoCD"
    else
        die "Failed to login to ArgoCD"
    fi
}

# ==============================================================================
# APPLICATION SYNC
# ==============================================================================

sync_application() {
    print_header "Syncing Application: orgmgmt-${ENVIRONMENT}"

    local app_name="orgmgmt-${ENVIRONMENT}"
    local sync_options=""

    # Build sync command options
    if [ "$PRUNE" = true ]; then
        sync_options="$sync_options --prune"
    fi

    if [ "$FORCE" = true ]; then
        sync_options="$sync_options --force"
    fi

    # Sync application
    log_info "Triggering sync for ${app_name}..."

    if [ "$WAIT" = true ]; then
        argocd app sync "$app_name" $sync_options --timeout "$TIMEOUT"
    else
        argocd app sync "$app_name" $sync_options
    fi

    if [ $? -eq 0 ]; then
        log_success "Application sync initiated"
    else
        die "Failed to sync application"
    fi
}

# ==============================================================================
# WAIT FOR SYNC
# ==============================================================================

wait_for_sync_completion() {
    if [ "$WAIT" = false ]; then
        return 0
    fi

    print_header "Waiting for Sync Completion"

    local app_name="orgmgmt-${ENVIRONMENT}"
    local max_attempts=$((TIMEOUT / 5))
    local attempt=0

    log_info "Monitoring sync progress..."

    while [ $attempt -lt $max_attempts ]; do
        local sync_status=$(argocd app get "$app_name" -o json | jq -r '.status.sync.status')
        local health_status=$(argocd app get "$app_name" -o json | jq -r '.status.health.status')

        echo -ne "${CYAN}Sync: ${sync_status} | Health: ${health_status}${NC}\r"

        if [ "$sync_status" = "Synced" ] && [ "$health_status" = "Healthy" ]; then
            echo ""
            log_success "Application is synced and healthy"
            return 0
        fi

        if [ "$sync_status" = "OutOfSync" ]; then
            echo ""
            log_warning "Application is out of sync"
        fi

        attempt=$((attempt + 1))
        sleep 5
    done

    echo ""
    log_error "Sync did not complete within timeout period"
    return 1
}

# ==============================================================================
# DISPLAY APPLICATION STATUS
# ==============================================================================

display_application_status() {
    print_header "Application Status"

    local app_name="orgmgmt-${ENVIRONMENT}"

    log_info "Retrieving application status..."

    # Get application details
    argocd app get "$app_name"

    echo ""

    # Get application resources
    log_info "Application resources:"
    argocd app resources "$app_name"
}

# ==============================================================================
# DISPLAY POD STATUS
# ==============================================================================

display_pod_status() {
    print_header "Pod Status"

    local namespace="orgmgmt-${ENVIRONMENT}"

    log_info "Checking pod status in namespace: ${namespace}..."

    # Use kubectl or oc if available, otherwise use podman
    if check_command kubectl; then
        kubectl get pods -n "$namespace" 2>/dev/null || log_warning "Unable to get pod status"
    elif check_command podman; then
        # List containers matching the environment
        podman ps --filter "label=app.kubernetes.io/instance=orgmgmt-${ENVIRONMENT}" \
                 --format "table {{.Names}}\t{{.Status}}\t{{.RunningFor}}"
    else
        log_warning "Cannot retrieve pod status - kubectl and podman not available"
    fi
}

# ==============================================================================
# DISPLAY ACCESS INFORMATION
# ==============================================================================

display_access_info() {
    print_header "Access Information"

    local frontend_port backend_port

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

    print_summary \
        "Environment:${ENVIRONMENT}" \
        "Application:orgmgmt-${ENVIRONMENT}" \
        "Frontend:http://localhost:${frontend_port}" \
        "Backend:http://localhost:${backend_port}" \
        "Backend Health:http://localhost:${backend_port}/actuator/health" \
        "ArgoCD:http://localhost:5010"

    echo -e "${GREEN}✓ Deployment completed!${NC}"
    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "ArgoCD Deployment - Environment: ${ENVIRONMENT}"

    login_to_argocd
    sync_application
    wait_for_sync_completion
    display_application_status
    display_pod_status
    display_access_info
}

main "$@"
