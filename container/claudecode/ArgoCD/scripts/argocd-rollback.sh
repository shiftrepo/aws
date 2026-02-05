#!/bin/bash
#
# argocd-rollback.sh - ArgoCD Application Rollback
#
# This script handles application rollbacks via ArgoCD including:
# - Deployment history viewing
# - Rollback to previous or specific version
# - Rollback verification
#
# Usage: ./argocd-rollback.sh [OPTIONS]
#
# Options:
#   --environment ENV     Target environment (dev/staging/prod, required)
#   --revision REV       Specific revision to rollback to (optional)
#   --history            Show deployment history only
#   --wait               Wait for rollback to complete
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
REVISION=""
SHOW_HISTORY=false
WAIT=false
ARGOCD_SERVER="localhost:5010"

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
ArgoCD Application Rollback

Usage: $(basename "$0") [OPTIONS]

Rollback applications to previous versions via ArgoCD.

Options:
    --environment ENV    Target environment (dev/staging/prod, required)
    --revision REV      Specific revision to rollback to (optional)
    --history           Show deployment history only
    --wait              Wait for rollback to complete
    -h, --help          Show this help message

Examples:
    $(basename "$0") --environment dev --history          # Show deployment history
    $(basename "$0") --environment dev                    # Rollback to previous version
    $(basename "$0") --environment prod --revision 5      # Rollback to revision 5
    $(basename "$0") --environment staging --wait         # Rollback and wait

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
            --revision)
                REVISION="$2"
                shift 2
                ;;
            --history)
                SHOW_HISTORY=true
                shift
                ;;
            --wait)
                WAIT=true
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
    argocd login "$ARGOCD_SERVER" \
        --username admin \
        --password "$password" \
        --insecure > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log_success "Logged in to ArgoCD"
    else
        die "Failed to login to ArgoCD"
    fi
}

# ==============================================================================
# SHOW DEPLOYMENT HISTORY
# ==============================================================================

show_deployment_history() {
    print_header "Deployment History: orgmgmt-${ENVIRONMENT}"

    local app_name="orgmgmt-${ENVIRONMENT}"

    log_info "Retrieving deployment history..."
    echo ""

    argocd app history "$app_name"

    if [ $? -eq 0 ]; then
        echo ""
        log_success "Deployment history retrieved"
    else
        die "Failed to retrieve deployment history"
    fi
}

# ==============================================================================
# DETERMINE ROLLBACK REVISION
# ==============================================================================

determine_rollback_revision() {
    if [ -n "$REVISION" ]; then
        log_info "Using specified revision: $REVISION"
        return 0
    fi

    print_header "Determining Rollback Revision"

    local app_name="orgmgmt-${ENVIRONMENT}"

    log_info "Finding previous deployment..."

    # Get current revision
    local current_revision=$(argocd app get "$app_name" -o json | jq -r '.status.sync.revision' | cut -c1-7)

    log_info "Current revision: ${current_revision}"

    # Get history and find previous revision
    local history=$(argocd app history "$app_name" --output json)

    # Get the second most recent deployment (skip current)
    local previous_revision=$(echo "$history" | jq -r '.[1].id // empty')

    if [ -z "$previous_revision" ]; then
        die "No previous revision found to rollback to"
    fi

    REVISION="$previous_revision"
    log_success "Will rollback to revision: $REVISION"
}

# ==============================================================================
# CONFIRM ROLLBACK
# ==============================================================================

confirm_rollback() {
    print_header "Rollback Confirmation"

    local app_name="orgmgmt-${ENVIRONMENT}"

    log_warning "You are about to rollback application: ${app_name}"
    log_warning "Target revision: ${REVISION}"
    echo ""

    # In non-interactive mode, proceed automatically
    if [ -t 0 ]; then
        read -p "$(echo -e ${YELLOW}Do you want to proceed? [y/N]: ${NC})" -n 1 -r
        echo ""

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Rollback cancelled by user"
            exit 0
        fi
    else
        log_info "Non-interactive mode - proceeding with rollback"
    fi
}

# ==============================================================================
# EXECUTE ROLLBACK
# ==============================================================================

execute_rollback() {
    print_header "Executing Rollback"

    local app_name="orgmgmt-${ENVIRONMENT}"

    log_info "Rolling back ${app_name} to revision ${REVISION}..."

    argocd app rollback "$app_name" "$REVISION"

    if [ $? -eq 0 ]; then
        log_success "Rollback initiated successfully"
    else
        die "Failed to initiate rollback"
    fi
}

# ==============================================================================
# WAIT FOR ROLLBACK
# ==============================================================================

wait_for_rollback_completion() {
    if [ "$WAIT" = false ]; then
        log_info "Not waiting for rollback to complete (use --wait flag to wait)"
        return 0
    fi

    print_header "Waiting for Rollback Completion"

    local app_name="orgmgmt-${ENVIRONMENT}"
    local max_attempts=60
    local attempt=0

    log_info "Monitoring rollback progress..."

    while [ $attempt -lt $max_attempts ]; do
        local sync_status=$(argocd app get "$app_name" -o json | jq -r '.status.sync.status')
        local health_status=$(argocd app get "$app_name" -o json | jq -r '.status.health.status')

        echo -ne "${CYAN}Sync: ${sync_status} | Health: ${health_status}${NC}\r"

        if [ "$sync_status" = "Synced" ] && [ "$health_status" = "Healthy" ]; then
            echo ""
            log_success "Rollback completed successfully"
            return 0
        fi

        if [ "$health_status" = "Degraded" ]; then
            echo ""
            log_error "Application health is degraded"
            return 1
        fi

        attempt=$((attempt + 1))
        sleep 5
    done

    echo ""
    log_warning "Rollback monitoring timed out"
    return 1
}

# ==============================================================================
# VERIFY ROLLBACK
# ==============================================================================

verify_rollback() {
    print_header "Verifying Rollback"

    local app_name="orgmgmt-${ENVIRONMENT}"

    log_info "Checking application status..."

    # Get current status
    local sync_status=$(argocd app get "$app_name" -o json | jq -r '.status.sync.status')
    local health_status=$(argocd app get "$app_name" -o json | jq -r '.status.health.status')
    local current_revision=$(argocd app get "$app_name" -o json | jq -r '.status.sync.revision' | cut -c1-7)

    echo ""
    echo -e "  ${CYAN}Sync Status:${NC}    $sync_status"
    echo -e "  ${CYAN}Health Status:${NC}  $health_status"
    echo -e "  ${CYAN}Current Revision:${NC} $current_revision"
    echo ""

    if [ "$sync_status" = "Synced" ] && [ "$health_status" = "Healthy" ]; then
        log_success "Application is healthy after rollback"
        return 0
    else
        log_warning "Application status should be verified manually"
        return 1
    fi
}

# ==============================================================================
# RUN HEALTH CHECKS
# ==============================================================================

run_health_checks() {
    print_header "Running Health Checks"

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

    # Check backend health
    log_info "Checking backend health..."

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
    log_info "Checking frontend..."

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
        "Application:orgmgmt-${ENVIRONMENT}" \
        "Rolled back to:Revision ${REVISION}" \
        "Status:Completed"

    echo -e "${GREEN}✓ Rollback completed!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Verify application functionality"
    echo -e "  2. Check logs: ${CYAN}./scripts/logs.sh${NC}"
    echo -e "  3. Monitor ArgoCD: ${CYAN}http://localhost:5010${NC}"
    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "ArgoCD Rollback - Environment: ${ENVIRONMENT}"

    login_to_argocd

    # If only showing history, do that and exit
    if [ "$SHOW_HISTORY" = true ]; then
        show_deployment_history
        exit 0
    fi

    # Show history first
    show_deployment_history

    # Determine revision to rollback to
    determine_rollback_revision

    # Confirm rollback
    confirm_rollback

    # Execute rollback
    execute_rollback

    # Wait for completion
    wait_for_rollback_completion

    # Verify rollback
    verify_rollback

    # Run health checks
    run_health_checks

    # Display summary
    display_summary
}

main "$@"
