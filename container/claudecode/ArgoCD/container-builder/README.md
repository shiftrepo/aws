# Container Build Pipeline

This directory contains the container build pipeline for the OrgMgmt application. It provides a complete workflow for building, pushing, and deploying containerized applications using artifacts from Nexus repository.

## Overview

The container build pipeline consists of:

- **Multi-stage Dockerfiles** for backend (Java) and frontend (NPM)
- **Build automation scripts** for streamlined operations
- **GitOps integration** for automated deployments
- **Nginx configuration** for frontend reverse proxy

## Architecture

```
┌─────────────────┐
│ Nexus Repository│
│   - Maven       │
│   - NPM         │
└────────┬────────┘
         │
         │ Download artifacts
         ▼
┌─────────────────┐
│  Build Process  │
│  - Backend JAR  │
│  - Frontend TGZ │
└────────┬────────┘
         │
         │ Build images
         ▼
┌─────────────────┐
│ Container Images│
│  - Backend      │
│  - Frontend     │
└────────┬────────┘
         │
         │ Push
         ▼
┌─────────────────┐
│ Container       │
│ Registry        │
└────────┬────────┘
         │
         │ Deploy
         ▼
┌─────────────────┐
│ Kubernetes /    │
│ Podman Compose  │
└─────────────────┘
```

## Directory Structure

```
container-builder/
├── Dockerfile.backend          # Multi-stage Dockerfile for Java backend
├── Dockerfile.frontend         # Multi-stage Dockerfile for frontend
├── nginx.conf                  # Nginx configuration for frontend
├── .dockerignore              # Files to exclude from build context
├── README.md                  # This file
└── scripts/
    ├── build-from-nexus.sh    # Build images from Nexus artifacts
    ├── push-to-registry.sh    # Push images to container registry
    └── update-gitops.sh       # Update GitOps configurations
```

## Components

### 1. Dockerfile.backend

Multi-stage Dockerfile for building the Java backend service:

**Stage 1: Downloader**
- Base: `curlimages/curl`
- Downloads JAR artifact from Nexus Maven repository
- Handles SNAPSHOT version resolution
- Validates downloaded artifact

**Stage 2: Runtime**
- Base: `eclipse-temurin:17-jre-alpine`
- Minimal JRE for reduced image size
- Non-root user (uid 1000) for security
- Optimized JVM settings for containers
- Health check using Spring Boot Actuator
- OCI labels for metadata

**Build Arguments:**
- `NEXUS_URL`: Nexus repository URL (default: http://localhost:8081)
- `GROUP_ID`: Maven group ID (default: com.example)
- `ARTIFACT_ID`: Maven artifact ID (default: orgmgmt-backend)
- `VERSION`: Artifact version (default: 1.0.0-SNAPSHOT)
- `REPOSITORY`: Maven repository name (default: maven-snapshots)

### 2. Dockerfile.frontend

Multi-stage Dockerfile for building the frontend application:

**Stage 1: Downloader**
- Base: `curlimages/curl`
- Downloads NPM package tarball from Nexus
- Extracts distribution files

**Stage 2: Runtime**
- Base: `nginx:1.25-alpine`
- Serves static files
- Includes custom nginx configuration
- Health check for availability
- OCI labels for metadata

**Build Arguments:**
- `NEXUS_URL`: Nexus repository URL (default: http://localhost:8081)
- `PACKAGE_NAME`: NPM package name (default: @orgmgmt/frontend)
- `VERSION`: Package version (default: 1.0.0)
- `REPOSITORY`: NPM repository name (default: npm-hosted)

### 3. nginx.conf

Production-ready Nginx configuration:

- **SPA Routing**: Fallback to index.html for client-side routing
- **API Proxy**: Forwards `/api/*` requests to backend service
- **Compression**: Gzip enabled for better performance
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **Caching Strategy**:
  - HTML: no-cache
  - CSS/JS: 1 year (immutable)
  - Images/Fonts: 1 year
- **Health Check**: `/health` endpoint
- **WebSocket Support**: For real-time features

### 4. Scripts

#### build-from-nexus.sh

Builds container images from Nexus artifacts.

**Features:**
- Automatic version detection (git SHA or environment variable)
- Validates prerequisites (podman, Dockerfiles)
- Builds both backend and frontend images
- Tags with version and latest
- Adds build metadata labels
- Comprehensive logging with colors

**Usage:**
```bash
# Build with default settings
./scripts/build-from-nexus.sh

# Build with specific version
VERSION=1.2.3 ./scripts/build-from-nexus.sh

# Build with custom Nexus URL
NEXUS_URL=http://nexus.example.com:8081 ./scripts/build-from-nexus.sh

# Build with all custom parameters
VERSION=1.2.3 \
NEXUS_URL=http://nexus.example.com:8081 \
REGISTRY_URL=registry.example.com \
GROUP_ID=com.mycompany \
ARTIFACT_ID=my-backend \
./scripts/build-from-nexus.sh
```

**Environment Variables:**
- `VERSION`: Artifact version (auto-detected from git or defaults to 1.0.0-SNAPSHOT)
- `NEXUS_URL`: Nexus repository URL (default: http://localhost:8081)
- `REGISTRY_URL`: Container registry URL (default: localhost:5005)
- `GROUP_ID`: Maven group ID (default: com.example)
- `ARTIFACT_ID`: Maven artifact ID (default: orgmgmt-backend)
- `PACKAGE_NAME`: NPM package name (default: @orgmgmt/frontend)

#### push-to-registry.sh

Pushes container images to a container registry.

**Features:**
- Registry authentication with podman login
- Supports cached credentials
- Validates images exist locally
- Pushes both version and latest tags
- Optional automatic push
- Comprehensive error handling

**Usage:**
```bash
# Push with default settings
./scripts/push-to-registry.sh

# Push with authentication
REGISTRY_USER=myuser REGISTRY_PASS=mypass ./scripts/push-to-registry.sh

# Push to custom registry
REGISTRY_URL=registry.example.com VERSION=1.2.3 ./scripts/push-to-registry.sh

# Skip login (use cached credentials)
SKIP_LOGIN=true ./scripts/push-to-registry.sh
```

**Environment Variables:**
- `VERSION`: Image version tag (required if not in git repo)
- `REGISTRY_URL`: Container registry URL (default: localhost:5005)
- `REGISTRY_USER`: Registry username (optional)
- `REGISTRY_PASS`: Registry password (optional)
- `SKIP_LOGIN`: Skip registry login (default: false)

#### update-gitops.sh

Updates GitOps configurations with new image tags.

**Features:**
- Auto-detects GitOps directory
- Updates podman-compose.yml
- Updates kustomization.yaml
- Updates Kubernetes manifests
- Automatic git commit (optional)
- Automatic git push (optional)
- Backup before changes

**Usage:**
```bash
# Update with default settings
./scripts/update-gitops.sh

# Update specific environment
ENVIRONMENT=staging VERSION=1.2.3 ./scripts/update-gitops.sh

# Update and commit to git
GIT_COMMIT=true ./scripts/update-gitops.sh

# Update, commit, and push to git
GIT_COMMIT=true GIT_PUSH=true ./scripts/update-gitops.sh

# Update custom GitOps directory
GITOPS_DIR=/path/to/gitops ./scripts/update-gitops.sh
```

**Environment Variables:**
- `VERSION`: Image version tag (required if not in git repo)
- `REGISTRY_URL`: Container registry URL (default: localhost:5005)
- `GITOPS_DIR`: GitOps directory path (default: auto-detect)
- `ENVIRONMENT`: Target environment (default: dev)
- `GIT_COMMIT`: Commit changes to git (default: true)
- `GIT_PUSH`: Push changes to remote (default: false)

## Quick Start

### Prerequisites

1. **Podman** (or Docker) installed
2. **Nexus Repository** with artifacts
3. **Container Registry** (local or remote)
4. **Git** (for GitOps integration)

### Basic Workflow

```bash
# 1. Clone the repository
cd /root/aws.git/container/claudecode/ArgoCD/container-builder

# 2. Build images from Nexus
VERSION=1.0.0 NEXUS_URL=http://nexus.example.com:8081 ./scripts/build-from-nexus.sh

# 3. Test images locally
podman run -p 8080:8080 localhost:5005/orgmgmt/backend:1.0.0
podman run -p 80:80 localhost:5005/orgmgmt/frontend:1.0.0

# 4. Push to registry
VERSION=1.0.0 REGISTRY_URL=registry.example.com ./scripts/push-to-registry.sh

# 5. Update GitOps configurations
VERSION=1.0.0 ENVIRONMENT=dev ./scripts/update-gitops.sh
```

### Complete CI/CD Pipeline

```bash
#!/bin/bash
# Complete pipeline script

set -e

# Configuration
export VERSION=$(git rev-parse --short HEAD)
export NEXUS_URL=http://nexus.example.com:8081
export REGISTRY_URL=registry.example.com
export ENVIRONMENT=dev

# Build
./scripts/build-from-nexus.sh

# Test (optional)
# Add your test commands here

# Push
./scripts/push-to-registry.sh

# Update GitOps
GIT_COMMIT=true GIT_PUSH=true ./scripts/update-gitops.sh

echo "Pipeline completed successfully!"
```

## Advanced Usage

### Custom Maven Coordinates

```bash
VERSION=2.0.0 \
GROUP_ID=com.mycompany \
ARTIFACT_ID=my-backend \
./scripts/build-from-nexus.sh
```

### Private Registry with Authentication

```bash
# Using environment variables
export REGISTRY_USER=myuser
export REGISTRY_PASS=mypassword
export REGISTRY_URL=registry.example.com

./scripts/push-to-registry.sh

# Or inline
REGISTRY_USER=myuser REGISTRY_PASS=mypassword ./scripts/push-to-registry.sh
```

### Multi-Environment Deployment

```bash
# Build once
VERSION=1.0.0 ./scripts/build-from-nexus.sh
VERSION=1.0.0 ./scripts/push-to-registry.sh

# Deploy to multiple environments
for env in dev staging prod; do
    ENVIRONMENT=$env VERSION=1.0.0 ./scripts/update-gitops.sh
done
```

### Manual Docker Build (without scripts)

```bash
# Backend
podman build \
  -f Dockerfile.backend \
  -t localhost:5005/orgmgmt/backend:1.0.0 \
  --build-arg VERSION=1.0.0 \
  --build-arg NEXUS_URL=http://localhost:8081 \
  .

# Frontend
podman build \
  -f Dockerfile.frontend \
  -t localhost:5005/orgmgmt/frontend:1.0.0 \
  --build-arg VERSION=1.0.0 \
  --build-arg NEXUS_URL=http://localhost:8081 \
  .
```

## Image Details

### Backend Image

**Base Image:** eclipse-temurin:17-jre-alpine
**Exposed Ports:** 8080
**User:** appuser (uid: 1000)
**Health Check:** http://localhost:8080/actuator/health
**Size:** ~200 MB (approximate)

**Environment Variables:**
- `JAVA_OPTS`: JVM options (default: container-optimized settings)

**Labels:**
- `org.opencontainers.image.title`
- `org.opencontainers.image.version`
- `org.opencontainers.image.source`
- `build.timestamp`

### Frontend Image

**Base Image:** nginx:1.25-alpine
**Exposed Ports:** 80
**Health Check:** http://localhost/
**Size:** ~50 MB (approximate)

**Nginx Features:**
- Gzip compression
- SPA routing support
- API proxy to backend
- Security headers
- Caching strategy

## Troubleshooting

### Build Failures

**Issue:** Cannot download artifact from Nexus

```bash
# Check Nexus connectivity
curl -f http://localhost:8081/repository/maven-snapshots/

# Verify artifact exists
curl -I http://localhost:8081/repository/maven-snapshots/com/example/orgmgmt-backend/1.0.0-SNAPSHOT/
```

**Issue:** Image build fails

```bash
# Check Dockerfile syntax
podman build --no-cache -f Dockerfile.backend .

# Enable debug logging
podman build --log-level=debug -f Dockerfile.backend .
```

### Push Failures

**Issue:** Authentication failure

```bash
# Login manually
podman login localhost:5005

# Check credentials
cat ~/.config/containers/auth.json

# Test push
podman push localhost:5005/orgmgmt/backend:test
```

**Issue:** Image not found

```bash
# List local images
podman images | grep orgmgmt

# Rebuild if missing
./scripts/build-from-nexus.sh
```

### Runtime Issues

**Issue:** Backend health check failing

```bash
# Check container logs
podman logs <container-id>

# Test health endpoint manually
podman exec <container-id> curl http://localhost:8080/actuator/health

# Check Java process
podman exec <container-id> ps aux
```

**Issue:** Frontend cannot connect to backend

```bash
# Check nginx configuration
podman exec <container-id> nginx -t

# Check proxy settings
podman exec <container-id> cat /etc/nginx/conf.d/default.conf

# Test backend connectivity
podman exec <container-id> wget -O- http://orgmgmt-backend:8080/actuator/health
```

## Best Practices

### Security

1. **Non-root Users**: All images run as non-root users
2. **Minimal Base Images**: Alpine-based images for smaller attack surface
3. **Secret Management**: Never hardcode credentials in Dockerfiles
4. **Image Scanning**: Regularly scan images for vulnerabilities

```bash
# Scan images with trivy
trivy image localhost:5005/orgmgmt/backend:latest
```

### Performance

1. **Multi-stage Builds**: Minimize final image size
2. **Layer Caching**: Order Dockerfile commands for optimal caching
3. **Build Arguments**: Use build args for flexibility
4. **Health Checks**: Always include health checks

### CI/CD Integration

1. **Version Tags**: Use semantic versioning or git SHAs
2. **Automated Testing**: Test images before pushing
3. **GitOps**: Automate deployment updates
4. **Rollback Strategy**: Keep previous versions tagged

## Integration Examples

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        VERSION = "${GIT_COMMIT.take(7)}"
        NEXUS_URL = "http://nexus.example.com:8081"
        REGISTRY_URL = "registry.example.com"
    }

    stages {
        stage('Build') {
            steps {
                sh './scripts/build-from-nexus.sh'
            }
        }

        stage('Test') {
            steps {
                sh 'podman run --rm localhost:5005/orgmgmt/backend:${VERSION} java -version'
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'registry-creds',
                                                   usernameVariable: 'REGISTRY_USER',
                                                   passwordVariable: 'REGISTRY_PASS')]) {
                    sh './scripts/push-to-registry.sh'
                }
            }
        }

        stage('Update GitOps') {
            steps {
                sh 'GIT_COMMIT=true GIT_PUSH=true ./scripts/update-gitops.sh'
            }
        }
    }
}
```

### GitLab CI

```yaml
variables:
  VERSION: $CI_COMMIT_SHORT_SHA
  NEXUS_URL: http://nexus.example.com:8081
  REGISTRY_URL: registry.example.com

build:
  stage: build
  script:
    - ./scripts/build-from-nexus.sh
  artifacts:
    reports:
      dotenv: build.env

push:
  stage: push
  script:
    - echo $REGISTRY_PASS | podman login -u $REGISTRY_USER --password-stdin $REGISTRY_URL
    - ./scripts/push-to-registry.sh
  only:
    - main

deploy:
  stage: deploy
  script:
    - GIT_COMMIT=true GIT_PUSH=true ./scripts/update-gitops.sh
  only:
    - main
```

### GitHub Actions

```yaml
name: Container Build Pipeline

on:
  push:
    branches: [main]

env:
  VERSION: ${{ github.sha }}
  NEXUS_URL: http://nexus.example.com:8081
  REGISTRY_URL: registry.example.com

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build images
        run: ./scripts/build-from-nexus.sh

      - name: Login to registry
        run: |
          echo ${{ secrets.REGISTRY_PASS }} | podman login -u ${{ secrets.REGISTRY_USER }} --password-stdin $REGISTRY_URL

      - name: Push images
        run: ./scripts/push-to-registry.sh

      - name: Update GitOps
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          GIT_COMMIT=true GIT_PUSH=true ./scripts/update-gitops.sh
```

## Maintenance

### Cleanup Old Images

```bash
# Remove unused images
podman image prune -a

# Remove specific versions
podman rmi localhost:5005/orgmgmt/backend:old-version

# Clean build cache
podman builder prune
```

### Update Base Images

```bash
# Pull latest base images
podman pull eclipse-temurin:17-jre-alpine
podman pull nginx:1.25-alpine
podman pull curlimages/curl:latest

# Rebuild with --no-cache
VERSION=1.0.0 podman build --no-cache -f Dockerfile.backend .
```

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review container logs: `podman logs <container-id>`
3. Check build logs: `podman build --log-level=debug`
4. Open an issue in the repository

## License

Apache License 2.0

## References

- [Podman Documentation](https://docs.podman.io/)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
- [Spring Boot Actuator](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html)
