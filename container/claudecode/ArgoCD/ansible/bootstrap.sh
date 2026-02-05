#!/bin/bash
#
# ArgoCD Environment Bootstrap Script
# This script sets up Ansible and runs the complete environment setup
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PLAYBOOK="${SCRIPT_DIR}/playbooks/setup_complete_environment.yml"

# Logging
LOG_FILE="${BASE_DIR}/logs/bootstrap-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "${BASE_DIR}/logs"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo "" | tee -a "$LOG_FILE"
    echo "==========================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "==========================================" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Trap errors
trap 'print_error "Script failed at line $LINENO. Check log: $LOG_FILE"' ERR

# Main execution
main() {
    print_header "ArgoCD Environment Bootstrap"

    print_info "Starting bootstrap process..."
    print_info "Log file: $LOG_FILE"

    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. This is not recommended."
        print_warning "The script will use 'become' for privilege escalation when needed."
    fi

    # Check OS
    print_info "Checking operating system..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_info "OS: $NAME $VERSION"

        if [[ ! "$ID" =~ ^(rhel|rocky|centos)$ ]] || [[ ! "$VERSION_ID" =~ ^9 ]]; then
            print_warning "This script is designed for RHEL/Rocky/CentOS 9"
            print_warning "Current OS: $NAME $VERSION_ID"
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_error "Aborted by user"
                exit 1
            fi
        fi
    else
        print_warning "Cannot detect OS version. Proceeding anyway..."
    fi

    # Check if Ansible is installed
    print_info "Checking for Ansible..."
    if ! command -v ansible-playbook &> /dev/null; then
        print_warning "Ansible is not installed. Installing..."

        # Install Ansible
        print_info "Installing Ansible via pip..."
        if command -v python3 &> /dev/null; then
            sudo python3 -m pip install --upgrade pip
            sudo python3 -m pip install ansible
        else
            print_error "Python3 is not installed. Installing Python3 first..."
            sudo dnf install -y python3 python3-pip
            sudo python3 -m pip install ansible
        fi

        # Verify installation
        if command -v ansible-playbook &> /dev/null; then
            print_success "Ansible installed successfully"
        else
            print_error "Failed to install Ansible"
            exit 1
        fi
    else
        ANSIBLE_VERSION=$(ansible-playbook --version | head -1)
        print_success "Ansible is already installed: $ANSIBLE_VERSION"
    fi

    # Set up PATH for Ansible
    if [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
        export PATH="/usr/local/bin:$PATH"
        print_info "Added /usr/local/bin to PATH"
    fi

    # Check if playbook exists
    print_info "Checking for playbook..."
    if [ ! -f "$PLAYBOOK" ]; then
        print_error "Playbook not found: $PLAYBOOK"
        exit 1
    fi
    print_success "Playbook found: $PLAYBOOK"

    # Display system information
    print_header "System Information"
    print_info "Hostname: $(hostname)"
    print_info "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
    print_info "Disk Space: $(df -h "$BASE_DIR" | awk 'NR==2 {print $4 " available"}')"
    print_info "CPU Cores: $(nproc)"

    # Ask for confirmation
    echo "" | tee -a "$LOG_FILE"
    print_warning "This script will:"
    echo "  1. Install system packages (requires sudo)" | tee -a "$LOG_FILE"
    echo "  2. Install Podman and podman-compose" | tee -a "$LOG_FILE"
    echo "  3. Install Node.js 20.x and Maven 3.9.x" | tee -a "$LOG_FILE"
    echo "  4. Start 9 containers for the ArgoCD environment" | tee -a "$LOG_FILE"
    echo "  5. Configure services and initialize databases" | tee -a "$LOG_FILE"
    echo "  6. Build backend and frontend applications" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    print_info "Estimated time: 15-30 minutes (depending on network speed)"
    echo "" | tee -a "$LOG_FILE"

    read -p "Do you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Aborted by user"
        exit 0
    fi

    # Run the Ansible playbook
    print_header "Running Ansible Playbook"
    print_info "This may take 15-30 minutes..."
    print_info "You can monitor progress in another terminal: tail -f $LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    START_TIME=$(date +%s)

    # Run playbook with both stdout and log file
    if ansible-playbook \
        "$PLAYBOOK" \
        --inventory localhost, \
        --connection local \
        -e "ansible_python_interpreter=/usr/bin/python3" \
        --ask-become-pass \
        2>&1 | tee -a "$LOG_FILE"; then

        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        MINUTES=$((DURATION / 60))
        SECONDS=$((DURATION % 60))

        print_header "Bootstrap Complete!"
        print_success "Environment setup completed successfully"
        print_info "Duration: ${MINUTES}m ${SECONDS}s"
        print_info "Log file: $LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        # Display access information
        if [ -f "${BASE_DIR}/CREDENTIALS.txt" ]; then
            print_header "Service Access Information"
            print_info "Credentials saved to: ${BASE_DIR}/CREDENTIALS.txt"
            echo "" | tee -a "$LOG_FILE"
            print_info "Quick Access URLs:"
            echo "  PostgreSQL:  localhost:5432" | tee -a "$LOG_FILE"
            echo "  pgAdmin:     http://localhost:5050" | tee -a "$LOG_FILE"
            echo "  Nexus:       http://localhost:8081" | tee -a "$LOG_FILE"
            echo "  GitLab:      http://localhost:5003" | tee -a "$LOG_FILE"
            echo "  GitLab Reg:  http://localhost:5005" | tee -a "$LOG_FILE"
            echo "  ArgoCD:      http://localhost:5010" | tee -a "$LOG_FILE"
            echo "" | tee -a "$LOG_FILE"
            print_info "For detailed credentials, run: cat ${BASE_DIR}/CREDENTIALS.txt"
        fi

        # Display verification command
        echo "" | tee -a "$LOG_FILE"
        print_info "To verify the environment, run:"
        echo "  ${BASE_DIR}/verify-environment.sh" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        # Display next steps
        print_header "Next Steps"
        echo "1. Review credentials in ${BASE_DIR}/CREDENTIALS.txt" | tee -a "$LOG_FILE"
        echo "2. Login to GitLab (http://localhost:5003) and create 'orgmgmt' project" | tee -a "$LOG_FILE"
        echo "3. Configure GitLab Runner for CI/CD" | tee -a "$LOG_FILE"
        echo "4. Login to Nexus (http://localhost:8081) and configure repositories" | tee -a "$LOG_FILE"
        echo "5. Access ArgoCD (http://localhost:5010) to manage deployments" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        print_success "Bootstrap completed successfully!"
        exit 0

    else
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        MINUTES=$((DURATION / 60))
        SECONDS=$((DURATION % 60))

        print_header "Bootstrap Failed"
        print_error "Playbook execution failed"
        print_info "Duration before failure: ${MINUTES}m ${SECONDS}s"
        print_info "Check log file for details: $LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        print_info "Common issues and solutions:"
        echo "  1. Network issues: Check internet connectivity" | tee -a "$LOG_FILE"
        echo "  2. Permission denied: Run with sudo or fix permissions" | tee -a "$LOG_FILE"
        echo "  3. Insufficient resources: Ensure 8GB RAM and 50GB disk" | tee -a "$LOG_FILE"
        echo "  4. Port conflicts: Check if ports 5003, 5010, 8081 etc are available" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"

        print_info "To retry, run: $0"
        exit 1
    fi
}

# Run main function
main "$@"
