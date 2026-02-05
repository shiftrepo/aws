# ArgoCD Configuration for OrgMgmt System

This directory contains ArgoCD configuration files for deploying and managing the Organization Management System across multiple environments.

## Directory Structure

```
argocd/
├── applications/          # ArgoCD Application manifests
│   ├── orgmgmt-dev.yaml
│   ├── orgmgmt-staging.yaml
│   └── orgmgmt-prod.yaml
├── projects/              # ArgoCD Project definitions
│   └── orgmgmt.yaml
├── config/                # ArgoCD configuration
│   ├── argocd-cm.yaml
│   └── argocd-rbac-cm.yaml
└── README.md
```

## Prerequisites

- Kubernetes cluster (or Podman with kube-play support)
- ArgoCD installed and running
- kubectl configured to access your cluster
- argocd CLI installed (optional, for CLI operations)

## Setup Instructions

### 1. Install ArgoCD

```bash
# Create argocd namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s
```

### 2. Access ArgoCD UI

```bash
# Port-forward to access the UI
kubectl port-forward svc/argocd-server -n argocd 5010:443

# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Access UI at: http://localhost:5010
# Username: admin
# Password: (from the command above)
```

### 3. Apply ArgoCD Configuration

```bash
# Apply custom configuration
kubectl apply -f config/argocd-cm.yaml
kubectl apply -f config/argocd-rbac-cm.yaml

# Restart ArgoCD components to pick up new config
kubectl rollout restart deployment argocd-server -n argocd
kubectl rollout restart deployment argocd-repo-server -n argocd
```

### 4. Create AppProject

```bash
# Create the orgmgmt project
kubectl apply -f projects/orgmgmt.yaml

# Verify project creation
kubectl get appproject -n argocd orgmgmt
```

### 5. Deploy Applications

```bash
# Deploy development environment (auto-sync enabled)
kubectl apply -f applications/orgmgmt-dev.yaml

# Deploy staging environment (manual sync)
kubectl apply -f applications/orgmgmt-staging.yaml

# Deploy production environment (manual sync with approval)
kubectl apply -f applications/orgmgmt-prod.yaml

# Verify applications
kubectl get applications -n argocd
```

## Application Deployment Workflow

### Development Environment
- **Auto-sync**: Enabled
- **Self-heal**: Enabled
- **Prune**: Enabled
- Automatically deploys changes from the `dev` directory
- Best for rapid iteration and testing

### Staging Environment
- **Auto-sync**: Disabled (manual sync required)
- **Approval**: Required before sync
- Used for pre-production testing and validation
- Manual promotion ensures stability

### Production Environment
- **Auto-sync**: Disabled (manual sync only)
- **Approval**: Strict approval required
- **Notifications**: Enabled for sync events
- Highest level of control and safety
- Changes must be explicitly promoted

## Sync Policies Explanation

### Automated Sync (Dev)
```yaml
syncPolicy:
  automated:
    prune: true          # Remove resources not in Git
    selfHeal: true       # Revert manual changes
    allowEmpty: false    # Prevent empty syncs
```

### Manual Sync (Staging/Prod)
```yaml
syncPolicy:
  syncOptions:
    - CreateNamespace=false
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

## RBAC Configuration

### Default Roles

1. **readonly** - Default for all authenticated users
   - View applications and projects
   - No modification permissions

2. **developer** - Development team access
   - Full access to dev environment
   - Read-only access to staging/prod

3. **operator** - Operations team access
   - Full access to all environments
   - Manage applications and projects

4. **admin** - Full administrative access
   - Complete control over ArgoCD

### Role Assignment

Edit `config/argocd-rbac-cm.yaml` to assign roles:

```yaml
# Example: Assign user to developer role
g, user@example.com, role:developer

# Example: Assign group to operator role
g, ops-team, role:operator
```

## ArgoCD CLI Commands

### Login to ArgoCD
```bash
argocd login localhost:5010 --username admin --password <password>
```

### Application Management
```bash
# List applications
argocd app list

# Get application details
argocd app get orgmgmt-dev

# Sync application
argocd app sync orgmgmt-dev

# Sync with force
argocd app sync orgmgmt-prod --force

# View application logs
argocd app logs orgmgmt-dev

# Delete application
argocd app delete orgmgmt-dev
```

### Project Management
```bash
# List projects
argocd proj list

# Get project details
argocd proj get orgmgmt

# Add repository to project
argocd proj add-source orgmgmt http://localhost:5003/root/orgmgmt.git
```

### Sync Status and Health
```bash
# Watch sync status
argocd app sync orgmgmt-dev --watch

# Check application health
argocd app wait orgmgmt-dev --health

# View sync history
argocd app history orgmgmt-prod
```

## Troubleshooting

### Application is OutOfSync

```bash
# Check what's different
argocd app diff orgmgmt-dev

# View sync status details
kubectl describe application orgmgmt-dev -n argocd

# Force sync
argocd app sync orgmgmt-dev --force --prune
```

### Application Health is Degraded

```bash
# Check application events
kubectl get events -n default --sort-by='.lastTimestamp'

# View ArgoCD application status
argocd app get orgmgmt-dev --show-operation

# Check pod status in target namespace
kubectl get pods -n default
kubectl logs <pod-name> -n default
```

### Repository Connection Issues

```bash
# Check repository credentials
argocd repo list

# Test repository access
argocd repo get file:///gitops

# Verify filesystem path exists
kubectl exec -it deployment/argocd-repo-server -n argocd -- ls -la /gitops
```

### RBAC Permission Denied

```bash
# Check current user's permissions
argocd account can-i sync applications 'orgmgmt/orgmgmt-prod'

# View RBAC policy
kubectl get configmap argocd-rbac-cm -n argocd -o yaml

# Test with admin account
argocd login localhost:5010 --username admin
```

### ArgoCD Server Not Responding

```bash
# Check ArgoCD pod status
kubectl get pods -n argocd

# View ArgoCD server logs
kubectl logs -n argocd deployment/argocd-server

# Restart ArgoCD components
kubectl rollout restart deployment/argocd-server -n argocd
kubectl rollout restart deployment/argocd-repo-server -n argocd
kubectl rollout restart deployment/argocd-application-controller -n argocd
```

### Sync Hooks Failing

```bash
# View sync operation details
argocd app get orgmgmt-dev --show-operation

# Check hook logs
kubectl logs -n default <hook-pod-name>

# Skip hooks during sync
argocd app sync orgmgmt-dev --skip-hooks
```

## Best Practices

1. **GitOps Workflow**
   - Always commit changes to Git first
   - Let ArgoCD detect and sync changes
   - Avoid manual kubectl modifications in synced namespaces

2. **Environment Promotion**
   - Test thoroughly in dev before promoting to staging
   - Require peer review for production deployments
   - Use manual sync for staging and production

3. **Security**
   - Follow principle of least privilege
   - Regularly rotate ArgoCD admin password
   - Use RBAC to restrict access appropriately
   - Enable audit logging

4. **Monitoring**
   - Set up notifications for sync failures
   - Monitor application health status
   - Review sync history regularly

5. **Disaster Recovery**
   - Back up ArgoCD configuration regularly
   - Document manual recovery procedures
   - Test restore procedures

## Integration with CI/CD

### Example GitHub Actions Workflow

```yaml
name: Update GitOps Repository
on:
  push:
    branches: [main]

jobs:
  update-gitops:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout GitOps repo
        uses: actions/checkout@v3
        with:
          repository: your-org/gitops
          token: ${{ secrets.GITOPS_TOKEN }}

      - name: Update manifests
        run: |
          # Update image tags or configurations
          sed -i 's|image: .*|image: new-image:tag|' dev/deployment.yaml

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "Update dev environment"
          git push

      # ArgoCD will automatically detect and sync the changes
```

## Additional Resources

- [ArgoCD Official Documentation](https://argo-cd.readthedocs.io/)
- [ArgoCD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
- [GitOps Principles](https://www.gitops.tech/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## Support

For issues or questions:
- Check ArgoCD logs: `kubectl logs -n argocd deployment/argocd-server`
- Review application events: `kubectl describe application <app-name> -n argocd`
- Consult ArgoCD documentation: https://argo-cd.readthedocs.io/
