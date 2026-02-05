# Organization Management System with ArgoCD

A complete enterprise-grade DevOps platform demonstrating modern CI/CD practices using GitOps methodology with ArgoCD, containerization with Podman, and infrastructure automation with Ansible.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Testing](#testing)
- [Monitoring and Observability](#monitoring-and-observability)
- [Backup and Recovery](#backup-and-recovery)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project implements a complete organization management system with a modern DevOps pipeline. It demonstrates:

- **Full-stack Application**: Spring Boot backend with React frontend
- **GitOps Deployment**: Automated deployment using ArgoCD
- **Container Orchestration**: Podman and podman-compose for container management
- **CI/CD Pipeline**: Complete GitLab CI/CD pipeline with automated testing
- **Infrastructure as Code**: Ansible automation for infrastructure deployment
- **Artifact Management**: Nexus Repository for Maven and npm artifacts
- **End-to-End Testing**: Playwright-based automated testing
- **Database Management**: PostgreSQL with Flyway migrations

### Key Features

- Manage organizations, departments, and users
- RESTful API with Spring Boot
- Modern React frontend with Vite
- GitOps-based deployment workflow
- Automated testing and code coverage
- Multi-environment support (dev, staging, prod)
- Automated backup and restore
- Health monitoring and observability
- Role-based access control ready
- Containerized deployment

## Architecture

### System Architecture Diagram

```
                                    ┌─────────────────────────────────────┐
                                    │         Developer                   │
                                    │   (Git Push to GitLab)              │
                                    └────────────────┬────────────────────┘
                                                     │
                                                     ▼
                    ┌────────────────────────────────────────────────────┐
                    │              GitLab CE + Container Registry        │
                    │  - Source Code Management                          │
                    │  - CI/CD Pipeline Execution                        │
                    │  - Container Image Registry                        │
                    └────────────────┬──────────────┬────────────────────┘
                                     │              │
                    ┌────────────────▼──────────┐   │
                    │   GitLab Runner           │   │
                    │  - Build Jobs             │   │
                    │  - Test Execution         │   │
                    │  - Artifact Publishing    │   │
                    └────────────┬──────────────┘   │
                                 │                  │
                ┌────────────────▼──────────────┐   │
                │   Nexus Repository Manager    │   │
                │  - Maven Artifacts            │   │
                │  - npm Packages               │   │
                │  - Binary Storage             │   │
                └────────────┬──────────────────┘   │
                             │                      │
            ┌────────────────▼──────────────────────▼──────────────┐
            │          Container Builder                            │
            │  - Pull artifacts from Nexus                          │
            │  - Build container images                             │
            │  - Push to GitLab Registry                            │
            └────────────────┬─────────────────────────────────────┘
                             │
            ┌────────────────▼─────────────────────────────────────┐
            │          GitOps Repository                            │
            │  - deployment manifests                               │
            │  - podman-compose.yml files                           │
            │  - Image tag updates                                  │
            └────────────────┬─────────────────────────────────────┘
                             │
            ┌────────────────▼─────────────────────────────────────┐
            │              ArgoCD                                   │
            │  - Monitor GitOps repo                                │
            │  - Automated sync                                     │
            │  - Self-healing                                       │
            │  - Rollback capabilities                              │
            └────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────────┐                    ┌───────────────────┐
│   Dev Environment │                    │  Staging/Prod     │
│  - Backend API    │                    │  - Backend API    │
│  - Frontend UI    │                    │  - Frontend UI    │
│  - PostgreSQL DB  │                    │  - PostgreSQL DB  │
└───────────────────┘                    └───────────────────┘
```

### Technology Stack

**Backend:**
- Java 17
- Spring Boot 3.2.1
- Spring Data JPA
- PostgreSQL 16
- Flyway Database Migration
- Maven 3.9
- JaCoCo (Code Coverage)

**Frontend:**
- React 18.2
- Vite 5.0
- React Router 6
- Axios
- Jest (Testing)

**DevOps & Infrastructure:**
- Podman & podman-compose
- ArgoCD v2.10.0
- GitLab CE (latest)
- GitLab Runner
- Nexus Repository Manager 3
- Ansible 2.x
- Playwright (E2E Testing)

**Database:**
- PostgreSQL 16
- pgAdmin 4

**Monitoring:**
- Spring Boot Actuator
- Container health checks
- ArgoCD dashboard

## Prerequisites

### System Requirements

- **Operating System**: RHEL 9 or compatible Linux distribution
- **CPU**: 4 cores minimum (8 cores recommended)
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Disk Space**: 50GB free space minimum
- **Network**: Internet connection for downloading images and dependencies

### Required Software

Install the following software before starting:

```bash
# Update system
sudo dnf update -y

# Install Podman and podman-compose
sudo dnf install -y podman podman-compose

# Install Git
sudo dnf install -y git

# Install jq (JSON processor)
sudo dnf install -y jq

# Install curl
sudo dnf install -y curl

# Install OpenSSL
sudo dnf install -y openssl

# Install Ansible (optional, for infrastructure automation)
sudo dnf install -y ansible

# Install Node.js and npm (for local development)
sudo dnf install -y nodejs npm

# Verify installations
podman --version
podman-compose --version
git --version
jq --version
curl --version
node --version
npm --version
```

### Port Requirements

Ensure the following ports are available:

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| PostgreSQL | 5432 | TCP | Database |
| pgAdmin | 5050 | TCP | Database Management |
| GitLab | 5003 | TCP | Source Control |
| GitLab Registry | 5005 | TCP | Container Registry |
| GitLab SSH | 2222 | TCP | Git SSH Access |
| Nexus | 8081 | TCP | Artifact Repository |
| Nexus Docker | 8082 | TCP | Docker Registry |
| ArgoCD Server | 5010 | TCP | ArgoCD UI/API |
| Redis | 6379 | TCP | ArgoCD Cache |
| Backend API | 8080 | TCP | Application API |
| Frontend | 5006 | TCP | Application UI |

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone <repository-url>
cd ArgoCD

# 2. Run the setup script
./scripts/setup.sh

# 3. Wait for services to start (5-10 minutes)
# The script will automatically:
#   - Check prerequisites
#   - Start all infrastructure services
#   - Wait for services to be healthy
#   - Generate and save credentials

# 4. Access the services
# See credentials.txt for login information
cat credentials.txt
```

### Access URLs

After setup completes, access the services:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **Application UI** | http://localhost:5006 | No auth required |
| **Backend API** | http://localhost:8080 | No auth required |
| **ArgoCD** | http://localhost:5010 | admin / (see credentials.txt) |
| **GitLab** | http://localhost:5003 | root / (see credentials.txt) |
| **Nexus** | http://localhost:8081 | admin / (see credentials.txt) |
| **pgAdmin** | http://localhost:5050 | (see credentials.txt) |

### Quick Verification

```bash
# Check all services are running
./scripts/status.sh

# View logs
./scripts/logs.sh

# Run health checks
curl http://localhost:8080/actuator/health
curl http://localhost:5006
```

## Directory Structure

```
ArgoCD/
├── ansible/                          # Infrastructure automation
│   ├── inventory/
│   │   └── hosts.yml                 # Ansible inventory
│   └── playbooks/
│       ├── site.yml                  # Main playbook
│       ├── deploy_infrastructure.yml # Infrastructure deployment
│       ├── install_argocd.yml        # ArgoCD installation
│       ├── setup_application.yml     # Application setup
│       └── configure_podman_registry.yml
│
├── app/                              # Application source code
│   ├── backend/                      # Spring Boot backend
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/            # Java source code
│   │   │   │   │   └── com/example/orgmgmt/
│   │   │   │   │       ├── controller/    # REST controllers
│   │   │   │   │       ├── service/       # Business logic
│   │   │   │   │       ├── repository/    # Data access
│   │   │   │   │       ├── entity/        # JPA entities
│   │   │   │   │       ├── dto/           # Data transfer objects
│   │   │   │   │       └── exception/     # Exception handlers
│   │   │   │   └── resources/
│   │   │   │       ├── application.yml    # Spring configuration
│   │   │   │       └── db/migration/      # Flyway migrations
│   │   │   └── test/                      # Unit tests
│   │   ├── pom.xml                   # Maven configuration
│   │   ├── Dockerfile                # Backend container image
│   │   └── .dockerignore
│   │
│   └── frontend/                     # React frontend
│       ├── src/
│       │   ├── components/           # React components
│       │   ├── services/             # API services
│       │   ├── App.jsx               # Main app component
│       │   └── main.jsx              # Entry point
│       ├── __tests__/                # Unit tests
│       ├── package.json              # npm configuration
│       ├── vite.config.js            # Vite configuration
│       ├── Dockerfile                # Frontend container image
│       └── nginx.conf                # nginx configuration
│
├── infrastructure/                   # Infrastructure services
│   ├── podman-compose.yml            # Main compose file
│   ├── config/                       # Service configurations
│   │   ├── postgres/                 # PostgreSQL config
│   │   ├── gitlab/                   # GitLab config
│   │   ├── gitlab-runner/            # GitLab Runner config
│   │   └── nexus/                    # Nexus config
│   ├── start.sh                      # Start infrastructure
│   ├── stop.sh                       # Stop infrastructure
│   └── status.sh                     # Check status
│
├── gitops/                           # GitOps manifests
│   ├── dev/
│   │   └── podman-compose.yml        # Dev environment
│   ├── staging/
│   │   └── podman-compose.yml        # Staging environment
│   ├── prod/
│   │   └── podman-compose.yml        # Production environment
│   └── scripts/
│       ├── update-image-tag.sh       # Update image tags
│       └── validate-manifest.sh      # Validate manifests
│
├── argocd/                           # ArgoCD configuration
│   ├── applications/                 # Application definitions
│   │   ├── orgmgmt-dev.yaml
│   │   ├── orgmgmt-staging.yaml
│   │   └── orgmgmt-prod.yaml
│   ├── projects/
│   │   └── orgmgmt.yaml              # ArgoCD project
│   └── config/
│       ├── argocd-cm.yaml            # ArgoCD ConfigMap
│       └── argocd-rbac-cm.yaml       # RBAC configuration
│
├── container-builder/                # Container build pipeline
│   ├── scripts/
│   │   ├── build-from-nexus.sh       # Build from artifacts
│   │   ├── push-to-registry.sh       # Push to registry
│   │   └── update-gitops.sh          # Update GitOps manifests
│   └── Dockerfiles/
│       ├── backend.Dockerfile
│       └── frontend.Dockerfile
│
├── playwright-tests/                 # E2E tests
│   ├── tests/
│   │   ├── organizations/            # Organization tests
│   │   ├── departments/              # Department tests
│   │   ├── users/                    # User tests
│   │   └── error-scenarios/          # Error handling tests
│   ├── page-objects/                 # Page object models
│   ├── fixtures/                     # Test fixtures
│   ├── utils/                        # Test utilities
│   └── playwright.config.ts          # Playwright configuration
│
├── scripts/                          # Utility scripts
│   ├── common.sh                     # Common functions
│   ├── setup.sh                      # Master setup script
│   ├── build-and-deploy.sh           # Build and deploy
│   ├── argocd-deploy.sh              # Deploy with ArgoCD
│   ├── argocd-rollback.sh            # Rollback deployment
│   ├── test.sh                       # Run tests
│   ├── run-e2e-tests.sh              # Run E2E tests
│   ├── status.sh                     # Check service status
│   ├── logs.sh                       # View logs
│   ├── backup.sh                     # Backup data
│   ├── restore.sh                    # Restore data
│   └── cleanup.sh                    # Clean up resources
│
├── .gitlab-ci/                       # GitLab CI/CD
│   └── scripts/
│       ├── deploy-nexus-maven.sh     # Deploy Maven artifacts
│       ├── deploy-nexus-npm.sh       # Deploy npm packages
│       ├── sync-argocd.sh            # Sync ArgoCD
│       └── check-health.sh           # Health checks
│
├── .gitlab-ci.yml                    # GitLab CI/CD pipeline
├── README.md                         # This file
├── ARCHITECTURE.md                   # Architecture documentation
├── QUICKSTART.md                     # Quick start guide
├── TROUBLESHOOTING.md                # Troubleshooting guide
├── API.md                            # API documentation
├── CONTRIBUTING.md                   # Contribution guidelines
├── CHANGELOG.md                      # Version history
└── LICENSE                           # License file
```

## Getting Started

### Step-by-Step Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd ArgoCD
```

#### 2. Run Prerequisites Check

```bash
# Check if all required software is installed
./scripts/setup.sh --skip-checks  # Skip if you already verified

# Or manually check
podman --version
podman-compose --version
git --version
jq --version
```

#### 3. Start Infrastructure

```bash
# Start all infrastructure services
./scripts/setup.sh

# This will:
# - Create .env file with secure passwords
# - Start PostgreSQL, pgAdmin, Nexus, GitLab, ArgoCD
# - Wait for services to be healthy
# - Save credentials to credentials.txt
```

#### 4. Verify Services

```bash
# Check service status
./scripts/status.sh

# Should show all services as "healthy"
```

#### 5. Build and Deploy Application

```bash
# Build and deploy the application
./scripts/build-and-deploy.sh

# This will:
# - Build backend with Maven
# - Build frontend with npm
# - Create container images
# - Deploy to dev environment
```

#### 6. Access the Application

Open your browser and navigate to:
- Application: http://localhost:5006
- API Documentation: http://localhost:8080/actuator
- ArgoCD Dashboard: http://localhost:5010

### Manual Infrastructure Setup

If you prefer manual control:

```bash
# 1. Navigate to infrastructure directory
cd infrastructure

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env file with your settings
vim .env

# 4. Start services
podman-compose up -d

# 5. Check logs
podman-compose logs -f

# 6. Stop services
podman-compose down
```

## Development Workflow

### Local Development Setup

#### Backend Development

```bash
# Navigate to backend directory
cd app/backend

# Build the project
mvn clean install

# Run tests
mvn test

# Run locally (requires PostgreSQL)
mvn spring-boot:run

# Package as JAR
mvn package

# The backend will be available at http://localhost:8080
```

#### Frontend Development

```bash
# Navigate to frontend directory
cd app/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# The frontend will be available at http://localhost:5173
```

### Building Container Images

```bash
# Build backend image
cd app/backend
podman build -t orgmgmt-backend:latest .

# Build frontend image
cd app/frontend
podman build -t orgmgmt-frontend:latest .

# Test images locally
podman run -p 8080:8080 orgmgmt-backend:latest
podman run -p 5006:80 orgmgmt-frontend:latest
```

### Running Tests Locally

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

### Debugging Tips

```bash
# View logs for a specific service
podman logs -f orgmgmt-backend-dev
podman logs -f orgmgmt-frontend-dev

# Access container shell
podman exec -it orgmgmt-backend-dev /bin/bash

# View PostgreSQL logs
podman logs -f orgmgmt-postgres

# Check database connection
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Test API endpoints
curl http://localhost:8080/actuator/health
curl http://localhost:8080/api/organizations
```

## CI/CD Pipeline

### Pipeline Overview

The GitLab CI/CD pipeline consists of 10 stages:

```
1. build-backend     → Compile Java code with Maven
2. test-backend      → Run unit tests and generate coverage
3. build-frontend    → Build React application with Vite
4. test-frontend     → Run frontend tests with Jest
5. package           → Create JAR and tarball artifacts
6. nexus-deploy      → Push artifacts to Nexus Repository
7. container-build   → Build container images from Nexus artifacts
8. gitops-update     → Update GitOps manifests with new tags
9. argocd-sync       → Trigger ArgoCD synchronization
10. e2e-test         → Run Playwright E2E tests
```

### Pipeline Stages Explained

#### Stage 1: Build Backend

```yaml
maven-build:
  stage: build-backend
  image: maven:3.9-eclipse-temurin-17
  script:
    - cd app/backend
    - mvn clean compile
```

Compiles the Spring Boot application and caches Maven dependencies.

#### Stage 2: Test Backend

```yaml
maven-test:
  stage: test-backend
  script:
    - mvn test
  artifacts:
    reports:
      junit: target/surefire-reports/TEST-*.xml
      coverage_report:
        coverage_format: cobertura
```

Runs JUnit tests with JaCoCo code coverage. Requires 80% coverage to pass.

#### Stage 3-4: Build and Test Frontend

Similar to backend, builds and tests the React application.

#### Stage 5: Package

Creates deployable artifacts:
- Backend: JAR file
- Frontend: Tarball of dist folder

#### Stage 6: Nexus Deploy

Pushes artifacts to Nexus Repository Manager:
- Maven artifacts to maven-snapshots
- npm packages to npm-hosted

#### Stage 7: Container Build

Pulls artifacts from Nexus and builds container images:

```bash
# Pull JAR from Nexus
curl -o orgmgmt-backend.jar http://nexus:8081/repository/maven-snapshots/...

# Build container
podman build -t orgmgmt-backend:${VERSION} .

# Push to GitLab Registry
podman push orgmgmt-backend:${VERSION}
```

#### Stage 8: GitOps Update

Updates the GitOps repository with new image tags:

```bash
# Update dev/podman-compose.yml
sed -i "s|image: .*/backend:.*|image: localhost:5005/orgmgmt/backend:${VERSION}|" \
  gitops/dev/podman-compose.yml
```

#### Stage 9: ArgoCD Sync

Triggers ArgoCD to deploy the new version:

```bash
argocd app sync orgmgmt-dev --prune
```

#### Stage 10: E2E Test

Runs Playwright tests against the deployed application.

### GitLab CI Configuration

The pipeline is defined in `.gitlab-ci.yml`:

```yaml
stages:
  - build-backend
  - test-backend
  - build-frontend
  - test-frontend
  - package
  - nexus-deploy
  - container-build
  - gitops-update
  - argocd-sync
  - e2e-test

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"
  NEXUS_URL: "http://nexus:8081"
  REGISTRY_URL: "localhost:5005"
  VERSION: "$CI_COMMIT_SHORT_SHA"
```

### Nexus Integration

Configure Nexus repositories:

```bash
# Maven repository
URL: http://localhost:8081/repository/maven-snapshots/

# npm repository
URL: http://localhost:8081/repository/npm-hosted/
```

### Triggering Pipelines

```bash
# Push to trigger pipeline
git add .
git commit -m "feat: Add new feature"
git push origin main

# View pipeline status
# Visit http://localhost:5003/<project>/pipelines
```

## Deployment

### Multi-Environment Setup

The system supports three environments:

| Environment | Purpose | ArgoCD App | Auto-Sync |
|-------------|---------|------------|-----------|
| **dev** | Development | orgmgmt-dev | Enabled |
| **staging** | Pre-production | orgmgmt-staging | Manual |
| **prod** | Production | orgmgmt-prod | Manual |

### Automated Deployment (GitOps)

ArgoCD automatically deploys changes pushed to the GitOps repository:

```bash
# 1. Update GitOps manifest
vim gitops/dev/podman-compose.yml

# 2. Commit and push
git add gitops/dev/podman-compose.yml
git commit -m "Update dev environment"
git push

# 3. ArgoCD detects changes and syncs automatically
# View in ArgoCD UI: http://localhost:5010
```

### Manual Deployment

```bash
# Deploy to dev environment
./scripts/argocd-deploy.sh dev

# Deploy to staging
./scripts/argocd-deploy.sh staging

# Deploy to production
./scripts/argocd-deploy.sh prod

# Deploy specific version
./scripts/argocd-deploy.sh dev v1.2.3
```

### Deployment Verification

```bash
# Check deployment status
argocd app get orgmgmt-dev

# View sync status
argocd app list

# Check application health
curl http://localhost:8080/actuator/health
curl http://localhost:5006
```

### Rollback Procedures

#### Automatic Rollback (ArgoCD)

ArgoCD can automatically rollback failed deployments:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

#### Manual Rollback

```bash
# List deployment history
argocd app history orgmgmt-dev

# Rollback to previous version
./scripts/argocd-rollback.sh dev

# Rollback to specific version
argocd app rollback orgmgmt-dev <revision-id>
```

#### Emergency Rollback

```bash
# Quick rollback by reverting GitOps changes
cd gitops/dev
git revert HEAD
git push

# ArgoCD will automatically sync the rollback
```

### Blue-Green Deployment

For zero-downtime deployments:

```bash
# 1. Deploy new version to staging
./scripts/argocd-deploy.sh staging v2.0.0

# 2. Run smoke tests
./scripts/run-e2e-tests.sh staging

# 3. Switch production traffic
./scripts/argocd-deploy.sh prod v2.0.0

# 4. Monitor for issues
./scripts/status.sh

# 5. Rollback if needed
./scripts/argocd-rollback.sh prod
```

## Testing

### Unit Tests

#### Backend Tests

```bash
# Run all backend tests
cd app/backend
mvn test

# Run specific test class
mvn test -Dtest=OrganizationServiceTest

# Run with coverage
mvn clean test jacoco:report

# View coverage report
open target/site/jacoco/index.html
```

Test coverage requirements:
- Minimum line coverage: 80%
- JaCoCo enforces coverage in build

#### Frontend Tests

```bash
# Run all frontend tests
cd app/frontend
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Update snapshots
npm test -- -u
```

### Integration Tests

```bash
# Run integration tests
./scripts/test.sh --integration

# Test database migrations
cd app/backend
mvn flyway:migrate
mvn flyway:validate
```

### E2E Tests with Playwright

```bash
# Run all E2E tests
./scripts/run-e2e-tests.sh

# Run specific test suite
cd playwright-tests
npx playwright test tests/organizations/

# Run in headed mode (with browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug

# Generate HTML report
npx playwright show-report
```

E2E test scenarios:
- Organization CRUD operations
- Department management
- User management
- Form validation
- Error handling
- Navigation flows

### Coverage Reports

#### Backend Coverage

```bash
# Generate coverage report
cd app/backend
mvn clean test jacoco:report

# Coverage report location
open target/site/jacoco/index.html
```

#### Frontend Coverage

```bash
# Generate coverage report
cd app/frontend
npm test -- --coverage

# Coverage report location
open coverage/lcov-report/index.html
```

#### CI/CD Coverage

Coverage reports are automatically generated in CI/CD:
- Available in GitLab merge request widgets
- Published as artifacts
- Enforced coverage thresholds

### Performance Testing

```bash
# API performance test
ab -n 1000 -c 10 http://localhost:8080/api/organizations

# Load testing with curl
for i in {1..100}; do
  curl -X POST http://localhost:8080/api/organizations \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Org","code":"TEST001"}' &
done
```

## Monitoring and Observability

### Service Health Checks

```bash
# Check all services
./scripts/status.sh

# Check specific service
podman ps | grep orgmgmt-backend
podman healthcheck run orgmgmt-backend-dev

# Backend health endpoint
curl http://localhost:8080/actuator/health

# Frontend health
curl http://localhost:5006

# Database health
podman exec orgmgmt-postgres pg_isready
```

### Viewing Logs

```bash
# View all logs
./scripts/logs.sh

# View specific service logs
./scripts/logs.sh backend
./scripts/logs.sh frontend
./scripts/logs.sh postgres
./scripts/logs.sh argocd

# Follow logs in real-time
podman logs -f orgmgmt-backend-dev

# View last 100 lines
podman logs --tail 100 orgmgmt-backend-dev

# Export logs to file
podman logs orgmgmt-backend-dev > backend.log
```

### ArgoCD Dashboard

Access the ArgoCD dashboard to monitor deployments:

```bash
# Open ArgoCD UI
open http://localhost:5010

# Login with credentials from credentials.txt
Username: admin
Password: <from credentials.txt>
```

ArgoCD Dashboard features:
- Application sync status
- Resource health
- Sync history
- Manual sync/rollback
- Resource diff viewer
- Application logs

### Spring Boot Actuator

Backend monitoring endpoints:

```bash
# Health check
curl http://localhost:8080/actuator/health

# Application info
curl http://localhost:8080/actuator/info

# Metrics
curl http://localhost:8080/actuator/metrics

# Environment properties
curl http://localhost:8080/actuator/env

# HTTP traces
curl http://localhost:8080/actuator/httptrace
```

### Database Monitoring

```bash
# Connect to PostgreSQL
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# View active connections
SELECT * FROM pg_stat_activity;

# View database size
SELECT pg_size_pretty(pg_database_size('orgmgmt'));

# View table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Performance Metrics

```bash
# Container resource usage
podman stats

# Specific container stats
podman stats orgmgmt-backend-dev

# System resource usage
top
htop
free -h
df -h
```

## Backup and Recovery

### Automated Backup

```bash
# Run backup
./scripts/backup.sh

# Backups are stored in: backups/<timestamp>/
# Includes:
#   - PostgreSQL database dump
#   - Application configuration
#   - GitOps manifests
#   - Nexus data (optional)
```

### Manual Backup

#### Database Backup

```bash
# Backup PostgreSQL database
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt > orgmgmt_backup.sql

# Backup with compression
podman exec orgmgmt-postgres pg_dump -U orgmgmt_user orgmgmt | gzip > orgmgmt_backup.sql.gz

# Backup all databases
podman exec orgmgmt-postgres pg_dumpall -U orgmgmt_user > all_databases_backup.sql
```

#### Volume Backup

```bash
# Backup PostgreSQL data volume
podman volume export orgmgmt-postgres-data -o postgres-data-backup.tar

# Backup Nexus data
podman volume export orgmgmt-nexus-data -o nexus-data-backup.tar

# Backup GitLab data
podman volume export orgmgmt-gitlab-data -o gitlab-data-backup.tar
```

#### Configuration Backup

```bash
# Backup environment configuration
cp infrastructure/.env infrastructure/.env.backup

# Backup GitOps manifests
tar -czf gitops-backup.tar.gz gitops/

# Backup ArgoCD configuration
tar -czf argocd-backup.tar.gz argocd/
```

### Restore Procedures

#### Database Restore

```bash
# Restore from backup script
./scripts/restore.sh <backup-directory>

# Manual database restore
cat orgmgmt_backup.sql | podman exec -i orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Restore compressed backup
gunzip < orgmgmt_backup.sql.gz | podman exec -i orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt
```

#### Volume Restore

```bash
# Stop services
cd infrastructure
podman-compose down

# Restore PostgreSQL volume
podman volume rm orgmgmt-postgres-data
podman volume create orgmgmt-postgres-data
podman volume import orgmgmt-postgres-data postgres-data-backup.tar

# Restart services
podman-compose up -d
```

### Disaster Recovery Plan

#### Scenario 1: Database Corruption

```bash
# 1. Stop application
podman stop orgmgmt-backend-dev

# 2. Restore database from latest backup
./scripts/restore.sh backups/<latest-timestamp>/

# 3. Verify database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "SELECT COUNT(*) FROM organizations;"

# 4. Restart application
podman start orgmgmt-backend-dev
```

#### Scenario 2: Complete System Failure

```bash
# 1. Fresh system setup
./scripts/setup.sh

# 2. Restore volumes and data
./scripts/restore.sh backups/<latest-timestamp>/

# 3. Verify all services
./scripts/status.sh

# 4. Run smoke tests
./scripts/test.sh --smoke
```

#### Scenario 3: GitOps Repository Corruption

```bash
# 1. Clone clean repository
git clone <backup-repo-url> gitops-restore

# 2. Copy latest manifests
cp -r gitops-restore/* gitops/

# 3. Commit and push
cd gitops
git add .
git commit -m "Restore from backup"
git push

# 4. Sync ArgoCD
argocd app sync orgmgmt-dev --force
```

### Backup Best Practices

1. **Regular Backups**: Schedule daily backups using cron
2. **Test Restores**: Regularly test restore procedures
3. **Off-site Storage**: Store backups in separate location
4. **Retention Policy**: Keep backups for 30 days minimum
5. **Documentation**: Document restore procedures
6. **Monitoring**: Monitor backup job success/failure

## Security

### Authentication and Authorization

#### Service Authentication

| Service | Authentication | Default Credentials |
|---------|----------------|---------------------|
| PostgreSQL | Password | orgmgmt_user / (see credentials.txt) |
| pgAdmin | Email/Password | admin@orgmgmt.local / (see credentials.txt) |
| Nexus | Username/Password | admin / (see credentials.txt) |
| GitLab | Username/Password | root / (see credentials.txt) |
| ArgoCD | Username/Password | admin / (see credentials.txt) |

#### Changing Default Passwords

```bash
# PostgreSQL
podman exec -it orgmgmt-postgres psql -U postgres
ALTER USER orgmgmt_user WITH PASSWORD 'new_secure_password';

# ArgoCD
argocd account update-password --account admin

# GitLab
# Login to http://localhost:5003 and change via UI

# Nexus
# Login to http://localhost:8081 and change via UI
```

### Secrets Management

#### Environment Variables

```bash
# Store secrets in .env file
echo "DB_PASSWORD=secure_password" >> infrastructure/.env

# Never commit .env to Git
echo ".env" >> .gitignore
```

#### GitLab CI/CD Variables

```bash
# Set protected variables in GitLab
# Settings > CI/CD > Variables

# Mark as:
# - Protected (only available on protected branches)
# - Masked (hidden in logs)
```

### Network Security

#### Container Network Isolation

```yaml
networks:
  argocd-network:
    driver: bridge
    name: argocd-network
```

All services run in isolated bridge network.

#### Firewall Configuration

```bash
# Allow only necessary ports
sudo firewall-cmd --add-port=5006/tcp --permanent  # Frontend
sudo firewall-cmd --add-port=8080/tcp --permanent  # Backend API
sudo firewall-cmd --add-port=5010/tcp --permanent  # ArgoCD (optional)
sudo firewall-cmd --reload

# Block direct database access from external
sudo firewall-cmd --remove-port=5432/tcp --permanent
```

### Container Security

#### Image Security Scanning

```bash
# Scan images for vulnerabilities
podman scan orgmgmt-backend:latest
podman scan orgmgmt-frontend:latest

# Use trusted base images
FROM eclipse-temurin:17-jre-alpine
FROM nginx:alpine
```

#### Running as Non-Root

```dockerfile
# Backend Dockerfile
FROM eclipse-temurin:17-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring
```

#### Resource Limits

```yaml
services:
  orgmgmt-backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Production Hardening

#### 1. Disable Debug Mode

```yaml
# application.yml
spring:
  jpa:
    show-sql: false
logging:
  level:
    root: INFO
```

#### 2. Enable HTTPS

```yaml
server:
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: ${SSL_KEY_STORE_PASSWORD}
    key-store-type: PKCS12
```

#### 3. CORS Configuration

```java
@CrossOrigin(origins = "${allowed.origins}")
```

#### 4. SQL Injection Prevention

Using JPA/Hibernate with parameterized queries automatically prevents SQL injection.

#### 5. Rate Limiting

```yaml
# Add rate limiting for production
spring:
  cloud:
    gateway:
      routes:
        - id: api
          predicates:
            - Path=/api/**
          filters:
            - name: RequestRateLimiter
```

#### 6. Security Headers

```yaml
# Add security headers
server:
  servlet:
    context-path: /
  forward-headers-strategy: framework
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS for production
- [ ] Configure firewall rules
- [ ] Set up regular backups
- [ ] Enable audit logging
- [ ] Scan container images for vulnerabilities
- [ ] Implement rate limiting
- [ ] Configure CORS properly
- [ ] Use secrets management
- [ ] Enable network isolation
- [ ] Set resource limits
- [ ] Disable unnecessary services
- [ ] Keep software updated
- [ ] Monitor security logs
- [ ] Implement intrusion detection

## Troubleshooting

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Common Issues

#### Services Not Starting

```bash
# Check if ports are in use
sudo ss -tulpn | grep -E '5432|8080|5006'

# Check for existing containers
podman ps -a

# View service logs
podman logs orgmgmt-postgres
```

#### Database Connection Failed

```bash
# Verify PostgreSQL is running
podman exec orgmgmt-postgres pg_isready

# Check connection
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt

# Verify credentials in .env
cat infrastructure/.env | grep POSTGRES
```

#### Build Failures

```bash
# Clear Maven cache
rm -rf ~/.m2/repository

# Clear npm cache
npm cache clean --force

# Rebuild from scratch
mvn clean install -U
npm ci
```

#### ArgoCD Sync Failures

```bash
# Check ArgoCD application status
argocd app get orgmgmt-dev

# View sync history
argocd app history orgmgmt-dev

# Manual sync
argocd app sync orgmgmt-dev --prune --force
```

### Debug Commands

```bash
# View system resources
podman stats

# Check disk space
df -h

# View system logs
journalctl -u podman -f

# Network troubleshooting
podman network inspect argocd-network

# Container inspection
podman inspect orgmgmt-backend-dev
```

### Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions
2. Review logs with `./scripts/logs.sh`
3. Check service status with `./scripts/status.sh`
4. Search issues on GitHub
5. Contact support team

## API Reference

For complete API documentation, see [API.md](API.md).

### Base URL

```
http://localhost:8080
```

### Authentication

Currently, no authentication is required. In production, implement JWT or OAuth2.

### Organization Endpoints

#### Create Organization

```bash
POST /api/organizations
Content-Type: application/json

{
  "name": "Acme Corporation",
  "code": "ACME001",
  "description": "Leading tech company",
  "active": true
}
```

#### Get All Organizations

```bash
GET /api/organizations?page=0&size=20&sort=name,asc
```

#### Get Organization by ID

```bash
GET /api/organizations/{id}
```

#### Update Organization

```bash
PUT /api/organizations/{id}
Content-Type: application/json

{
  "name": "Updated Name",
  "code": "ACME001",
  "description": "Updated description",
  "active": true
}
```

#### Delete Organization

```bash
DELETE /api/organizations/{id}
```

#### Search Organizations

```bash
GET /api/organizations/search?q=Acme
```

### Department Endpoints

```bash
POST   /api/departments
GET    /api/departments
GET    /api/departments/{id}
PUT    /api/departments/{id}
DELETE /api/departments/{id}
GET    /api/departments/organization/{orgId}
```

### User Endpoints

```bash
POST   /api/users
GET    /api/users
GET    /api/users/{id}
PUT    /api/users/{id}
DELETE /api/users/{id}
GET    /api/users/department/{deptId}
```

### Health Check

```bash
GET /actuator/health
```

Response:
```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP"
    },
    "diskSpace": {
      "status": "UP"
    }
  }
}
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Run test suite
6. Submit pull request

### Code Style

- **Java**: Follow Google Java Style Guide
- **JavaScript**: Use ESLint configuration
- **Commits**: Use Conventional Commits format

### Testing Requirements

- Unit tests for all new features
- Integration tests for API endpoints
- E2E tests for critical user flows
- Minimum 80% code coverage

### Pull Request Process

1. Update documentation
2. Add tests
3. Ensure CI/CD passes
4. Request code review
5. Address feedback
6. Merge after approval

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Spring Boot team for excellent framework
- React team for amazing frontend library
- ArgoCD project for GitOps excellence
- Podman community for container innovation

## Support

For questions or issues:
- Open an issue on GitHub
- Contact the development team
- Check documentation
- Review troubleshooting guide

---

Built with ❤️ by the DevOps Team
