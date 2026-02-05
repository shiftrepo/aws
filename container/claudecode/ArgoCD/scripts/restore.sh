#!/bin/bash
#
# restore.sh - Restore Script
#
# This script restores from backups including:
# - PostgreSQL database
# - Nexus data
# - GitLab data
# - GitOps manifests
# - Configuration files
#
# Usage: ./restore.sh BACKUP_FILE [OPTIONS]
#
# Options:
#   --database-only      Restore database only
#   --config-only        Restore configuration only
#   --no-restart        Don't restart services
#   --force             Skip confirmation prompts
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

BACKUP_FILE=""
DATABASE_ONLY=false
CONFIG_ONLY=false
NO_RESTART=false
FORCE=false

RESTORE_TEMP_DIR="${PROJECT_ROOT}/.restore-tmp"

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Restore Script

Usage: $(basename "$0") BACKUP_FILE [OPTIONS]

Restore from a backup archive or directory.

Arguments:
    BACKUP_FILE         Path to backup archive (.tar.gz) or directory

Options:
    --database-only     Restore database only
    --config-only       Restore configuration only
    --no-restart       Don't restart services
    --force            Skip confirmation prompts
    -h, --help         Show this help message

Examples:
    $(basename "$0") backups/argocd-backup-20240101-120000.tar.gz
    $(basename "$0") backups/argocd-backup-20240101-120000 --database-only
    $(basename "$0") backups/argocd-backup-20240101-120000.tar.gz --force

WARNING: Restore will overwrite existing data!

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    if [ $# -eq 0 ]; then
        log_error "Backup file is required"
        show_usage
        exit 1
    fi

    BACKUP_FILE="$1"
    shift

    while [[ $# -gt 0 ]]; do
        case $1 in
            --database-only)
                DATABASE_ONLY=true
                shift
                ;;
            --config-only)
                CONFIG_ONLY=true
                shift
                ;;
            --no-restart)
                NO_RESTART=true
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
}

# ==============================================================================
# VALIDATE BACKUP
# ==============================================================================

validate_backup() {
    print_header "Validating Backup"

    # Check if backup exists
    if [ ! -e "$BACKUP_FILE" ]; then
        die "Backup not found: $BACKUP_FILE"
    fi

    log_info "Backup file: $BACKUP_FILE"

    # Check if it's a file or directory
    if [ -f "$BACKUP_FILE" ]; then
        # Assume it's a tar.gz archive
        if [[ ! "$BACKUP_FILE" =~ \.tar\.gz$ ]]; then
            log_warning "Backup file doesn't have .tar.gz extension"
        fi

        log_info "Backup type: Archive"
    elif [ -d "$BACKUP_FILE" ]; then
        log_info "Backup type: Directory"
    else
        die "Backup is neither a file nor directory"
    fi

    log_success "Backup validated"
}

# ==============================================================================
# EXTRACT BACKUP
# ==============================================================================

extract_backup() {
    print_header "Extracting Backup"

    # Clean up any existing temp directory
    if [ -d "$RESTORE_TEMP_DIR" ]; then
        rm -rf "$RESTORE_TEMP_DIR"
    fi

    mkdir -p "$RESTORE_TEMP_DIR"

    if [ -f "$BACKUP_FILE" ]; then
        log_info "Extracting backup archive..."

        tar -xzf "$BACKUP_FILE" -C "$RESTORE_TEMP_DIR"

        if [ $? -eq 0 ]; then
            log_success "Backup extracted"

            # Find the backup directory
            local backup_dir=$(find "$RESTORE_TEMP_DIR" -maxdepth 1 -type d -name "argocd-backup-*" | head -1)

            if [ -z "$backup_dir" ]; then
                die "Could not find backup directory in archive"
            fi

            BACKUP_DIR="$backup_dir"
        else
            die "Failed to extract backup"
        fi
    else
        # It's already a directory
        BACKUP_DIR="$BACKUP_FILE"
        log_info "Using backup directory: $BACKUP_DIR"
    fi

    # Validate backup contents
    if [ ! -f "${BACKUP_DIR}/backup-metadata.txt" ]; then
        log_warning "Backup metadata not found"
    else
        log_info "Backup metadata:"
        cat "${BACKUP_DIR}/backup-metadata.txt"
    fi
}

# ==============================================================================
# CONFIRM RESTORE
# ==============================================================================

confirm_restore() {
    if [ "$FORCE" = true ]; then
        log_warning "Force mode enabled - skipping confirmation"
        return 0
    fi

    print_header "Restore Confirmation"

    log_warning "This operation will overwrite existing data!"
    echo ""

    if [ "$DATABASE_ONLY" = true ]; then
        echo -e "  ${RED}• Database will be restored${NC}"
    elif [ "$CONFIG_ONLY" = true ]; then
        echo -e "  ${RED}• Configuration will be restored${NC}"
    else
        echo -e "  ${RED}• All data will be restored${NC}"
        echo -e "  ${RED}• Existing data will be lost${NC}"
    fi

    echo ""

    if [ -t 0 ]; then
        read -p "$(echo -e ${YELLOW}Are you sure you want to proceed? [y/N]: ${NC})" -n 1 -r
        echo ""

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Restore cancelled by user"
            exit 0
        fi
    else
        log_warning "Non-interactive mode - proceeding with restore"
    fi
}

# ==============================================================================
# RESTORE POSTGRESQL
# ==============================================================================

restore_postgresql() {
    if [ "$CONFIG_ONLY" = true ]; then
        log_info "Skipping database restore (--config-only)"
        return 0
    fi

    print_header "Restoring PostgreSQL Database"

    local db_dump="${BACKUP_DIR}/postgres-dump.sql"

    if [ ! -f "$db_dump" ]; then
        log_warning "PostgreSQL dump not found in backup"
        return 0
    fi

    # Check if PostgreSQL is running
    if ! is_container_running "orgmgmt-postgres"; then
        log_error "PostgreSQL container is not running"
        log_info "Start infrastructure first: cd ${INFRASTRUCTURE_DIR} && podman-compose up -d postgres"
        return 1
    fi

    log_info "Restoring database from dump..."

    # Drop and recreate database
    podman exec orgmgmt-postgres psql -U orgmgmt_user -d postgres -c "DROP DATABASE IF EXISTS orgmgmt;"
    podman exec orgmgmt-postgres psql -U orgmgmt_user -d postgres -c "CREATE DATABASE orgmgmt;"

    # Restore database
    podman exec -i orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt < "$db_dump"

    if [ $? -eq 0 ]; then
        log_success "PostgreSQL database restored"
    else
        log_error "Failed to restore PostgreSQL database"
        return 1
    fi
}

# ==============================================================================
# RESTORE NEXUS DATA
# ==============================================================================

restore_nexus_data() {
    if [ "$CONFIG_ONLY" = true ] || [ "$DATABASE_ONLY" = true ]; then
        log_info "Skipping Nexus data restore"
        return 0
    fi

    print_header "Restoring Nexus Data"

    local nexus_backup="${BACKUP_DIR}/nexus-data"

    if [ ! -d "$nexus_backup" ]; then
        log_warning "Nexus data not found in backup"
        return 0
    fi

    # Check if Nexus is running
    if ! is_container_running "orgmgmt-nexus"; then
        log_warning "Nexus container is not running, skipping Nexus restore"
        return 0
    fi

    log_info "Stopping Nexus container..."
    podman stop orgmgmt-nexus

    log_info "Restoring Nexus data..."

    # Remove existing data and restore
    podman exec orgmgmt-nexus rm -rf /nexus-data/*
    podman cp "${nexus_backup}/nexus-data/." orgmgmt-nexus:/nexus-data/

    if [ $? -eq 0 ]; then
        log_success "Nexus data restored"

        log_info "Starting Nexus container..."
        podman start orgmgmt-nexus
    else
        log_error "Failed to restore Nexus data"
        return 1
    fi
}

# ==============================================================================
# RESTORE GITLAB DATA
# ==============================================================================

restore_gitlab_data() {
    if [ "$CONFIG_ONLY" = true ] || [ "$DATABASE_ONLY" = true ]; then
        log_info "Skipping GitLab data restore"
        return 0
    fi

    print_header "Restoring GitLab Data"

    local gitlab_backup="${BACKUP_DIR}/gitlab-data"

    if [ ! -d "$gitlab_backup" ]; then
        log_warning "GitLab data not found in backup"
        return 0
    fi

    # Check if GitLab is running
    if ! is_container_running "orgmgmt-gitlab"; then
        log_warning "GitLab container is not running, skipping GitLab restore"
        return 0
    fi

    log_info "Restoring GitLab backup files..."

    # Copy backup files to GitLab container
    podman cp "${gitlab_backup}/backups/." orgmgmt-gitlab:/var/opt/gitlab/backups/

    # Find the backup timestamp
    local backup_file=$(podman exec orgmgmt-gitlab ls -t /var/opt/gitlab/backups/ | grep "_gitlab_backup.tar$" | head -1)

    if [ -n "$backup_file" ]; then
        local backup_timestamp=$(echo "$backup_file" | sed 's/_gitlab_backup.tar//')

        log_info "Restoring GitLab from backup: $backup_timestamp"

        # Stop GitLab services
        podman exec orgmgmt-gitlab gitlab-ctl stop unicorn
        podman exec orgmgmt-gitlab gitlab-ctl stop puma
        podman exec orgmgmt-gitlab gitlab-ctl stop sidekiq

        # Restore
        podman exec orgmgmt-gitlab gitlab-backup restore BACKUP="$backup_timestamp" force=yes

        # Restart GitLab
        podman exec orgmgmt-gitlab gitlab-ctl restart

        log_success "GitLab data restored"
    else
        log_error "No GitLab backup file found"
        return 1
    fi
}

# ==============================================================================
# RESTORE GITOPS MANIFESTS
# ==============================================================================

restore_gitops_manifests() {
    if [ "$DATABASE_ONLY" = true ]; then
        log_info "Skipping GitOps manifests restore (--database-only)"
        return 0
    fi

    print_header "Restoring GitOps Manifests"

    local gitops_backup="${BACKUP_DIR}/gitops"

    if [ ! -d "$gitops_backup" ]; then
        log_warning "GitOps manifests not found in backup"
        return 0
    fi

    log_info "Restoring GitOps manifests..."

    # Backup current manifests
    if [ -d "$GITOPS_DIR" ]; then
        local backup_current="${GITOPS_DIR}.backup-$(date +%Y%m%d-%H%M%S)"
        mv "$GITOPS_DIR" "$backup_current"
        log_info "Current manifests backed up to: $backup_current"
    fi

    # Restore manifests
    cp -r "$gitops_backup" "$GITOPS_DIR"

    if [ $? -eq 0 ]; then
        log_success "GitOps manifests restored"
    else
        log_error "Failed to restore GitOps manifests"
        return 1
    fi
}

# ==============================================================================
# RESTORE CONFIGURATION
# ==============================================================================

restore_configuration() {
    if [ "$DATABASE_ONLY" = true ]; then
        log_info "Skipping configuration restore (--database-only)"
        return 0
    fi

    print_header "Restoring Configuration Files"

    local config_backup="${BACKUP_DIR}/config"

    if [ ! -d "$config_backup" ]; then
        log_warning "Configuration files not found in backup"
        return 0
    fi

    log_info "Restoring configuration files..."

    # Restore .env file
    if [ -f "${config_backup}/infrastructure.env" ]; then
        cp "${config_backup}/infrastructure.env" "${INFRASTRUCTURE_DIR}/.env"
        log_success "Restored infrastructure .env file"
    fi

    # Restore infrastructure config
    if [ -d "${config_backup}/infrastructure" ]; then
        cp -r "${config_backup}/infrastructure/." "${INFRASTRUCTURE_DIR}/config/"
        log_success "Restored infrastructure configuration"
    fi

    # Restore credentials file
    if [ -f "${config_backup}/credentials.txt" ]; then
        cp "${config_backup}/credentials.txt" "${PROJECT_ROOT}/"
        log_success "Restored credentials file"
    fi

    log_success "Configuration restored"
}

# ==============================================================================
# RESTART SERVICES
# ==============================================================================

restart_services() {
    if [ "$NO_RESTART" = true ]; then
        log_info "Skipping service restart (--no-restart)"
        return 0
    fi

    print_header "Restarting Services"

    log_info "Restarting affected services..."

    cd "$INFRASTRUCTURE_DIR" || die "Failed to change to infrastructure directory"

    podman-compose restart

    if [ $? -eq 0 ]; then
        log_success "Services restarted"
    else
        log_warning "Some services may not have restarted cleanly"
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# VERIFY RESTORE
# ==============================================================================

verify_restore() {
    print_header "Verifying Restore"

    log_info "Running basic health checks..."

    # Check PostgreSQL
    if check_postgres; then
        log_success "PostgreSQL is healthy"
    else
        log_warning "PostgreSQL health check failed"
    fi

    # Give services time to start
    sleep 5

    log_info "Restore verification complete"
    log_warning "Please manually verify data integrity"
}

# ==============================================================================
# CLEANUP
# ==============================================================================

cleanup_temp_files() {
    if [ -d "$RESTORE_TEMP_DIR" ]; then
        log_info "Cleaning up temporary files..."
        rm -rf "$RESTORE_TEMP_DIR"
    fi
}

# ==============================================================================
# DISPLAY RESTORE SUMMARY
# ==============================================================================

display_restore_summary() {
    print_summary \
        "Backup File:${BACKUP_FILE}" \
        "Database:$([ "$CONFIG_ONLY" = false ] && echo "Restored" || echo "Skipped")" \
        "Configuration:$([ "$DATABASE_ONLY" = false ] && echo "Restored" || echo "Skipped")" \
        "Services:$([ "$NO_RESTART" = false ] && echo "Restarted" || echo "Not Restarted")"

    echo -e "${GREEN}✓ Restore completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Verify services: ${CYAN}./scripts/status.sh${NC}"
    echo -e "  2. Check logs: ${CYAN}./scripts/logs.sh${NC}"
    echo -e "  3. Test application functionality"
    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "Restore - ArgoCD Project"

    validate_backup
    extract_backup
    confirm_restore
    restore_postgresql
    restore_nexus_data
    restore_gitlab_data
    restore_gitops_manifests
    restore_configuration
    restart_services
    verify_restore
    cleanup_temp_files
    display_restore_summary
}

# Trap to ensure cleanup on exit
trap cleanup_temp_files EXIT

main "$@"
