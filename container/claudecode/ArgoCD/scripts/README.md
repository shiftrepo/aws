# ArgoCD Project - Automation Scripts

This directory contains comprehensive automation scripts for managing the ArgoCD project infrastructure, development workflow, and deployments.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Script Reference](#script-reference)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

## Overview

The automation scripts provide a complete DevOps workflow including:

- **Infrastructure Management**: Setup, teardown, and monitoring
- **Build & Deployment**: Automated CI/CD workflows
- **Testing**: Unit, integration, and E2E test execution
- **ArgoCD Operations**: Deployment and rollback management
- **Backup & Restore**: Data protection and disaster recovery
- **Utilities**: Logging, status checking, and maintenance

## Prerequisites

### Required Tools

- `podman` - Container runtime
- `podman-compose` - Container orchestration
- `git` - Version control
- `jq` - JSON processing
- `curl` - HTTP client
- `openssl` - Cryptographic operations
- `maven` - Java build tool (for backend)
- `npm` - Node package manager (for frontend)
- `argocd` - ArgoCD CLI (for ArgoCD operations)

### System Requirements

- **Memory**: 4GB minimum, 8GB recommended
- **Disk Space**: 10GB minimum, 20GB recommended
- **Operating System**: Linux (tested on RHEL/CentOS/Fedora)

## Script Reference

### Core Scripts

#### `common.sh`

Shared utility library used by all scripts.

**Features:**
- Color-coded logging functions
- Error handling utilities
- Service health checks
- Container management helpers
- Environment validation

**Usage:**
```bash
source scripts/common.sh
```

---

#### `setup.sh`

Master setup script for complete environment initialization.

**Features:**
- Prerequisites validation
- Secure password generation
- Infrastructure deployment
- Service health monitoring
- Credential management

**Usage:**
```bash
# Full setup
./scripts/setup.sh

# Skip prerequisite checks
./scripts/setup.sh --skip-checks

# Setup without service initialization
./scripts/setup.sh --no-init

# Use custom environment file
./scripts/setup.sh --env-file /path/to/.env
```

**What it does:**
1. Checks system prerequisites and resources
2. Creates `.env` file with secure passwords
3. Starts all infrastructure services
4. Waits for services to be healthy
5. Retrieves initial credentials
6. Saves access information to `credentials.txt`

**Output:**
- Environment configuration in `infrastructure/.env`
- Access credentials in `credentials.txt`

---

### Build & Deployment

#### `build-and-deploy.sh`

Complete build and deployment workflow.

**Features:**
- Backend Maven build and test
- Frontend npm build and test
- Container image creation
- Registry push
- GitOps manifest updates
- ArgoCD synchronization

**Usage:**
```bash
# Full build and deploy to dev
./scripts/build-and-deploy.sh

# Deploy to production
./scripts/build-and-deploy.sh --environment prod

# Skip tests
./scripts/build-and-deploy.sh --skip-tests

# Deploy specific version
./scripts/build-and-deploy.sh --version 1.2.3

# Build only backend
./scripts/build-and-deploy.sh --skip-frontend

# Deploy without ArgoCD sync
./scripts/build-and-deploy.sh --no-sync
```

**Workflow:**
1. Validates environment is running
2. Builds backend JAR file
3. Runs backend tests (JUnit)
4. Builds frontend bundle
5. Runs frontend tests (Jest)
6. Creates container images
7. Pushes to Nexus registry
8. Updates GitOps manifests
9. Triggers ArgoCD sync
10. Performs health checks

---

### ArgoCD Operations

#### `argocd-deploy.sh`

Deploy applications via ArgoCD.

**Features:**
- Application synchronization
- Deployment monitoring
- Health status checking
- Resource display

**Usage:**
```bash
# Deploy to dev
./scripts/argocd-deploy.sh --environment dev

# Deploy to production and wait
./scripts/argocd-deploy.sh --environment prod --wait

# Force sync with prune
./scripts/argocd-deploy.sh --environment staging --force --prune

# Custom timeout
./scripts/argocd-deploy.sh --environment dev --wait --timeout 600
```

**Options:**
- `--environment`: Target environment (dev/staging/prod)
- `--wait`: Wait for sync to complete
- `--timeout`: Sync timeout in seconds (default: 300)
- `--prune`: Prune resources during sync
- `--force`: Force sync even if up-to-date

---

#### `argocd-rollback.sh`

Rollback applications to previous versions.

**Features:**
- Deployment history viewing
- Automatic rollback to previous version
- Rollback to specific revision
- Rollback verification

**Usage:**
```bash
# Show deployment history
./scripts/argocd-rollback.sh --environment dev --history

# Rollback to previous version
./scripts/argocd-rollback.sh --environment prod

# Rollback to specific revision
./scripts/argocd-rollback.sh --environment staging --revision 5

# Rollback and wait for completion
./scripts/argocd-rollback.sh --environment dev --wait
```

**Workflow:**
1. Displays deployment history
2. Determines rollback revision
3. Confirms rollback operation
4. Executes rollback
5. Monitors rollback progress
6. Verifies application health

---

### Testing

#### `test.sh`

Comprehensive test runner for all test types.

**Features:**
- Backend unit tests (JUnit)
- Frontend unit tests (Jest)
- E2E tests (Playwright)
- Coverage report generation
- Test result aggregation

**Usage:**
```bash
# Run all tests
./scripts/test.sh

# Run with coverage
./scripts/test.sh --coverage

# Backend tests only
./scripts/test.sh --backend-only

# Frontend tests only
./scripts/test.sh --frontend-only

# Skip E2E tests
./scripts/test.sh --skip-e2e

# Watch mode (frontend)
./scripts/test.sh --frontend-only --watch
```

**Test Reports:**
- Backend: `app/backend/target/site/jacoco/index.html`
- Frontend: `app/frontend/coverage/index.html`
- E2E: `playwright-tests/playwright-report/index.html`

---

#### `run-e2e-tests.sh`

Dedicated E2E test runner with Playwright.

**Features:**
- Pre-deployment health checks
- Multiple browser support
- Debug mode
- Screenshot capture
- Test artifact archival

**Usage:**
```bash
# Run E2E tests on dev
./scripts/run-e2e-tests.sh

# Run on production
./scripts/run-e2e-tests.sh --environment prod

# Debug mode with visible browser
./scripts/run-e2e-tests.sh --headed --debug

# Run specific browser
./scripts/run-e2e-tests.sh --project chromium

# Run tests matching pattern
./scripts/run-e2e-tests.sh --grep "login"

# Skip health checks
./scripts/run-e2e-tests.sh --skip-health
```

**Test Artifacts:**
- HTML reports in `playwright-tests/playwright-report/`
- Screenshots in `playwright-tests/test-results/`
- Archived results in `test-results/`

---

### Utilities

#### `status.sh`

Check status of all services.

**Features:**
- Container status display
- Service health checks
- Resource usage monitoring
- Access URL display

**Usage:**
```bash
# Basic status
./scripts/status.sh

# Detailed status
./scripts/status.sh --detailed

# Watch mode (continuous monitoring)
./scripts/status.sh --watch

# JSON output
./scripts/status.sh --json
```

**Status Indicators:**
- ✓ (Green) - Service is healthy
- ✗ (Red) - Service is unhealthy or stopped
- ⟳ (Yellow) - Service is starting
- N/A (Cyan) - Health check not applicable

---

#### `logs.sh`

View container logs.

**Features:**
- View all service logs
- Filter by service
- Follow logs in real-time
- Time-based filtering

**Usage:**
```bash
# View all logs
./scripts/logs.sh

# View specific service
./scripts/logs.sh postgres
./scripts/logs.sh argocd-server

# Follow logs
./scripts/logs.sh gitlab -f

# Show last 50 lines
./scripts/logs.sh nexus --tail 50

# Show logs from last hour
./scripts/logs.sh postgres --since 1h

# Show logs with timestamps
./scripts/logs.sh --timestamps
```

**Available Services:**
- `postgres` - PostgreSQL database
- `pgadmin` - pgAdmin interface
- `nexus` - Nexus Repository
- `gitlab` - GitLab CE
- `gitlab-runner` - GitLab Runner
- `argocd-server` - ArgoCD API Server
- `argocd-repo-server` - ArgoCD Repository Server
- `argocd-application-controller` - ArgoCD Controller
- `argocd-redis` - Redis for ArgoCD

---

#### `cleanup.sh`

Clean up environment and artifacts.

**Features:**
- Container shutdown
- Volume removal
- Build artifact cleanup
- Cache clearing
- Database reset

**Usage:**
```bash
# Stop containers only
./scripts/cleanup.sh

# Clean build artifacts
./scripts/cleanup.sh --artifacts

# Remove all volumes (WARNING: deletes data!)
./scripts/cleanup.sh --volumes

# Complete cleanup
./scripts/cleanup.sh --all

# Clear caches
./scripts/cleanup.sh --cache

# Reset database
./scripts/cleanup.sh --reset-db
```

**WARNING:**
- `--all` and `--volumes` will delete all data
- `--reset-db` will erase the database
- Always backup before cleanup

---

### Backup & Restore

#### `backup.sh`

Create backups of all data and configuration.

**Features:**
- PostgreSQL database backup
- Nexus data backup
- GitLab data backup
- GitOps manifests backup
- Configuration backup
- Automatic compression

**Usage:**
```bash
# Full backup
./scripts/backup.sh

# Custom output directory
./scripts/backup.sh --output-dir /mnt/backups

# Database only
./scripts/backup.sh --databases-only

# Skip volumes
./scripts/backup.sh --no-volumes
```

**Backup Contents:**
- PostgreSQL dump (`postgres-dump.sql`)
- Nexus data volume
- GitLab data and configuration
- GitOps manifests
- Environment files
- Credentials file
- Backup metadata

**Output:**
- Compressed: `backups/argocd-backup-YYYYMMDD-HHMMSS.tar.gz`
- Uncompressed: `backups/argocd-backup-YYYYMMDD-HHMMSS/`

---

#### `restore.sh`

Restore from backup.

**Features:**
- Full or partial restore
- Database restoration
- Volume restoration
- Configuration restoration
- Service restart
- Restore verification

**Usage:**
```bash
# Full restore
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz

# Database only
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz --database-only

# Configuration only
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz --config-only

# Skip service restart
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz --no-restart

# Force restore without confirmation
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz --force
```

**WARNING:**
- Restore will overwrite existing data
- Always confirm you have the correct backup
- Services will be restarted by default

---

## Common Workflows

### Initial Setup

Complete first-time setup:

```bash
# 1. Run setup script
./scripts/setup.sh

# 2. Check status
./scripts/status.sh

# 3. View access credentials
cat credentials.txt

# 4. Check logs if needed
./scripts/logs.sh
```

---

### Development Workflow

Typical development cycle:

```bash
# 1. Make code changes
# ... edit files ...

# 2. Run tests
./scripts/test.sh

# 3. Build and deploy
./scripts/build-and-deploy.sh --environment dev

# 4. Run E2E tests
./scripts/run-e2e-tests.sh --environment dev

# 5. Check deployment status
./scripts/argocd-deploy.sh --environment dev
```

---

### Production Deployment

Deploy to production:

```bash
# 1. Backup current state
./scripts/backup.sh --output-dir /backups/pre-deployment

# 2. Run all tests
./scripts/test.sh --coverage

# 3. Build and tag release
./scripts/build-and-deploy.sh --environment prod --version 1.2.3

# 4. Monitor deployment
./scripts/argocd-deploy.sh --environment prod --wait

# 5. Verify deployment
./scripts/status.sh
./scripts/run-e2e-tests.sh --environment prod

# 6. If issues occur, rollback
# ./scripts/argocd-rollback.sh --environment prod
```

---

### Disaster Recovery

Restore from backup:

```bash
# 1. Stop current environment
./scripts/cleanup.sh

# 2. Restore from backup
./scripts/restore.sh /backups/argocd-backup-20240101-120000.tar.gz

# 3. Verify services
./scripts/status.sh

# 4. Check logs
./scripts/logs.sh

# 5. Run health checks
./scripts/test.sh --skip-e2e
```

---

### Daily Operations

Regular maintenance tasks:

```bash
# Morning: Check status
./scripts/status.sh --detailed

# Monitor logs
./scripts/logs.sh --follow

# View specific service logs
./scripts/logs.sh argocd-server -f

# Check deployment status
./scripts/argocd-deploy.sh --environment dev

# Evening: Create backup
./scripts/backup.sh
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check what's running
./scripts/status.sh

# View logs for failing service
./scripts/logs.sh <service-name> --tail 100

# Clean up and restart
./scripts/cleanup.sh
./scripts/setup.sh
```

---

### Build Failures

```bash
# Clean build artifacts
./scripts/cleanup.sh --artifacts --cache

# Rebuild from scratch
./scripts/build-and-deploy.sh --environment dev
```

---

### Tests Failing

```bash
# Run tests with verbose output
./scripts/test.sh --backend-only

# Check E2E test environment
./scripts/run-e2e-tests.sh --headed --debug

# View test logs
./scripts/logs.sh
```

---

### Deployment Issues

```bash
# Check ArgoCD status
./scripts/argocd-deploy.sh --environment dev

# View deployment history
./scripts/argocd-rollback.sh --environment dev --history

# Rollback if needed
./scripts/argocd-rollback.sh --environment dev --wait
```

---

### Database Problems

```bash
# Check PostgreSQL status
./scripts/logs.sh postgres

# Reset database (WARNING: deletes data!)
./scripts/cleanup.sh --reset-db

# Restore from backup
./scripts/restore.sh backups/latest-backup.tar.gz --database-only
```

---

## Environment Variables

Scripts use environment variables from `infrastructure/.env`:

### Infrastructure
- `POSTGRES_*` - PostgreSQL configuration
- `PGADMIN_*` - pgAdmin configuration
- `NEXUS_*` - Nexus configuration
- `GITLAB_*` - GitLab configuration
- `ARGOCD_*` - ArgoCD configuration

### Application
- `APP_BACKEND_PORT` - Backend port
- `APP_FRONTEND_PORT` - Frontend port
- `APP_VERSION` - Application version

### Build
- `BUILD_TAG_STRATEGY` - Image tagging strategy

---

## Script Exit Codes

All scripts use consistent exit codes:

- `0` - Success
- `1` - General error
- `2` - Missing prerequisites
- `3` - Configuration error
- `4` - Service health check failure

---

## Best Practices

### Security

1. **Never commit credentials** - Keep `credentials.txt` and `.env` files secure
2. **Change default passwords** - Always change passwords before production
3. **Regular backups** - Schedule daily backups
4. **Restrict access** - Limit who can run scripts

### Operations

1. **Always test first** - Test in dev before deploying to production
2. **Monitor logs** - Use `--watch` mode for continuous monitoring
3. **Backup before changes** - Create backup before major operations
4. **Verify after deployment** - Always run health checks post-deployment

### Development

1. **Run tests locally** - Use `test.sh` before pushing code
2. **Check status frequently** - Use `status.sh` to monitor services
3. **Clean regularly** - Run `cleanup.sh --artifacts` to free space
4. **Follow logs** - Use `logs.sh -f` during development

---

## Contributing

When adding new scripts:

1. Follow the existing structure and naming conventions
2. Use `common.sh` functions for consistency
3. Add comprehensive help text (`--help`)
4. Include error handling and validation
5. Update this README with usage examples

---

## Support

For issues or questions:

1. Check the logs: `./scripts/logs.sh`
2. Check service status: `./scripts/status.sh --detailed`
3. Review the troubleshooting section above
4. Check script help: `./scripts/<script-name>.sh --help`

---

## License

These scripts are part of the ArgoCD Project and follow the same license.
