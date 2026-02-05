# Ansible Automation Playbooks

This directory contains Ansible playbooks for automating the deployment and configuration of the ArgoCD infrastructure and application stack.

## Directory Structure

```
ansible/
├── ansible.cfg                           # Ansible configuration
├── inventory/
│   └── hosts.yml                         # Inventory file (localhost)
├── playbooks/
│   ├── site.yml                          # Master playbook (runs all)
│   ├── configure_podman_registry.yml     # Configure insecure registry
│   ├── install_argocd.yml                # Install ArgoCD CLI
│   ├── deploy_infrastructure.yml         # Deploy with podman-compose
│   └── setup_application.yml             # Initialize application components
└── README.md                             # This file
```

## Prerequisites

### System Requirements
- RHEL/CentOS/Fedora or compatible Linux distribution
- Python 3.x
- Ansible 2.9 or later
- Podman
- Podman Compose
- sudo/root access for certain operations

### Install Prerequisites

```bash
# Install Ansible (on RHEL/CentOS)
sudo dnf install ansible -y

# Install Ansible (on Ubuntu/Debian)
sudo apt install ansible -y

# Install Podman and Podman Compose
sudo dnf install podman podman-compose -y
```

## Playbooks Overview

### 1. site.yml (Master Playbook)
Orchestrates all playbooks in the correct order:
1. Configure Podman insecure registry
2. Install ArgoCD CLI
3. Deploy infrastructure
4. Setup application components

**Usage:**
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/site.yml
```

**Skip confirmation prompt:**
```bash
ANSIBLE_AUTO_CONTINUE=true ansible-playbook playbooks/site.yml
```

**Run specific steps using tags:**
```bash
ansible-playbook playbooks/site.yml --tags registry
ansible-playbook playbooks/site.yml --tags cli
ansible-playbook playbooks/site.yml --tags infrastructure
ansible-playbook playbooks/site.yml --tags application
```

### 2. configure_podman_registry.yml
Configures Podman to trust the insecure GitLab container registry.

**Features:**
- Creates `/etc/containers/registries.conf.d/gitlab.conf`
- Configures `localhost:5005` as insecure registry
- Creates helper script for registry login
- Restarts Podman socket if needed

**Usage:**
```bash
ansible-playbook playbooks/configure_podman_registry.yml
```

**Helper script created:**
```bash
/usr/local/bin/gitlab-registry-login
```

### 3. install_argocd.yml
Downloads and installs the ArgoCD CLI tool.

**Features:**
- Downloads ArgoCD CLI v2.10.0
- Installs to `/usr/local/bin/argocd`
- Makes binary executable
- Verifies installation
- Idempotent (skips if already installed)

**Usage:**
```bash
ansible-playbook playbooks/install_argocd.yml
```

**Verify installation:**
```bash
argocd version --client
```

### 4. deploy_infrastructure.yml
Deploys the complete infrastructure stack using podman-compose.

**Features:**
- Checks prerequisites (podman, podman-compose)
- Stops existing containers
- Starts all services with `podman-compose up -d`
- Waits for services to be healthy:
  - PostgreSQL
  - Nexus
  - GitLab
  - ArgoCD
- Displays access information

**Usage:**
```bash
ansible-playbook playbooks/deploy_infrastructure.yml
```

**Services Deployed:**
- PostgreSQL (port 5432)
- pgAdmin (port 5050)
- Nexus (port 8081)
- GitLab (port 5003)
- GitLab Registry (port 5005)
- ArgoCD Server (port 5010)
- ArgoCD Redis, Repo Server, Application Controller

### 5. setup_application.yml
Initializes and configures application components.

**Features:**
- Verifies GitLab API accessibility
- Checks Nexus status and retrieves initial password
- Retrieves ArgoCD admin password
- Logs into ArgoCD
- Tests database connectivity
- Provides configuration guidance

**Usage:**
```bash
ansible-playbook playbooks/setup_application.yml
```

**Manual Steps Required:**
1. Configure GitLab projects and runners
2. Set up Nexus repositories (Maven, npm)
3. Create ArgoCD applications
4. Run database migrations

## Quick Start

### Complete Setup (All Steps)
```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/site.yml
```

### Individual Components

**Only configure registry:**
```bash
ansible-playbook playbooks/configure_podman_registry.yml
```

**Only install ArgoCD CLI:**
```bash
ansible-playbook playbooks/install_argocd.yml
```

**Only deploy infrastructure:**
```bash
ansible-playbook playbooks/deploy_infrastructure.yml
```

**Only setup applications:**
```bash
ansible-playbook playbooks/setup_application.yml
```

## Service Access Information

After successful deployment:

### PostgreSQL
- **Host:** localhost:5432
- **Database:** orgmgmt
- **User:** orgmgmt_user
- **Password:** SecurePassword123!

### pgAdmin
- **URL:** http://localhost:5050
- **Email:** admin@orgmgmt.local
- **Password:** AdminPassword123!

### Nexus Repository Manager
- **URL:** http://localhost:8081
- **Username:** admin
- **Password:** Check `/nexus-data/admin.password` in container
  ```bash
  podman exec orgmgmt-nexus cat /nexus-data/admin.password
  ```

### GitLab
- **URL:** http://localhost:5003
- **Username:** root
- **Password:** GitLabRoot123!
- **Registry:** http://localhost:5005

### ArgoCD
- **URL:** http://localhost:5010
- **Username:** admin
- **Password:** Get with command:
  ```bash
  podman exec argocd-server argocd admin initial-password
  ```

## Common Operations

### Check Running Containers
```bash
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Container Logs
```bash
podman logs -f orgmgmt-postgres
podman logs -f orgmgmt-gitlab
podman logs -f argocd-server
```

### Stop Infrastructure
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose down
```

### Start Infrastructure
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose up -d
```

### Login to GitLab Registry
```bash
podman login localhost:5005 --username root --password GitLabRoot123! --tls-verify=false
```

Or use the helper script:
```bash
/usr/local/bin/gitlab-registry-login
```

### Login to ArgoCD CLI
```bash
# Get password first
ARGOCD_PASSWORD=$(podman exec argocd-server argocd admin initial-password | head -n1)

# Login
argocd login localhost:5010 --insecure --username admin --password $ARGOCD_PASSWORD
```

## Ansible Options

### Dry Run (Check Mode)
Preview changes without making them:
```bash
ansible-playbook playbooks/site.yml --check
```

### Verbose Output
Increase verbosity for debugging:
```bash
ansible-playbook playbooks/site.yml -v      # verbose
ansible-playbook playbooks/site.yml -vv     # more verbose
ansible-playbook playbooks/site.yml -vvv    # very verbose
```

### List Tasks
Show all tasks without running them:
```bash
ansible-playbook playbooks/site.yml --list-tasks
```

### List Tags
Show available tags:
```bash
ansible-playbook playbooks/site.yml --list-tags
```

### Syntax Check
Verify playbook syntax:
```bash
ansible-playbook playbooks/site.yml --syntax-check
```

## Troubleshooting

### Issue: Podman not found
```bash
# Install Podman
sudo dnf install podman -y
```

### Issue: Podman Compose not found
```bash
# Install Podman Compose
sudo dnf install podman-compose -y
# Or with pip
pip3 install podman-compose
```

### Issue: Service not healthy
Check service logs:
```bash
podman logs <container-name>
```

Restart specific service:
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose restart <service-name>
```

### Issue: Permission denied
Run with sudo or as root:
```bash
sudo ansible-playbook playbooks/site.yml
```

### Issue: Port already in use
Stop conflicting service or change port in `.env` file:
```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
vi .env  # Edit port numbers
podman-compose down
podman-compose up -d
```

### Issue: Registry login fails
Ensure GitLab is running and healthy:
```bash
curl http://localhost:5003/-/health
```

Wait for GitLab to fully start (may take 5-10 minutes).

## Environment Variables

Create a `.env` file in the infrastructure directory to customize settings:

```bash
# PostgreSQL
POSTGRES_VERSION=16-alpine
POSTGRES_DB=orgmgmt
POSTGRES_USER=orgmgmt_user
POSTGRES_PASSWORD=SecurePassword123!
POSTGRES_PORT=5432

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@orgmgmt.local
PGADMIN_DEFAULT_PASSWORD=AdminPassword123!
PGADMIN_PORT=5050

# Nexus
NEXUS_VERSION=3.63.0
NEXUS_HTTP_PORT=8081
NEXUS_DOCKER_PORT=8082

# GitLab
GITLAB_VERSION=latest
GITLAB_EXTERNAL_URL=http://localhost:5003
GITLAB_REGISTRY_EXTERNAL_URL=http://localhost:5005
GITLAB_ROOT_PASSWORD=GitLabRoot123!
GITLAB_HTTP_PORT=5003
GITLAB_REGISTRY_PORT=5005
GITLAB_SSH_PORT=2222

# ArgoCD
ARGOCD_VERSION=v2.10.0
ARGOCD_SERVER_PORT=5010
ARGOCD_SERVER_INSECURE=true
```

## Best Practices

1. **Idempotency:** All playbooks are designed to be idempotent - safe to run multiple times
2. **Error Handling:** Tasks include proper error handling with `failed_when` and `ignore_errors`
3. **Health Checks:** Services are verified to be healthy before proceeding
4. **Logging:** All operations include debug output for visibility
5. **Backups:** Existing configurations are backed up before modification

## Security Considerations

**WARNING:** The default passwords in this setup are for development/testing only.

For production use:
1. Change all default passwords
2. Enable TLS for all services
3. Use proper certificate management
4. Restrict network access with firewall rules
5. Use secrets management (Vault, etc.)
6. Enable authentication and authorization
7. Regular security updates

## Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [Podman Documentation](https://docs.podman.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitLab Documentation](https://docs.gitlab.com/)
- [Nexus Documentation](https://help.sonatype.com/repomanager3)

## Support

For issues or questions:
1. Check container logs: `podman logs <container-name>`
2. Verify services are running: `podman ps`
3. Check Ansible verbose output: `ansible-playbook -vvv`
4. Review playbook tasks and error messages

## License

This project is part of the ArgoCD infrastructure setup and follows the same license as the parent project.
