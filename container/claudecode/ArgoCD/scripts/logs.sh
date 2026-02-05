#!/bin/bash
#
# logs.sh - Log Viewer Script
#
# This script provides easy access to container logs including:
# - View logs from all services
# - View logs from specific service
# - Follow logs in real-time
# - Filter by time range
#
# Usage: ./logs.sh [SERVICE] [OPTIONS]
#
# Options:
#   --tail N             Show last N lines (default: 100)
#   --follow, -f         Follow log output
#   --since TIME         Show logs since timestamp (e.g., 2h, 30m)
#   --timestamps         Show timestamps
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

SERVICE=""
TAIL=100
FOLLOW=false
SINCE=""
TIMESTAMPS=false

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Log Viewer Script

Usage: $(basename "$0") [SERVICE] [OPTIONS]

View container logs from infrastructure services.

Arguments:
    SERVICE             Service name (optional, shows all if not specified)

Available Services:
    postgres            PostgreSQL database
    pgadmin             pgAdmin web interface
    nexus               Nexus Repository Manager
    gitlab              GitLab CE
    gitlab-runner       GitLab Runner
    argocd-server       ArgoCD API Server
    argocd-repo-server  ArgoCD Repository Server
    argocd-application-controller  ArgoCD Application Controller
    argocd-redis        Redis for ArgoCD

Options:
    --tail N            Show last N lines (default: 100)
    --follow, -f        Follow log output
    --since TIME        Show logs since timestamp (e.g., 2h, 30m)
    --timestamps        Show timestamps
    -h, --help          Show this help message

Examples:
    $(basename "$0")                        # Show all logs
    $(basename "$0") postgres               # Show PostgreSQL logs
    $(basename "$0") argocd-server -f       # Follow ArgoCD server logs
    $(basename "$0") nexus --tail 50        # Show last 50 lines of Nexus logs
    $(basename "$0") gitlab --since 1h      # Show GitLab logs from last hour

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    # First argument might be service name
    if [ $# -gt 0 ] && [[ ! "$1" =~ ^-- ]] && [[ ! "$1" =~ ^-[fh]$ ]]; then
        SERVICE="$1"
        shift
    fi

    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --tail)
                TAIL="$2"
                shift 2
                ;;
            --follow|-f)
                FOLLOW=true
                shift
                ;;
            --since)
                SINCE="$2"
                shift 2
                ;;
            --timestamps)
                TIMESTAMPS=true
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
}

# ==============================================================================
# MAP SERVICE NAME TO CONTAINER
# ==============================================================================

get_container_name() {
    local service=$1
    local container=""

    case "$service" in
        postgres)
            container="orgmgmt-postgres"
            ;;
        pgadmin)
            container="orgmgmt-pgadmin"
            ;;
        nexus)
            container="orgmgmt-nexus"
            ;;
        gitlab)
            container="orgmgmt-gitlab"
            ;;
        gitlab-runner)
            container="orgmgmt-gitlab-runner"
            ;;
        argocd-server)
            container="argocd-server"
            ;;
        argocd-repo-server)
            container="argocd-repo-server"
            ;;
        argocd-application-controller)
            container="argocd-application-controller"
            ;;
        argocd-redis|redis)
            container="argocd-redis"
            ;;
        *)
            # Assume it's already a container name
            container="$service"
            ;;
    esac

    echo "$container"
}

# ==============================================================================
# DISPLAY LOGS
# ==============================================================================

display_logs() {
    cd "$INFRASTRUCTURE_DIR" || die "Failed to change to infrastructure directory"

    # Build log command
    local log_cmd="podman-compose logs"

    # Add options
    if [ "$FOLLOW" = true ]; then
        log_cmd="$log_cmd -f"
    fi

    if [ "$TIMESTAMPS" = true ]; then
        log_cmd="$log_cmd -t"
    fi

    if [ -n "$TAIL" ]; then
        log_cmd="$log_cmd --tail=$TAIL"
    fi

    if [ -n "$SINCE" ]; then
        log_cmd="$log_cmd --since=$SINCE"
    fi

    # Add service if specified
    if [ -n "$SERVICE" ]; then
        local container=$(get_container_name "$SERVICE")

        # Check if container exists
        if ! podman ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
            log_error "Container not found: $container"
            echo ""
            echo "Available containers:"
            podman ps -a --format "{{.Names}}" | grep -E "^(orgmgmt-|argocd-)"
            exit 1
        fi

        print_header "Logs: $container"
        log_cmd="$log_cmd $SERVICE"
    else
        print_header "Logs: All Services"
    fi

    # Execute log command
    log_info "Displaying logs..."
    echo ""

    eval $log_cmd

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"
    display_logs
}

main "$@"
