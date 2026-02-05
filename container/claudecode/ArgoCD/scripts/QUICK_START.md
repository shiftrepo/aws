# Quick Start Guide - ArgoCD Project Automation Scripts

## First Time Setup (5 minutes)

```bash
# 1. Run the master setup script
cd /root/aws.git/container/claudecode/ArgoCD
./scripts/setup.sh

# 2. Wait for all services to start (this takes ~5-10 minutes)
# The script will automatically wait for services to be healthy

# 3. View your access credentials
cat credentials.txt
```

That's it! Your environment is now ready.

---

## Quick Command Reference

### Check Everything is Running

```bash
./scripts/status.sh
```

### Build and Deploy Your App

```bash
# Deploy to dev environment
./scripts/build-and-deploy.sh

# Deploy to production
./scripts/build-and-deploy.sh --environment prod
```

### Run Tests

```bash
# Run all tests
./scripts/test.sh

# Run only E2E tests
./scripts/run-e2e-tests.sh
```

### View Logs

```bash
# View all logs
./scripts/logs.sh

# Follow ArgoCD logs
./scripts/logs.sh argocd-server -f

# View PostgreSQL logs
./scripts/logs.sh postgres --tail 100
```

### Deploy with ArgoCD

```bash
# Deploy to dev
./scripts/argocd-deploy.sh --environment dev --wait

# Deploy to prod
./scripts/argocd-deploy.sh --environment prod --wait
```

### Rollback a Deployment

```bash
# See deployment history
./scripts/argocd-rollback.sh --environment dev --history

# Rollback to previous version
./scripts/argocd-rollback.sh --environment dev
```

### Backup Your Data

```bash
# Create full backup
./scripts/backup.sh

# Backup will be saved to: backups/argocd-backup-YYYYMMDD-HHMMSS.tar.gz
```

### Restore from Backup

```bash
# Restore everything
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz

# Restore database only
./scripts/restore.sh backups/argocd-backup-20240101-120000.tar.gz --database-only
```

### Clean Up

```bash
# Stop containers
./scripts/cleanup.sh

# Stop and remove all data (WARNING!)
./scripts/cleanup.sh --all

# Clean build artifacts
./scripts/cleanup.sh --artifacts
```

---

## Common Issues & Solutions

### "Service not healthy" during setup
**Solution:** Wait longer. Some services (GitLab, Nexus) take 5-10 minutes to start.
```bash
./scripts/logs.sh <service-name>
```

### "Container not running" error
**Solution:** Start the infrastructure first.
```bash
cd infrastructure
podman-compose up -d
```

### Build fails with "command not found"
**Solution:** Install missing dependencies.
```bash
# Check what's missing
./scripts/setup.sh --skip-checks
```

### Tests fail
**Solution:** Ensure application is deployed and healthy.
```bash
./scripts/status.sh
./scripts/build-and-deploy.sh
```

---

## Access URLs (Default Ports)

After running `setup.sh`, access services at:

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| ArgoCD | http://localhost:5010 | See credentials.txt |
| GitLab | http://localhost:5003 | See credentials.txt |
| Nexus | http://localhost:8081 | See credentials.txt |
| pgAdmin | http://localhost:5050 | See credentials.txt |
| Dev Frontend | http://localhost:5006 | - |
| Dev Backend | http://localhost:8080 | - |

**Important:** Check `credentials.txt` for all passwords.

---

## Daily Workflow

### Start Your Day
```bash
./scripts/status.sh --detailed
```

### Make Changes and Test
```bash
# 1. Edit code
# 2. Run tests
./scripts/test.sh

# 3. Deploy
./scripts/build-and-deploy.sh --environment dev

# 4. Verify
./scripts/run-e2e-tests.sh
```

### End Your Day
```bash
# Create backup
./scripts/backup.sh

# Optional: Stop containers to save resources
./scripts/cleanup.sh
```

---

## Production Deployment Checklist

- [ ] Run full test suite: `./scripts/test.sh --coverage`
- [ ] Create backup: `./scripts/backup.sh --output-dir /backups/pre-deployment`
- [ ] Deploy to staging: `./scripts/build-and-deploy.sh --environment staging`
- [ ] Test on staging: `./scripts/run-e2e-tests.sh --environment staging`
- [ ] Deploy to production: `./scripts/build-and-deploy.sh --environment prod --version X.Y.Z`
- [ ] Monitor deployment: `./scripts/argocd-deploy.sh --environment prod --wait`
- [ ] Run smoke tests: `./scripts/run-e2e-tests.sh --environment prod --grep "smoke"`
- [ ] Verify status: `./scripts/status.sh --detailed`
- [ ] Monitor logs: `./scripts/logs.sh --follow`

---

## Get Help

Each script has built-in help:
```bash
./scripts/<script-name>.sh --help
```

For detailed documentation, see: [scripts/README.md](README.md)

---

## Pro Tips

1. **Use watch mode** to monitor services continuously:
   ```bash
   ./scripts/status.sh --watch
   ```

2. **Follow logs in real-time** during deployments:
   ```bash
   ./scripts/logs.sh argocd-server -f
   ```

3. **Chain commands** for complete workflows:
   ```bash
   ./scripts/test.sh && ./scripts/build-and-deploy.sh && ./scripts/run-e2e-tests.sh
   ```

4. **Create backups before risky operations**:
   ```bash
   ./scripts/backup.sh && ./scripts/build-and-deploy.sh --environment prod
   ```

5. **Use grep to filter logs**:
   ```bash
   ./scripts/logs.sh postgres | grep ERROR
   ```

---

## Next Steps

1. Read the full documentation: [scripts/README.md](README.md)
2. Explore the GitOps manifests: `gitops/`
3. Review the infrastructure: `infrastructure/`
4. Check the application code: `app/`

---

**Happy Automating! 🚀**
