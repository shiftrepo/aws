#!/bin/bash
# ========================================
# Environment Setup Script
# ========================================
# Detects environment and creates configuration files
# Usage: ./scripts/setup-environment.sh [--force]
# ========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$BASE_DIR/config"
ENV_FILE="$CONFIG_DIR/environment.yml"
ENV_EXAMPLE="$CONFIG_DIR/environment.yml.example"

FORCE=false
if [[ "$1" == "--force" ]]; then
    FORCE=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========================================
# Helper Functions
# ========================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ========================================
# Environment Detection
# ========================================

detect_public_ip() {
    local ip=""

    # Try AWS EC2 metadata
    if ip=$(curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null); then
        if [[ -n "$ip" && "$ip" != "404"* ]]; then
            echo "$ip"
            return
        fi
    fi

    # Try external service
    if ip=$(curl -s --connect-timeout 5 https://ifconfig.me 2>/dev/null); then
        if [[ -n "$ip" ]]; then
            echo "$ip"
            return
        fi
    fi

    # Fallback to hostname -I
    ip=$(hostname -I | awk '{print $1}')
    echo "${ip:-127.0.0.1}"
}

detect_private_ip() {
    # Get primary network interface IP
    local ip=$(hostname -I | awk '{print $1}')
    echo "${ip:-127.0.0.1}"
}

detect_network_interface() {
    # Get primary network interface name
    local iface=$(ip route | grep default | awk '{print $5}' | head -n1)
    echo "${iface:-eth0}"
}

check_port_available() {
    local port=$1
    if ss -tuln | grep -q ":$port "; then
        return 1
    fi
    return 0
}

find_available_port() {
    local start_port=$1
    local max_tries=100

    for ((i=0; i<max_tries; i++)); do
        local port=$((start_port + i))
        if check_port_available $port; then
            echo $port
            return
        fi
    done

    log_error "Could not find available port starting from $start_port"
    exit 1
}

# ========================================
# Port Configuration
# ========================================

setup_ports() {
    log_info "Checking port availability..."

    declare -A PORTS=(
        ["postgres_external"]=5001
        ["pgadmin"]=5002
        ["kubernetes_dashboard"]=5004
        ["frontend"]=5006
        ["argocd"]=5010
        ["nexus_http"]=8000
        ["nexus_docker"]=8082
        ["registry"]=5000
        ["redis"]=6379
        ["backend"]=8080
    )

    declare -A AVAILABLE_PORTS

    for name in "${!PORTS[@]}"; do
        port="${PORTS[$name]}"
        if ! check_port_available $port; then
            log_warning "Port $port ($name) is in use, finding alternative..."
            new_port=$(find_available_port $((port + 1)))
            AVAILABLE_PORTS[$name]=$new_port
            log_info "Using port $new_port for $name"
        else
            AVAILABLE_PORTS[$name]=$port
        fi
    done

    # Export for use in templates
    for name in "${!AVAILABLE_PORTS[@]}"; do
        export "PORT_${name^^}=${AVAILABLE_PORTS[$name]}"
    done
}

# ========================================
# Git Repository Detection
# ========================================

detect_git_repo() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")
        if [[ -n "$remote_url" ]]; then
            echo "$remote_url"
            return
        fi
    fi
    echo "https://github.com/yourusername/yourrepo.git"
}

detect_git_branch() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
        echo "$branch"
    else
        echo "main"
    fi
}

# ========================================
# Configuration File Generation
# ========================================

generate_environment_config() {
    log_info "Generating environment configuration..."

    # Detect environment
    PUBLIC_IP=$(detect_public_ip)
    PRIVATE_IP=$(detect_private_ip)
    NETWORK_IFACE=$(detect_network_interface)
    GIT_REPO=$(detect_git_repo)
    GIT_BRANCH=$(detect_git_branch)

    log_info "Detected configuration:"
    log_info "  Public IP: $PUBLIC_IP"
    log_info "  Private IP: $PRIVATE_IP"
    log_info "  Network Interface: $NETWORK_IFACE"
    log_info "  Git Repository: $GIT_REPO"
    log_info "  Git Branch: $GIT_BRANCH"

    # Create config directory
    mkdir -p "$CONFIG_DIR"

    # Copy example if environment.yml doesn't exist
    if [[ ! -f "$ENV_FILE" ]] || [[ "$FORCE" == true ]]; then
        if [[ -f "$ENV_EXAMPLE" ]]; then
            cp "$ENV_EXAMPLE" "$ENV_FILE"

            # Replace placeholders with detected values
            sed -i "s|public_ip: \"\"|public_ip: \"$PUBLIC_IP\"|g" "$ENV_FILE"
            sed -i "s|private_ip: \"\"|private_ip: \"$PRIVATE_IP\"|g" "$ENV_FILE"
            sed -i "s|interface: \"\"|interface: \"$NETWORK_IFACE\"|g" "$ENV_FILE"
            sed -i "s|https://github.com/yourusername/yourrepo.git|$GIT_REPO|g" "$ENV_FILE"
            sed -i "s|branch: \"main\"|branch: \"$GIT_BRANCH\"|g" "$ENV_FILE"

            log_success "Created $ENV_FILE with detected values"
        else
            log_error "Example configuration file not found: $ENV_EXAMPLE"
            exit 1
        fi
    else
        log_info "Configuration file already exists: $ENV_FILE"
        log_info "Use --force to regenerate"
    fi
}

# ========================================
# Ansible Variables Generation
# ========================================

generate_ansible_vars() {
    log_info "Generating Ansible variables..."

    local ansible_vars_dir="$BASE_DIR/ansible/group_vars"
    mkdir -p "$ansible_vars_dir"

    cat > "$ansible_vars_dir/all.yml" << 'EOF'
---
# ========================================
# Ansible Global Variables
# ========================================
# Auto-generated from environment.yml
# ========================================

# Load environment configuration
environment_config: "{{ lookup('file', playbook_dir + '/../config/environment.yml') | from_yaml }}"

# Network Configuration
public_ip: "{{ environment_config.network.public_ip | default(ansible_default_ipv4.address) }}"
private_ip: "{{ environment_config.network.private_ip | default(ansible_default_ipv4.address) }}"
domain: "{{ environment_config.network.domain | default('') }}"

# Port Configuration
ports: "{{ environment_config.ports }}"

# Directory Configuration
base_dir: "{{ environment_config.directories.base_dir | default(playbook_dir + '/..') }}"
data_dir: "{{ environment_config.directories.data_dir }}"
gitops_dir: "{{ environment_config.directories.gitops_dir }}"
kubectl_path: "{{ environment_config.directories.kubectl_path }}"

# Container Configuration
container_runtime: "{{ environment_config.containers.runtime }}"
container_network: "{{ environment_config.containers.network_name }}"
registry_url: "{{ environment_config.containers.registry.url }}"
registry_insecure: "{{ environment_config.containers.registry.insecure }}"

# Application Configuration
app_name: "{{ environment_config.application.name }}"
app_version: "{{ environment_config.application.version }}"
frontend_image: "{{ environment_config.application.frontend.image_name }}"
frontend_replicas: "{{ environment_config.application.frontend.replicas }}"
backend_image: "{{ environment_config.application.backend.image_name }}"
backend_replicas: "{{ environment_config.application.backend.replicas }}"

# Database Configuration
db_name: "{{ environment_config.database.name }}"
db_user: "{{ environment_config.database.user }}"
db_password: "{{ environment_config.database.password }}"
postgres_version: "{{ environment_config.database.postgres.version }}"

# Authentication Configuration
pgadmin_email: "{{ environment_config.authentication.pgadmin.email }}"
pgadmin_password: "{{ environment_config.authentication.pgadmin.password }}"
nexus_username: "{{ environment_config.authentication.nexus.username }}"
nexus_password: "{{ environment_config.authentication.nexus.password }}"

# Git Configuration
git_repo_url: "{{ environment_config.git.repository_url }}"
git_branch: "{{ environment_config.git.branch }}"
git_manifests_path: "{{ environment_config.git.manifests_path }}"
git_user_name: "{{ environment_config.git.user_name }}"
git_user_email: "{{ environment_config.git.user_email }}"

# ArgoCD Configuration
argocd_version: "{{ environment_config.argocd.version }}"
argocd_namespace: "{{ environment_config.argocd.namespace }}"
argocd_app_name: "{{ environment_config.argocd.application.name }}"
argocd_auto_sync: "{{ environment_config.argocd.application.auto_sync }}"
argocd_prune: "{{ environment_config.argocd.application.prune }}"
argocd_self_heal: "{{ environment_config.argocd.application.self_heal }}"

# Kubernetes Dashboard Configuration
dashboard_version: "{{ environment_config.kubernetes_dashboard.version }}"
dashboard_namespace: "{{ environment_config.kubernetes_dashboard.namespace }}"
dashboard_admin_user: "{{ environment_config.kubernetes_dashboard.admin_user }}"

# Nexus Configuration
nexus_version: "{{ environment_config.nexus.version }}"
nexus_repositories: "{{ environment_config.nexus.repositories }}"

# Feature Flags
argocd_enabled: "{{ environment_config.features.argocd_enabled }}"
dashboard_enabled: "{{ environment_config.features.dashboard_enabled }}"
nexus_enabled: "{{ environment_config.features.nexus_enabled }}"
monitoring_enabled: "{{ environment_config.features.monitoring_enabled }}"
backup_enabled: "{{ environment_config.features.backup_enabled }}"

# Firewall Configuration
firewall_enabled: "{{ environment_config.firewall.enabled }}"
firewall_service: "{{ environment_config.firewall.service }}"
firewall_public_ports: "{{ environment_config.firewall.public_ports }}"
firewall_private_ports: "{{ environment_config.firewall.private_ports }}"
EOF

    log_success "Created Ansible variables: $ansible_vars_dir/all.yml"
}

# ========================================
# Docker Compose Template Generation
# ========================================

generate_compose_template() {
    log_info "Generating Podman Compose template..."

    # This will be done by Ansible using Jinja2 templates
    log_info "Compose template will be generated by Ansible playbooks"
}

# ========================================
# Validation
# ========================================

validate_configuration() {
    log_info "Validating configuration..."

    local errors=0

    # Check if config file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Configuration file not found: $ENV_FILE"
        ((errors++))
    fi

    # Check if Ansible is installed
    if ! command -v ansible-playbook &> /dev/null; then
        log_error "Ansible is not installed"
        ((errors++))
    fi

    # Check if kubectl path is valid
    if [[ ! -x "/usr/local/bin/kubectl" ]]; then
        log_warning "kubectl not found at /usr/local/bin/kubectl"
    fi

    # Check if git is configured
    if ! git config user.name &> /dev/null; then
        log_warning "Git user.name not configured"
    fi

    if ! git config user.email &> /dev/null; then
        log_warning "Git user.email not configured"
    fi

    if [[ $errors -gt 0 ]]; then
        log_error "Validation failed with $errors errors"
        return 1
    fi

    log_success "Validation passed"
    return 0
}

# ========================================
# Summary
# ========================================

show_summary() {
    cat << EOF

========================================
Environment Setup Complete
========================================

Configuration File: $ENV_FILE

Next Steps:
1. Review and customize: $ENV_FILE
2. Run infrastructure setup:
   cd $BASE_DIR
   ansible-playbook -i ansible/inventory/hosts.yml \\
     ansible/playbooks/deploy_infrastructure.yml

3. Run complete CD pipeline:
   ansible-playbook -i ansible/inventory/hosts.yml \\
     ansible/playbooks/complete_cd_pipeline.yml

Documentation:
- README.md - Complete setup guide
- SERVICE-ACCESS-GUIDE.md - Service access information
- HOST-OS-COMMANDS.md - Command reference

========================================

EOF
}

# ========================================
# Main Execution
# ========================================

main() {
    log_info "Starting environment setup..."
    log_info "Base directory: $BASE_DIR"

    # Setup ports
    setup_ports

    # Generate configuration
    generate_environment_config

    # Generate Ansible variables
    generate_ansible_vars

    # Generate compose template
    generate_compose_template

    # Validate
    if validate_configuration; then
        show_summary
        exit 0
    else
        log_error "Setup completed with warnings. Please review configuration."
        exit 1
    fi
}

# Run main function
main
