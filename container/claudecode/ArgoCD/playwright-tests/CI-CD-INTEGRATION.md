# CI/CD Integration Guide

Complete guide for integrating Playwright E2E tests into your CI/CD pipeline.

## Table of Contents

- [Overview](#overview)
- [GitLab CI Integration](#gitlab-ci-integration)
- [GitHub Actions Integration](#github-actions-integration)
- [Jenkins Integration](#jenkins-integration)
- [Docker Integration](#docker-integration)
- [Pre-deployment Testing](#pre-deployment-testing)
- [Post-deployment Testing](#post-deployment-testing)
- [Test Parallelization](#test-parallelization)
- [Artifact Management](#artifact-management)
- [Notifications](#notifications)

## Overview

The Playwright test framework can be integrated into various CI/CD pipelines to:
- Validate deployments before production
- Run regression tests automatically
- Provide fast feedback on code changes
- Generate test reports and artifacts
- Block deployments on test failures

## GitLab CI Integration

### Basic Integration

Add to your `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - deploy

e2e-tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  before_script:
    - cd playwright-tests
    - npm ci
  script:
    - npm test
  artifacts:
    when: always
    paths:
      - playwright-tests/playwright-report/
      - playwright-tests/test-results/
      - playwright-tests/test-results.json
      - playwright-tests/junit-results.xml
    reports:
      junit: playwright-tests/junit-results.xml
    expire_in: 30 days
  only:
    - main
    - develop
    - merge_requests
```

### Advanced Integration with Environment

```yaml
e2e-tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  variables:
    PLAYWRIGHT_BASE_URL: "http://frontend-service:5006"
    PLAYWRIGHT_HEADLESS: "true"
    CI: "true"
  services:
    - name: postgres:15
      alias: db
    - name: backend-service:latest
      alias: backend
    - name: frontend-service:latest
      alias: frontend
  before_script:
    - cd playwright-tests
    - npm ci
    - sleep 10  # Wait for services to be ready
  script:
    - npm test
  artifacts:
    when: always
    paths:
      - playwright-tests/playwright-report/
      - playwright-tests/test-results/
      - playwright-tests/screenshots/
    reports:
      junit: playwright-tests/junit-results.xml
    expire_in: 30 days
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  retry:
    max: 2
    when:
      - script_failure
```

### Parallel Execution

```yaml
e2e-tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  parallel:
    matrix:
      - BROWSER: [chromium, firefox, webkit]
  variables:
    PLAYWRIGHT_BASE_URL: "${CI_ENVIRONMENT_URL}"
  before_script:
    - cd playwright-tests
    - npm ci
  script:
    - npx playwright test --project=${BROWSER}
  artifacts:
    when: always
    paths:
      - playwright-tests/playwright-report-${BROWSER}/
    expire_in: 7 days
```

### Multi-Environment Testing

```yaml
.e2e-test-template:
  stage: test
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  before_script:
    - cd playwright-tests
    - npm ci
  script:
    - npm test
  artifacts:
    when: always
    paths:
      - playwright-tests/playwright-report/
    expire_in: 30 days

e2e-staging:
  extends: .e2e-test-template
  variables:
    PLAYWRIGHT_BASE_URL: "https://staging.example.com"
  only:
    - develop

e2e-production:
  extends: .e2e-test-template
  variables:
    PLAYWRIGHT_BASE_URL: "https://production.example.com"
  only:
    - main
  when: manual
```

## GitHub Actions Integration

### Basic Workflow

Create `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd playwright-tests
          npm ci

      - name: Install Playwright browsers
        run: |
          cd playwright-tests
          npx playwright install --with-deps

      - name: Run Playwright tests
        run: |
          cd playwright-tests
          npm test
        env:
          PLAYWRIGHT_BASE_URL: http://localhost:5006

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-tests/playwright-report/
          retention-days: 30

      - name: Upload test screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: playwright-tests/screenshots/
```

### Advanced Workflow with Services

```yaml
name: E2E Tests with Services

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: orgmgmt
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      backend:
        image: ghcr.io/${{ github.repository }}/backend:latest
        env:
          DATABASE_URL: postgresql://postgres:postgres@postgres:5432/orgmgmt
        ports:
          - 8080:8080

      frontend:
        image: ghcr.io/${{ github.repository }}/frontend:latest
        env:
          VITE_API_BASE_URL: http://backend:8080
        ports:
          - 5006:5006

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: playwright-tests/package-lock.json

      - name: Install dependencies
        run: |
          cd playwright-tests
          npm ci
          npx playwright install --with-deps

      - name: Wait for services
        run: |
          sleep 10
          curl --retry 10 --retry-delay 3 --retry-connrefused http://localhost:5006

      - name: Run tests
        run: |
          cd playwright-tests
          npm test
        env:
          PLAYWRIGHT_BASE_URL: http://localhost:5006

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-tests/playwright-report/
```

### Matrix Testing

```yaml
name: E2E Tests Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        browser: [chromium, firefox, webkit]

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd playwright-tests
          npm ci
          npx playwright install --with-deps ${{ matrix.browser }}

      - name: Run tests
        run: |
          cd playwright-tests
          npx playwright test --project=${{ matrix.browser }}

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report-${{ matrix.os }}-${{ matrix.browser }}
          path: playwright-tests/playwright-report/
```

## Jenkins Integration

### Jenkinsfile

```groovy
pipeline {
    agent {
        docker {
            image 'mcr.microsoft.com/playwright:v1.40.0-focal'
        }
    }

    environment {
        PLAYWRIGHT_BASE_URL = 'http://localhost:5006'
        PLAYWRIGHT_HEADLESS = 'true'
        CI = 'true'
    }

    stages {
        stage('Install') {
            steps {
                dir('playwright-tests') {
                    sh 'npm ci'
                }
            }
        }

        stage('Test') {
            steps {
                dir('playwright-tests') {
                    sh 'npm test'
                }
            }
        }
    }

    post {
        always {
            dir('playwright-tests') {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'playwright-report',
                    reportFiles: 'index.html',
                    reportName: 'Playwright Test Report'
                ])

                junit 'junit-results.xml'

                archiveArtifacts artifacts: 'playwright-report/**/*', allowEmptyArchive: true
                archiveArtifacts artifacts: 'screenshots/**/*', allowEmptyArchive: true
            }
        }

        failure {
            emailext (
                subject: "E2E Tests Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "E2E tests have failed. Check ${env.BUILD_URL} for details.",
                to: 'team@example.com'
            )
        }
    }
}
```

## Docker Integration

### Build Test Container

```bash
cd playwright-tests
docker build -t orgmgmt-e2e-tests .
```

### Run Tests in Container

```bash
# Run with default settings
docker run orgmgmt-e2e-tests

# Run with custom URL
docker run -e PLAYWRIGHT_BASE_URL=http://host.docker.internal:5006 orgmgmt-e2e-tests

# Run with volume mounts for reports
docker run \
  -v $(pwd)/reports:/tests/playwright-report \
  -e PLAYWRIGHT_BASE_URL=http://host.docker.internal:5006 \
  orgmgmt-e2e-tests

# Run specific suite
docker run orgmgmt-e2e-tests npm run test:organizations
```

### Docker Compose Integration

Create `docker-compose.test.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: orgmgmt
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/orgmgmt
    ports:
      - "8080:8080"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    environment:
      VITE_API_BASE_URL: http://backend:8080
    ports:
      - "5006:5006"

  e2e-tests:
    build: ./playwright-tests
    depends_on:
      - frontend
    environment:
      PLAYWRIGHT_BASE_URL: http://frontend:5006
    volumes:
      - ./playwright-tests/playwright-report:/tests/playwright-report
      - ./playwright-tests/test-results:/tests/test-results
```

Run with:

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit e2e-tests
```

## Pre-deployment Testing

### ArgoCD Pre-Sync Hook

Create `argocd-presync-test.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: e2e-tests-presync
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
spec:
  template:
    spec:
      containers:
      - name: playwright-tests
        image: mcr.microsoft.com/playwright:v1.40.0-focal
        command:
          - /bin/sh
          - -c
          - |
            cd /tests
            npm ci
            npm test
        env:
        - name: PLAYWRIGHT_BASE_URL
          value: "http://frontend-service:5006"
        volumeMounts:
        - name: test-code
          mountPath: /tests
      volumes:
      - name: test-code
        configMap:
          name: playwright-tests
      restartPolicy: Never
  backoffLimit: 2
```

## Post-deployment Testing

### Smoke Tests

Create `smoke-tests.sh`:

```bash
#!/bin/bash

# Run smoke tests after deployment
cd playwright-tests

# Run only critical path tests
npx playwright test tests/organizations/crud.spec.ts -g "should create new organization"
npx playwright test tests/users/crud.spec.ts -g "should create new user"

if [ $? -eq 0 ]; then
  echo "Smoke tests passed"
  exit 0
else
  echo "Smoke tests failed"
  exit 1
fi
```

### Health Check Tests

```bash
#!/bin/bash

# Quick health check
cd playwright-tests

npx playwright test \
  --grep "should list" \
  --project=chromium \
  --workers=1

exit $?
```

## Test Parallelization

### Parallel Execution by Suite

```bash
# GitLab CI
parallel:
  matrix:
    - SUITE: [organizations, departments, users, errors]

script:
  - npm run test:${SUITE}
```

### Parallel Execution by Browser

```bash
# Run all browsers in parallel
npx playwright test --workers=3
```

### Sharding for Large Test Suites

```yaml
# GitLab CI
parallel: 4

script:
  - npx playwright test --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
```

## Artifact Management

### Store Test Reports

```yaml
# GitLab CI
artifacts:
  when: always
  paths:
    - playwright-tests/playwright-report/
    - playwright-tests/test-results/
    - playwright-tests/screenshots/
  expire_in: 30 days
  reports:
    junit: playwright-tests/junit-results.xml
```

### Upload to External Storage

```bash
# Upload to S3
aws s3 cp playwright-report/ s3://test-reports/e2e-tests/ --recursive

# Upload to Azure Blob
az storage blob upload-batch -s playwright-report/ -d test-reports
```

## Notifications

### Slack Notification

```bash
#!/bin/bash

# Send test results to Slack
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

if [ $TEST_RESULT -eq 0 ]; then
  STATUS="✅ Passed"
  COLOR="good"
else
  STATUS="❌ Failed"
  COLOR="danger"
fi

curl -X POST $SLACK_WEBHOOK -H 'Content-type: application/json' -d "{
  \"attachments\": [{
    \"color\": \"$COLOR\",
    \"title\": \"E2E Tests $STATUS\",
    \"text\": \"Branch: $CI_COMMIT_BRANCH\nCommit: $CI_COMMIT_SHORT_SHA\",
    \"fields\": [
      {\"title\": \"Total Tests\", \"value\": \"$TOTAL_TESTS\", \"short\": true},
      {\"title\": \"Passed\", \"value\": \"$PASSED_TESTS\", \"short\": true}
    ]
  }]
}"
```

### Email Notification

```yaml
# GitLab CI
after_script:
  - |
    if [ $CI_JOB_STATUS == 'failed' ]; then
      echo "E2E tests failed" | mail -s "E2E Test Failure" team@example.com
    fi
```

## Best Practices

1. **Run on Every PR**
   - Catch issues early
   - Prevent broken merges

2. **Parallel Execution**
   - Faster feedback
   - Efficient resource usage

3. **Store Artifacts**
   - Debug failures
   - Historical tracking

4. **Retry Failed Tests**
   - Handle flakiness
   - Reduce false failures

5. **Environment Isolation**
   - Clean test environment
   - Consistent results

6. **Fast Smoke Tests**
   - Quick validation
   - Pre-deployment checks

7. **Comprehensive Reports**
   - HTML reports
   - JUnit XML
   - Screenshots

8. **Notifications**
   - Alert on failures
   - Keep team informed

## Troubleshooting

### Tests Fail in CI but Pass Locally

- Check environment variables
- Verify service availability
- Review timing/waits
- Check resource constraints

### Flaky Tests

- Add explicit waits
- Enable retries
- Review test isolation
- Check network stability

### Slow Execution

- Enable parallelization
- Optimize test data
- Review timeout values
- Use sharding

## Monitoring and Metrics

### Track Test Metrics

- Execution time
- Success rate
- Flakiness rate
- Coverage trends

### Dashboard Integration

- Grafana for metrics
- Test result trends
- Failure analysis
- Performance tracking

## Conclusion

Integrating Playwright E2E tests into your CI/CD pipeline:
- Ensures quality before deployment
- Provides fast feedback
- Prevents regressions
- Automates testing workflow
- Improves release confidence

Choose the integration method that best fits your CI/CD platform and customize as needed.
