# Complete ArgoCD Environment Setup Guide

This guide provides a comprehensive, automated setup for the complete ArgoCD environment including all infrastructure services, build tools, and application deployments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [What Gets Installed](#what-gets-installed)
- [Installation Process](#installation-process)
- [Time Estimates](#time-estimates)
- [Expected Output](#expected-output)
- [Verification Steps](#verification-steps)
- [Post-Installation](#post-installation)
- [Troubleshooting](#troubleshooting)
- [Manual Setup](#manual-setup)
- [Cleanup](#cleanup)

## Overview

The complete setup automation installs and configures:

- **Infrastructure Services**: PostgreSQL, pgAdmin, Nexus, GitLab, ArgoCD
- **Build Tools**: Maven 3.9.x, Node.js 20.x
- **Container Runtime**: Podman with podman-compose
- **Applications**: Backend (Java/Spring Boot) and Frontend (React)
- **GitOps**: ArgoCD projects and applications

All services run as Podman containers with proper networking, volumes, and health checks.

## Prerequisites

### System Requirements

**Operating System:**
- RHEL 9, Rocky Linux 9, or CentOS Stream 9
- 64-bit architecture

**Hardware:**
- **CPU**: 4+ cores recommended
- **Memory**: 8 GB RAM minimum (16 GB recommended)
- **Disk**: 50 GB free space minimum (100 GB recommended)
- **Network**: Stable internet connection for downloading packages and images

### Required Ports

The following ports must be available:

| Port | Service | Description |
|------|---------|-------------|
| 5432 | PostgreSQL | Database server |
| 5050 | pgAdmin | Database management UI |
| 5003 | GitLab | Git repository and CI/CD |
| 5005 | GitLab Registry | Container registry |
| 2222 | GitLab SSH | Git SSH access |
| 8081 | Nexus | Artifact repository |
| 8082 | Nexus Docker | Docker registry |
| 5010 | ArgoCD | GitOps deployment |
| 6379 | Redis | ArgoCD cache |

### User Permissions

- Regular user account (non-root)
- Sudo access for package installation
- User should be in `wheel` group

## Quick Start

### One-Command Setup

Run the bootstrap script to set up the entire environment:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
./bootstrap.sh
```

That's it! The script will:
1. Check prerequisites
2. Install Ansible if needed
3. Run the complete environment setup
4. Display access credentials
5. Create verification scripts

**Expected Duration:** 15-30 minutes (depending on network speed and system performance)

## What Gets Installed

### Phase 1: Prerequisites (5-10 minutes)

**System Packages:**
- Git, curl, jq, wget, tar, unzip, openssl
- Python 3 and pip3
- Podman, podman-compose, buildah, skopeo

**Build Tools:**
- Node.js 20.x (from NodeSource repository)
- npm (bundled with Node.js)
- Maven 3.9.9 (downloaded and installed to /opt/maven)
- Java 17 (dependency of Maven)

**Python Packages:**
- podman-compose
- psycopg2-binary
- requests

### Phase 2: Infrastructure (10-15 minutes)

**9 Containers Started:**

1. **orgmgmt-postgres** (PostgreSQL 16)
   - Database: orgmgmt
   - Port: 5432
   - Auto-initialized with schema

2. **orgmgmt-pgadmin** (pgAdmin 4)
   - Web interface for PostgreSQL
   - Port: 5050

3. **orgmgmt-nexus** (Nexus 3.63.0)
   - Maven and npm artifact repository
   - Docker registry
   - Ports: 8081 (HTTP), 8082 (Docker)

4. **orgmgmt-gitlab** (GitLab CE)
   - Source control
   - CI/CD pipelines
   - Container registry
   - Ports: 5003 (HTTP), 5005 (Registry), 2222 (SSH)

5. **orgmgmt-gitlab-runner** (GitLab Runner)
   - CI/CD job executor
   - Shell executor configured

6. **argocd-redis** (Redis 7)
   - Cache for ArgoCD
   - Port: 6379

7. **argocd-repo-server** (ArgoCD Repository Server)
   - Git repository management
   - Manifest generation

8. **argocd-application-controller** (ArgoCD Controller)
   - Application sync and health checks
   - Resource reconciliation

9. **argocd-server** (ArgoCD API/UI Server)
   - Web UI and API
   - Port: 5010

**Networking:**
- All containers connected to `argocd-network` bridge
- Internal DNS resolution enabled

**Storage:**
- Persistent volumes for all data
- Automatic volume creation
- Named volumes for easy identification

### Phase 3: Service Configuration (2-5 minutes)

**Podman Configuration:**
- Insecure registry support for GitLab (localhost:5005)
- Registry configuration in /etc/containers/registries.conf.d/gitlab.conf

**ArgoCD CLI:**
- Version 2.10.0 installed to /usr/local/bin/argocd
- CLI configured and tested

**Credentials:**
- Secure random passwords generated
- Admin passwords retrieved from containers
- All credentials saved to CREDENTIALS.txt

### Phase 4: Application Build (5-10 minutes, optional)

**Backend (Java/Spring Boot):**
- Maven clean and package
- Unit tests executed
- JAR artifact created

**Frontend (React):**
- npm install dependencies
- npm run build
- Production bundle created

### Phase 5: ArgoCD Setup (1-2 minutes)

**ArgoCD Configuration:**
- CLI login to ArgoCD server
- Project creation from manifests
- Application creation (dev, staging, prod)
- Repository connections

### Phase 6: Verification (1 minute)

**Health Checks:**
- Container status verification
- Service endpoint accessibility
- Database connectivity
- API availability

## Installation Process

### Step-by-Step Breakdown

#### 1. Run Bootstrap Script

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
./bootstrap.sh
```

The script will prompt for sudo password when needed.

#### 2. Monitor Progress

The script displays progress in real-time. You can also monitor the log:

```bash
# In another terminal
tail -f /root/aws.git/container/claudecode/ArgoCD/logs/bootstrap-*.log
```

#### 3. Review Output

The script displays:
- Installation progress for each phase
- Health check results
- Service URLs
- Credential locations

#### 4. Access Services

Once complete, services are immediately accessible:

```bash
# Check all services are running
podman ps

# Verify environment
/root/aws.git/container/claudecode/ArgoCD/verify-environment.sh
```

## Time Estimates

| Phase | Duration | Notes |
|-------|----------|-------|
| Prerequisites | 5-10 min | Depends on network speed |
| Infrastructure | 10-15 min | GitLab takes longest (5-10 min) |
| Configuration | 2-5 min | Password retrieval and setup |
| Application Build | 5-10 min | Can be skipped if not building |
| ArgoCD Setup | 1-2 min | Manifest application |
| Verification | 1 min | Health checks |
| **Total** | **15-30 min** | First-time installation |

**Subsequent Runs:** 5-10 minutes (cached images and installed tools)

## Expected Output

### Successful Installation

```
==========================================
ArgoCD Environment Setup Complete!
==========================================

Service Access URLs:
  PostgreSQL:  localhost:5432
  pgAdmin:     http://localhost:5050
  Nexus:       http://localhost:8081
  GitLab:      http://localhost:5003
  GitLab Reg:  http://localhost:5005
  ArgoCD:      http://localhost:5010

Credentials saved to: /root/aws.git/container/claudecode/ArgoCD/CREDENTIALS.txt

Service Health:
  PostgreSQL: OK
  pgAdmin:    OK
  Nexus:      OK
  GitLab:     OK
  ArgoCD:     OK

Containers:  9/9 running

Next Steps:
  1. Review credentials in CREDENTIALS.txt
  2. Login to GitLab and create 'orgmgmt' project
  3. Configure GitLab Runner
  4. Setup Nexus repositories
  5. Deploy applications via ArgoCD

==========================================
```

### Container List

```bash
$ podman ps
NAMES                              STATUS          PORTS
orgmgmt-postgres                   Up 10 minutes   0.0.0.0:5432->5432/tcp
orgmgmt-pgadmin                    Up 10 minutes   0.0.0.0:5050->80/tcp
orgmgmt-nexus                      Up 10 minutes   0.0.0.0:8081->8081/tcp, 0.0.0.0:8082->8082/tcp
orgmgmt-gitlab                     Up 10 minutes   0.0.0.0:2222->22/tcp, 0.0.0.0:5003->5003/tcp, 0.0.0.0:5005->5005/tcp
orgmgmt-gitlab-runner              Up 10 minutes
argocd-redis                       Up 10 minutes   0.0.0.0:6379->6379/tcp
argocd-repo-server                 Up 10 minutes
argocd-application-controller      Up 10 minutes
argocd-server                      Up 10 minutes   0.0.0.0:5010->8080/tcp
```

## Verification Steps

### 1. Check Container Status

```bash
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

All 9 containers should be in "Up" status.

### 2. Run Verification Script

```bash
/root/aws.git/container/claudecode/ArgoCD/verify-environment.sh
```

Expected output:
```
==========================================
ArgoCD Environment Verification
==========================================

Running Containers:
[List of 9 containers]

Service Health Checks:
PostgreSQL: OK
Redis: OK
Nexus: OK
GitLab: OK
ArgoCD: OK
pgAdmin: OK
```

### 3. Test Service Access

**PostgreSQL:**
```bash
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "SELECT version();"
```

**ArgoCD:**
```bash
argocd version
argocd app list
```

**GitLab:**
```bash
curl -s http://localhost:5003/-/health | jq
```

**Nexus:**
```bash
curl -s http://localhost:8081/service/rest/v1/status | jq
```

### 4. Check Web UIs

Open in browser:
- pgAdmin: http://localhost:5050
- Nexus: http://localhost:8081
- GitLab: http://localhost:5003
- ArgoCD: http://localhost:5010

## Post-Installation

### 1. Review Credentials

```bash
cat /root/aws.git/container/claudecode/ArgoCD/CREDENTIALS.txt
```

**Important:** Keep this file secure and do not commit to git!

### 2. Configure GitLab

1. Login to GitLab: http://localhost:5003
   - Username: `root`
   - Password: (from CREDENTIALS.txt)

2. Create a new project:
   - Name: `orgmgmt`
   - Visibility: Private

3. Create Personal Access Token:
   - Go to: User Settings > Access Tokens
   - Name: `ansible-automation`
   - Scopes: `api`, `read_repository`, `write_repository`
   - Expiration: 1 year
   - Save the token securely

4. Configure project settings:
   - Enable CI/CD
   - Enable Container Registry

### 3. Configure Nexus

1. Login to Nexus: http://localhost:8081
   - Username: `admin`
   - Password: (from CREDENTIALS.txt or `/nexus-data/admin.password`)

2. Complete setup wizard:
   - Change admin password
   - Configure anonymous access
   - Enable realms if needed

3. Create repositories:
   - Maven hosted (releases)
   - Maven hosted (snapshots)
   - Maven proxy (central)
   - Maven group (public)
   - npm hosted
   - npm proxy
   - Docker hosted

### 4. Configure GitLab Runner

```bash
# Get runner registration token from GitLab
# Settings > CI/CD > Runners > Expand > Registration token

# Register runner
podman exec -it orgmgmt-gitlab-runner gitlab-runner register \
  --non-interactive \
  --url "http://gitlab:5003" \
  --registration-token "YOUR_TOKEN" \
  --executor "shell" \
  --description "shell-runner" \
  --tag-list "shell,linux"
```

### 5. Configure ArgoCD

1. Login to ArgoCD: http://localhost:5010
   - Username: `admin`
   - Password: (from CREDENTIALS.txt)

2. Add Git repository:
   ```bash
   argocd repo add http://gitlab:5003/root/orgmgmt.git \
     --username root \
     --password YOUR_GITLAB_PASSWORD \
     --insecure-skip-server-verification
   ```

3. Create applications:
   ```bash
   # Development
   argocd app create orgmgmt-dev \
     --repo http://gitlab:5003/root/orgmgmt.git \
     --path gitops/dev \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace dev

   # Staging
   argocd app create orgmgmt-staging \
     --repo http://gitlab:5003/root/orgmgmt.git \
     --path gitops/staging \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace staging

   # Production
   argocd app create orgmgmt-prod \
     --repo http://gitlab:5003/root/orgmgmt.git \
     --path gitops/prod \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace prod
   ```

## Troubleshooting

### Common Issues

#### 1. Insufficient Memory

**Symptom:** Containers fail to start or crash frequently

**Solution:**
```bash
# Check available memory
free -h

# Stop unnecessary services
systemctl stop <service-name>

# Increase swap space
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 2. Port Already in Use

**Symptom:** "address already in use" errors

**Solution:**
```bash
# Check what's using the port
sudo ss -tulpn | grep :5003

# Stop the conflicting service
sudo systemctl stop <service-name>

# Or change the port in .env file
vi /root/aws.git/container/claudecode/ArgoCD/infrastructure/.env
```

#### 3. GitLab Takes Too Long to Start

**Symptom:** GitLab health checks timeout

**Solution:**
```bash
# Check GitLab logs
podman logs -f orgmgmt-gitlab

# GitLab can take 5-10 minutes on first start
# Wait longer or increase timeout in playbook

# Check GitLab status
podman exec orgmgmt-gitlab gitlab-ctl status
```

#### 4. ArgoCD Cannot Connect to Git

**Symptom:** ArgoCD fails to sync applications

**Solution:**
```bash
# Verify GitLab is accessible from ArgoCD container
podman exec argocd-server curl -I http://gitlab:5003

# Check network connectivity
podman network inspect argocd-network

# Verify repository URL
argocd repo list
```

#### 5. Build Failures

**Symptom:** Maven or npm builds fail

**Solution:**
```bash
# Check Maven installation
source /etc/profile.d/maven.sh
mvn --version

# Check Node.js installation
node --version
npm --version

# Clear caches
mvn clean
npm cache clean --force

# Build manually to see detailed errors
cd /root/aws.git/container/claudecode/ArgoCD/app/backend
mvn clean package

cd /root/aws.git/container/claudecode/ArgoCD/app/frontend
npm run build
```

#### 6. Nexus Admin Password Not Found

**Symptom:** Cannot find Nexus initial password

**Solution:**
```bash
# Wait for Nexus to fully start
sleep 60

# Try again
podman exec orgmgmt-nexus cat /nexus-data/admin.password

# Check Nexus logs
podman logs orgmgmt-nexus | grep -i password
```

### Recovery Procedures

#### Restart Individual Service

```bash
# Restart specific container
podman restart <container-name>

# Example
podman restart orgmgmt-gitlab
```

#### Restart All Services

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose restart
```

#### Clean Restart

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure

# Stop all services
podman-compose down

# Start services
podman-compose up -d

# Check status
podman ps
```

#### Complete Reset (DESTRUCTIVE)

**Warning:** This will delete all data!

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure

# Stop and remove containers
podman-compose down -v

# Remove all volumes
podman volume prune -f

# Remove all images (optional)
podman image prune -af

# Re-run setup
cd ../ansible
./bootstrap.sh
```

### Getting Help

#### Check Logs

```bash
# All containers
podman logs <container-name>

# Follow logs
podman logs -f <container-name>

# Last 100 lines
podman logs --tail 100 <container-name>

# Specific time range
podman logs --since 10m <container-name>
```

#### View Ansible Logs

```bash
# Latest bootstrap log
ls -lt /root/aws.git/container/claudecode/ArgoCD/logs/bootstrap-*.log | head -1

# View log
cat /root/aws.git/container/claudecode/ArgoCD/logs/bootstrap-*.log
```

#### Container Diagnostics

```bash
# Inspect container
podman inspect <container-name>

# Check container resources
podman stats <container-name>

# Execute commands in container
podman exec -it <container-name> /bin/bash
```

## Manual Setup

If automated setup fails or you prefer manual control:

### 1. Install Prerequisites

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/setup_complete_environment.yml --tags prerequisites
```

### 2. Start Infrastructure Only

```bash
ansible-playbook playbooks/deploy_infrastructure.yml
```

### 3. Configure Services

```bash
ansible-playbook playbooks/configure_podman_registry.yml
ansible-playbook playbooks/install_argocd.yml
```

### 4. Setup Applications

```bash
ansible-playbook playbooks/setup_application.yml
```

## Cleanup

### Stop Services (Preserve Data)

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose down
```

### Remove Specific Service

```bash
podman stop <container-name>
podman rm <container-name>
podman volume rm <volume-name>
```

### Complete Cleanup

```bash
cd /root/aws.git/container/claudecode/ArgoCD
./scripts/cleanup.sh --all
```

## Additional Resources

### Documentation

- [Main README](../README.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [API Documentation](../API.md)

### Scripts

- `bootstrap.sh` - Complete environment setup
- `verify-environment.sh` - Health check script
- `scripts/status.sh` - Detailed status information
- `scripts/logs.sh` - Centralized log viewing
- `scripts/backup.sh` - Backup data
- `scripts/restore.sh` - Restore from backup

### Ansible Playbooks

- `playbooks/setup_complete_environment.yml` - Master playbook
- `playbooks/deploy_infrastructure.yml` - Infrastructure only
- `playbooks/install_argocd.yml` - ArgoCD CLI
- `playbooks/configure_podman_registry.yml` - Registry configuration
- `playbooks/setup_application.yml` - Application setup

### Configuration Files

- `group_vars/all.yml` - All variables
- `inventory/hosts.yml` - Inventory configuration
- `ansible.cfg` - Ansible configuration

## Support

For issues, questions, or contributions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `tail -f logs/bootstrap-*.log`
3. Check container logs: `podman logs <container-name>`
4. Verify system resources: `free -h && df -h`
5. Review [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

## License

See [LICENSE](../LICENSE) file for details.
