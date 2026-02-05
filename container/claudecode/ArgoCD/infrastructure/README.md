# Infrastructure Setup with Podman Compose

This directory contains a complete infrastructure setup for the Organization Management System using Podman Compose. It includes all necessary services for development, CI/CD, and deployment.

## Services Overview

The infrastructure includes the following services:

### Core Services
- **PostgreSQL 16** - Primary database
- **pgAdmin 4** - Database management interface
- **Nexus Repository 3** - Artifact repository and Docker registry
- **GitLab CE** - Source control and CI/CD platform
- **GitLab Runner** - CI/CD job executor

### ArgoCD Services
- **ArgoCD Server** - API server and web UI
- **ArgoCD Application Controller** - Application reconciliation
- **ArgoCD Repo Server** - Repository management
- **Redis** - ArgoCD data store

## Quick Start

### 1. Prerequisites

Ensure you have the following installed:
- Podman 4.0 or higher
- Podman Compose 1.0 or higher

```bash
# Check versions
podman --version
podman-compose --version
```

### 2. Configure Environment

Copy the example environment file and customize it:

```bash
cd /root/aws.git/container/claudecode/ArgoCD/infrastructure
cp .env.example .env
# Edit .env with your preferred settings
nano .env
```

**IMPORTANT:** Change all default passwords in production!

### 3. Create GitOps Directory

ArgoCD requires a gitops directory to be mounted:

```bash
mkdir -p gitops
```

### 4. Start All Services

```bash
# Start all services in detached mode
podman-compose up -d

# View logs
podman-compose logs -f

# View logs for specific service
podman-compose logs -f argocd-server
```

### 5. Stop Services

```bash
# Stop all services
podman-compose down

# Stop and remove volumes (WARNING: destroys all data)
podman-compose down -v
```

## Port Mappings

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| PostgreSQL | 5432 | TCP | Database connection |
| pgAdmin | 5050 | HTTP | Database management UI |
| Nexus HTTP | 8081 | HTTP | Repository manager UI |
| Nexus Docker | 8082 | HTTP | Docker registry |
| GitLab HTTP | 5003 | HTTP | GitLab web interface |
| GitLab Registry | 5005 | HTTP | Container registry |
| GitLab SSH | 2222 | SSH | Git SSH access |
| ArgoCD Server | 5010 | HTTP | ArgoCD web UI & API |
| Redis | 6379 | TCP | ArgoCD cache (internal) |

## Default Credentials

### PostgreSQL
- **Host:** localhost:5432
- **Database:** orgmgmt
- **Username:** orgmgmt_user
- **Password:** SecurePassword123!

### pgAdmin
- **URL:** http://localhost:5050
- **Email:** admin@orgmgmt.local
- **Password:** AdminPassword123!

### Nexus Repository
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

### ArgoCD
- **URL:** http://localhost:5010
- **Username:** admin
- **Password:** Get initial password with:
  ```bash
  podman exec argocd-server argocd admin initial-password
  ```

## Volume Information

All data is persisted in named volumes:

| Volume | Purpose | Location |
|--------|---------|----------|
| orgmgmt-postgres-data | PostgreSQL database files | /var/lib/postgresql/data |
| orgmgmt-pgadmin-data | pgAdmin configuration | /var/lib/pgadmin |
| orgmgmt-nexus-data | Nexus artifacts & config | /nexus-data |
| orgmgmt-gitlab-config | GitLab configuration | /etc/gitlab |
| orgmgmt-gitlab-logs | GitLab logs | /var/log/gitlab |
| orgmgmt-gitlab-data | GitLab repositories & data | /var/opt/gitlab |
| orgmgmt-gitlab-runner-config | Runner configuration | /etc/gitlab-runner |
| argocd-redis-data | Redis data files | /data |
| argocd-repo-data | Repository cache | /app/config |
| argocd-controller-data | Controller state | /app/config |
| argocd-server-data | Server configuration | /app/config |

### Volume Management

```bash
# List all volumes
podman volume ls

# Inspect a volume
podman volume inspect orgmgmt-postgres-data

# Backup a volume
podman run --rm -v orgmgmt-postgres-data:/source:ro -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /source .

# Restore a volume
podman run --rm -v orgmgmt-postgres-data:/target -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /target
```

## Health Check Commands

### Check All Services

```bash
podman-compose ps
```

### Individual Service Health

```bash
# PostgreSQL
podman exec orgmgmt-postgres pg_isready -U orgmgmt_user

# Redis
podman exec argocd-redis redis-cli ping

# ArgoCD Server
curl -f http://localhost:5010/healthz

# GitLab
curl -f http://localhost:5003/-/health

# Nexus
curl -f http://localhost:8081/service/rest/v1/status
```

### View Service Logs

```bash
# All services
podman-compose logs

# Specific service with follow
podman-compose logs -f postgres

# Last 100 lines
podman-compose logs --tail=100 argocd-server
```

## Post-Installation Configuration

### 1. Configure pgAdmin

1. Access pgAdmin at http://localhost:5050
2. Login with credentials from .env
3. Add PostgreSQL server:
   - Host: postgres
   - Port: 5432
   - Database: orgmgmt
   - Username: orgmgmt_user
   - Password: from .env

### 2. Configure Nexus

1. Access Nexus at http://localhost:8081
2. Get admin password: `podman exec orgmgmt-nexus cat /nexus-data/admin.password`
3. Complete setup wizard
4. Create Docker registry repositories:
   - Create blob store
   - Create hosted Docker repository on port 8082
   - Enable Docker Bearer Token Realm

### 3. Register GitLab Runner

```bash
# Get registration token from GitLab:
# Settings > CI/CD > Runners > New instance runner

# Register runner
podman exec -it orgmgmt-gitlab-runner gitlab-runner register \
  --non-interactive \
  --url "http://gitlab:5003" \
  --registration-token "YOUR_TOKEN" \
  --executor "shell" \
  --description "podman-runner" \
  --tag-list "docker,podman" \
  --run-untagged="true" \
  --locked="false"
```

### 4. Configure ArgoCD

```bash
# Get initial admin password
podman exec argocd-server argocd admin initial-password

# Login via CLI (optional)
podman exec -it argocd-server argocd login localhost:8080 --username admin --password <password> --insecure

# Add Git repository
podman exec -it argocd-server argocd repo add http://gitlab:5003/group/repo.git --username root --password <gitlab-password>
```

## Networking

All services are connected via the `argocd-network` bridge network, allowing them to communicate using service names as hostnames:

- Services can reference each other by container name (e.g., `postgres`, `gitlab`, `argocd-redis`)
- External access is provided through port mappings
- DNS resolution is automatic within the network

## Troubleshooting

### Services Won't Start

```bash
# Check service status
podman-compose ps

# View logs for failing service
podman-compose logs service-name

# Restart specific service
podman-compose restart service-name

# Recreate service
podman-compose up -d --force-recreate service-name
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :5432

# Change port in .env file
nano .env

# Restart services
podman-compose down && podman-compose up -d
```

### GitLab Taking Too Long to Start

GitLab can take 5-10 minutes to fully initialize on first start. Check progress:

```bash
podman-compose logs -f gitlab
```

Wait for the message: "gitlab Reconfigured!"

### Nexus Storage Issues

```bash
# Check available disk space
df -h

# Clean up old volumes
podman volume prune

# Increase Docker/Podman storage
```

### ArgoCD Can't Connect to Git

```bash
# Check network connectivity
podman exec argocd-server ping gitlab

# Verify GitLab is healthy
curl http://localhost:5003/-/health

# Check ArgoCD server logs
podman-compose logs argocd-server
```

### Permission Denied Errors

```bash
# Fix SELinux context (if applicable)
chcon -Rt svirt_sandbox_file_t ./config

# Or disable SELinux for testing
sudo setenforce 0
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "SELECT version();"

# Check PostgreSQL logs
podman-compose logs postgres

# Verify credentials in .env
cat .env | grep POSTGRES
```

### Reset Everything

```bash
# WARNING: This destroys all data!
podman-compose down -v
podman network rm argocd-network
podman volume prune -f
podman-compose up -d
```

## Performance Tuning

### For Low Memory Environments

Edit podman-compose.yml to reduce resource usage:

```yaml
# Reduce GitLab workers
environment:
  GITLAB_OMNIBUS_CONFIG: |
    puma['worker_processes'] = 1
    sidekiq['max_concurrency'] = 5

# Reduce Nexus memory
environment:
  INSTALL4J_ADD_VM_PARAMS: "-Xms512m -Xmx512m"
```

### For High Performance

```yaml
# Increase PostgreSQL connections
environment:
  POSTGRES_MAX_CONNECTIONS: 200

# Increase Nexus memory
environment:
  INSTALL4J_ADD_VM_PARAMS: "-Xms2048m -Xmx2048m"
```

## Backup and Restore

### Automated Backup Script

```bash
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > $BACKUP_DIR/postgres.sql

# Backup volumes
for vol in postgres-data nexus-data gitlab-config gitlab-data; do
  podman run --rm -v orgmgmt-$vol:/source:ro -v $(pwd)/$BACKUP_DIR:/backup \
    alpine tar czf /backup/$vol.tar.gz -C /source .
done

echo "Backup completed: $BACKUP_DIR"
```

## Security Considerations

### Production Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS/TLS for all services
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable audit logging
- [ ] Configure SELinux/AppArmor
- [ ] Use secrets management (Vault, etc.)
- [ ] Enable two-factor authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts

## Additional Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Compose Documentation](https://github.com/containers/podman-compose)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitLab Documentation](https://docs.gitlab.com/)
- [Nexus Documentation](https://help.sonatype.com/repomanager3)

## Support

For issues or questions:
1. Check the logs: `podman-compose logs -f`
2. Review this README's troubleshooting section
3. Check service-specific documentation
4. Review container status: `podman-compose ps`

## License

This infrastructure setup is part of the Organization Management System project.
