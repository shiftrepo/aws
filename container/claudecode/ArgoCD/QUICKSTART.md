# Quick Start Guide

Get the Organization Management System up and running in 5 minutes!

## Table of Contents

- [Prerequisites](#prerequisites)
- [5-Minute Setup](#5-minute-setup)
- [Access Services](#access-services)
- [Quick Verification](#quick-verification)
- [Common Tasks](#common-tasks)
- [Quick Troubleshooting](#quick-troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

### Minimum Requirements

- **OS**: RHEL 9 or compatible Linux
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 50GB free space
- **Software**: podman, podman-compose, git, jq

### Install Required Software

```bash
# Install all prerequisites in one command
sudo dnf install -y podman podman-compose git jq curl

# Verify installations
podman --version
podman-compose --version
git --version
jq --version
```

## 5-Minute Setup

### Step 1: Clone Repository (30 seconds)

```bash
# Clone the repository
git clone <repository-url>
cd ArgoCD
```

### Step 2: Run Setup Script (4-5 minutes)

```bash
# Run the master setup script
./scripts/setup.sh

# This will:
# ✓ Check prerequisites
# ✓ Create environment configuration
# ✓ Start all infrastructure services
# ✓ Wait for services to be healthy
# ✓ Generate secure passwords
# ✓ Save credentials to credentials.txt
```

### Step 3: View Credentials (5 seconds)

```bash
# View all access credentials
cat credentials.txt
```

That's it! Your system is ready to use.

## Access Services

### Quick Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Application** | http://localhost:5006 | Main application UI |
| **API** | http://localhost:8080 | Backend REST API |
| **ArgoCD** | http://localhost:5010 | GitOps dashboard |
| **GitLab** | http://localhost:5003 | Source control |
| **Nexus** | http://localhost:8081 | Artifact repository |
| **pgAdmin** | http://localhost:5050 | Database management |

### Default Login Credentials

All passwords are in `credentials.txt` file.

**Quick Access:**
```bash
# Extract specific credentials
grep "ArgoCD" -A 3 credentials.txt
grep "GitLab" -A 3 credentials.txt
grep "Nexus" -A 3 credentials.txt
```

## Quick Verification

### Check All Services

```bash
# Check service status
./scripts/status.sh

# Expected output: All services should show "healthy"
```

### Test Backend API

```bash
# Health check
curl http://localhost:8080/actuator/health

# Expected output:
# {"status":"UP"}

# List organizations (should be empty initially)
curl http://localhost:8080/api/organizations
```

### Test Frontend

```bash
# Check if frontend is accessible
curl -I http://localhost:5006

# Expected output:
# HTTP/1.1 200 OK
```

### Create Test Data

```bash
# Create a test organization
curl -X POST http://localhost:8080/api/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Organization",
    "code": "TEST001",
    "description": "Test organization for verification",
    "active": true
  }'

# Verify it was created
curl http://localhost:8080/api/organizations
```

## Common Tasks

### Start Services

```bash
# Start all services
cd infrastructure
podman-compose up -d

# Or use the script
./scripts/setup.sh
```

### Stop Services

```bash
# Stop all services (preserves data)
cd infrastructure
podman-compose down

# Or use the script
./infrastructure/stop.sh
```

### View Logs

```bash
# View all logs
./scripts/logs.sh

# View specific service
./scripts/logs.sh backend
./scripts/logs.sh frontend
./scripts/logs.sh postgres

# Follow logs in real-time
podman logs -f orgmgmt-backend-dev
```

### Check Service Status

```bash
# Quick status check
./scripts/status.sh

# Detailed container info
podman ps

# Check specific container health
podman healthcheck run orgmgmt-backend-dev
```

### Build and Deploy Application

```bash
# Build and deploy
./scripts/build-and-deploy.sh

# This will:
# 1. Build backend with Maven
# 2. Build frontend with npm
# 3. Create container images
# 4. Deploy to dev environment
```

### Run Tests

```bash
# Run all tests
./scripts/test.sh

# Run backend tests only
cd app/backend
mvn test

# Run frontend tests only
cd app/frontend
npm test

# Run E2E tests
./scripts/run-e2e-tests.sh
```

### Database Operations

```bash
# Connect to database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# View tables
\dt

# View organizations
SELECT * FROM organizations;

# Exit
\q
```

### Backup Data

```bash
# Create backup
./scripts/backup.sh

# Backups are stored in: backups/<timestamp>/
```

### Restore Data

```bash
# Restore from backup
./scripts/restore.sh backups/<timestamp>/
```

### Clean Up

```bash
# Stop and remove all containers and volumes
./scripts/cleanup.sh

# Warning: This will DELETE ALL DATA!
```

## Quick Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
sudo ss -tulpn | grep -E '5432|8080|5006|5010'

# Kill processes using required ports
sudo kill <PID>

# Restart services
./scripts/setup.sh
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
podman ps | grep postgres

# Check PostgreSQL logs
podman logs orgmgmt-postgres

# Verify credentials
cat infrastructure/.env | grep POSTGRES

# Restart PostgreSQL
podman restart orgmgmt-postgres
```

### Frontend Not Loading

```bash
# Check frontend container
podman ps | grep frontend

# Check frontend logs
podman logs orgmgmt-frontend-dev

# Verify nginx is running
podman exec orgmgmt-frontend-dev ps aux | grep nginx

# Restart frontend
podman restart orgmgmt-frontend-dev
```

### Backend API Errors

```bash
# Check backend logs
./scripts/logs.sh backend

# Check database connection
curl http://localhost:8080/actuator/health

# Restart backend
podman restart orgmgmt-backend-dev
```

### ArgoCD Not Syncing

```bash
# Check ArgoCD status
argocd app get orgmgmt-dev

# Manual sync
argocd app sync orgmgmt-dev

# Check ArgoCD logs
podman logs argocd-server
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up old images
podman image prune -a

# Clean up old containers
podman container prune

# Clean up volumes (WARNING: deletes data)
podman volume prune
```

### Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Or change the port in .env file
vim infrastructure/.env
# Change: APP_BACKEND_PORT=8080 to APP_BACKEND_PORT=8081
```

### Performance Issues

```bash
# Check system resources
free -h
df -h
top

# Check container resources
podman stats

# Restart heavy services
podman restart orgmgmt-gitlab
podman restart orgmgmt-nexus
```

## Next Steps

### For Developers

1. **Explore the API**
   ```bash
   # View API documentation
   curl http://localhost:8080/actuator

   # Try different endpoints
   curl http://localhost:8080/api/organizations
   curl http://localhost:8080/api/departments
   curl http://localhost:8080/api/users
   ```

2. **Start Local Development**
   ```bash
   # Backend development
   cd app/backend
   mvn spring-boot:run

   # Frontend development (in another terminal)
   cd app/frontend
   npm run dev
   ```

3. **Make Changes and Test**
   ```bash
   # Edit code in your IDE

   # Run tests
   ./scripts/test.sh

   # Build and deploy
   ./scripts/build-and-deploy.sh
   ```

### For DevOps Engineers

1. **Set Up CI/CD Pipeline**
   - Create GitLab project
   - Configure GitLab Runner
   - Push code to trigger pipeline

2. **Configure Multi-Environment**
   ```bash
   # Edit staging environment
   vim gitops/staging/podman-compose.yml

   # Create ArgoCD application for staging
   argocd app create orgmgmt-staging \
     --repo file:///gitops \
     --path staging \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace default
   ```

3. **Set Up Monitoring**
   - Configure Prometheus for metrics
   - Set up Grafana dashboards
   - Configure alerting

### For System Administrators

1. **Secure the System**
   ```bash
   # Change default passwords
   vim infrastructure/.env

   # Configure firewall
   sudo firewall-cmd --add-port=5006/tcp --permanent
   sudo firewall-cmd --add-port=8080/tcp --permanent
   sudo firewall-cmd --reload
   ```

2. **Set Up Backups**
   ```bash
   # Schedule daily backups
   crontab -e
   # Add: 0 2 * * * /path/to/ArgoCD/scripts/backup.sh
   ```

3. **Configure Monitoring**
   ```bash
   # Set up log rotation
   # Set up health check monitoring
   # Configure alerting
   ```

### Learn More

- **Full Documentation**: See [README.md](README.md)
- **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Reference**: See [API.md](API.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Quick Reference Commands

### Essential Commands

```bash
# Start everything
./scripts/setup.sh

# Check status
./scripts/status.sh

# View logs
./scripts/logs.sh

# Build and deploy
./scripts/build-and-deploy.sh

# Run tests
./scripts/test.sh

# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh <backup-dir>

# Clean up
./scripts/cleanup.sh
```

### Container Commands

```bash
# List containers
podman ps

# View logs
podman logs -f <container-name>

# Execute command in container
podman exec -it <container-name> /bin/bash

# Restart container
podman restart <container-name>

# Stop container
podman stop <container-name>

# Remove container
podman rm <container-name>

# View stats
podman stats
```

### Database Commands

```bash
# Connect to database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Backup database
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > backup.sql

# Restore database
cat backup.sql | podman exec -i orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt
```

### ArgoCD Commands

```bash
# Login to ArgoCD
argocd login localhost:5010

# List applications
argocd app list

# Get application details
argocd app get orgmgmt-dev

# Sync application
argocd app sync orgmgmt-dev

# Rollback application
argocd app rollback orgmgmt-dev
```

## Support

Need help? Check these resources:

1. **Documentation**: Read the full [README.md](README.md)
2. **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Logs**: Run `./scripts/logs.sh`
4. **Status**: Run `./scripts/status.sh`
5. **Issues**: Check GitHub issues
6. **Community**: Ask on community forums

---

Happy coding! 🚀
