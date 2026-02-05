# GitLab CI/CD Pipeline Overview

## Pipeline Architecture

This comprehensive GitLab CI/CD pipeline implements a complete DevOps workflow for the Organization Management application, featuring 10 stages with automated testing, artifact management, container builds, GitOps updates, and end-to-end testing.

## Pipeline Stages

```
build-backend → test-backend → build-frontend → test-frontend → package →
nexus-deploy → container-build → gitops-update → argocd-sync → e2e-test
```

### Stage Details

| Stage | Job | Purpose | Duration |
|-------|-----|---------|----------|
| 1. build-backend | maven-build | Compile Java source code | ~2-3 min |
| 2. test-backend | maven-test | Run unit tests + JaCoCo coverage | ~3-5 min |
| 3. build-frontend | npm-build | Build React application | ~2-3 min |
| 4. test-frontend | npm-test | Run Jest tests + coverage | ~1-2 min |
| 5. package | package-backend<br>package-frontend | Create JAR and tarball | ~1-2 min |
| 6. nexus-deploy | deploy-maven<br>deploy-npm | Upload artifacts to Nexus | ~1 min |
| 7. container-build | build-containers | Build and push container images | ~3-5 min |
| 8. gitops-update | update-manifests | Update GitOps manifests | ~1 min |
| 9. argocd-sync | deploy-dev | Sync ArgoCD application | ~2-3 min |
| 10. e2e-test | playwright-tests | Run E2E tests | ~5-10 min |

**Total Pipeline Duration:** ~20-35 minutes

## Job Configuration Matrix

### Build & Test Jobs

#### maven-build
```yaml
stage: build-backend
image: maven:3.9-eclipse-temurin-17
cache: .m2/repository/
artifacts: app/backend/target/ (1 hour)
```

#### maven-test
```yaml
stage: test-backend
dependencies: [maven-build]
coverage: JaCoCo XML report
reports: JUnit + Cobertura
artifacts: target/site/jacoco/ (1 week)
```

#### npm-build
```yaml
stage: build-frontend
image: node:20-alpine
cache: node_modules/
artifacts: dist/ (1 hour)
```

#### npm-test
```yaml
stage: test-frontend
dependencies: [npm-build]
coverage: Jest coverage
reports: Cobertura
artifacts: coverage/ (1 week)
```

### Package Jobs

#### package-backend
```yaml
stage: package
dependencies: [maven-build, maven-test]
output: orgmgmt-backend.jar
artifacts: target/*.jar (1 day)
```

#### package-frontend
```yaml
stage: package
dependencies: [npm-build]
output: frontend-{VERSION}.tgz
artifacts: *.tgz (1 day)
```

### Deployment Jobs

#### deploy-maven
```yaml
stage: nexus-deploy
script: .gitlab-ci/scripts/deploy-nexus-maven.sh
target: maven-snapshots repository
only: [main, develop]
```

#### deploy-npm
```yaml
stage: nexus-deploy
script: .gitlab-ci/scripts/deploy-nexus-npm.sh
target: npm-hosted repository
only: [main, develop]
```

#### build-containers
```yaml
stage: container-build
script:
  - container-builder/scripts/build-from-nexus.sh
  - container-builder/scripts/push-to-registry.sh
output:
  - localhost:5005/orgmgmt-backend:{VERSION}
  - localhost:5005/orgmgmt-frontend:{VERSION}
only: [main, develop]
```

#### update-manifests
```yaml
stage: gitops-update
script: container-builder/scripts/update-gitops.sh
updates: gitops/dev/podman-compose.yml
only: [main]
```

#### deploy-dev
```yaml
stage: argocd-sync
script: .gitlab-ci/scripts/sync-argocd.sh dev
target: orgmgmt-dev application
environment: development
only: [main]
```

#### playwright-tests
```yaml
stage: e2e-test
script: scripts/run-e2e-tests.sh
artifacts: playwright-report/, screenshots/
only: [main]
allow_failure: true
```

## Pipeline Variables

### Global Variables

```yaml
MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
NEXUS_URL: "http://nexus:8081"
REGISTRY_URL: "localhost:5005"
ARGOCD_URL: "localhost:5010"
VERSION: "$CI_COMMIT_SHORT_SHA"
MAVEN_REPO: "maven-snapshots"
NPM_REPO: "npm-hosted"
BACKEND_IMAGE: "orgmgmt-backend"
FRONTEND_IMAGE: "orgmgmt-frontend"
```

### Secret Variables (Configure in GitLab)

Required secret variables to configure in GitLab CI/CD settings:

```
NEXUS_USERNAME=admin
NEXUS_PASSWORD=admin123
REGISTRY_USERNAME=admin
REGISTRY_PASSWORD=admin123
ARGOCD_USERNAME=admin
ARGOCD_PASSWORD=admin123
```

## Cache Strategy

### Maven Cache
- **Key:** maven-cache
- **Paths:** .m2/repository/
- **Shared by:** maven-build, maven-test, package-backend, deploy-maven
- **Policy:** pull (after initial build)

### NPM Cache
- **Key:** npm-cache
- **Paths:** app/frontend/.npm/, app/frontend/node_modules/
- **Shared by:** npm-build, npm-test, playwright-tests
- **Policy:** pull (after initial build)

## Artifact Flow

```
maven-build (target/)
    ↓
maven-test (uses target/)
    ↓
package-backend (creates JAR)
    ↓
deploy-maven (uploads JAR to Nexus)
    ↓
build-containers (downloads from Nexus)

npm-build (dist/)
    ↓
npm-test (uses dist/)
    ↓
package-frontend (creates tarball)
    ↓
deploy-npm (uploads tarball to Nexus)
    ↓
build-containers (downloads from Nexus)
```

## Branch Strategy

### Main Branch
- All 10 stages execute
- Deploys to development environment
- Triggers ArgoCD sync
- Runs E2E tests

### Develop Branch
- Stages 1-7 execute (up to container-build)
- No ArgoCD sync
- No E2E tests

### Feature Branches
- Stages 1-5 execute (up to package)
- No deployment stages
- No container builds

### Configuration Example

```yaml
# Jobs that run only on main
only:
  - main

# Jobs that run on main and develop
only:
  - main
  - develop
```

## Coverage Reporting

### Backend Coverage (JaCoCo)
- **Format:** Cobertura XML
- **Path:** app/backend/target/site/jacoco/jacoco.xml
- **Minimum:** 80% line coverage
- **Report:** Available in GitLab MR widget

### Frontend Coverage (Jest)
- **Format:** Cobertura XML
- **Path:** app/frontend/coverage/cobertura-coverage.xml
- **Report:** Available in GitLab MR widget

### Coverage Badges

Add to README.md:
```markdown
![Backend Coverage](https://gitlab.com/user/repo/badges/main/coverage.svg?job=maven-test)
![Frontend Coverage](https://gitlab.com/user/repo/badges/main/coverage.svg?job=npm-test)
```

## Deployment Environments

### Development
- **URL:** http://localhost:5006
- **ArgoCD App:** orgmgmt-dev
- **Deployed From:** main branch
- **Auto-sync:** Yes
- **E2E Tests:** Yes

### Staging (Future)
- **URL:** TBD
- **ArgoCD App:** orgmgmt-staging
- **Deployed From:** release branches
- **Auto-sync:** No (manual approval)

### Production (Future)
- **URL:** TBD
- **ArgoCD App:** orgmgmt-prod
- **Deployed From:** tags
- **Auto-sync:** No (manual approval)

## Supporting Scripts

### deploy-nexus-maven.sh
Deploys Maven artifacts to Nexus Repository.

**Features:**
- Configures Maven settings.xml with credentials
- Updates pom.xml URLs with environment variables
- Deploys to maven-snapshots repository
- Verifies deployment success

**Variables:**
- NEXUS_URL, NEXUS_USERNAME, NEXUS_PASSWORD
- MAVEN_REPO, CI_PROJECT_DIR

### deploy-nexus-npm.sh
Deploys frontend artifacts to Nexus Repository.

**Features:**
- Uploads tarball using curl
- Validates upload with HTTP status codes
- Verifies artifact accessibility
- Supports npm-hosted or raw repositories

**Variables:**
- NEXUS_URL, NEXUS_USERNAME, NEXUS_PASSWORD
- NPM_REPO, VERSION, CI_PROJECT_DIR

### sync-argocd.sh
Triggers ArgoCD application sync.

**Features:**
- Authenticates with ArgoCD server
- Checks application exists
- Triggers sync with prune
- Waits for sync completion with timeout
- Displays sync status and history

**Variables:**
- ARGOCD_URL, ARGOCD_USERNAME, ARGOCD_PASSWORD
- ARGOCD_SYNC_TIMEOUT (default: 300s)

**Usage:**
```bash
./sync-argocd.sh dev
./sync-argocd.sh staging
./sync-argocd.sh prod
```

### check-health.sh
Verifies application health.

**Features:**
- Checks backend /actuator/health endpoint
- Checks frontend accessibility
- Retries with configurable attempts
- Provides diagnostics on failure
- Displays container status

**Variables:**
- BACKEND_URL, FRONTEND_URL
- HEALTH_CHECK_ATTEMPTS (default: 30)
- HEALTH_CHECK_INTERVAL (default: 10s)

## Pipeline Execution Flow

### On Push to Feature Branch

```
1. maven-build
2. maven-test
3. npm-build
4. npm-test
5. package-backend
6. package-frontend
[STOP - No deployment]
```

### On Push to Develop Branch

```
1-6. [Same as feature branch]
7. deploy-maven
8. deploy-npm
9. build-containers
[STOP - No GitOps/ArgoCD]
```

### On Push to Main Branch

```
1-9. [Same as develop branch]
10. update-manifests
11. deploy-dev
12. playwright-tests
[COMPLETE - Full pipeline]
```

## Error Handling

### Job Failures

All critical jobs have `allow_failure: false`:
- Pipeline stops on first failure
- Prevents cascading failures
- Saves CI/CD minutes

Exception: `playwright-tests` has `allow_failure: true`
- E2E tests are informational
- Don't block merges
- Can be flaky in CI environment

### Retry Strategy

Scripts implement retry logic:
- Health checks: 30 attempts × 10s = 5 minutes
- ArgoCD sync: 300s timeout
- Nexus uploads: Single attempt (fast fail)

### Debugging Failed Jobs

1. **Check job logs:** GitLab CI/CD → Jobs → Failed job
2. **View artifacts:** Download artifacts for inspection
3. **Review environment:** Check if services are running
4. **Validate credentials:** Ensure secret variables are set
5. **Test locally:** Run scripts with local environment

## Performance Optimization

### Cache Hits
- First run: ~25-30 minutes (no cache)
- Subsequent runs: ~15-20 minutes (with cache)
- Savings: ~40-50% time reduction

### Parallel Execution
- package-backend and package-frontend run in parallel
- deploy-maven and deploy-npm run in parallel
- Total savings: ~2-3 minutes

### Artifact Size Management
- Short expiration for build artifacts (1 hour)
- Medium expiration for test reports (1 week)
- Long expiration for packages (1 day)

## Monitoring & Observability

### Pipeline Metrics
- Success rate
- Average duration
- Failure reasons
- Coverage trends

### View in GitLab
- **Pipelines:** CI/CD → Pipelines
- **Jobs:** CI/CD → Jobs
- **Coverage:** Repository → Analytics → Coverage
- **Environments:** Deployments → Environments

### ArgoCD Metrics
- Sync status
- Health status
- Resource count
- Deployment history

### View in ArgoCD
- **Applications:** http://localhost:5010/applications
- **orgmgmt-dev:** http://localhost:5010/applications/orgmgmt-dev

## Troubleshooting Guide

### Pipeline Stuck on maven-build

**Symptoms:** Job runs for >10 minutes

**Causes:**
- Downloading dependencies (first run)
- Network issues with Maven Central
- Nexus proxy not working

**Solutions:**
- Wait for cache to populate
- Check Nexus is running: `podman ps | grep nexus`
- Verify Maven mirror configuration

### Nexus Deployment 401 Unauthorized

**Symptoms:** deploy-maven or deploy-npm fails with HTTP 401

**Causes:**
- Incorrect credentials
- Nexus user doesn't have write permissions
- Repository doesn't exist

**Solutions:**
- Verify NEXUS_USERNAME and NEXUS_PASSWORD
- Check Nexus user roles
- Create repositories in Nexus

### ArgoCD Sync Fails

**Symptoms:** deploy-dev fails with timeout or error

**Causes:**
- ArgoCD not running
- Application not created
- Git repository not accessible
- Health check fails

**Solutions:**
- Verify ArgoCD is running: `podman ps | grep argocd`
- Check application exists: `argocd app list`
- Review application status: `argocd app get orgmgmt-dev`
- Check pod health: `podman ps`

### E2E Tests Timeout

**Symptoms:** playwright-tests fails with timeout

**Causes:**
- Application not ready
- Health check passed but app not stable
- Network connectivity issues

**Solutions:**
- Increase sleep time in before_script
- Check application logs
- Run tests locally first
- Increase HEALTH_CHECK_ATTEMPTS

## Best Practices

### 1. Commit Messages
```
feat: Add employee CRUD endpoints
fix: Resolve pagination issue
test: Add integration tests for departments
docs: Update API documentation
```

### 2. Branch Naming
```
feature/employee-crud
bugfix/pagination-error
hotfix/security-vulnerability
release/v1.0.0
```

### 3. Merge Requests
- Wait for pipeline to pass
- Review coverage reports
- Check for deployment success
- Verify E2E test results

### 4. Secret Management
- Never commit credentials
- Use GitLab CI/CD variables
- Mark sensitive variables as masked
- Use protected variables for production

### 5. Testing Strategy
- Unit tests: >80% coverage
- Integration tests: Critical paths
- E2E tests: User workflows
- Health checks: Before E2E tests

## Maintenance Tasks

### Weekly
- Review failed pipelines
- Check artifact storage usage
- Monitor coverage trends
- Review E2E test results

### Monthly
- Update dependencies
- Review and optimize cache strategy
- Clean up old artifacts
- Update documentation

### Quarterly
- Update container base images
- Review and update secrets
- Optimize pipeline performance
- Conduct security audit

## Future Enhancements

### Planned Features
1. Staging environment deployment
2. Production environment with approvals
3. Slack/email notifications
4. Performance testing stage
5. Security scanning (SAST/DAST)
6. Container vulnerability scanning
7. Automated rollback on failure
8. Blue-green deployment strategy

### Configuration Examples

#### Add Slack Notifications
```yaml
.notify-slack:
  script:
    - 'curl -X POST -H "Content-type: application/json" --data "{\"text\":\"Pipeline ${CI_PIPELINE_STATUS}\"}" ${SLACK_WEBHOOK_URL}'
```

#### Add Security Scanning
```yaml
security-scan:
  stage: test
  image: aquasec/trivy:latest
  script:
    - trivy image ${REGISTRY_URL}/${BACKEND_IMAGE}:${VERSION}
```

## Resources

### Documentation
- GitLab CI/CD: https://docs.gitlab.com/ee/ci/
- ArgoCD: https://argo-cd.readthedocs.io/
- Nexus Repository: https://help.sonatype.com/repomanager3

### Support
- Script documentation: `.gitlab-ci/scripts/README.md`
- Pipeline configuration: `.gitlab-ci.yml`
- Container builds: `container-builder/README.md`
- GitOps manifests: `gitops/README.md`

## Version History

- **v1.0.0** (2025-02-05): Initial complete pipeline
  - 10-stage pipeline
  - 4 supporting scripts
  - Maven settings template
  - Comprehensive documentation

---

For questions or issues, review the troubleshooting guide or check job logs in GitLab CI/CD.
