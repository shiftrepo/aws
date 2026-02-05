# Infrastructure Setup Checklist

Use this checklist to ensure your infrastructure is properly configured and running.

## Pre-Deployment

- [ ] Podman is installed and running
- [ ] Podman Compose is installed
- [ ] Sufficient disk space available (minimum 20GB recommended)
- [ ] Ports are not in use by other services:
  - [ ] 5432 (PostgreSQL)
  - [ ] 5050 (pgAdmin)
  - [ ] 8081 (Nexus HTTP)
  - [ ] 8082 (Nexus Docker)
  - [ ] 5003 (GitLab HTTP)
  - [ ] 5005 (GitLab Registry)
  - [ ] 2222 (GitLab SSH)
  - [ ] 5010 (ArgoCD)
  - [ ] 6379 (Redis)

## Initial Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Update passwords in `.env` file:
  - [ ] POSTGRES_PASSWORD
  - [ ] PGADMIN_DEFAULT_PASSWORD
  - [ ] NEXUS_ADMIN_PASSWORD
  - [ ] GITLAB_ROOT_PASSWORD
  - [ ] ARGOCD_ADMIN_PASSWORD
- [ ] Review and customize other environment variables
- [ ] Ensure `gitops/` directory exists

## Deployment

- [ ] Run `./start.sh` or `podman-compose up -d`
- [ ] Wait for all services to start (5-10 minutes for GitLab)
- [ ] Check service status with `./status.sh` or `podman-compose ps`
- [ ] Verify all containers are healthy

## Post-Deployment Configuration

### PostgreSQL

- [ ] Verify database is running: `podman exec orgmgmt-postgres pg_isready`
- [ ] Confirm database exists: `podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "\l"`
- [ ] Test connection from application

### pgAdmin

- [ ] Access pgAdmin at http://localhost:5050
- [ ] Login with credentials from `.env`
- [ ] Add PostgreSQL server connection:
  - Host: `postgres`
  - Port: `5432`
  - Database: `orgmgmt`
  - Username: `orgmgmt_user`
  - Password: from `.env`
- [ ] Verify you can browse tables

### Nexus Repository

- [ ] Access Nexus at http://localhost:8081
- [ ] Retrieve initial admin password:
  ```bash
  podman exec orgmgmt-nexus cat /nexus-data/admin.password
  ```
- [ ] Complete setup wizard
- [ ] Change admin password
- [ ] Configure repositories:
  - [ ] Create Docker hosted repository
  - [ ] Create Maven hosted repository (if needed)
  - [ ] Create npm hosted repository (if needed)
- [ ] Enable Docker Bearer Token Realm (Security > Realms)
- [ ] Test Docker registry:
  ```bash
  podman login localhost:8082
  ```

### GitLab

- [ ] Access GitLab at http://localhost:5003
- [ ] Login as root with password from `.env`
- [ ] Change root password (recommended)
- [ ] Disable sign-up if not needed (Admin > Settings > General > Sign-up restrictions)
- [ ] Create test project
- [ ] Configure Container Registry settings
- [ ] Test Git clone/push operations

### GitLab Runner

- [ ] Get runner registration token from GitLab:
  - Go to Admin Area > CI/CD > Runners
  - Or Project Settings > CI/CD > Runners
- [ ] Register runner:
  ```bash
  podman exec -it orgmgmt-gitlab-runner gitlab-runner register \
    --non-interactive \
    --url "http://gitlab:5003" \
    --registration-token "YOUR_TOKEN" \
    --executor "shell" \
    --description "podman-runner" \
    --tag-list "docker,podman,shell" \
    --run-untagged="true" \
    --locked="false"
  ```
- [ ] Verify runner appears in GitLab UI (green dot)
- [ ] Run a test CI/CD pipeline

### ArgoCD

- [ ] Access ArgoCD at http://localhost:5010
- [ ] Get initial admin password:
  ```bash
  podman exec argocd-server argocd admin initial-password
  ```
- [ ] Login with username `admin` and retrieved password
- [ ] Change admin password (Settings > Accounts > admin > Update Password)
- [ ] Add Git repository:
  ```bash
  # Option 1: Via UI
  Settings > Repositories > Connect Repo

  # Option 2: Via CLI
  podman exec -it argocd-server argocd login localhost:8080 --insecure
  podman exec -it argocd-server argocd repo add http://gitlab:5003/group/repo.git
  ```
- [ ] Create test application
- [ ] Verify sync works correctly

## Verification Tests

### Health Checks

Run the following commands to verify each service:

```bash
# PostgreSQL
podman exec orgmgmt-postgres pg_isready -U orgmgmt_user

# Redis
podman exec argocd-redis redis-cli ping

# ArgoCD
curl -f http://localhost:5010/healthz

# GitLab
curl -f http://localhost:5003/-/health

# Nexus
curl -f http://localhost:8081/service/rest/v1/status
```

- [ ] All health checks pass
- [ ] All services respond on their respective ports

### Integration Tests

- [ ] Create a project in GitLab
- [ ] Commit code to GitLab
- [ ] Trigger CI/CD pipeline
- [ ] Build Docker image
- [ ] Push image to Nexus registry
- [ ] Deploy application with ArgoCD
- [ ] Application connects to PostgreSQL

## Security Hardening (Production)

- [ ] Enable HTTPS/TLS for all services
- [ ] Configure firewall rules
- [ ] Change all default passwords
- [ ] Enable two-factor authentication
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Review and restrict network access
- [ ] Enable audit logging
- [ ] Configure SELinux/AppArmor policies
- [ ] Implement secrets management (Vault, etc.)
- [ ] Regular security updates policy

## Backup Strategy

- [ ] Set up automated backups for:
  - [ ] PostgreSQL database
  - [ ] GitLab repositories
  - [ ] Nexus artifacts
  - [ ] ArgoCD configuration
- [ ] Test backup restoration process
- [ ] Document backup procedures
- [ ] Configure backup retention policy

## Monitoring Setup

- [ ] Configure health check monitoring
- [ ] Set up log aggregation
- [ ] Configure alerting for service failures
- [ ] Monitor disk usage
- [ ] Monitor memory usage
- [ ] Monitor CPU usage
- [ ] Track service response times

## Documentation

- [ ] Document custom configurations
- [ ] Document backup/restore procedures
- [ ] Document troubleshooting steps
- [ ] Create runbook for common operations
- [ ] Document service dependencies
- [ ] Create disaster recovery plan

## Maintenance

- [ ] Schedule regular updates
- [ ] Plan for database migrations
- [ ] Monitor volume growth
- [ ] Review logs regularly
- [ ] Test disaster recovery procedures
- [ ] Update documentation as needed

## Troubleshooting Resources

If you encounter issues, check:

1. Service logs: `podman-compose logs -f [service-name]`
2. Container status: `podman-compose ps`
3. Network connectivity: `podman network inspect argocd-network`
4. Volume status: `podman volume ls`
5. README.md troubleshooting section
6. Service-specific documentation

## Quick Commands Reference

```bash
# Start all services
./start.sh

# Check status
./status.sh

# Stop all services
./stop.sh

# View logs
podman-compose logs -f [service-name]

# Restart a service
podman-compose restart [service-name]

# Execute command in container
podman exec -it [container-name] [command]

# Backup volumes
podman run --rm -v [volume-name]:/source:ro -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /source .
```

## Completion

- [ ] All services are running and healthy
- [ ] All post-deployment configurations completed
- [ ] All verification tests passed
- [ ] Documentation updated
- [ ] Team trained on infrastructure
- [ ] Backup strategy implemented
- [ ] Monitoring configured

**Date Completed:** _______________

**Completed By:** _______________

**Sign-off:** _______________
