#!/bin/bash
#
# backup.sh - Backup Script
#
# This script creates backups of:
# - PostgreSQL database
# - Nexus data
# - GitLab data
# - GitOps manifests
# - Configuration files
#
# Usage: ./backup.sh [OPTIONS]
#
# Options:
#   --output-dir DIR     Backup output directory (default: ./backups)
#   --compress           Compress backup archives
#   --databases-only     Backup databases only
#   --no-volumes        Skip volume backups
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

OUTPUT_DIR="${PROJECT_ROOT}/backups"
COMPRESS=true
DATABASES_ONLY=false
NO_VOLUMES=false

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="argocd-backup-${TIMESTAMP}"

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Backup Script

Usage: $(basename "$0") [OPTIONS]

Create backups of databases, volumes, and configuration files.

Options:
    --output-dir DIR    Backup output directory (default: ./backups)
    --compress          Compress backup archives (default)
    --databases-only    Backup databases only
    --no-volumes       Skip volume backups
    -h, --help         Show this help message

Examples:
    $(basename "$0")                                    # Full backup
    $(basename "$0") --databases-only                   # Database backup only
    $(basename "$0") --output-dir /mnt/backups          # Custom backup location

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --output-dir)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            --compress)
                COMPRESS=true
                shift
                ;;
            --databases-only)
                DATABASES_ONLY=true
                NO_VOLUMES=true
                shift
                ;;
            --no-volumes)
                NO_VOLUMES=true
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
# PREPARE BACKUP DIRECTORY
# ==============================================================================

prepare_backup_directory() {
    print_header "Preparing Backup Directory"

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Create backup subdirectory
    BACKUP_DIR="${OUTPUT_DIR}/${BACKUP_NAME}"
    mkdir -p "$BACKUP_DIR"

    log_success "Backup directory created: $BACKUP_DIR"
}

# ==============================================================================
# BACKUP POSTGRESQL
# ==============================================================================

backup_postgresql() {
    print_header "Backing Up PostgreSQL Database"

    # Check if PostgreSQL is running
    if ! is_container_running "orgmgmt-postgres"; then
        log_warning "PostgreSQL container is not running, skipping database backup"
        return 0
    fi

    log_info "Dumping PostgreSQL database..."

    local db_backup_file="${BACKUP_DIR}/postgres-dump.sql"

    # Perform database dump
    podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > "$db_backup_file"

    if [ $? -eq 0 ]; then
        local file_size=$(du -h "$db_backup_file" | cut -f1)
        log_success "PostgreSQL backup created: ${db_backup_file} (${file_size})"
    else
        log_error "Failed to backup PostgreSQL database"
        return 1
    fi
}

# ==============================================================================
# BACKUP NEXUS DATA
# ==============================================================================

backup_nexus_data() {
    if [ "$NO_VOLUMES" = true ]; then
        log_info "Skipping Nexus data backup (--no-volumes)"
        return 0
    fi

    print_header "Backing Up Nexus Data"

    # Check if Nexus is running
    if ! is_container_running "orgmgmt-nexus"; then
        log_warning "Nexus container is not running, skipping Nexus backup"
        return 0
    fi

    log_info "Backing up Nexus data volume..."

    local nexus_backup_dir="${BACKUP_DIR}/nexus-data"
    mkdir -p "$nexus_backup_dir"

    # Copy Nexus data from volume
    podman cp orgmgmt-nexus:/nexus-data "$nexus_backup_dir/"

    if [ $? -eq 0 ]; then
        local dir_size=$(du -sh "$nexus_backup_dir" | cut -f1)
        log_success "Nexus data backed up: ${nexus_backup_dir} (${dir_size})"
    else
        log_warning "Failed to backup Nexus data"
    fi
}

# ==============================================================================
# BACKUP GITLAB DATA
# ==============================================================================

backup_gitlab_data() {
    if [ "$NO_VOLUMES" = true ]; then
        log_info "Skipping GitLab data backup (--no-volumes)"
        return 0
    fi

    print_header "Backing Up GitLab Data"

    # Check if GitLab is running
    if ! is_container_running "orgmgmt-gitlab"; then
        log_warning "GitLab container is not running, skipping GitLab backup"
        return 0
    fi

    log_info "Creating GitLab backup..."

    local gitlab_backup_dir="${BACKUP_DIR}/gitlab-data"
    mkdir -p "$gitlab_backup_dir"

    # Trigger GitLab backup
    log_info "Running GitLab backup command (this may take a while)..."

    podman exec orgmgmt-gitlab gitlab-backup create

    # Copy backup files from GitLab container
    podman cp orgmgmt-gitlab:/var/opt/gitlab/backups "$gitlab_backup_dir/"

    if [ $? -eq 0 ]; then
        local dir_size=$(du -sh "$gitlab_backup_dir" | cut -f1)
        log_success "GitLab data backed up: ${gitlab_backup_dir} (${dir_size})"
    else
        log_warning "Failed to backup GitLab data"
    fi
}

# ==============================================================================
# BACKUP GITOPS MANIFESTS
# ==============================================================================

backup_gitops_manifests() {
    if [ "$DATABASES_ONLY" = true ]; then
        log_info "Skipping GitOps manifests backup (--databases-only)"
        return 0
    fi

    print_header "Backing Up GitOps Manifests"

    log_info "Copying GitOps manifests..."

    local gitops_backup_dir="${BACKUP_DIR}/gitops"

    cp -r "${GITOPS_DIR}" "$gitops_backup_dir"

    if [ $? -eq 0 ]; then
        local dir_size=$(du -sh "$gitops_backup_dir" | cut -f1)
        log_success "GitOps manifests backed up: ${gitops_backup_dir} (${dir_size})"
    else
        log_warning "Failed to backup GitOps manifests"
    fi
}

# ==============================================================================
# BACKUP CONFIGURATION FILES
# ==============================================================================

backup_configuration() {
    if [ "$DATABASES_ONLY" = true ]; then
        log_info "Skipping configuration backup (--databases-only)"
        return 0
    fi

    print_header "Backing Up Configuration Files"

    log_info "Copying configuration files..."

    local config_backup_dir="${BACKUP_DIR}/config"
    mkdir -p "$config_backup_dir"

    # Backup .env file
    if [ -f "${INFRASTRUCTURE_DIR}/.env" ]; then
        cp "${INFRASTRUCTURE_DIR}/.env" "${config_backup_dir}/infrastructure.env"
        log_success "Backed up infrastructure .env file"
    fi

    # Backup infrastructure config
    if [ -d "${INFRASTRUCTURE_DIR}/config" ]; then
        cp -r "${INFRASTRUCTURE_DIR}/config" "${config_backup_dir}/infrastructure"
        log_success "Backed up infrastructure configuration"
    fi

    # Backup credentials file if it exists
    if [ -f "${PROJECT_ROOT}/credentials.txt" ]; then
        cp "${PROJECT_ROOT}/credentials.txt" "${config_backup_dir}/"
        log_success "Backed up credentials file"
    fi

    local dir_size=$(du -sh "$config_backup_dir" | cut -f1)
    log_success "Configuration backed up: ${config_backup_dir} (${dir_size})"
}

# ==============================================================================
# CREATE BACKUP METADATA
# ==============================================================================

create_backup_metadata() {
    print_header "Creating Backup Metadata"

    local metadata_file="${BACKUP_DIR}/backup-metadata.txt"

    cat > "$metadata_file" << EOF
========================================
  Backup Metadata
========================================
Backup Name:     ${BACKUP_NAME}
Created:         $(date)
Hostname:        $(hostname)
Project Root:    ${PROJECT_ROOT}

Backup Contents:
----------------
EOF

    # List backed up components
    if [ -f "${BACKUP_DIR}/postgres-dump.sql" ]; then
        echo "✓ PostgreSQL Database" >> "$metadata_file"
    fi

    if [ -d "${BACKUP_DIR}/nexus-data" ]; then
        echo "✓ Nexus Data" >> "$metadata_file"
    fi

    if [ -d "${BACKUP_DIR}/gitlab-data" ]; then
        echo "✓ GitLab Data" >> "$metadata_file"
    fi

    if [ -d "${BACKUP_DIR}/gitops" ]; then
        echo "✓ GitOps Manifests" >> "$metadata_file"
    fi

    if [ -d "${BACKUP_DIR}/config" ]; then
        echo "✓ Configuration Files" >> "$metadata_file"
    fi

    echo "" >> "$metadata_file"
    echo "========================================" >> "$metadata_file"

    log_success "Backup metadata created"
}

# ==============================================================================
# COMPRESS BACKUP
# ==============================================================================

compress_backup() {
    if [ "$COMPRESS" = false ]; then
        log_info "Skipping compression"
        return 0
    fi

    print_header "Compressing Backup"

    log_info "Creating compressed archive..."

    cd "$OUTPUT_DIR" || die "Failed to change to output directory"

    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"

    if [ $? -eq 0 ]; then
        local archive_size=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
        log_success "Backup compressed: ${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz (${archive_size})"

        # Remove uncompressed directory
        rm -rf "$BACKUP_NAME"
        log_info "Removed uncompressed backup directory"
    else
        log_error "Failed to compress backup"
        return 1
    fi

    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# DISPLAY BACKUP SUMMARY
# ==============================================================================

display_backup_summary() {
    print_header "Backup Summary"

    local backup_location

    if [ "$COMPRESS" = true ]; then
        backup_location="${OUTPUT_DIR}/${BACKUP_NAME}.tar.gz"
    else
        backup_location="${BACKUP_DIR}"
    fi

    # Calculate total size
    local total_size=$(du -sh "$backup_location" | cut -f1)

    print_summary \
        "Backup Name:${BACKUP_NAME}" \
        "Location:${backup_location}" \
        "Size:${total_size}" \
        "Created:$(date)"

    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Backup Location:${NC}"
    echo -e "  ${CYAN}${backup_location}${NC}"
    echo ""
    echo -e "${YELLOW}To restore from this backup:${NC}"
    echo -e "  ${CYAN}./scripts/restore.sh ${backup_location}${NC}"
    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "Backup - ArgoCD Project"

    log_info "Starting backup process..."
    log_info "Timestamp: $TIMESTAMP"

    prepare_backup_directory
    backup_postgresql
    backup_nexus_data
    backup_gitlab_data
    backup_gitops_manifests
    backup_configuration
    create_backup_metadata
    compress_backup
    display_backup_summary
}

main "$@"
