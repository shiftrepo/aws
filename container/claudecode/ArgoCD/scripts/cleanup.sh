#!/bin/bash
#
# cleanup.sh - Environment Cleanup Script
#
# This script cleans up the development environment including:
# - Stopping containers
# - Removing volumes
# - Cleaning build artifacts
# - Clearing caches
#
# Usage: ./cleanup.sh [OPTIONS]
#
# Options:
#   --all                Remove everything including volumes
#   --volumes            Remove volumes only
#   --artifacts          Clean build artifacts only
#   --cache              Clear build caches
#   --reset-db           Reset database (removes data)
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

ALL=false
VOLUMES=false
ARTIFACTS=false
CACHE=false
RESET_DB=false

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Environment Cleanup Script

Usage: $(basename "$0") [OPTIONS]

Clean up development environment and build artifacts.

Options:
    --all               Remove everything including volumes
    --volumes           Remove volumes only
    --artifacts         Clean build artifacts only
    --cache             Clear build caches
    --reset-db          Reset database (removes data)
    -h, --help          Show this help message

Examples:
    $(basename "$0")                    # Stop containers only
    $(basename "$0") --artifacts        # Clean build artifacts
    $(basename "$0") --all              # Complete cleanup
    $(basename "$0") --volumes          # Remove volumes

WARNING: --all and --reset-db will delete all data!

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    # If no arguments, only stop containers
    if [ $# -eq 0 ]; then
        return
    fi

    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                ALL=true
                VOLUMES=true
                ARTIFACTS=true
                CACHE=true
                shift
                ;;
            --volumes)
                VOLUMES=true
                shift
                ;;
            --artifacts)
                ARTIFACTS=true
                shift
                ;;
            --cache)
                CACHE=true
                shift
                ;;
            --reset-db)
                RESET_DB=true
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
# CONFIRMATION
# ==============================================================================

confirm_cleanup() {
    if [ "$ALL" = true ] || [ "$VOLUMES" = true ] || [ "$RESET_DB" = true ]; then
        print_header "Cleanup Confirmation"

        log_warning "This operation will delete data. This cannot be undone!"
        echo ""

        if [ "$ALL" = true ]; then
            echo -e "  ${RED}• Stop all containers${NC}"
            echo -e "  ${RED}• Remove all volumes${NC}"
            echo -e "  ${RED}• Delete all data${NC}"
            echo -e "  ${RED}• Clean build artifacts${NC}"
            echo -e "  ${RED}• Clear caches${NC}"
        elif [ "$VOLUMES" = true ]; then
            echo -e "  ${RED}• Remove all volumes${NC}"
            echo -e "  ${RED}• Delete all data${NC}"
        elif [ "$RESET_DB" = true ]; then
            echo -e "  ${RED}• Reset database${NC}"
            echo -e "  ${RED}• Delete all database data${NC}"
        fi

        echo ""

        if [ -t 0 ]; then
            read -p "$(echo -e ${YELLOW}Are you sure you want to proceed? [y/N]: ${NC})" -n 1 -r
            echo ""

            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Cleanup cancelled by user"
                exit 0
            fi
        else
            log_warning "Non-interactive mode - proceeding with cleanup"
        fi
    fi
}

# ==============================================================================
# STOP CONTAINERS
# ==============================================================================

stop_containers() {
    print_header "Stopping Containers"

    cd "$INFRASTRUCTURE_DIR" || die "Failed to change to infrastructure directory"

    log_info "Stopping all services..."

    if [ "$VOLUMES" = true ]; then
        podman-compose down -v
    else
        podman-compose down
    fi

    if [ $? -eq 0 ]; then
        log_success "All containers stopped"
    else
        log_warning "Some containers may not have stopped cleanly"
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# REMOVE VOLUMES
# ==============================================================================

remove_volumes() {
    if [ "$VOLUMES" = false ] && [ "$ALL" = false ]; then
        return 0
    fi

    print_header "Removing Volumes"

    log_info "Removing persistent volumes..."

    # List of volumes to remove
    local volumes=(
        "orgmgmt-postgres-data"
        "orgmgmt-pgadmin-data"
        "orgmgmt-nexus-data"
        "orgmgmt-gitlab-config"
        "orgmgmt-gitlab-logs"
        "orgmgmt-gitlab-data"
        "orgmgmt-gitlab-runner-config"
        "argocd-redis-data"
        "argocd-repo-data"
        "argocd-controller-data"
        "argocd-server-data"
    )

    for volume in "${volumes[@]}"; do
        if podman volume exists "$volume" 2>/dev/null; then
            log_info "Removing volume: $volume"
            podman volume rm "$volume" 2>/dev/null || log_warning "Failed to remove volume: $volume"
        fi
    done

    log_success "Volumes removed"
}

# ==============================================================================
# CLEAN BUILD ARTIFACTS
# ==============================================================================

clean_build_artifacts() {
    if [ "$ARTIFACTS" = false ] && [ "$ALL" = false ]; then
        return 0
    fi

    print_header "Cleaning Build Artifacts"

    # Clean backend artifacts
    if [ -d "${APP_DIR}/backend" ]; then
        log_info "Cleaning backend build artifacts..."

        cd "${APP_DIR}/backend" || die "Failed to change to backend directory"

        if [ -d "target" ]; then
            rm -rf target
            log_success "Removed backend target directory"
        fi

        cd "$PROJECT_ROOT" || die "Failed to return to project root"
    fi

    # Clean frontend artifacts
    if [ -d "${APP_DIR}/frontend" ]; then
        log_info "Cleaning frontend build artifacts..."

        cd "${APP_DIR}/frontend" || die "Failed to change to frontend directory"

        if [ -d "dist" ]; then
            rm -rf dist
            log_success "Removed frontend dist directory"
        fi

        if [ -d "coverage" ]; then
            rm -rf coverage
            log_success "Removed frontend coverage directory"
        fi

        cd "$PROJECT_ROOT" || die "Failed to return to project root"
    fi

    # Clean Playwright artifacts
    if [ -d "${PROJECT_ROOT}/playwright-tests" ]; then
        log_info "Cleaning Playwright test artifacts..."

        cd "${PROJECT_ROOT}/playwright-tests" || die "Failed to change to playwright directory"

        if [ -d "test-results" ]; then
            rm -rf test-results
            log_success "Removed test-results directory"
        fi

        if [ -d "playwright-report" ]; then
            rm -rf playwright-report
            log_success "Removed playwright-report directory"
        fi

        cd "$PROJECT_ROOT" || die "Failed to return to project root"
    fi

    log_success "Build artifacts cleaned"
}

# ==============================================================================
# CLEAR CACHES
# ==============================================================================

clear_caches() {
    if [ "$CACHE" = false ] && [ "$ALL" = false ]; then
        return 0
    fi

    print_header "Clearing Build Caches"

    # Clear Maven cache (optional)
    if [ -d "$HOME/.m2/repository" ]; then
        log_info "Maven cache location: $HOME/.m2/repository"
        log_info "Skipping Maven cache cleanup (use manually if needed)"
    fi

    # Clear npm cache
    if check_command npm; then
        log_info "Clearing npm cache..."
        npm cache clean --force 2>/dev/null || log_warning "Failed to clear npm cache"
        log_success "npm cache cleared"
    fi

    # Clear frontend node_modules (optional)
    if [ -d "${APP_DIR}/frontend/node_modules" ]; then
        log_info "Removing frontend node_modules..."
        rm -rf "${APP_DIR}/frontend/node_modules"
        log_success "Frontend node_modules removed"
    fi

    # Clear Playwright node_modules
    if [ -d "${PROJECT_ROOT}/playwright-tests/node_modules" ]; then
        log_info "Removing Playwright node_modules..."
        rm -rf "${PROJECT_ROOT}/playwright-tests/node_modules"
        log_success "Playwright node_modules removed"
    fi

    log_success "Caches cleared"
}

# ==============================================================================
# RESET DATABASE
# ==============================================================================

reset_database() {
    if [ "$RESET_DB" = false ]; then
        return 0
    fi

    print_header "Resetting Database"

    log_info "Removing PostgreSQL volume..."

    if podman volume exists "orgmgmt-postgres-data" 2>/dev/null; then
        podman volume rm "orgmgmt-postgres-data" 2>/dev/null || log_warning "Failed to remove database volume"
        log_success "Database volume removed"
    else
        log_info "Database volume does not exist"
    fi

    log_success "Database reset complete"
}

# ==============================================================================
# DISPLAY CLEANUP SUMMARY
# ==============================================================================

display_cleanup_summary() {
    print_header "Cleanup Summary"

    local items_cleaned=()

    items_cleaned+=("Containers stopped")

    if [ "$VOLUMES" = true ] || [ "$ALL" = true ]; then
        items_cleaned+=("Volumes removed")
    fi

    if [ "$ARTIFACTS" = true ] || [ "$ALL" = true ]; then
        items_cleaned+=("Build artifacts cleaned")
    fi

    if [ "$CACHE" = true ] || [ "$ALL" = true ]; then
        items_cleaned+=("Caches cleared")
    fi

    if [ "$RESET_DB" = true ]; then
        items_cleaned+=("Database reset")
    fi

    echo ""
    for item in "${items_cleaned[@]}"; do
        echo -e "  ${GREEN}✓${NC} $item"
    done
    echo ""

    log_success "Cleanup completed successfully!"
    echo ""

    if [ "$ALL" = true ] || [ "$VOLUMES" = true ]; then
        echo -e "${YELLOW}Note:${NC} All data has been removed. Run setup.sh to reinitialize."
    else
        echo -e "${YELLOW}Note:${NC} Run 'podman-compose up -d' to restart services."
    fi

    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "Environment Cleanup"

    confirm_cleanup
    stop_containers
    remove_volumes
    clean_build_artifacts
    clear_caches
    reset_database
    display_cleanup_summary
}

main "$@"
