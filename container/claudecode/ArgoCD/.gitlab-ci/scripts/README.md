# GitLab CI/CD Scripts

This directory contains supporting scripts for the GitLab CI/CD pipeline.

## Scripts Overview

### 1. deploy-nexus-maven.sh

Deploys Maven artifacts (JAR files) to Nexus Repository Manager.

**Purpose:**
- Uploads backend JAR files to Nexus maven-snapshots or maven-releases repository
- Configures Maven deployment settings
- Validates successful upload

**Usage:**
```bash
./deploy-nexus-maven.sh
```

**Environment Variables:**
- `NEXUS_URL` - Nexus server URL (default: http://nexus:8081)
- `NEXUS_USERNAME` - Nexus username (default: admin)
- `NEXUS_PASSWORD` - Nexus password (default: admin123)
- `MAVEN_REPO` - Target repository name (default: maven-snapshots)
- `CI_PROJECT_DIR` - GitLab CI project directory

**Requirements:**
- Maven 3.9+ with Java 17+
- settings.xml configured at /root/.m2/settings.xml
- Backend JAR file in app/backend/target/

**Exit Codes:**
- 0: Success
- 1: Failure (settings not found, deployment failed, etc.)

---

### 2. deploy-nexus-npm.sh

Deploys frontend artifacts (tarballs) to Nexus Repository Manager.

**Purpose:**
- Uploads frontend tarball to Nexus npm-hosted or raw repository
- Uses curl for direct HTTP upload
- Verifies successful upload

**Usage:**
```bash
./deploy-nexus-npm.sh
```

**Environment Variables:**
- `NEXUS_URL` - Nexus server URL (default: http://nexus:8081)
- `NEXUS_USERNAME` - Nexus username (default: admin)
- `NEXUS_PASSWORD` - Nexus password (default: admin123)
- `NPM_REPO` - Target repository name (default: npm-hosted)
- `VERSION` - Artifact version tag (default: latest)
- `CI_PROJECT_DIR` - GitLab CI project directory

**Requirements:**
- curl command-line tool
- Frontend tarball in app/frontend/ (frontend-*.tgz)

**Exit Codes:**
- 0: Success
- 1: Failure (tarball not found, upload failed, etc.)

---

### 3. sync-argocd.sh

Triggers ArgoCD application sync and waits for completion.

**Purpose:**
- Authenticates with ArgoCD server
- Triggers sync for specified application
- Waits for sync to complete with health checks
- Displays sync status and history

**Usage:**
```bash
./sync-argocd.sh <environment>
```

**Arguments:**
- `environment` - Target environment (dev, staging, prod)

**Example:**
```bash
./sync-argocd.sh dev
./sync-argocd.sh staging
./sync-argocd.sh prod
```

**Environment Variables:**
- `ARGOCD_URL` - ArgoCD server URL (default: localhost:5010)
- `ARGOCD_USERNAME` - ArgoCD username (default: admin)
- `ARGOCD_PASSWORD` - ArgoCD password (default: admin123)
- `ARGOCD_SYNC_TIMEOUT` - Sync timeout in seconds (default: 300)

**Requirements:**
- ArgoCD CLI installed
- ArgoCD server accessible
- Application exists in ArgoCD (orgmgmt-{environment})

**Exit Codes:**
- 0: Sync completed successfully
- 1: Failure (login failed, app not found, sync failed, timeout, etc.)

---

### 4. check-health.sh

Checks health status of backend and frontend services.

**Purpose:**
- Verifies backend is responding at /actuator/health
- Verifies frontend is accessible
- Retries with configurable attempts and intervals
- Provides diagnostics on failure

**Usage:**
```bash
./check-health.sh
```

**Environment Variables:**
- `BACKEND_URL` - Backend base URL (default: http://localhost:8080)
- `FRONTEND_URL` - Frontend base URL (default: http://localhost:5006)
- `HEALTH_CHECK_ATTEMPTS` - Maximum retry attempts (default: 30)
- `HEALTH_CHECK_INTERVAL` - Seconds between retries (default: 10)

**Requirements:**
- curl command-line tool
- Backend service running with Spring Actuator
- Frontend service running

**Exit Codes:**
- 0: All health checks passed
- 1: One or more health checks failed

**Health Check Logic:**
- Backend: Expects HTTP 200 with status: UP from /actuator/health
- Frontend: Expects HTTP 200 or redirect (301/302)
- Retries with exponential backoff
- Displays diagnostics with container status

---

## Pipeline Integration

These scripts are called by jobs in `.gitlab-ci.yml`:

```yaml
# Deploy to Nexus
deploy-maven:
  script:
    - .gitlab-ci/scripts/deploy-nexus-maven.sh

deploy-npm:
  script:
    - .gitlab-ci/scripts/deploy-nexus-npm.sh

# Sync with ArgoCD
deploy-dev:
  script:
    - .gitlab-ci/scripts/sync-argocd.sh dev

# Health checks
playwright-tests:
  before_script:
    - .gitlab-ci/scripts/check-health.sh
```

## Configuration Files

### settings.xml.template

Maven settings template for Nexus authentication and repository configuration.

**Location:** `.gitlab-ci/settings.xml.template`

**Usage:**
The template contains placeholder variables that are replaced at runtime:
- `NEXUS_URL` - Replaced with actual Nexus URL
- `NEXUS_USERNAME` - Replaced with username
- `NEXUS_PASSWORD` - Replaced with password

**Processing:**
```bash
cp .gitlab-ci/settings.xml.template /root/.m2/settings.xml
sed -i "s|NEXUS_URL|${NEXUS_URL}|g" /root/.m2/settings.xml
sed -i "s|NEXUS_USERNAME|${NEXUS_USERNAME}|g" /root/.m2/settings.xml
sed -i "s|NEXUS_PASSWORD|${NEXUS_PASSWORD}|g" /root/.m2/settings.xml
```

## Error Handling

All scripts follow these error handling practices:

1. **Strict Mode:** `set -e` to exit on first error
2. **Validation:** Check required files and services exist
3. **Informative Messages:** Clear output for debugging
4. **Exit Codes:** Proper exit codes for CI integration
5. **Retry Logic:** Automatic retries for network operations

## Security Considerations

1. **Credentials:** Use GitLab CI variables for sensitive data
2. **Masked Variables:** Mark passwords as masked in GitLab
3. **Protected Branches:** Restrict deployment scripts to protected branches
4. **Timeout Limits:** Set reasonable timeouts to prevent hanging

## Troubleshooting

### Maven Deployment Fails

**Problem:** Maven deployment returns 401 Unauthorized

**Solution:**
- Check NEXUS_USERNAME and NEXUS_PASSWORD variables
- Verify Nexus credentials are correct
- Check settings.xml was properly configured

### ArgoCD Sync Fails

**Problem:** ArgoCD login or sync fails

**Solution:**
- Verify ArgoCD server is accessible
- Check ARGOCD_URL, username, and password
- Ensure application exists in ArgoCD
- Check ArgoCD CLI version compatibility

### Health Check Fails

**Problem:** Health check times out

**Solution:**
- Increase HEALTH_CHECK_ATTEMPTS or HEALTH_CHECK_INTERVAL
- Verify services are running: `podman ps`
- Check service logs: `podman logs <container>`
- Verify network connectivity to services

### Frontend Tarball Not Found

**Problem:** deploy-nexus-npm.sh cannot find tarball

**Solution:**
- Ensure package-frontend job completed successfully
- Check artifacts were passed to deploy-npm job
- Verify tarball naming matches pattern: frontend-*.tgz

## Maintenance

### Adding New Scripts

1. Create script in `.gitlab-ci/scripts/`
2. Add shebang: `#!/bin/bash`
3. Add `set -e` for error handling
4. Add descriptive header comment
5. Make executable: `chmod +x script.sh`
6. Document in this README
7. Add job to `.gitlab-ci.yml`

### Testing Scripts Locally

```bash
# Set required environment variables
export NEXUS_URL="http://nexus:8081"
export NEXUS_USERNAME="admin"
export NEXUS_PASSWORD="admin123"
export CI_PROJECT_DIR="/path/to/project"

# Run script
./script-name.sh
```

## Support

For issues or questions:
1. Check script output for error messages
2. Review GitLab CI job logs
3. Verify environment variables are set
4. Check service availability and logs
5. Review this documentation

## Version History

- v1.0.0 (2025-02-05): Initial release with all core scripts
  - deploy-nexus-maven.sh
  - deploy-nexus-npm.sh
  - sync-argocd.sh
  - check-health.sh
