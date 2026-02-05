# Infrastructure Quick Reference Card

## Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | `localhost:5432` | User: `orgmgmt_user` / Check `.env` |
| pgAdmin | http://localhost:5050 | Email: `admin@orgmgmt.local` / Check `.env` |
| Nexus | http://localhost:8081 | User: `admin` / Run: `podman exec orgmgmt-nexus cat /nexus-data/admin.password` |
| GitLab | http://localhost:5003 | User: `root` / Check `.env` |
| GitLab SSH | `ssh://git@localhost:2222` | Use SSH key |
| GitLab Registry | http://localhost:5005 | Same as GitLab |
| ArgoCD | http://localhost:5010 | User: `admin` / Run: `podman exec argocd-server argocd admin initial-password` |

## Common Commands

### Start/Stop
```bash
./start.sh              # Start all services
./stop.sh               # Stop all services
./status.sh             # Check service health
```

### Manual Control
```bash
podman-compose up -d                    # Start all services
podman-compose down                     # Stop all services
podman-compose down -v                  # Stop and remove volumes (DESTROYS DATA!)
podman-compose restart [service]        # Restart specific service
podman-compose ps                       # Show running containers
```

### Logs
```bash
podman-compose logs -f                  # All logs (follow mode)
podman-compose logs -f [service]        # Specific service logs
podman-compose logs --tail=100 [svc]    # Last 100 lines
```

### Health Checks
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

### Container Access
```bash
# PostgreSQL
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Redis
podman exec -it argocd-redis redis-cli

# ArgoCD
podman exec -it argocd-server sh

# GitLab
podman exec -it orgmgmt-gitlab bash

# Nexus
podman exec -it orgmgmt-nexus sh
```

## Database Operations

### PostgreSQL
```bash
# Connect to database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Backup database
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > backup.sql

# Restore database
cat backup.sql | podman exec -i orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# List databases
podman exec orgmgmt-postgres psql -U orgmgmt_user -c "\l"

# List tables
podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "\dt"
```

## GitLab Operations

### GitLab Runner Registration
```bash
# Get registration token from GitLab UI: Admin Area > CI/CD > Runners

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

# List runners
podman exec orgmgmt-gitlab-runner gitlab-runner list

# Verify runner
podman exec orgmgmt-gitlab-runner gitlab-runner verify
```

### GitLab Commands
```bash
# Check GitLab status
podman exec orgmgmt-gitlab gitlab-ctl status

# Reconfigure GitLab
podman exec orgmgmt-gitlab gitlab-ctl reconfigure

# GitLab console
podman exec -it orgmgmt-gitlab gitlab-rails console

# Check logs
podman exec orgmgmt-gitlab gitlab-ctl tail
```

## ArgoCD Operations

### CLI Commands
```bash
# Get initial password
podman exec argocd-server argocd admin initial-password

# Login
podman exec -it argocd-server argocd login localhost:8080 --username admin --insecure

# List applications
podman exec argocd-server argocd app list

# Get application status
podman exec argocd-server argocd app get <app-name>

# Sync application
podman exec argocd-server argocd app sync <app-name>

# Add repository
podman exec argocd-server argocd repo add http://gitlab:5003/group/repo.git --username user --password pass

# List repositories
podman exec argocd-server argocd repo list
```

## Nexus Operations

### Get Initial Password
```bash
podman exec orgmgmt-nexus cat /nexus-data/admin.password
```

### Docker Registry
```bash
# Login to Nexus Docker registry
podman login localhost:8082

# Tag image
podman tag myimage:latest localhost:8082/myimage:latest

# Push image
podman push localhost:8082/myimage:latest

# Pull image
podman pull localhost:8082/myimage:latest
```

## Volume Management

### List Volumes
```bash
podman volume ls
```

### Backup Volume
```bash
# Replace VOLUME_NAME with actual volume name
podman run --rm -v VOLUME_NAME:/source:ro -v $(pwd):/backup \
  alpine tar czf /backup/VOLUME_NAME-backup.tar.gz -C /source .
```

### Restore Volume
```bash
podman run --rm -v VOLUME_NAME:/target -v $(pwd):/backup \
  alpine tar xzf /backup/VOLUME_NAME-backup.tar.gz -C /target
```

### Inspect Volume
```bash
podman volume inspect VOLUME_NAME
```

### Remove Volume (DANGEROUS!)
```bash
podman volume rm VOLUME_NAME
```

## Network Management

### Inspect Network
```bash
podman network inspect argocd-network
```

### List Networks
```bash
podman network ls
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
podman-compose logs [service-name]

# Check container status
podman inspect [container-name]

# Force recreate
podman-compose up -d --force-recreate [service-name]
```

### Port Conflicts
```bash
# Find process using port
sudo lsof -i :5432
sudo ss -tulpn | grep :5432

# Kill process (if safe)
sudo kill [PID]

# Or change port in .env
nano .env
```

### Out of Disk Space
```bash
# Check disk usage
df -h

# Clean up unused resources
podman system prune -a -f

# Clean up volumes (DANGEROUS!)
podman volume prune -f
```

### Permission Issues
```bash
# Fix SELinux labels
chcon -Rt svirt_sandbox_file_t ./config

# Check SELinux status
getenforce

# Temporarily disable (testing only)
sudo setenforce 0
```

### Service Not Responding
```bash
# Check if container is running
podman ps -a

# Restart container
podman-compose restart [service-name]

# Check health
podman inspect [container-name] | grep -A 20 Health

# View resource usage
podman stats [container-name]
```

## Performance Monitoring

### Resource Usage
```bash
# All containers
podman stats

# Specific container
podman stats [container-name]

# One-time snapshot
podman stats --no-stream
```

### Disk Usage
```bash
# Container disk usage
podman system df

# Detailed breakdown
podman system df -v
```

## Maintenance Tasks

### Update Images
```bash
# Pull latest images
podman-compose pull

# Recreate containers with new images
podman-compose up -d --force-recreate
```

### Cleanup
```bash
# Remove stopped containers
podman container prune -f

# Remove unused images
podman image prune -a -f

# Remove unused volumes (DANGEROUS!)
podman volume prune -f

# Remove everything unused (DANGEROUS!)
podman system prune -a -f --volumes
```

### Logs Rotation
```bash
# Manually rotate logs
podman exec orgmgmt-gitlab gitlab-ctl rotate-logs

# GitLab logs cleanup
podman exec orgmgmt-gitlab find /var/log/gitlab -name "*.log" -mtime +7 -delete
```

## Environment Variables

### View Current Values
```bash
cat .env
```

### Reload After Changes
```bash
# Stop services
podman-compose down

# Start with new config
podman-compose up -d
```

## Backup Strategy

### Full Backup Script
```bash
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# PostgreSQL
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > $BACKUP_DIR/postgres.sql

# Volumes
for vol in postgres-data nexus-data gitlab-config gitlab-data; do
  podman run --rm -v orgmgmt-$vol:/source:ro -v $(pwd)/$BACKUP_DIR:/backup \
    alpine tar czf /backup/$vol.tar.gz -C /source .
done
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall
- [ ] Enable two-factor authentication
- [ ] Regular security updates
- [ ] Audit logging enabled
- [ ] Secrets management configured
- [ ] Network access restricted

## Emergency Procedures

### Complete Reset (DESTROYS ALL DATA!)
```bash
podman-compose down -v
podman network rm argocd-network
podman volume prune -f
rm -rf gitops/*
podman-compose up -d
```

### Restore from Backup
```bash
# Stop services
podman-compose down

# Restore volumes (adjust paths)
for vol in postgres-data nexus-data gitlab-data; do
  podman run --rm -v orgmgmt-$vol:/target -v $(pwd)/backup:/backup \
    alpine tar xzf /backup/$vol.tar.gz -C /target
done

# Start services
podman-compose up -d
```

## Support Resources

- Infrastructure README: `./README.md`
- Setup Checklist: `./SETUP_CHECKLIST.md`
- Directory Structure: `./STRUCTURE.txt`
- [Podman Documentation](https://docs.podman.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitLab Documentation](https://docs.gitlab.com/)
- [Nexus Documentation](https://help.sonatype.com/repomanager3)

---

**Last Updated:** 2026-02-05
**Version:** 1.0.0
