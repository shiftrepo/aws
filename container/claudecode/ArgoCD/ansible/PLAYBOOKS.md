# Ansible Playbooks Reference

This document describes all available Ansible playbooks for managing the ArgoCD environment.

## Quick Reference

| Playbook | Purpose | Time | Become |
|----------|---------|------|--------|
| `setup_complete_environment.yml` | Complete environment setup | 15-30 min | Yes |
| `install_prerequisites.yml` | Install system packages and tools | 5-10 min | Yes |
| `configure_podman_registry.yml` | Configure insecure registry | 1-2 min | Yes |
| `install_argocd.yml` | Install ArgoCD CLI | 1-2 min | Yes |
| `deploy_infrastructure.yml` | Start all containers | 10-15 min | No |
| `setup_application.yml` | Configure services | 2-5 min | No |
| `verify_environment.yml` | Health checks | 1 min | No |
| `cleanup_environment.yml` | Stop and cleanup | 1-2 min | No |
| `site.yml` | Run all playbooks in sequence | 15-20 min | Yes |

## Main Playbooks

### setup_complete_environment.yml

**Purpose:** Master playbook that builds the complete environment from scratch

**Usage:**
```bash
ansible-playbook playbooks/setup_complete_environment.yml --ask-become-pass
```

**What it does:**

1. **Phase 1: Prerequisites (5-10 minutes)**
   - Check OS compatibility (RHEL/Rocky/CentOS 9)
   - Check system resources (8GB RAM, 50GB disk)
   - Install system packages
   - Install Podman and podman-compose
   - Install Node.js 20.x
   - Install Maven 3.9.x
   - Create required directories

2. **Phase 2: Infrastructure (10-15 minutes)**
   - Generate secure passwords
   - Create .env file
   - Start 9 containers with podman-compose
   - Wait for all services to be healthy
   - PostgreSQL, pgAdmin, Nexus, GitLab, ArgoCD

3. **Phase 3: Service Configuration (2-5 minutes)**
   - Configure Podman insecure registry
   - Install ArgoCD CLI
   - Retrieve admin passwords
   - Initialize services

4. **Phase 4: Application Build (5-10 minutes, optional)**
   - Build backend with Maven
   - Build frontend with npm
   - Run tests

5. **Phase 5: ArgoCD Setup (1-2 minutes)**
   - Login to ArgoCD
   - Create projects and applications

6. **Phase 6: Verification (1 minute)**
   - Verify all containers running
   - Check service health
   - Save credentials

**Variables:**
- `skip_application_build: false` - Skip building applications
- `postgres_password` - Custom PostgreSQL password
- `gitlab_password` - Custom GitLab password
- `clean_volumes_on_restart: false` - Clean volumes on restart

**Output Files:**
- `CREDENTIALS.txt` - All service credentials
- `verify-environment.sh` - Health check script

### install_prerequisites.yml

**Purpose:** Install all required system packages and build tools

**Usage:**
```bash
ansible-playbook playbooks/install_prerequisites.yml --ask-become-pass
```

**Installs:**
- System packages: git, curl, jq, wget, tar, unzip, openssl
- Container runtime: Podman, podman-compose, buildah, skopeo
- Python packages: podman-compose, psycopg2-binary
- Node.js 20.x from NodeSource
- Maven 3.9.9 to /opt/maven
- Java (Maven dependency)

**Idempotent:** Yes - safe to run multiple times

### configure_podman_registry.yml

**Purpose:** Configure Podman to trust the GitLab insecure registry

**Usage:**
```bash
ansible-playbook playbooks/configure_podman_registry.yml --ask-become-pass
```

**Actions:**
- Creates `/etc/containers/registries.conf.d/gitlab.conf`
- Configures localhost:5005 as insecure registry
- Creates helper script `/usr/local/bin/gitlab-registry-login`
- Tests registry connectivity

**Idempotent:** Yes

### install_argocd.yml

**Purpose:** Download and install ArgoCD CLI

**Usage:**
```bash
ansible-playbook playbooks/install_argocd.yml --ask-become-pass
```

**Actions:**
- Downloads ArgoCD CLI v2.10.0
- Installs to /usr/local/bin/argocd
- Verifies installation
- Checks version compatibility

**Idempotent:** Yes - skips if correct version already installed

### deploy_infrastructure.yml

**Purpose:** Start all infrastructure containers with podman-compose

**Usage:**
```bash
ansible-playbook playbooks/deploy_infrastructure.yml
```

**Actions:**
- Verifies podman and podman-compose installed
- Stops existing containers (if any)
- Starts all containers with `podman-compose up -d`
- Waits for each service to be healthy:
  - PostgreSQL (30 retries, 10s delay)
  - Redis (20 retries, 5s delay)
  - Nexus (40 retries, 15s delay)
  - GitLab (60 retries, 15s delay)
  - ArgoCD (40 retries, 10s delay)
- Displays access information

**Expected Duration:** 10-15 minutes (GitLab takes longest)

**Idempotent:** Yes - safe to re-run

### setup_application.yml

**Purpose:** Configure services and initialize applications

**Usage:**
```bash
ansible-playbook playbooks/setup_application.yml
```

**Actions:**
- Wait for GitLab to be fully ready
- Retrieve Nexus admin password
- Retrieve ArgoCD admin password
- Login to ArgoCD
- Check PostgreSQL connectivity
- Display setup summary

**Note:** Manual configuration still required for:
- GitLab project creation
- GitLab Runner registration
- Nexus repository setup

**Idempotent:** Yes

### verify_environment.yml

**Purpose:** Comprehensive health check of the entire environment

**Usage:**
```bash
ansible-playbook playbooks/verify_environment.yml
```

**Checks:**
- Container count (9 expected)
- Container status
- Service health (PostgreSQL, Redis, Nexus, GitLab, ArgoCD, pgAdmin)
- Database connectivity
- ArgoCD CLI installation
- Network status
- Volume count
- Disk space
- Memory usage

**Output:** Health score and status summary

**Idempotent:** Yes - read-only checks

### cleanup_environment.yml

**Purpose:** Stop containers and optionally clean up data

**Usage:**
```bash
# Stop containers only (preserve data)
ansible-playbook playbooks/cleanup_environment.yml

# Complete cleanup (delete everything)
ansible-playbook playbooks/cleanup_environment.yml \
  -e cleanup_volumes=true \
  -e cleanup_images=true \
  -e cleanup_network=true
```

**Actions:**
- Stops all containers with podman-compose down
- Optionally removes volumes (if cleanup_volumes=true)
- Optionally removes images (if cleanup_images=true)
- Optionally removes network (if cleanup_network=true)
- Removes credentials file (if cleanup_volumes=true)

**Warning:** cleanup_volumes=true is DESTRUCTIVE and will delete all data!

**Idempotent:** Yes

### site.yml

**Purpose:** Run all playbooks in the correct sequence

**Usage:**
```bash
# Run all
ansible-playbook playbooks/site.yml --ask-become-pass

# Run specific steps with tags
ansible-playbook playbooks/site.yml --tags registry
ansible-playbook playbooks/site.yml --tags cli
ansible-playbook playbooks/site.yml --tags infrastructure
ansible-playbook playbooks/site.yml --tags application

# Skip confirmation prompt
ANSIBLE_AUTO_CONTINUE=true ansible-playbook playbooks/site.yml
```

**Sequence:**
1. Configure Podman registry (tag: registry, podman)
2. Install ArgoCD CLI (tag: argocd, cli)
3. Deploy infrastructure (tag: infrastructure, deploy)
4. Setup applications (tag: application, setup)

**Creates:** Quick reference script at `ansible-commands.sh`

## Helper Scripts

### bootstrap.sh

**Purpose:** Automated setup script that installs Ansible and runs complete setup

**Usage:**
```bash
./bootstrap.sh
```

**What it does:**
- Checks OS compatibility
- Displays system information
- Prompts for confirmation
- Installs Ansible if needed
- Runs `setup_complete_environment.yml`
- Displays final summary
- Creates verification script

**Output:** Log file in `logs/bootstrap-YYYYMMDD-HHMMSS.log`

**Features:**
- Colored output
- Progress tracking
- Error handling
- Time tracking
- Automatic cleanup on failure

## Variables

### Configuration File

All variables are defined in `group_vars/all.yml`:

**Key Variables:**
```yaml
# Project
project_name: orgmgmt
base_directory: /root/aws.git/container/claudecode/ArgoCD

# Ports
postgres_port: 5432
pgadmin_port: 5050
nexus_http_port: 8081
gitlab_http_port: 5003
gitlab_registry_port: 5005
argocd_server_port: 5010

# Versions
postgres_version: "16-alpine"
nexus_version: "3.63.0"
argocd_version: v2.10.0
maven_version: "3.9.9"
nodejs_version: "20.x"

# Resource Requirements
min_memory_mb: 8192
min_disk_gb: 50

# Timeouts
gitlab_health_check_retries: 60
gitlab_health_check_delay: 15
```

### Override Variables

**Command Line:**
```bash
ansible-playbook playbooks/setup_complete_environment.yml \
  -e postgres_password="MyPassword" \
  -e skip_application_build=true
```

**Environment Variables:**
```bash
export POSTGRES_PASSWORD="MyPassword"
export GITLAB_ROOT_PASSWORD="GitLabPassword"
ansible-playbook playbooks/setup_complete_environment.yml
```

**Inventory File:**
```yaml
# inventory/hosts.yml
all:
  vars:
    postgres_password: "MyPassword"
    gitlab_password: "GitLabPassword"
```

## Common Patterns

### Complete Fresh Install
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
./bootstrap.sh
```

### Reinstall Without Rebuilding Apps
```bash
ansible-playbook playbooks/setup_complete_environment.yml \
  -e skip_application_build=true \
  --ask-become-pass
```

### Update Only Infrastructure
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose down
ansible-playbook ../ansible/playbooks/deploy_infrastructure.yml
```

### Reconfigure Services
```bash
ansible-playbook playbooks/setup_application.yml
```

### Full Cleanup and Reinstall
```bash
# Cleanup
ansible-playbook playbooks/cleanup_environment.yml \
  -e cleanup_volumes=true \
  -e cleanup_images=true

# Reinstall
./bootstrap.sh
```

### Verify Installation
```bash
ansible-playbook playbooks/verify_environment.yml
```

## Troubleshooting Playbooks

### Check What Failed
```bash
# Run in check mode (dry run)
ansible-playbook playbooks/setup_complete_environment.yml --check

# Verbose output
ansible-playbook playbooks/setup_complete_environment.yml -vvv

# Step through tasks
ansible-playbook playbooks/setup_complete_environment.yml --step
```

### Start From Specific Task
```bash
# List all tasks
ansible-playbook playbooks/setup_complete_environment.yml --list-tasks

# Start from specific task
ansible-playbook playbooks/setup_complete_environment.yml \
  --start-at-task="Install ArgoCD CLI"
```

### Run Only Failed Tasks
```bash
# First run
ansible-playbook playbooks/setup_complete_environment.yml

# If failed, retry only failed tasks
ansible-playbook playbooks/setup_complete_environment.yml --limit @playbooks/setup_complete_environment.retry
```

## Best Practices

### 1. Always Run Verification After Setup
```bash
ansible-playbook playbooks/verify_environment.yml
```

### 2. Save Logs
```bash
ansible-playbook playbooks/setup_complete_environment.yml 2>&1 | tee setup.log
```

### 3. Use Check Mode First
```bash
ansible-playbook playbooks/setup_complete_environment.yml --check
```

### 4. Backup Before Cleanup
```bash
# Backup
cd /root/aws.git/container/claudecode/ArgoCD
./scripts/backup.sh

# Then cleanup
cd ansible
ansible-playbook playbooks/cleanup_environment.yml -e cleanup_volumes=true
```

### 5. Use Variables for Passwords
```bash
# Never hardcode passwords in playbooks
# Use variables or environment variables
ansible-playbook playbooks/setup_complete_environment.yml \
  -e postgres_password="$(openssl rand -base64 20)"
```

## Related Documentation

- [README-COMPLETE-SETUP.md](README-COMPLETE-SETUP.md) - Complete setup guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [../README.md](../README.md) - Main project README
- [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - Troubleshooting guide
- [EXAMPLES.md](EXAMPLES.md) - Usage examples

## Support

For issues with playbooks:

1. Check logs: `tail -f logs/bootstrap-*.log`
2. Run verification: `ansible-playbook playbooks/verify_environment.yml`
3. Check Ansible version: `ansible --version` (2.9+ required)
4. Review [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
5. Check variables: `ansible-playbook playbooks/setup_complete_environment.yml --list-vars`
