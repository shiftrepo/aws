# Ansible Playbooks - Usage Examples

This document provides practical examples for common scenarios using the Ansible playbooks.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Production Deployment](#production-deployment)
- [Development Workflow](#development-workflow)
- [Maintenance Operations](#maintenance-operations)
- [Troubleshooting Scenarios](#troubleshooting-scenarios)
- [Advanced Usage](#advanced-usage)

## Basic Usage

### Complete Setup from Scratch

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# Run all playbooks in sequence
ansible-playbook playbooks/site.yml
```

**Timeline:**
- Registry configuration: ~30 seconds
- ArgoCD CLI installation: ~1-2 minutes
- Infrastructure deployment: ~10-15 minutes (GitLab takes longest)
- Application setup: ~2-3 minutes

**Total time:** 15-20 minutes

### Quick Development Setup

Skip the confirmation prompt for automated runs:

```bash
ANSIBLE_AUTO_CONTINUE=true ansible-playbook playbooks/site.yml
```

### Selective Component Setup

Only setup what you need:

```bash
# Only configure registry and install CLI
ansible-playbook playbooks/site.yml --tags registry,cli

# Only deploy infrastructure
ansible-playbook playbooks/site.yml --tags infrastructure

# Only setup applications
ansible-playbook playbooks/site.yml --tags application
```

## Production Deployment

### Pre-Deployment Validation

Check syntax before running:

```bash
# Validate all playbooks
ansible-playbook playbooks/site.yml --syntax-check

# Run in check mode (dry-run)
ansible-playbook playbooks/site.yml --check

# List all tasks that would run
ansible-playbook playbooks/site.yml --list-tasks
```

### Staged Deployment

Deploy components one at a time with verification:

```bash
# Stage 1: Registry and CLI
ansible-playbook playbooks/configure_podman_registry.yml
ansible-playbook playbooks/install_argocd.yml

# Verify
argocd version --client
podman info | grep -i insecure

# Stage 2: Infrastructure
ansible-playbook playbooks/deploy_infrastructure.yml

# Verify services
podman ps --format "table {{.Names}}\t{{.Status}}"
curl http://localhost:5010/healthz

# Stage 3: Application setup
ansible-playbook playbooks/setup_application.yml

# Verify
ARGOCD_PASS=$(podman exec argocd-server argocd admin initial-password | head -n1)
argocd login localhost:5010 --insecure --username admin --password $ARGOCD_PASS
argocd app list
```

### Monitoring Deployment Progress

Run with verbose output to monitor progress:

```bash
# Level 1 verbosity (recommended)
ansible-playbook playbooks/site.yml -v

# Level 2 verbosity (more details)
ansible-playbook playbooks/site.yml -vv

# Level 3 verbosity (debug level)
ansible-playbook playbooks/site.yml -vvv
```

Save output to a log file:

```bash
ansible-playbook playbooks/site.yml -v 2>&1 | tee deployment-$(date +%Y%m%d-%H%M%S).log
```

## Development Workflow

### Daily Development Setup

Start your environment:

```bash
# Quick start (assumes already deployed once)
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose up -d

# Wait for services
sleep 60

# Verify
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Re-deploy After Changes

If you modified infrastructure configuration:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/ansible

# Stop existing infrastructure
cd ../infrastructure
podman-compose down

# Re-deploy
cd ../ansible
ansible-playbook playbooks/deploy_infrastructure.yml
```

### Update Single Service

Update only specific services:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure

# Restart specific service
podman-compose restart argocd-server

# Or rebuild and restart
podman-compose up -d --force-recreate argocd-server
```

### Reset Environment

Complete environment reset:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure

# Stop and remove all containers
podman-compose down

# Remove volumes (WARNING: deletes all data)
podman volume prune -f

# Re-deploy everything
cd ../ansible
ansible-playbook playbooks/site.yml
```

## Maintenance Operations

### Update ArgoCD CLI

Install a newer version:

```bash
# Edit playbook to change version
cd /root/aws.git/container/claudecode/ArgoCD/ansible
vi playbooks/install_argocd.yml
# Change: argocd_version: "v2.11.0"

# Run installation playbook
ansible-playbook playbooks/install_argocd.yml

# Verify
argocd version --client
```

### Backup Configuration

Backup before making changes:

```bash
# Backup volumes
podman volume ls
for vol in $(podman volume ls -q | grep orgmgmt); do
    echo "Backing up $vol..."
    podman run --rm -v $vol:/data -v /backup:/backup alpine tar czf /backup/$vol-$(date +%Y%m%d).tar.gz -C /data .
done

# Backup configurations
tar czf ansible-backup-$(date +%Y%m%d).tar.gz /root/aws.git/container/claudecode/ArgoCD/ansible/
tar czf infrastructure-backup-$(date +%Y%m%d).tar.gz /root/aws.git/container/claudecode/ArgoCD/infrastructure/
```

### Health Check Routine

Regular health checks:

```bash
#!/bin/bash
# health-check.sh

echo "Checking PostgreSQL..."
podman exec orgmgmt-postgres pg_isready -U orgmgmt_user

echo "Checking Nexus..."
curl -s http://localhost:8081/service/rest/v1/status | jq .

echo "Checking GitLab..."
curl -s http://localhost:5003/-/health

echo "Checking ArgoCD..."
curl -s http://localhost:5010/healthz

echo "Checking containers..."
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"
```

Make it executable and run:

```bash
chmod +x health-check.sh
./health-check.sh
```

## Troubleshooting Scenarios

### Scenario 1: GitLab Not Starting

```bash
# Check logs
podman logs -f orgmgmt-gitlab

# Common issue: Not enough memory
# Solution: Increase container memory or wait longer

# Restart GitLab
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
podman-compose restart gitlab

# Wait for GitLab (takes 5-10 minutes)
watch -n 10 'curl -s http://localhost:5003/-/health'
```

### Scenario 2: ArgoCD Password Not Working

```bash
# Get fresh password
ARGOCD_PASS=$(podman exec argocd-server argocd admin initial-password | head -n1)
echo "Password: $ARGOCD_PASS"

# Change password (recommended)
argocd login localhost:5010 --insecure --username admin --password $ARGOCD_PASS
argocd account update-password --current-password $ARGOCD_PASS --new-password NewSecurePassword123!
```

### Scenario 3: Registry Login Fails

```bash
# Check GitLab is running
curl http://localhost:5003/-/health

# Check registry configuration
cat /etc/containers/registries.conf.d/gitlab.conf

# Re-run registry configuration
cd /root/aws.git/container/claudecode/ArgoCD/ansible
ansible-playbook playbooks/configure_podman_registry.yml

# Try login again
podman login localhost:5005 --username root --password GitLabRoot123! --tls-verify=false
```

### Scenario 4: Port Conflicts

```bash
# Find conflicting process
sudo lsof -i :5010  # Replace with your port

# Kill conflicting process
sudo kill -9 <PID>

# Or change port in .env file
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
vi .env
# Change: ARGOCD_SERVER_PORT=5011

# Restart services
podman-compose down
podman-compose up -d
```

### Scenario 5: Database Connection Issues

```bash
# Check PostgreSQL is running
podman ps | grep postgres

# Test connection
podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "SELECT version();"

# Check logs
podman logs orgmgmt-postgres

# Restart PostgreSQL
podman-compose restart postgres
```

## Advanced Usage

### Custom Variable Override

Override variables at runtime:

```bash
ansible-playbook playbooks/deploy_infrastructure.yml \
  -e "compose_file_path=/custom/path/podman-compose.yml"
```

### Run Specific Tasks

Use `--start-at-task` to resume from a specific point:

```bash
ansible-playbook playbooks/deploy_infrastructure.yml \
  --start-at-task "Wait for PostgreSQL to be healthy"
```

### Parallel Execution

Run multiple independent playbooks in parallel:

```bash
# In separate terminals
ansible-playbook playbooks/configure_podman_registry.yml &
ansible-playbook playbooks/install_argocd.yml &
wait
```

### Integration with CI/CD

Example GitLab CI job:

```yaml
deploy_infrastructure:
  stage: deploy
  script:
    - cd /root/aws.git/container/claudecode/ArgoCD/ansible
    - ANSIBLE_AUTO_CONTINUE=true ansible-playbook playbooks/site.yml -v
  tags:
    - ansible
  only:
    - main
```

### Custom Inventory

Use a different inventory:

```bash
# Create custom inventory
cat > custom-inventory.yml << EOF
all:
  hosts:
    server1:
      ansible_host: 192.168.1.100
      ansible_user: admin
EOF

# Run with custom inventory
ansible-playbook -i custom-inventory.yml playbooks/deploy_infrastructure.yml
```

### Ansible Vault for Secrets

Encrypt sensitive data:

```bash
# Create encrypted vars file
ansible-vault create secrets.yml
# Add content:
# gitlab_root_password: SuperSecretPassword123!
# postgres_password: VerySecurePassword456!

# Use in playbook
ansible-playbook playbooks/setup_application.yml \
  -e @secrets.yml \
  --ask-vault-pass
```

### Conditional Execution

Skip certain tasks based on conditions:

```bash
# Skip health checks (faster but risky)
ansible-playbook playbooks/deploy_infrastructure.yml \
  --skip-tags health-checks

# Only run health checks
ansible-playbook playbooks/deploy_infrastructure.yml \
  --tags health-checks
```

## Performance Optimization

### Faster Deployment

```bash
# Disable fact gathering (if not needed)
ansible-playbook playbooks/site.yml --skip-tags facts

# Increase parallelism
ANSIBLE_FORKS=10 ansible-playbook playbooks/site.yml

# Use cached facts
# Already configured in ansible.cfg
```

### Resource Monitoring

Monitor resource usage during deployment:

```bash
# In separate terminal
watch -n 2 'podman stats --no-stream'

# Or with formatting
watch -n 2 'podman stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
```

## Best Practices

### 1. Version Control Integration

```bash
# Always commit before running
cd /root/aws.git/container/claudecode/ArgoCD
git add ansible/
git commit -m "Update Ansible playbooks"

# Tag releases
git tag -a v1.0.0 -m "Initial Ansible automation release"
```

### 2. Documentation

Document your runs:

```bash
# Create run log
cat > ansible-run-$(date +%Y%m%d).log << EOF
Date: $(date)
User: $(whoami)
Purpose: Initial deployment
Notes: First production deployment
EOF

ansible-playbook playbooks/site.yml -v 2>&1 | tee -a ansible-run-$(date +%Y%m%d).log
```

### 3. Testing

Always test in check mode first:

```bash
# Check mode
ansible-playbook playbooks/site.yml --check

# Diff mode (shows changes)
ansible-playbook playbooks/site.yml --check --diff
```

### 4. Rollback Plan

Always have a rollback ready:

```bash
# Before deployment
podman ps -a > containers-before.txt
podman volume ls > volumes-before.txt

# After issues
podman-compose down
# Restore from backup
# Re-run ansible-playbook
```

## Conclusion

These examples cover the most common scenarios. For more advanced use cases, refer to:
- [Ansible Documentation](https://docs.ansible.com/)
- Main README.md in this directory
- QUICKSTART.md for quick reference

Remember to always:
- Test in non-production first
- Keep backups
- Document your changes
- Monitor during deployment
- Verify after completion
