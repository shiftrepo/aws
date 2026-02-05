# GitLab CI/CD Pipeline - Quick Start Guide

## Prerequisites

1. GitLab instance running
2. GitLab Runner with these tags: `argocd`, `podman`
3. Services running:
   - Nexus Repository: http://nexus:8081
   - Container Registry: localhost:5005
   - ArgoCD: localhost:5010

## Setup Steps

### 1. Configure GitLab CI/CD Variables

Navigate to: **Settings > CI/CD > Variables**

Add these secret variables:

```
NEXUS_USERNAME = admin
NEXUS_PASSWORD = admin123
REGISTRY_USERNAME = admin
REGISTRY_PASSWORD = admin123
ARGOCD_USERNAME = admin
ARGOCD_PASSWORD = admin123
```

Mark all as:
- [x] Protected
- [x] Masked

### 2. Verify Runner Configuration

Check that your GitLab Runner has the required tags:

```bash
# On GitLab Runner host
gitlab-runner list
```

Expected output should show tags: `argocd, podman`

### 3. Push to GitLab

```bash
# Add GitLab remote (if not already added)
git remote add gitlab https://gitlab.example.com/your-org/orgmgmt.git

# Push to GitLab
git push gitlab main
```

### 4. Verify Pipeline Execution

1. Go to: **CI/CD > Pipelines**
2. Click on the latest pipeline
3. Watch stages execute in order

Expected stages:
```
build-backend → test-backend → build-frontend → test-frontend →
package → nexus-deploy → container-build → gitops-update →
argocd-sync → e2e-test
```

## Pipeline Behavior by Branch

### Feature Branches
- Runs stages 1-5 (build, test, package)
- No deployment
- Duration: ~10 minutes

### Develop Branch
- Runs stages 1-7 (includes nexus-deploy, container-build)
- No ArgoCD sync or E2E tests
- Duration: ~15-20 minutes

### Main Branch
- Runs all 10 stages
- Deploys to development environment
- Runs E2E tests
- Duration: ~25-35 minutes

## Viewing Results

### Pipeline Status
- **URL:** GitLab → CI/CD → Pipelines
- **Status:** Success/Failed/Running
- **Duration:** Total execution time

### Test Coverage
- **URL:** GitLab → Repository → Analytics → Coverage
- **Backend:** JaCoCo coverage report
- **Frontend:** Jest coverage report
- **Target:** 80% minimum

### Artifacts
- **URL:** GitLab → CI/CD → Jobs → Specific Job → Download Artifacts
- **Backend JAR:** package-backend job
- **Frontend Tarball:** package-frontend job
- **Test Reports:** maven-test, npm-test jobs
- **E2E Results:** playwright-tests job

### ArgoCD Deployment
- **URL:** http://localhost:5010
- **Application:** orgmgmt-dev
- **Status:** Check sync status and health

## Troubleshooting

### Pipeline Fails on maven-build

**Problem:** Maven cannot download dependencies

**Solution:**
```bash
# Check Nexus is running
podman ps | grep nexus

# Check Nexus is accessible
curl http://nexus:8081/
```

### Pipeline Fails on deploy-maven

**Problem:** 401 Unauthorized

**Solution:**
1. Verify NEXUS_USERNAME and NEXUS_PASSWORD in GitLab variables
2. Check Nexus user has deployment permissions
3. Ensure repositories exist in Nexus

### Pipeline Fails on deploy-dev

**Problem:** ArgoCD sync fails

**Solution:**
```bash
# Check ArgoCD is running
podman ps | grep argocd

# Login to ArgoCD CLI
argocd login localhost:5010 --username admin --password admin123 --insecure

# Check application exists
argocd app list

# Check application status
argocd app get orgmgmt-dev
```

### Pipeline Fails on playwright-tests

**Problem:** E2E tests timeout or fail

**Note:** This job has `allow_failure: true`, so it won't block the pipeline

**Solution:**
1. Check application is accessible
2. Run health check manually:
   ```bash
   .gitlab-ci/scripts/check-health.sh
   ```
3. Review test logs in job artifacts

## Testing Pipeline Locally

### Test Scripts Individually

```bash
# Set environment variables
export CI_PROJECT_DIR="/path/to/project"
export NEXUS_URL="http://nexus:8081"
export NEXUS_USERNAME="admin"
export NEXUS_PASSWORD="admin123"
export VERSION="test-123"

# Test Maven deployment
cd app/backend
mvn clean package
cd ../..
.gitlab-ci/scripts/deploy-nexus-maven.sh

# Test NPM deployment
cd app/frontend
npm run build
tar -czf frontend-test.tgz dist/
cd ../..
.gitlab-ci/scripts/deploy-nexus-npm.sh

# Test ArgoCD sync
.gitlab-ci/scripts/sync-argocd.sh dev

# Test health check
.gitlab-ci/scripts/check-health.sh
```

### Test with GitLab Runner Locally

```bash
# Install gitlab-runner locally
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh | sudo bash
sudo yum install gitlab-runner

# Run specific job
gitlab-runner exec docker maven-build \
  --docker-image maven:3.9-eclipse-temurin-17
```

## Manual Pipeline Triggers

### Trigger Pipeline from GitLab UI

1. Go to: **CI/CD > Pipelines**
2. Click: **Run pipeline**
3. Select branch: `main`
4. Click: **Run pipeline**

### Trigger Pipeline from CLI

```bash
# Using GitLab API
curl -X POST \
  -F token=<pipeline_token> \
  -F ref=main \
  https://gitlab.example.com/api/v4/projects/<project_id>/trigger/pipeline
```

## Monitoring Tips

### Watch Pipeline Progress

```bash
# Using GitLab CLI
glab ci view

# Or watch in browser
# URL: https://gitlab.example.com/your-org/orgmgmt/-/pipelines
```

### Check Job Logs

```bash
# Using GitLab CLI
glab ci trace <job-id>

# Or view in browser
# URL: https://gitlab.example.com/your-org/orgmgmt/-/jobs/<job-id>
```

### Monitor ArgoCD Sync

```bash
# Watch sync progress
argocd app sync orgmgmt-dev --async
argocd app wait orgmgmt-dev

# Check application health
watch argocd app get orgmgmt-dev
```

## Performance Tips

### Enable Distributed Cache

For faster builds, enable distributed caching:

```yaml
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .m2/repository/
    - node_modules/
  policy: pull-push
```

### Use Kaniko for Container Builds

Replace Podman with Kaniko for better CI performance:

```yaml
build-containers:
  image:
    name: gcr.io/kaniko-project/executor:debug
    entrypoint: [""]
  script:
    - /kaniko/executor --context . --dockerfile Dockerfile
```

### Parallel Matrix Jobs

Run tests in parallel:

```yaml
maven-test:
  parallel:
    matrix:
      - PROFILE: [unit, integration]
  script:
    - mvn test -P${PROFILE}
```

## Security Best Practices

1. **Never commit secrets** - Use GitLab CI/CD variables
2. **Use protected variables** - For production credentials
3. **Enable branch protection** - Require pipeline success before merge
4. **Regular updates** - Keep base images updated
5. **Scan vulnerabilities** - Add security scanning stages

## Next Steps

1. Review pipeline results
2. Check code coverage reports
3. Verify ArgoCD deployment
4. Run manual tests on deployed application
5. Monitor application health
6. Review and optimize pipeline performance

## Support Resources

- **Pipeline Overview:** `.gitlab-ci/PIPELINE-OVERVIEW.md`
- **Script Documentation:** `.gitlab-ci/scripts/README.md`
- **GitLab CI/CD Docs:** https://docs.gitlab.com/ee/ci/
- **ArgoCD Docs:** https://argo-cd.readthedocs.io/

## Quick Commands Reference

```bash
# Check pipeline status
glab ci status

# View latest pipeline
glab ci view

# Download artifacts
glab ci artifact <job-name>

# Retry failed job
glab ci retry <job-id>

# Cancel running pipeline
glab ci delete <pipeline-id>

# View pipeline variables
glab ci list --output-format json | jq '.[0].variables'
```

---

**Ready to deploy?** Push to `main` branch and watch your pipeline execute!
