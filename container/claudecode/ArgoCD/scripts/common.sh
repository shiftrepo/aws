#!/bin/bash
#
# common.sh - Shared functions and utilities for automation scripts
#
# This file contains common functions used across multiple automation scripts
# including color definitions, logging utilities, error handling, and service checks.
#

# ==============================================================================
# COLOR DEFINITIONS
# ==============================================================================

# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==============================================================================
# LOGGING FUNCTIONS
# ==============================================================================

# Print an informational message with timestamp
# Arguments:
#   $1 - Message to print
log_info() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} ${1}"
}

# Print a success message with timestamp
# Arguments:
#   $1 - Message to print
log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} ${1}"
}

# Print a warning message with timestamp
# Arguments:
#   $1 - Message to print
log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} ${1}"
}

# Print an error message with timestamp to stderr
# Arguments:
#   $1 - Message to print
log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} ${1}" >&2
}

# Print a header/section title
# Arguments:
#   $1 - Header text
print_header() {
    echo ""
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}  ${1}${NC}"
    echo -e "${MAGENTA}========================================${NC}"
    echo ""
}

# Print a step message
# Arguments:
#   $1 - Step number
#   $2 - Step description
print_step() {
    echo -e "${BLUE}[Step $1]${NC} ${2}"
}

# ==============================================================================
# ERROR HANDLING
# ==============================================================================

# Exit with error message
# Arguments:
#   $1 - Error message
#   $2 - Exit code (optional, default: 1)
die() {
    log_error "$1"
    exit "${2:-1}"
}

# Handle script errors
error_handler() {
    local line_no=$1
    log_error "Script failed at line ${line_no}"
    exit 1
}

# ==============================================================================
# PREREQUISITE CHECKS
# ==============================================================================

# Check if a command exists
# Arguments:
#   $1 - Command name
check_command() {
    if ! command -v "$1" &> /dev/null; then
        return 1
    fi
    return 0
}

# Verify required commands are available
# Arguments:
#   $@ - List of required commands
check_prerequisites() {
    local missing=()

    for cmd in "$@"; do
        if ! check_command "$cmd"; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required commands: ${missing[*]}"
        log_info "Please install missing dependencies and try again"
        return 1
    fi

    log_success "All prerequisites are available"
    return 0
}

# ==============================================================================
# SYSTEM CHECKS
# ==============================================================================

# Check if system has minimum required memory
# Arguments:
#   $1 - Minimum memory in GB (default: 4)
check_memory() {
    local min_memory_gb=${1:-4}
    local min_memory_kb=$((min_memory_gb * 1024 * 1024))

    if [ -f /proc/meminfo ]; then
        local total_memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')

        if [ "$total_memory_kb" -lt "$min_memory_kb" ]; then
            log_warning "System has less than ${min_memory_gb}GB RAM. This may cause performance issues."
            return 1
        fi
    fi

    return 0
}

# Check if system has minimum required disk space
# Arguments:
#   $1 - Path to check (default: current directory)
#   $2 - Minimum space in GB (default: 10)
check_disk_space() {
    local path=${1:-$(pwd)}
    local min_space_gb=${2:-10}

    local available_gb=$(df -BG "$path" | tail -1 | awk '{print $4}' | sed 's/G//')

    if [ "$available_gb" -lt "$min_space_gb" ]; then
        log_warning "Available disk space (${available_gb}GB) is less than recommended (${min_space_gb}GB)"
        return 1
    fi

    return 0
}

# ==============================================================================
# SERVICE HEALTH CHECKS
# ==============================================================================

# Wait for a service to be healthy
# Arguments:
#   $1 - Service name
#   $2 - Health check command
#   $3 - Max retries (default: 30)
#   $4 - Retry interval in seconds (default: 10)
wait_for_service() {
    local service_name=$1
    local health_check=$2
    local max_retries=${3:-30}
    local retry_interval=${4:-10}
    local retries=0

    log_info "Waiting for ${service_name} to be ready..."

    while [ $retries -lt $max_retries ]; do
        if eval "$health_check" &> /dev/null; then
            log_success "${service_name} is ready"
            return 0
        fi

        retries=$((retries + 1))
        echo -ne "${YELLOW}Attempt ${retries}/${max_retries}...${NC}\r"
        sleep "$retry_interval"
    done

    log_error "${service_name} failed to become ready after ${max_retries} attempts"
    return 1
}

# Check if PostgreSQL is ready
# Arguments:
#   $1 - Host (default: localhost)
#   $2 - Port (default: 5432)
#   $3 - User (default: orgmgmt_user)
#   $4 - Database (default: orgmgmt)
check_postgres() {
    local host=${1:-localhost}
    local port=${2:-5432}
    local user=${3:-orgmgmt_user}
    local db=${4:-orgmgmt}

    if check_command pg_isready; then
        pg_isready -h "$host" -p "$port" -U "$user" -d "$db" &> /dev/null
        return $?
    else
        # Fallback to podman exec if pg_isready not available
        podman exec orgmgmt-postgres pg_isready -U "$user" -d "$db" &> /dev/null
        return $?
    fi
}

# Check if a HTTP service is ready
# Arguments:
#   $1 - URL to check
#   $2 - Expected HTTP status code (default: 200)
check_http_service() {
    local url=$1
    local expected_status=${2:-200}

    local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$status" = "$expected_status" ]; then
        return 0
    fi

    return 1
}

# Check if Nexus is ready
# Arguments:
#   $1 - Host (default: localhost)
#   $2 - Port (default: 8081)
check_nexus() {
    local host=${1:-localhost}
    local port=${2:-8081}
    check_http_service "http://${host}:${port}/service/rest/v1/status"
}

# Check if GitLab is ready
# Arguments:
#   $1 - Host (default: localhost)
#   $2 - Port (default: 5003)
check_gitlab() {
    local host=${1:-localhost}
    local port=${2:-5003}
    check_http_service "http://${host}:${port}/-/health"
}

# Check if ArgoCD is ready
# Arguments:
#   $1 - Host (default: localhost)
#   $2 - Port (default: 5010)
check_argocd() {
    local host=${1:-localhost}
    local port=${2:-5010}
    check_http_service "http://${host}:${port}/healthz"
}

# ==============================================================================
# CONTAINER/PODMAN UTILITIES
# ==============================================================================

# Check if a container is running
# Arguments:
#   $1 - Container name
is_container_running() {
    local container_name=$1
    podman ps --filter "name=${container_name}" --format "{{.Names}}" | grep -q "^${container_name}$"
    return $?
}

# Get container status
# Arguments:
#   $1 - Container name
get_container_status() {
    local container_name=$1
    podman ps -a --filter "name=${container_name}" --format "{{.Status}}" 2>/dev/null | head -1
}

# Check if all services in compose file are running
# Arguments:
#   $1 - Path to compose file directory
check_compose_services() {
    local compose_dir=$1

    if [ ! -f "${compose_dir}/podman-compose.yml" ]; then
        log_error "Compose file not found: ${compose_dir}/podman-compose.yml"
        return 1
    fi

    cd "$compose_dir" || return 1

    # Get list of services
    local services=$(podman-compose ps --services 2>/dev/null)
    local all_running=true

    for service in $services; do
        if ! is_container_running "$service"; then
            log_warning "Service not running: $service"
            all_running=false
        fi
    done

    if [ "$all_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# ==============================================================================
# FILE UTILITIES
# ==============================================================================

# Generate a random password
# Arguments:
#   $1 - Password length (default: 16)
generate_password() {
    local length=${1:-16}
    openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-"$length"
}

# Load environment variables from .env file
# Arguments:
#   $1 - Path to .env file
load_env_file() {
    local env_file=$1

    if [ ! -f "$env_file" ]; then
        log_error "Environment file not found: $env_file"
        return 1
    fi

    # Export all variables from .env file
    set -a
    source "$env_file"
    set +a

    log_success "Loaded environment from: $env_file"
    return 0
}

# ==============================================================================
# ARGOCD UTILITIES
# ==============================================================================

# Login to ArgoCD
# Arguments:
#   $1 - ArgoCD server URL (default: localhost:5010)
#   $2 - Username (default: admin)
#   $3 - Password (will try to read from env or get from pod)
argocd_login() {
    local server=${1:-localhost:5010}
    local username=${2:-admin}
    local password=$3

    # If password not provided, try to get it
    if [ -z "$password" ]; then
        if [ -n "$ARGOCD_ADMIN_PASSWORD" ]; then
            password="$ARGOCD_ADMIN_PASSWORD"
        else
            password=$(podman exec argocd-server argocd admin initial-password 2>/dev/null | head -1)
        fi
    fi

    if [ -z "$password" ]; then
        log_error "Unable to determine ArgoCD password"
        return 1
    fi

    argocd login "$server" --username "$username" --password "$password" --insecure &> /dev/null

    if [ $? -eq 0 ]; then
        log_success "Logged in to ArgoCD"
        return 0
    else
        log_error "Failed to login to ArgoCD"
        return 1
    fi
}

# ==============================================================================
# PROGRESS INDICATORS
# ==============================================================================

# Show a spinner while a command runs
# Arguments:
#   $1 - PID of background process
#   $2 - Message to display
show_spinner() {
    local pid=$1
    local message=${2:-"Processing..."}
    local spin='-\|/'
    local i=0

    while kill -0 "$pid" 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r${CYAN}${message} ${spin:$i:1}${NC}"
        sleep .1
    done

    printf "\r"
}

# ==============================================================================
# SUMMARY UTILITIES
# ==============================================================================

# Print a summary table
# Arguments:
#   $@ - Array of "key:value" pairs
print_summary() {
    local max_key_length=0

    # Find longest key for alignment
    for item in "$@"; do
        local key="${item%%:*}"
        if [ ${#key} -gt $max_key_length ]; then
            max_key_length=${#key}
        fi
    done

    echo ""
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}  SUMMARY${NC}"
    echo -e "${MAGENTA}========================================${NC}"

    for item in "$@"; do
        local key="${item%%:*}"
        local value="${item#*:}"
        printf "  ${CYAN}%-${max_key_length}s${NC} : %s\n" "$key" "$value"
    done

    echo -e "${MAGENTA}========================================${NC}"
    echo ""
}

# ==============================================================================
# VALIDATION UTILITIES
# ==============================================================================

# Validate environment variable is set
# Arguments:
#   $1 - Variable name
#   $2 - Error message (optional)
validate_env_var() {
    local var_name=$1
    local error_msg=${2:-"Required environment variable not set: $var_name"}

    if [ -z "${!var_name}" ]; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# Validate file exists
# Arguments:
#   $1 - File path
#   $2 - Error message (optional)
validate_file() {
    local file_path=$1
    local error_msg=${2:-"Required file not found: $file_path"}

    if [ ! -f "$file_path" ]; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# Validate directory exists
# Arguments:
#   $1 - Directory path
#   $2 - Error message (optional)
validate_directory() {
    local dir_path=$1
    local error_msg=${2:-"Required directory not found: $dir_path"}

    if [ ! -d "$dir_path" ]; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# ==============================================================================
# INITIALIZATION
# ==============================================================================

# Get the project root directory (parent of scripts directory)
get_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

# Export the project root
export PROJECT_ROOT=$(get_project_root)
export INFRASTRUCTURE_DIR="${PROJECT_ROOT}/infrastructure"
export GITOPS_DIR="${PROJECT_ROOT}/gitops"
export APP_DIR="${PROJECT_ROOT}/app"
export SCRIPTS_DIR="${PROJECT_ROOT}/scripts"
