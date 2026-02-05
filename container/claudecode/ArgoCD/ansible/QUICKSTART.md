# Ansible Playbooks - Quick Start Guide

## Fastest Setup (Recommended)

**One command to set up everything:**

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
./bootstrap.sh
```

This automated script will:
- Install Ansible if needed
- Install all prerequisites (Podman, Node.js, Maven)
- Start all 9 containers
- Configure services
- Build applications
- Set up ArgoCD

**Time:** 15-30 minutes

## Prerequisites

- RHEL/Rocky/CentOS 9
- 8GB RAM minimum
- 50GB disk space
- Sudo access

The bootstrap script will install everything else automatically.

## Manual Setup Options

### Option 1: Complete Setup Playbook

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/setup_complete_environment.yml --ask-become-pass
```

### Option 2: Site Playbook (Infrastructure Only)

```bash
ansible-playbook playbooks/site.yml --ask-become-pass
```

This will:
1. Configure Podman insecure registry
2. Install ArgoCD CLI
3. Deploy all infrastructure services
4. Setup application components

## Step-by-Step Setup

If you prefer to run each step individually:

### Step 1: Configure Podman Registry
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/configure_podman_registry.yml
```

### Step 2: Install ArgoCD CLI
```bash
ansible-playbook playbooks/install_argocd.yml
```

### Step 3: Deploy Infrastructure
```bash
ansible-playbook playbooks/deploy_infrastructure.yml
```

### Step 4: Setup Applications
```bash
ansible-playbook playbooks/setup_application.yml
```

## Post-Installation

### Get ArgoCD Password
```bash
podman exec argocd-server argocd admin initial-password | head -n1
```

### Get Nexus Password
```bash
podman exec orgmgmt-nexus cat /nexus-data/admin.password
```

### Login to ArgoCD
```bash
ARGOCD_PASSWORD=$(podman exec argocd-server argocd admin initial-password | head -n1)
argocd login localhost:5010 --insecure --username admin --password $ARGOCD_PASSWORD
```

### Login to GitLab Registry
```bash
podman login localhost:5005 --username root --password GitLabRoot123! --tls-verify=false
```

Or use the helper script:
```bash
/usr/local/bin/gitlab-registry-login
```

## Access URLs

After successful deployment:

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| PostgreSQL | localhost:5432 | orgmgmt_user | SecurePassword123! |
| pgAdmin | http://localhost:5050 | admin@orgmgmt.local | AdminPassword123! |
| Nexus | http://localhost:8081 | admin | See command above |
| GitLab | http://localhost:5003 | root | GitLabRoot123! |
| GitLab Registry | http://localhost:5005 | root | GitLabRoot123! |
| ArgoCD | http://localhost:5010 | admin | See command above |

## Verify Deployment

### Option 1: Run Verification Script (Easiest)

```bash
/root/aws.git/container/claudecode/ArgoCD/verify-environment.sh
```

### Option 2: Run Verification Playbook

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/verify_environment.yml
```

### Option 3: Manual Checks

```bash
# Check all containers are running
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check specific service
curl http://localhost:5010/healthz  # ArgoCD
curl http://localhost:5003/-/health # GitLab
curl http://localhost:8081/service/rest/v1/status # Nexus
```

## Common Issues

### Services not healthy?
Wait a few minutes - GitLab takes 5-10 minutes to fully start.

### Port conflicts?
Edit `/root/aws.git/container/claudecode/ArgoCD/infrastructure/.env` and change port numbers.

### Permission errors?
Run with sudo:
```bash
sudo ansible-playbook playbooks/site.yml
```

## Stop/Start Infrastructure

### Stop all services (preserves data)
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose down
```

### Start all services
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose up -d
```

### Restart specific service
```bash
podman restart <container-name>
```

### Complete cleanup (DESTRUCTIVE - deletes all data)
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/cleanup_environment.yml \
  -e cleanup_volumes=true \
  -e cleanup_images=true
```

## Getting Help

View detailed documentation:
```bash
cat /root/aws.git/container/claudecode/ArgoCD/ansible/README.md
```

List all available commands:
```bash
/root/aws.git/container/claudecode/ArgoCD/ansible/ansible-commands.sh
```

View playbook tasks:
```bash
ansible-playbook playbooks/site.yml --list-tasks
```

Run with verbose output:
```bash
ansible-playbook playbooks/site.yml -vvv
```
