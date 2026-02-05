# Deployment Guide - ArgoCD CD Pipeline

**Version:** 1.0
**Date:** 2026-02-05

---

## 📋 Overview

This guide explains how to deploy the ArgoCD-based CD pipeline to any environment. The system is fully parameterized and environment-agnostic.

---

## 🎯 Key Features

✅ **Environment-Agnostic**: No hardcoded IPs, ports, or paths
✅ **Auto-Detection**: Automatically detects network configuration
✅ **Port Conflict Resolution**: Finds available ports if defaults are in use
✅ **Flexible Configuration**: All settings in one place
✅ **Documentation Generation**: Creates environment-specific docs
✅ **Easy Migration**: Move between environments without code changes

---

## 📦 Prerequisites

### System Requirements

- **OS**: RHEL 9, CentOS 9, Rocky Linux 9, or compatible
- **CPU**: 4 cores minimum (8 recommended)
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 50GB minimum (100GB recommended)

### Software Requirements

```bash
# Install required packages
sudo dnf install -y \
  podman \
  podman-compose \
  python3 \
  python3-pip \
  ansible-core \
  git \
  curl \
  jq \
  openssl \
  firewalld

# Install Ansible collections
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix
```

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo/container/claudecode/ArgoCD

# Or if already cloned
cd /path/to/ArgoCD
```

### Step 2: Environment Setup

```bash
# Run environment setup script
./scripts/setup-environment.sh

# This will:
# - Detect your network configuration
# - Check for port conflicts
# - Create config/environment.yml
# - Generate Ansible variables
```

### Step 3: Review Configuration

```bash
# Edit if needed
vim config/environment.yml

# Key settings to review:
# - network.public_ip (auto-detected)
# - network.private_ip (auto-detected)
# - ports.* (default or auto-adjusted)
# - git.repository_url (update to your repo)
# - authentication.* (passwords)
```

### Step 4: Deploy

```bash
# Full deployment
./scripts/setup.sh

# Or step-by-step:
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy_infrastructure.yml
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/complete_cd_pipeline.yml
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/setup_port_forwarding.yml
```

### Step 5: Verify

```bash
# Check service status
systemctl status k3s
podman ps
sudo kubectl get pods -A

# View credentials
cat docs/generated/show-credentials.sh

# Test services
curl http://localhost:5006/api/organizations
```

---

## ⚙️ Configuration

### Environment Configuration File

All environment-specific settings are in `config/environment.yml`:

```yaml
network:
  public_ip: "13.219.96.72"        # Your public IP
  private_ip: "10.0.1.191"         # Your private IP
  domain: ""                        # Optional domain

ports:
  postgres_external: 5001
  pgadmin: 5002
  kubernetes_dashboard: 5004
  frontend: 5006
  argocd: 5010
  nexus_http: 8000
  # ... more ports

directories:
  base_dir: "{{ playbook_dir | dirname }}"
  data_dir: "{{ playbook_dir | dirname }}/infrastructure/volumes"
  # ... more directories

git:
  repository_url: "https://github.com/yourusername/yourrepo.git"
  branch: "main"
  manifests_path: "container/claudecode/ArgoCD/gitops/orgmgmt-frontend"

authentication:
  pgadmin:
    email: "admin@orgmgmt.local"
    password: "password"  # Change in production
  nexus:
    username: "admin"
    password: "admin123"  # Change in production
  # ... more credentials
```

### Customization

#### Change Ports

Edit `config/environment.yml`:

```yaml
ports:
  kubernetes_dashboard: 8443  # Changed from 5004
  frontend: 3000              # Changed from 5006
  # ...
```

#### Change Database Credentials

```yaml
database:
  name: "myapp"              # Changed from orgmgmt
  user: "myapp_user"
  password: "{{ lookup('env', 'DB_PASSWORD') }}"  # From environment variable
```

#### Use Custom Domain

```yaml
network:
  domain: "example.com"      # Use domain instead of IP

  # Services will be accessible at:
  # - https://dashboard.example.com
  # - http://app.example.com
```

#### Enable HTTPS

```yaml
features:
  https_enabled: true

# Provide SSL certificates in:
# - infrastructure/config/ssl/certificate.crt
# - infrastructure/config/ssl/private.key
```

---

## 🔧 Advanced Configuration

### Using Environment Variables

Override any setting with environment variables:

```bash
# Export variables
export DB_PASSWORD="super_secure_password"
export NEXUS_PASSWORD="another_secure_password"
export PUBLIC_IP="1.2.3.4"

# Run setup
./scripts/setup-environment.sh
```

### Multiple Environments

Create separate configurations:

```bash
# Development
cp config/environment.yml config/environment-dev.yml

# Staging
cp config/environment.yml config/environment-staging.yml

# Production
cp config/environment.yml config/environment-prod.yml

# Deploy to specific environment
ansible-playbook \
  -i ansible/inventory/hosts.yml \
  -e @config/environment-prod.yml \
  ansible/playbooks/deploy_infrastructure.yml
```

### Custom Inventory

Create custom Ansible inventory for remote deployment:

```yaml
# ansible/inventory/production.yml
all:
  hosts:
    prod-server:
      ansible_host: 192.168.1.100
      ansible_user: deployment
      ansible_become: yes
  vars:
    environment_config_file: "{{ playbook_dir }}/../config/environment-prod.yml"
```

Deploy remotely:

```bash
ansible-playbook \
  -i ansible/inventory/production.yml \
  ansible/playbooks/deploy_infrastructure.yml
```

---

## 🌐 Network Configuration

### Firewall

Ports are automatically opened if firewalld is running:

```bash
# Public ports (exposed externally):
- Kubernetes Dashboard: 5004
- ArgoCD: 5010
- Frontend App: 5006
- Nexus: 8000

# Private ports (internal only):
- PostgreSQL: 5001
- pgAdmin: 5002
- Container Registry: 5000
```

### Custom Firewall Rules

```bash
# Open additional port
sudo firewall-cmd --permanent --add-port=9090/tcp
sudo firewall-cmd --reload

# Or add to config/environment.yml:
firewall:
  public_ports:
    - "5004/tcp"
    - "9090/tcp"  # Custom port
```

### SELinux

If SELinux is enabled (default on RHEL/CentOS):

```bash
# Allow container networking
sudo setsebool -P container_manage_cgroup on

# Allow port binding
sudo semanage port -a -t http_port_t -p tcp 5006

# Or disable SELinux (not recommended for production)
sudo setenforce 0
```

---

## 🔐 Security

### Password Management

**Development:**
- Use simple passwords in `config/environment.yml`
- Credentials stored in plain text

**Production:**
- Use environment variables
- Integrate with secrets management (HashiCorp Vault, AWS Secrets Manager)
- Enable HTTPS
- Rotate passwords regularly

### Environment Variables

```bash
# Set passwords via environment
export DB_PASSWORD="$(openssl rand -base64 24)"
export NEXUS_PASSWORD="$(openssl rand -base64 24)"
export PGADMIN_PASSWORD="$(openssl rand -base64 24)"

# Run setup
./scripts/setup-environment.sh
```

### Ansible Vault

Encrypt sensitive data:

```bash
# Create encrypted file
ansible-vault create config/secrets.yml

# Content:
---
database_password: "super_secure_password"
nexus_password: "another_secure_password"

# Use in playbook
ansible-playbook \
  -i ansible/inventory/hosts.yml \
  -e @config/secrets.yml \
  --ask-vault-pass \
  ansible/playbooks/deploy_infrastructure.yml
```

---

## 📊 Monitoring and Logging

### Service Status

```bash
# Check all services
./scripts/status.sh

# Check specific service
systemctl status k3s
podman ps
sudo kubectl get pods -A
```

### Logs

```bash
# View all logs
./scripts/logs.sh

# Specific service
./scripts/logs.sh orgmgmt-postgres
./scripts/logs.sh argocd-server

# Kubernetes logs
sudo kubectl logs -f deployment/orgmgmt-frontend -n default
```

### Health Checks

```bash
# Test all endpoints
curl http://localhost:5006/api/organizations
curl http://localhost:8000/service/rest/v1/status
curl -k https://localhost:5004/
```

---

## 🔄 Migration Between Environments

### Export Configuration

```bash
# On source environment
./scripts/backup.sh

# This creates:
# - Database backup
# - Configuration files
# - Container images
# - GitOps manifests
```

### Import to New Environment

```bash
# 1. Copy repository
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo/container/claudecode/ArgoCD

# 2. Setup new environment
./scripts/setup-environment.sh

# 3. Update configuration
vim config/environment.yml
# - Update IP addresses
# - Update domain names
# - Update passwords

# 4. Deploy
./scripts/setup.sh

# 5. Restore data (if needed)
./scripts/restore.sh /path/to/backup.tar.gz
```

---

## 🐛 Troubleshooting

### Port Conflicts

If ports are in use:

```bash
# Check what's using the port
sudo ss -tlnp | grep :5004

# Option 1: Stop conflicting service
sudo systemctl stop service-name

# Option 2: Use different port
vim config/environment.yml
# Change port number

# Re-run setup
./scripts/setup-environment.sh --force
```

### Service Won't Start

```bash
# Check logs
./scripts/logs.sh service-name

# Check container status
podman ps -a

# Restart service
podman restart service-name

# Or restart all
cd infrastructure
podman-compose restart
```

### Network Issues

```bash
# Check firewall
sudo firewall-cmd --list-all

# Check SELinux
sudo getenforce
sudo ausearch -m AVC -ts recent

# Test connectivity
curl -v http://localhost:5006
```

### ArgoCD Sync Failures

```bash
# Check ArgoCD logs
sudo kubectl logs -f deployment/argocd-application-controller -n argocd

# Manual sync
argocd app sync orgmgmt-frontend

# Reset sync
argocd app delete orgmgmt-frontend
argocd app create orgmgmt-frontend --repo https://... --path gitops/...
```

---

## 📚 Documentation

After deployment, documentation is auto-generated:

```
SERVICE-ACCESS-GUIDE.md          - Service URLs and credentials
QUICKSTART.md                    - Quick start guide
HOST-OS-COMMANDS.md              - Command reference
docs/generated/
  ├── ENVIRONMENT-REPORT.md      - Environment-specific report
  └── show-credentials.sh        - Display all credentials
```

View credentials:

```bash
./docs/generated/show-credentials.sh
```

---

## 🎓 Best Practices

### Development Environment

- Use default ports
- Simple passwords
- Enable all features for testing
- Disable HTTPS (self-signed certs)

### Staging Environment

- Use production-like configuration
- Strong passwords
- Enable monitoring
- Test deployment procedures

### Production Environment

- Use custom domain
- Strong, rotated passwords
- Enable HTTPS with valid certificates
- Restrict firewall access
- Enable monitoring and alerting
- Regular backups
- Disaster recovery plan

---

## 🆘 Support

### Documentation

- `README.md` - Main documentation
- `SERVICE-ACCESS-GUIDE.md` - Service access
- `HOST-OS-COMMANDS.md` - Command reference
- `TROUBLESHOOTING.md` - Common issues

### Logs

```bash
# Service logs
./scripts/logs.sh [service]

# System logs
sudo journalctl -u k3s -f
sudo journalctl -u k3s-dashboard-forward -f
```

### Cleanup and Restart

```bash
# Clean everything
./scripts/cleanup.sh --all

# Fresh start
./scripts/setup.sh
```

---

## 📝 Summary

This deployment is:

✅ **Portable** - Deploy anywhere
✅ **Flexible** - Customize everything
✅ **Automated** - One-command setup
✅ **Documented** - Auto-generated docs
✅ **Secure** - Multiple authentication options
✅ **Monitored** - Built-in health checks

**Time to Deploy:** ~10 minutes
**Time to Migrate:** ~5 minutes
**Supported Platforms:** Any Linux with Podman

---

**Ready to deploy to any environment!** 🚀
