# ArgoCD CD Pipeline - Quick Reference Card

> **One-page reference for common tasks and commands**

---

## 🚀 Quick Start (First Time)

```bash
cd /root/aws.git/container/claudecode/ArgoCD
./scripts/setup.sh                    # Complete setup (10-15 min)
./scripts/status.sh                   # Verify all services
```

---

## 🌐 Access URLs

| Service | URL | User | Password |
|---------|-----|------|----------|
| App (Frontend) | http://localhost:5006 | - | - |
| App (Backend) | http://localhost:8080 | - | - |
| ArgoCD | http://localhost:5010 | admin | ArgoCDAdmin123! |
| GitLab | http://localhost:5003 | root | GitLabRoot123! |
| Nexus | http://localhost:8081 | admin | NexusAdmin123! |
| pgAdmin | http://localhost:5050 | admin@orgmgmt.local | AdminPassword123! |

---

## 📜 Essential Commands

### Service Management
```bash
# Start everything
cd infrastructure && podman-compose up -d

# Stop everything
cd infrastructure && podman-compose down

# Restart service
cd infrastructure && podman-compose restart <service>

# Check status
./scripts/status.sh
./scripts/status.sh --watch    # Continuous monitoring
```

### Application Deployment
```bash
# Build and deploy
./scripts/build-and-deploy.sh

# Deploy specific environment
./scripts/argocd-deploy.sh dev
./scripts/argocd-deploy.sh staging
./scripts/argocd-deploy.sh prod

# Rollback
./scripts/argocd-rollback.sh dev        # To previous version
./scripts/argocd-rollback.sh dev 5      # To specific revision
```

### Testing
```bash
# Run all tests
./scripts/test.sh

# Backend tests only
cd app/backend && mvn test

# Frontend tests only
cd app/frontend && npm test

# E2E tests
./scripts/run-e2e-tests.sh
./scripts/run-e2e-tests.sh --headed     # With browser visible
```

### Logging
```bash
# All logs
./scripts/logs.sh

# Specific service
./scripts/logs.sh postgres
./scripts/logs.sh argocd-server
./scripts/logs.sh orgmgmt-backend-dev

# Follow mode
./scripts/logs.sh --follow
```

### Backup & Restore
```bash
# Create backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh /path/to/backup.tar.gz
```

### Cleanup
```bash
# Stop containers (keep volumes)
./scripts/cleanup.sh

# Stop and remove volumes
./scripts/cleanup.sh --all

# Clean build artifacts
./scripts/cleanup.sh --artifacts
```

---

## 🔧 Direct Podman Commands

```bash
# List containers
podman ps -a

# View logs
podman logs -f <container-name>

# Execute command in container
podman exec -it postgres psql -U orgmgmt_user orgmgmt

# Inspect container
podman inspect <container-name>

# Check resources
podman stats

# Remove stopped containers
podman container prune
```

---

## 🐘 Database Quick Commands

```bash
# Connect to PostgreSQL
podman exec -it postgres psql -U orgmgmt_user orgmgmt

# Run SQL file
podman exec -i postgres psql -U orgmgmt_user orgmgmt < script.sql

# Database backup
podman exec postgres pg_dump -U orgmgmt_user orgmgmt > backup.sql

# Database restore
podman exec -i postgres psql -U orgmgmt_user orgmgmt < backup.sql

# Check database size
podman exec postgres psql -U orgmgmt_user -c "SELECT pg_size_pretty(pg_database_size('orgmgmt'));"
```

---

## 🔄 ArgoCD Commands

```bash
# Login
argocd login localhost:5010 --username admin --password ArgoCDAdmin123! --insecure

# List applications
argocd app list

# Get application details
argocd app get orgmgmt-dev

# Sync application
argocd app sync orgmgmt-dev
argocd app sync orgmgmt-dev --prune     # Remove extra resources

# View history
argocd app history orgmgmt-dev

# Rollback
argocd app rollback orgmgmt-dev

# Delete application
argocd app delete orgmgmt-dev
```

---

## 🦊 GitLab Commands

```bash
# Check GitLab health
curl http://localhost:5003/-/health

# View runner status
podman exec gitlab-runner gitlab-runner status

# Register runner (if needed)
podman exec gitlab-runner gitlab-runner register

# GitLab logs
podman logs -f gitlab
```

---

## 📦 Nexus Operations

```bash
# Upload Maven artifact
mvn deploy:deploy-file \
  -DgroupId=com.example \
  -DartifactId=orgmgmt-backend \
  -Dversion=1.0.0-SNAPSHOT \
  -Dpackaging=jar \
  -Dfile=target/orgmgmt-backend.jar \
  -DrepositoryId=nexus-snapshots \
  -Durl=http://localhost:8081/repository/maven-snapshots/

# Download from Nexus
curl -O http://localhost:8081/repository/maven-snapshots/com/example/orgmgmt-backend/1.0.0-SNAPSHOT/orgmgmt-backend-1.0.0-SNAPSHOT.jar
```

---

## 🏗️ Build Commands

```bash
# Backend build
cd app/backend
mvn clean package                      # Build JAR
mvn test                               # Run tests
mvn clean install -DskipTests         # Install without tests

# Frontend build
cd app/frontend
npm install                            # Install dependencies
npm run build                          # Production build
npm run dev                            # Development server

# Container build
cd container-builder
VERSION=1.0.0 ./scripts/build-from-nexus.sh     # Build images
VERSION=1.0.0 ./scripts/push-to-registry.sh     # Push to registry
```

---

## 🧪 Test Commands

```bash
# Backend unit tests
cd app/backend && mvn test

# Frontend unit tests
cd app/frontend && npm test

# E2E tests (all browsers)
cd playwright-tests && npx playwright test

# E2E tests (specific browser)
npx playwright test --project=chromium

# E2E tests (headed mode)
npx playwright test --headed

# E2E tests (debug mode)
npx playwright test --debug

# View test report
npx playwright show-report
```

---

## 🔍 Health Checks

```bash
# Backend health
curl http://localhost:8080/actuator/health

# Frontend health
curl http://localhost:5006

# PostgreSQL
podman exec postgres pg_isready -U orgmgmt_user

# Nexus
curl http://localhost:8081/service/rest/v1/status

# GitLab
curl http://localhost:5003/-/health

# ArgoCD
curl http://localhost:5010/healthz
```

---

## 🐛 Troubleshooting Quick Fixes

### Service Won't Start
```bash
# Check logs
./scripts/logs.sh <service-name>

# Check port conflicts
sudo lsof -i :<port>

# Restart service
cd infrastructure && podman-compose restart <service>
```

### Application Not Responding
```bash
# Check if running
podman ps | grep orgmgmt

# Check logs
./scripts/logs.sh orgmgmt-backend-dev
./scripts/logs.sh orgmgmt-frontend-dev

# Check health
curl http://localhost:8080/actuator/health
```

### Database Connection Issues
```bash
# Test connection
podman exec postgres pg_isready

# Check credentials
cat infrastructure/.env | grep POSTGRES

# Restart PostgreSQL
cd infrastructure && podman-compose restart postgres
```

### ArgoCD Sync Fails
```bash
# Check ArgoCD logs
./scripts/logs.sh argocd-server

# Validate manifest
cd gitops && ./scripts/validate-manifest.sh dev

# Manual sync with details
argocd app sync orgmgmt-dev --prune --force
```

### Build Fails
```bash
# Clean and rebuild backend
cd app/backend
mvn clean
mvn package -X    # Debug mode

# Clean and rebuild frontend
cd app/frontend
rm -rf node_modules dist
npm install
npm run build
```

---

## 📊 Monitoring Commands

```bash
# Container resource usage
podman stats

# Disk usage
podman system df

# Check volumes
podman volume ls

# Network inspection
podman network inspect argocd-network

# Service status with details
./scripts/status.sh --detailed
```

---

## 🔐 Security Operations

```bash
# Change ArgoCD password
argocd account update-password

# Generate new secrets
openssl rand -base64 32

# View container security
podman inspect --format='{{.Config.User}}' <container>

# Check file permissions
ls -la infrastructure/volumes/
```

---

## 📁 Important Directories

| Path | Purpose |
|------|---------|
| `app/backend` | Spring Boot backend source |
| `app/frontend` | React frontend source |
| `infrastructure` | Podman compose + configs |
| `gitops/` | Deployment manifests |
| `argocd/` | ArgoCD configuration |
| `scripts/` | Automation scripts |
| `playwright-tests/` | E2E tests |
| `container-builder/` | Container build files |

---

## 🔗 Key Files

| File | Purpose |
|------|---------|
| `.gitlab-ci.yml` | CI/CD pipeline |
| `infrastructure/podman-compose.yml` | Services definition |
| `infrastructure/.env` | Environment variables |
| `scripts/setup.sh` | Complete setup |
| `README.md` | Full documentation |

---

## 💡 Tips & Tricks

### Speed Up Development
```bash
# Use watch mode for tests
cd app/backend && mvn test -Dtest=OrganizationServiceTest --watch

# Use Vite dev server for frontend
cd app/frontend && npm run dev

# Skip tests during build
mvn package -DskipTests
```

### Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Debug ArgoCD sync
argocd app sync orgmgmt-dev --dry-run

# Debug Playwright tests
npx playwright test --debug --headed
```

### Performance
```bash
# Check slow queries
podman exec postgres psql -U orgmgmt_user -c "SELECT * FROM pg_stat_activity;"

# Monitor API performance
curl -w "@curl-format.txt" http://localhost:8080/api/organizations
```

---

## 🆘 Emergency Commands

```bash
# Complete reset (DANGER!)
./scripts/cleanup.sh --all
./scripts/setup.sh

# Rollback deployment
./scripts/argocd-rollback.sh dev

# Restore from backup
./scripts/restore.sh <backup-file>

# Stop everything immediately
cd infrastructure && podman-compose down
```

---

## 📚 Documentation Links

- **Complete Guide:** README.md
- **Quick Start:** QUICKSTART.md
- **Architecture:** ARCHITECTURE.md
- **Troubleshooting:** TROUBLESHOOTING.md
- **API Reference:** API.md
- **This Card:** QUICK-REFERENCE.md

---

## 🎯 Common Workflows

### Daily Development
```bash
1. ./scripts/status.sh                    # Check status
2. cd app/backend && mvn clean package   # Build
3. ./scripts/argocd-deploy.sh dev        # Deploy
4. ./scripts/test.sh                     # Test
```

### Production Deployment
```bash
1. ./scripts/build-and-deploy.sh         # Build all
2. ./scripts/argocd-deploy.sh staging    # Deploy to staging
3. ./scripts/run-e2e-tests.sh            # Run E2E tests
4. ./scripts/argocd-deploy.sh prod       # Deploy to prod
5. ./scripts/backup.sh                   # Backup
```

### Troubleshooting Session
```bash
1. ./scripts/status.sh                   # Check overall status
2. ./scripts/logs.sh <service>           # Check specific logs
3. podman ps -a                          # Check containers
4. curl <health-endpoint>                # Test endpoints
5. ./scripts/cleanup.sh && ./scripts/setup.sh  # If all else fails
```

---

**Last Updated:** 2026-02-05
**Project:** ArgoCD CD Pipeline
**Location:** `/root/aws.git/container/claudecode/ArgoCD/`

---

**For detailed information, always refer to README.md**
