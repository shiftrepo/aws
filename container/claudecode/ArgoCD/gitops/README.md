# GitOps Deployment Manifests

This directory contains GitOps-ready deployment manifests for the Organization Management application across multiple environments.

## Directory Structure

```
gitops/
├── dev/                          # Development environment
│   ├── podman-compose.yml        # Dev compose configuration
│   └── .env                      # Dev environment variables
├── staging/                      # Staging environment
│   ├── podman-compose.yml        # Staging compose configuration
│   └── .env                      # Staging environment variables
├── prod/                         # Production environment
│   ├── podman-compose.yml        # Prod compose configuration
│   └── .env                      # Prod environment variables
├── scripts/                      # Automation scripts
│   ├── update-image-tag.sh       # Update image tags script
│   └── validate-manifest.sh      # Manifest validation script
└── README.md                     # This file
```

## Environment Differences

### Development (dev)
- **Purpose**: Local development and testing
- **Image Tags**: `latest`
- **Ports**: Backend 8080, Frontend 5006
- **Profile**: `SPRING_PROFILES_ACTIVE=dev`
- **Logging**: `DEBUG` level
- **Replicas**: 1
- **Resources**: No limits (for flexibility)
- **Features**:
  - Hot-reload support
  - Verbose logging
  - Direct port exposure
  - Minimal health check intervals

### Staging (staging)
- **Purpose**: Pre-production testing and QA
- **Image Tags**: `staging`
- **Ports**: Backend 8081, Frontend 5007
- **Profile**: `SPRING_PROFILES_ACTIVE=staging`
- **Logging**: `INFO` level
- **Replicas**: 2
- **Resources**:
  - Backend: 2 CPU / 2GB RAM limit
  - Frontend: 1 CPU / 512MB RAM limit
- **Features**:
  - Production-like configuration
  - Moderate resource limits
  - Standard health checks
  - Separate port mapping

### Production (prod)
- **Purpose**: Live production workload
- **Image Tags**: Specific versions (e.g., `v1.0.0`)
- **Ports**: Backend 8082, Frontend 5008
- **Profile**: `SPRING_PROFILES_ACTIVE=prod`
- **Logging**: `WARN` level
- **Replicas**: 3
- **Resources**:
  - Backend: 4 CPU / 4GB RAM limit
  - Frontend: 2 CPU / 1GB RAM limit
- **Features**:
  - Strict resource limits
  - Minimal logging
  - Aggressive health checks
  - Version-pinned images (no `latest`)

## Services Configuration

### Backend Service (orgmgmt-backend)
- **Image**: `localhost:5005/orgmgmt/backend:<tag>`
- **Port**: 8080 (internal)
- **Database**: PostgreSQL (from external argocd-network)
- **Health Check**: `/actuator/health` endpoint
- **Dependencies**: PostgreSQL database

### Frontend Service (orgmgmt-frontend)
- **Image**: `localhost:5005/orgmgmt/frontend:<tag>`
- **Port**: 80 (internal)
- **API Connection**: Backend service via internal network
- **Health Check**: HTTP GET to root path
- **Dependencies**: Backend service

## Network Configuration

All services use the **external network** `argocd-network` which must be created separately by the infrastructure compose file. This network enables:
- Communication between application services
- Access to shared infrastructure (PostgreSQL, ArgoCD)
- Isolation from other applications

## Updating Image Tags

### Using the Update Script (Recommended)

```bash
# Update dev environment to latest
./scripts/update-image-tag.sh dev latest

# Update staging environment
./scripts/update-image-tag.sh staging staging

# Update production to specific version
./scripts/update-image-tag.sh prod v1.2.3
```

The script will:
1. Validate the environment and version
2. Create a backup of the current manifest
3. Update image tags for both services
4. Validate the updated manifest
5. Provide git commands for committing changes

### Manual Update

Edit the `podman-compose.yml` file directly:

```yaml
services:
  orgmgmt-backend:
    image: localhost:5005/orgmgmt/backend:v1.2.3  # Update this line

  orgmgmt-frontend:
    image: localhost:5005/orgmgmt/frontend:v1.2.3  # Update this line
```

## Validating Manifests

Validate a manifest before deployment:

```bash
# Validate dev environment
./scripts/validate-manifest.sh dev

# Validate staging environment
./scripts/validate-manifest.sh staging

# Validate production environment
./scripts/validate-manifest.sh prod
```

The validation checks:
- YAML syntax correctness
- Image tags are not empty
- Required environment variables exist
- Network configuration is proper
- Service dependencies are defined
- Health checks are configured
- Restart policies are set

## Manual Deployment

### Deploy a Specific Environment

```bash
# Deploy development environment
cd /root/aws.git/container/claudecode/ArgoCD/gitops/dev
podman-compose --env-file .env up -d

# Deploy staging environment
cd /root/aws.git/container/claudecode/ArgoCD/gitops/staging
podman-compose --env-file .env up -d

# Deploy production environment
cd /root/aws.git/container/claudecode/ArgoCD/gitops/prod
podman-compose --env-file .env up -d
```

### Stop Services

```bash
# Stop specific environment
cd /root/aws.git/container/claudecode/ArgoCD/gitops/<env>
podman-compose down

# Stop and remove volumes (CAREFUL!)
podman-compose down -v
```

### View Logs

```bash
# View logs for all services
podman-compose logs -f

# View logs for specific service
podman-compose logs -f orgmgmt-backend
podman-compose logs -f orgmgmt-frontend
```

## ArgoCD Integration

### GitOps Workflow

1. **Developer pushes code changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git push
   ```

2. **CI/CD pipeline builds and pushes images**
   - Builds Docker/Podman images
   - Tags with version (e.g., `v1.2.3`)
   - Pushes to registry `localhost:5005`

3. **Update manifest with new image tag**
   ```bash
   ./scripts/update-image-tag.sh prod v1.2.3
   git add gitops/prod/podman-compose.yml
   git commit -m "chore: Update prod images to v1.2.3"
   git push
   ```

4. **ArgoCD detects changes**
   - Monitors git repository
   - Compares desired state (git) vs actual state (cluster)
   - Auto-syncs or waits for manual approval

5. **ArgoCD deploys changes**
   - Pulls new manifests from git
   - Applies changes using podman-compose
   - Validates deployment health

### ArgoCD Application Configuration

Create ArgoCD applications for each environment:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: orgmgmt-dev
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo
    targetRevision: main
    path: gitops/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Sync Strategies

#### Development (Auto-sync)
- **Automated**: Yes
- **Prune**: Yes (remove deleted resources)
- **Self-heal**: Yes (auto-fix drift)
- **Reason**: Fast iteration, immediate feedback

#### Staging (Auto-sync with caution)
- **Automated**: Yes
- **Prune**: Yes
- **Self-heal**: Yes
- **Reason**: Quick QA validation

#### Production (Manual sync)
- **Automated**: No
- **Prune**: Manual
- **Self-heal**: No
- **Reason**: Controlled releases, manual approval

## Environment Variables

### Required Variables

All environments require:
- `SPRING_PROFILES_ACTIVE`: Application profile (dev/staging/prod)
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `LOG_LEVEL`: Logging verbosity
- `DEPLOYMENT_REPLICAS`: Number of replicas (informational)

### Sensitive Variables

Store sensitive variables securely:
- Use `.env` files for local development
- Use secrets management for production (Vault, Sealed Secrets)
- Never commit passwords to git

### Override Variables

Override at runtime:

```bash
# Override specific variable
POSTGRES_PASSWORD=newpass podman-compose up -d

# Use different env file
podman-compose --env-file .env.local up -d
```

## Best Practices

### Version Pinning
- **Never** use `latest` tag in production
- Use semantic versioning (e.g., `v1.2.3`)
- Tag images with git commit SHA for traceability

### Image Management
- Build images in CI/CD pipeline
- Push to private registry with authentication
- Scan images for vulnerabilities
- Use multi-stage builds for smaller images

### Security
- Rotate passwords regularly
- Use secrets management tools
- Limit container privileges
- Enable network policies
- Regular security updates

### Monitoring
- Check health check status
- Monitor resource usage
- Set up alerts for failures
- Log aggregation for debugging

### Rollback Strategy
```bash
# Rollback to previous version
./scripts/update-image-tag.sh prod v1.1.0
git add gitops/prod/podman-compose.yml
git commit -m "rollback: Revert to v1.1.0 due to critical bug"
git push
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
podman-compose logs

# Check network exists
podman network ls | grep argocd-network

# Recreate network if needed
podman network create argocd-network
```

### Health Checks Failing

```bash
# Test backend health endpoint
curl http://localhost:8080/actuator/health

# Test frontend
curl http://localhost:5006
```

### Database Connection Issues

```bash
# Verify database is running
podman ps | grep postgres

# Check database connectivity from backend
podman exec -it orgmgmt-backend-dev curl postgres:5432
```

### Image Pull Failures

```bash
# Verify registry is accessible
curl http://localhost:5005/v2/_catalog

# Login to registry if needed
podman login localhost:5005
```

## Additional Resources

- [Podman Compose Documentation](https://github.com/containers/podman-compose)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Principles](https://www.gitops.tech/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)

## Support

For issues or questions:
1. Check service logs: `podman-compose logs`
2. Validate manifest: `./scripts/validate-manifest.sh <env>`
3. Review ArgoCD UI for sync status
4. Contact DevOps team
