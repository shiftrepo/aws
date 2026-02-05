#!/bin/bash
#
# status.sh - Status Checker Script
#
# This script checks the status of all services including:
# - Container status
# - Service health
# - Resource usage
# - Network connectivity
#
# Usage: ./status.sh [OPTIONS]
#
# Options:
#   --detailed           Show detailed information
#   --json              Output in JSON format
#   --watch             Continuously monitor status
#   -h, --help          Show this help message
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

DETAILED=false
JSON_OUTPUT=false
WATCH=false

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Status Checker Script

Usage: $(basename "$0") [OPTIONS]

Check the status of all infrastructure services.

Options:
    --detailed          Show detailed information
    --json             Output in JSON format
    --watch            Continuously monitor status
    -h, --help         Show this help message

Examples:
    $(basename "$0")                # Show basic status
    $(basename "$0") --detailed     # Show detailed status
    $(basename "$0") --watch        # Monitor status continuously

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed)
                DETAILED=true
                shift
                ;;
            --json)
                JSON_OUTPUT=true
                shift
                ;;
            --watch)
                WATCH=true
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
# CHECK CONTAINER STATUS
# ==============================================================================

check_container_status() {
    local container=$1
    local status="Unknown"
    local health="N/A"

    if podman ps --format "{{.Names}}" | grep -q "^${container}$"; then
        status="${GREEN}Running${NC}"

        # Get health status if available
        health=$(podman inspect "$container" --format '{{.State.Health.Status}}' 2>/dev/null || echo "N/A")

        case "$health" in
            healthy)
                health="${GREEN}✓ Healthy${NC}"
                ;;
            unhealthy)
                health="${RED}✗ Unhealthy${NC}"
                ;;
            starting)
                health="${YELLOW}⟳ Starting${NC}"
                ;;
            *)
                health="${CYAN}N/A${NC}"
                ;;
        esac
    elif podman ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
        status="${RED}Stopped${NC}"
        health="${RED}Down${NC}"
    else
        status="${YELLOW}Not Found${NC}"
        health="${YELLOW}N/A${NC}"
    fi

    echo -e "${status}|${health}"
}

# ==============================================================================
# CHECK SERVICE HEALTH
# ==============================================================================

check_service_health() {
    local service=$1
    local check_result="Unknown"

    case "$service" in
        postgres)
            if check_postgres; then
                check_result="${GREEN}✓${NC}"
            else
                check_result="${RED}✗${NC}"
            fi
            ;;
        nexus)
            if check_nexus; then
                check_result="${GREEN}✓${NC}"
            else
                check_result="${RED}✗${NC}"
            fi
            ;;
        gitlab)
            if check_gitlab; then
                check_result="${GREEN}✓${NC}"
            else
                check_result="${RED}✗${NC}"
            fi
            ;;
        argocd-server)
            if check_argocd; then
                check_result="${GREEN}✓${NC}"
            else
                check_result="${RED}✗${NC}"
            fi
            ;;
        *)
            check_result="${CYAN}N/A${NC}"
            ;;
    esac

    echo -e "$check_result"
}

# ==============================================================================
# GET RESOURCE USAGE
# ==============================================================================

get_resource_usage() {
    local container=$1

    if ! podman ps --format "{{.Names}}" | grep -q "^${container}$"; then
        echo "N/A|N/A"
        return
    fi

    # Get CPU and memory usage
    local stats=$(podman stats --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}" "$container" 2>/dev/null || echo "N/A|N/A")

    echo "$stats"
}

# ==============================================================================
# DISPLAY STATUS TABLE
# ==============================================================================

display_status_table() {
    print_header "Service Status"

    # Define services to check
    local services=(
        "orgmgmt-postgres:PostgreSQL:postgres"
        "orgmgmt-pgadmin:pgAdmin:none"
        "orgmgmt-nexus:Nexus:nexus"
        "orgmgmt-gitlab:GitLab:gitlab"
        "orgmgmt-gitlab-runner:GitLab Runner:none"
        "argocd-redis:Redis:none"
        "argocd-repo-server:ArgoCD Repo:none"
        "argocd-application-controller:ArgoCD Controller:none"
        "argocd-server:ArgoCD Server:argocd-server"
    )

    # Print table header
    echo ""
    printf "${CYAN}%-30s %-15s %-15s %-10s${NC}\n" "Service" "Status" "Health" "Check"
    printf "${CYAN}%-30s %-15s %-15s %-10s${NC}\n" "$(printf '%30s' | tr ' ' '-')" "$(printf '%15s' | tr ' ' '-')" "$(printf '%15s' | tr ' ' '-')" "$(printf '%10s' | tr ' ' '-')"

    # Check each service
    for service_info in "${services[@]}"; do
        IFS=':' read -r container display_name health_check <<< "$service_info"

        # Get container status and health
        local status_health=$(check_container_status "$container")
        IFS='|' read -r status health <<< "$status_health"

        # Get service health check
        local check="N/A"
        if [ "$health_check" != "none" ]; then
            check=$(check_service_health "$health_check")
        else
            check="${CYAN}N/A${NC}"
        fi

        # Print row
        printf "%-30s " "$display_name"
        printf "%b " "$status"
        printf "%b " "$health"
        printf "%b\n" "$check"
    done

    echo ""
}

# ==============================================================================
# DISPLAY DETAILED STATUS
# ==============================================================================

display_detailed_status() {
    print_header "Detailed Service Status"

    # Get all project containers
    local containers=$(podman ps -a --filter "name=orgmgmt-" --filter "name=argocd-" --format "{{.Names}}")

    for container in $containers; do
        echo ""
        echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Container: ${NC}$container"
        echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        # Get container details
        local status=$(podman inspect "$container" --format '{{.State.Status}}' 2>/dev/null || echo "unknown")
        local uptime=$(podman inspect "$container" --format '{{.State.StartedAt}}' 2>/dev/null || echo "N/A")
        local health=$(podman inspect "$container" --format '{{.State.Health.Status}}' 2>/dev/null || echo "N/A")

        echo -e "  Status:     $status"
        echo -e "  Started:    $uptime"
        echo -e "  Health:     $health"

        # Get resource usage
        if [ "$status" = "running" ]; then
            local resource_usage=$(get_resource_usage "$container")
            IFS='|' read -r cpu mem <<< "$resource_usage"

            echo -e "  CPU:        $cpu"
            echo -e "  Memory:     $mem"

            # Get port mappings
            local ports=$(podman port "$container" 2>/dev/null || echo "None")
            echo -e "  Ports:      $ports"
        fi
    done

    echo ""
}

# ==============================================================================
# DISPLAY RESOURCE SUMMARY
# ==============================================================================

display_resource_summary() {
    print_header "Resource Summary"

    # System resources
    log_info "System Resources:"

    # Memory
    if [ -f /proc/meminfo ]; then
        local total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        local avail_mem=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
        local used_mem=$((total_mem - avail_mem))

        local total_mem_gb=$(awk "BEGIN {printf \"%.2f\", $total_mem/1024/1024}")
        local used_mem_gb=$(awk "BEGIN {printf \"%.2f\", $used_mem/1024/1024}")
        local avail_mem_gb=$(awk "BEGIN {printf \"%.2f\", $avail_mem/1024/1024}")

        echo -e "  Memory: ${used_mem_gb}GB / ${total_mem_gb}GB used (${avail_mem_gb}GB available)"
    fi

    # Disk
    local disk_info=$(df -h "$PROJECT_ROOT" | tail -1)
    local disk_usage=$(echo "$disk_info" | awk '{print $5}')
    local disk_avail=$(echo "$disk_info" | awk '{print $4}')

    echo -e "  Disk:   ${disk_usage} used (${disk_avail} available)"

    echo ""
}

# ==============================================================================
# DISPLAY ACCESS URLS
# ==============================================================================

display_access_urls() {
    print_header "Access URLs"

    # Load environment
    if [ -f "${INFRASTRUCTURE_DIR}/.env" ]; then
        load_env_file "${INFRASTRUCTURE_DIR}/.env" > /dev/null 2>&1
    fi

    echo ""
    echo -e "${CYAN}Infrastructure Services:${NC}"
    echo -e "  PostgreSQL:  ${GREEN}localhost:${POSTGRES_PORT:-5432}${NC}"
    echo -e "  pgAdmin:     ${GREEN}http://localhost:${PGADMIN_PORT:-5050}${NC}"
    echo -e "  Nexus:       ${GREEN}http://localhost:${NEXUS_HTTP_PORT:-8081}${NC}"
    echo -e "  GitLab:      ${GREEN}http://localhost:${GITLAB_HTTP_PORT:-5003}${NC}"
    echo -e "  ArgoCD:      ${GREEN}http://localhost:${ARGOCD_SERVER_PORT:-5010}${NC}"

    echo ""
    echo -e "${CYAN}Application Services:${NC}"
    echo -e "  Dev Frontend:      ${GREEN}http://localhost:5006${NC}"
    echo -e "  Dev Backend:       ${GREEN}http://localhost:8080${NC}"
    echo -e "  Staging Frontend:  ${GREEN}http://localhost:5007${NC}"
    echo -e "  Staging Backend:   ${GREEN}http://localhost:8081${NC}"
    echo -e "  Prod Frontend:     ${GREEN}http://localhost:5008${NC}"
    echo -e "  Prod Backend:      ${GREEN}http://localhost:8082${NC}"

    echo ""
}

# ==============================================================================
# WATCH MODE
# ==============================================================================

watch_status() {
    while true; do
        clear
        display_status_table

        if [ "$DETAILED" = true ]; then
            display_resource_summary
        fi

        echo ""
        echo -e "${CYAN}Refreshing in 5 seconds... (Press Ctrl+C to exit)${NC}"
        sleep 5
    done
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    if [ "$WATCH" = true ]; then
        watch_status
    else
        display_status_table

        if [ "$DETAILED" = true ]; then
            display_detailed_status
            display_resource_summary
        fi

        display_access_urls
    fi
}

main "$@"
