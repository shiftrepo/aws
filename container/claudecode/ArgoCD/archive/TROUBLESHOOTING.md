# Troubleshooting Guide

Comprehensive troubleshooting guide for the Organization Management System.

## Table of Contents

- [Infrastructure Issues](#infrastructure-issues)
- [Database Issues](#database-issues)
- [Build Issues](#build-issues)
- [Deployment Issues](#deployment-issues)
- [Runtime Issues](#runtime-issues)
- [Test Issues](#test-issues)
- [Network Issues](#network-issues)
- [Performance Issues](#performance-issues)
- [GitOps Issues](#gitops-issues)
- [Common Error Messages](#common-error-messages)

## Infrastructure Issues

### Container Not Starting

#### Symptom
```bash
podman ps
# Container is not listed or shows "Exited" status
```

#### Root Cause
- Port conflict with existing service
- Volume permission issues
- Insufficient resources
- Configuration error

#### Solution

**Step 1: Check container logs**
```bash
podman logs <container-name>
# Look for specific error messages
```

**Step 2: Check port availability**
```bash
# Check if port is in use
sudo ss -tulpn | grep <port-number>

# Kill process using the port
sudo kill -9 <PID>
```

**Step 3: Check volume permissions**
```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect <volume-name>

# Fix permissions if needed
sudo chown -R $(id -u):$(id -g) /path/to/volume
```

**Step 4: Check system resources**
```bash
# Check memory
free -h

# Check disk space
df -h

# Check CPU
top
```

**Step 5: Restart container**
```bash
# Remove and recreate container
podman rm -f <container-name>
cd infrastructure
podman-compose up -d <service-name>
```

#### Prevention
- Always check logs before troubleshooting
- Monitor system resources
- Use health checks
- Document port assignments

### Port Conflicts

#### Symptom
```
Error: cannot bind to port 8080: address already in use
```

#### Root Cause
Another service is using the required port.

#### Solution

**Option 1: Kill the conflicting process**
```bash
# Find what's using the port
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Restart the service
podman restart <container-name>
```

**Option 2: Change the port**
```bash
# Edit environment file
vim infrastructure/.env

# Change port mapping
# Example: APP_BACKEND_PORT=8081

# Restart services
cd infrastructure
podman-compose down
podman-compose up -d
```

#### Prevention
- Document all port assignments
- Use standard ports when possible
- Check ports before starting services

### Volume Permission Issues

#### Symptom
```
Error: permission denied
chown: cannot access '/var/lib/postgresql/data': Permission denied
```

#### Root Cause
Container user doesn't have permission to access mounted volumes.

#### Solution

**Step 1: Check volume ownership**
```bash
podman volume inspect <volume-name>
ls -la /path/to/volume
```

**Step 2: Fix permissions**
```bash
# For PostgreSQL
sudo chown -R 999:999 /var/lib/containers/storage/volumes/<volume-name>

# For other services, check the UID in container
podman exec <container> id
sudo chown -R <uid>:<gid> /path/to/volume
```

**Step 3: Recreate volume if needed**
```bash
# Backup data first
podman volume export <volume-name> -o backup.tar

# Remove volume
podman volume rm <volume-name>

# Recreate with correct permissions
podman volume create <volume-name>

# Restore data
podman volume import <volume-name> backup.tar
```

#### Prevention
- Use named volumes
- Document UID/GID requirements
- Test volume mounts before production

### Network Connectivity Issues

#### Symptom
```
Error: unable to connect to service
curl: (7) Failed to connect to localhost port 8080: Connection refused
```

#### Root Cause
- Service not running
- Network misconfiguration
- Firewall blocking connections

#### Solution

**Step 1: Verify service is running**
```bash
podman ps | grep <service>
```

**Step 2: Check network**
```bash
# Inspect network
podman network inspect argocd-network

# Verify container is connected
podman inspect <container> | grep NetworkSettings -A 20
```

**Step 3: Test connectivity from host**
```bash
# Test port
telnet localhost <port>

# Or use curl
curl -v http://localhost:<port>
```

**Step 4: Test connectivity between containers**
```bash
# Execute in container
podman exec <container1> ping <container2>
podman exec <container1> curl http://<container2>:<port>
```

**Step 5: Check firewall**
```bash
# Check firewall status
sudo firewall-cmd --list-all

# Add port if needed
sudo firewall-cmd --add-port=<port>/tcp --permanent
sudo firewall-cmd --reload
```

#### Prevention
- Use health checks
- Document network architecture
- Monitor network connectivity

## Database Issues

### Connection Failures

#### Symptom
```
org.postgresql.util.PSQLException: Connection refused
Could not connect to database
```

#### Root Cause
- PostgreSQL not running
- Wrong credentials
- Network issues
- Connection pool exhausted

#### Solution

**Step 1: Verify PostgreSQL is running**
```bash
podman ps | grep postgres

# Check health
podman healthcheck run orgmgmt-postgres

# Check logs
podman logs orgmgmt-postgres
```

**Step 2: Test connection**
```bash
# From host
podman exec -it orgmgmt-postgres pg_isready -U orgmgmt_user

# Connect to database
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt
```

**Step 3: Verify credentials**
```bash
# Check environment variables
cat infrastructure/.env | grep POSTGRES

# Check application configuration
cat app/backend/src/main/resources/application.yml | grep datasource -A 5
```

**Step 4: Check connection pool**
```bash
# View active connections
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname = 'orgmgmt';"

# Kill idle connections if needed
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'orgmgmt' AND state = 'idle';"
```

**Step 5: Restart services**
```bash
# Restart PostgreSQL
podman restart orgmgmt-postgres

# Wait for it to be healthy
sleep 10

# Restart backend
podman restart orgmgmt-backend-dev
```

#### Prevention
- Monitor connection pool usage
- Set appropriate connection limits
- Use connection pooling (HikariCP)
- Implement retry logic

### Migration Errors

#### Symptom
```
FlywayException: Migration V1__init.sql failed
```

#### Root Cause
- SQL syntax error
- Missing dependencies
- Duplicate migration
- Schema already exists

#### Solution

**Step 1: Check Flyway status**
```bash
cd app/backend
mvn flyway:info
```

**Step 2: View migration history**
```bash
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "SELECT * FROM flyway_schema_history;"
```

**Step 3: Identify failed migration**
```bash
# Check backend logs
podman logs orgmgmt-backend-dev | grep -i flyway
```

**Step 4: Fix the migration**

**Option A: Repair and retry**
```bash
cd app/backend
mvn flyway:repair
mvn flyway:migrate
```

**Option B: Clean and restart (DEVELOPMENT ONLY)**
```bash
# WARNING: This deletes all data!
mvn flyway:clean
mvn flyway:migrate
```

**Option C: Manual fix**
```bash
# Mark migration as successful if already applied
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "UPDATE flyway_schema_history SET success = true WHERE version = '<version>';"
```

#### Prevention
- Test migrations before commit
- Use idempotent SQL
- Version migrations properly
- Backup before migrations

### Performance Problems

#### Symptom
```
Slow queries
Database timeout errors
High CPU usage
```

#### Root Cause
- Missing indexes
- Inefficient queries
- Large result sets
- Lock contention

#### Solution

**Step 1: Identify slow queries**
```bash
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds';"
```

**Step 2: Analyze query performance**
```bash
# Use EXPLAIN ANALYZE
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "EXPLAIN ANALYZE SELECT * FROM organizations WHERE active = true;"
```

**Step 3: Add indexes**
```sql
-- Create indexes for frequently queried columns
CREATE INDEX CONCURRENTLY idx_org_active ON organizations(active);
CREATE INDEX CONCURRENTLY idx_dept_org_id ON departments(organization_id);
CREATE INDEX CONCURRENTLY idx_user_email ON users(email);
```

**Step 4: Optimize queries**
```java
// Use pagination
Page<Organization> findAll(Pageable pageable);

// Use projections for large objects
@Query("SELECT new com.example.orgmgmt.dto.OrganizationDTO(o.id, o.name) FROM Organization o")
List<OrganizationDTO> findAllProjections();

// Use JOIN FETCH to avoid N+1
@Query("SELECT o FROM Organization o LEFT JOIN FETCH o.departments")
List<Organization> findAllWithDepartments();
```

**Step 5: Database maintenance**
```bash
# Vacuum and analyze
podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "VACUUM ANALYZE;"

# Reindex
podman exec orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c "REINDEX DATABASE orgmgmt;"
```

#### Prevention
- Add indexes for foreign keys
- Use query optimization
- Implement pagination
- Monitor query performance
- Regular vacuum and analyze

## Build Issues

### Maven Build Failures

#### Symptom
```
[ERROR] Failed to execute goal
[ERROR] Compilation failure
```

#### Root Cause
- Missing dependencies
- Compilation errors
- Test failures
- Plugin issues

#### Solution

**Step 1: Clean and rebuild**
```bash
cd app/backend

# Clean everything
mvn clean

# Update dependencies
mvn dependency:resolve -U

# Rebuild
mvn clean install
```

**Step 2: Check for dependency conflicts**
```bash
# View dependency tree
mvn dependency:tree

# Check for conflicts
mvn dependency:analyze
```

**Step 3: Skip tests temporarily**
```bash
# Build without tests
mvn clean install -DskipTests

# Then run tests separately
mvn test
```

**Step 4: Clear Maven cache**
```bash
# Remove local repository
rm -rf ~/.m2/repository

# Or specific artifact
rm -rf ~/.m2/repository/com/example/orgmgmt
```

**Step 5: Check Java version**
```bash
# Verify Java version
java -version
mvn -version

# Should be Java 17
```

#### Prevention
- Lock dependency versions
- Use dependency management
- Run tests before commit
- Use CI/CD for validation

### npm Build Failures

#### Symptom
```
ERROR in ./src/App.jsx
Module not found
npm ERR! code ELIFECYCLE
```

#### Root Cause
- Missing dependencies
- Syntax errors
- Version conflicts
- Cache issues

#### Solution

**Step 1: Clean install**
```bash
cd app/frontend

# Remove node_modules and lock file
rm -rf node_modules package-lock.json

# Clean npm cache
npm cache clean --force

# Install dependencies
npm install
```

**Step 2: Fix vulnerabilities**
```bash
# Audit dependencies
npm audit

# Fix vulnerabilities
npm audit fix

# Force fix (may have breaking changes)
npm audit fix --force
```

**Step 3: Check Node version**
```bash
# Verify Node version
node --version
npm --version

# Should be Node 20+
```

**Step 4: Build with verbose logging**
```bash
# Build with detailed output
npm run build --verbose
```

**Step 5: Check for syntax errors**
```bash
# Run linter
npm run lint

# Fix automatically
npm run lint -- --fix
```

#### Prevention
- Lock dependency versions
- Use package-lock.json
- Run linter before commit
- Test builds locally

### Container Build Failures

#### Symptom
```
Error building image
COPY failed: no source files were specified
```

#### Root Cause
- Missing build artifacts
- Wrong Dockerfile path
- Context issues
- Layer caching problems

#### Solution

**Step 1: Verify build artifacts exist**
```bash
# For backend
ls -lh app/backend/target/*.jar

# For frontend
ls -lh app/frontend/dist/
```

**Step 2: Clean build**
```bash
# Backend
cd app/backend
mvn clean package

# Frontend
cd app/frontend
rm -rf dist
npm run build
```

**Step 3: Build container with no cache**
```bash
# Backend
podman build --no-cache -t orgmgmt-backend:latest app/backend

# Frontend
podman build --no-cache -t orgmgmt-frontend:latest app/frontend
```

**Step 4: Check Dockerfile**
```bash
# Verify Dockerfile syntax
cat app/backend/Dockerfile
cat app/frontend/Dockerfile
```

**Step 5: Build with verbose output**
```bash
podman build --log-level debug -t orgmgmt-backend:latest app/backend
```

#### Prevention
- Test Dockerfiles locally
- Use multi-stage builds
- Document build process
- Version images properly

## Deployment Issues

### ArgoCD Sync Failures

#### Symptom
```
Application is OutOfSync
Sync failed: manifest is invalid
```

#### Root Cause
- Invalid manifest syntax
- Missing required fields
- Resource conflicts
- Network issues

#### Solution

**Step 1: Check application status**
```bash
# Get application details
argocd app get orgmgmt-dev

# View sync status
argocd app list
```

**Step 2: View sync errors**
```bash
# Get detailed error message
argocd app get orgmgmt-dev -o yaml | grep -A 10 "message:"
```

**Step 3: Validate manifest**
```bash
# Validate manifest syntax
./gitops/scripts/validate-manifest.sh gitops/dev/podman-compose.yml
```

**Step 4: Manual sync**
```bash
# Force sync
argocd app sync orgmgmt-dev --force --prune

# Sync with replace
argocd app sync orgmgmt-dev --replace
```

**Step 5: Check ArgoCD logs**
```bash
# View ArgoCD server logs
podman logs argocd-server

# View repo server logs
podman logs argocd-repo-server

# View controller logs
podman logs argocd-application-controller
```

#### Prevention
- Validate manifests before commit
- Use ArgoCD dry-run
- Test in dev environment first
- Monitor ArgoCD dashboard

### Health Check Failures

#### Symptom
```
Container unhealthy
Health check failed
```

#### Root Cause
- Application not started
- Wrong health check endpoint
- Timeout too short
- Service dependencies not ready

#### Solution

**Step 1: Check health status**
```bash
# Check health
podman healthcheck run orgmgmt-backend-dev

# View health logs
podman inspect orgmgmt-backend-dev | grep -A 20 Health
```

**Step 2: Manually test endpoint**
```bash
# Test health endpoint
curl -v http://localhost:8080/actuator/health

# Or inside container
podman exec orgmgmt-backend-dev curl http://localhost:8080/actuator/health
```

**Step 3: Check application logs**
```bash
# View startup logs
podman logs orgmgmt-backend-dev | head -100

# Check for errors
podman logs orgmgmt-backend-dev | grep -i error
```

**Step 4: Increase health check timeout**
```yaml
# In podman-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s  # Increase this
```

**Step 5: Check dependencies**
```bash
# Verify database is up
podman ps | grep postgres

# Test database connection
podman exec orgmgmt-postgres pg_isready
```

#### Prevention
- Set appropriate health check intervals
- Implement proper health endpoints
- Check dependencies first
- Monitor health status

### GitOps Manifest Errors

#### Symptom
```
Failed to parse manifest
Invalid YAML syntax
```

#### Root Cause
- YAML syntax error
- Invalid image tag
- Missing environment variables
- Wrong indentation

#### Solution

**Step 1: Validate YAML syntax**
```bash
# Use yamllint
yamllint gitops/dev/podman-compose.yml

# Or use Python
python -c "import yaml; yaml.safe_load(open('gitops/dev/podman-compose.yml'))"
```

**Step 2: Check for common issues**
```bash
# Verify image exists
podman pull localhost:5005/orgmgmt/backend:latest

# Check environment variables
grep -r "UNDEFINED" gitops/

# Verify indentation
cat -A gitops/dev/podman-compose.yml | head -20
```

**Step 3: Compare with working manifest**
```bash
# Diff with previous version
git diff HEAD~1 gitops/dev/podman-compose.yml

# Or with another environment
diff gitops/dev/podman-compose.yml gitops/staging/podman-compose.yml
```

**Step 4: Use validation script**
```bash
./gitops/scripts/validate-manifest.sh gitops/dev/podman-compose.yml
```

#### Prevention
- Use YAML linter
- Validate before commit
- Use templates
- Test in dev first

## Runtime Issues

### Application Crashes

#### Symptom
```
Container keeps restarting
Exit code 1 or 137
```

#### Root Cause
- Out of memory
- Uncaught exception
- Configuration error
- Resource limits

#### Solution

**Step 1: Check exit code**
```bash
# View container status
podman ps -a | grep orgmgmt-backend

# Inspect exit code
podman inspect orgmgmt-backend-dev | grep -i exitcode
```

**Step 2: View logs**
```bash
# View all logs
podman logs orgmgmt-backend-dev

# View last crash
podman logs --tail 100 orgmgmt-backend-dev
```

**Step 3: Check resource usage**
```bash
# View container stats
podman stats orgmgmt-backend-dev

# Check system resources
free -h
df -h
```

**Step 4: Increase resources**
```yaml
# In podman-compose.yml
services:
  orgmgmt-backend:
    deploy:
      resources:
        limits:
          memory: 2G  # Increase this
          cpus: '2'
```

**Step 5: Check for memory leaks**
```bash
# Generate heap dump
podman exec orgmgmt-backend-dev jmap -dump:live,format=b,file=/tmp/heap.bin 1

# Analyze with jhat or VisualVM
```

#### Prevention
- Set appropriate resource limits
- Implement error handling
- Monitor resource usage
- Use profiling tools

### API Errors

#### Symptom
```
HTTP 500 Internal Server Error
HTTP 404 Not Found
HTTP 400 Bad Request
```

#### Root Cause
- Validation errors
- Database errors
- Logic errors
- Missing resources

#### Solution

**Step 1: Check API logs**
```bash
# View recent errors
podman logs orgmgmt-backend-dev | grep -i error | tail -20

# View specific request
podman logs orgmgmt-backend-dev | grep "REQUEST_ID"
```

**Step 2: Test API directly**
```bash
# Test endpoint
curl -v http://localhost:8080/api/organizations

# Test with data
curl -X POST http://localhost:8080/api/organizations \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","code":"TEST001","active":true}'
```

**Step 3: Check database state**
```bash
# Verify data
podman exec -it orgmgmt-postgres psql -U orgmgmt_user -d orgmgmt -c \
  "SELECT * FROM organizations LIMIT 10;"
```

**Step 4: Review validation rules**
```java
// Check entity validation
@NotNull
@Size(min = 1, max = 100)
private String name;
```

**Step 5: Check exception handler**
```bash
# View exception handling
cat app/backend/src/main/java/com/example/orgmgmt/exception/GlobalExceptionHandler.java
```

#### Prevention
- Implement proper validation
- Use exception handlers
- Log errors properly
- Test edge cases

### Frontend Not Loading

#### Symptom
```
Blank page
404 Not Found
Unable to load resources
```

#### Root Cause
- Build errors
- Routing issues
- API connection errors
- Cache issues

#### Solution

**Step 1: Check frontend logs**
```bash
# View nginx logs
podman logs orgmgmt-frontend-dev

# Check nginx status
podman exec orgmgmt-frontend-dev ps aux | grep nginx
```

**Step 2: Check browser console**
```javascript
// Open browser developer tools (F12)
// Check Console tab for errors
// Check Network tab for failed requests
```

**Step 3: Verify build output**
```bash
# Check dist folder exists
podman exec orgmgmt-frontend-dev ls -la /usr/share/nginx/html

# Verify index.html
podman exec orgmgmt-frontend-dev cat /usr/share/nginx/html/index.html | head -20
```

**Step 4: Test API connectivity**
```bash
# From container
podman exec orgmgmt-frontend-dev wget -O- http://orgmgmt-backend-dev:8080/actuator/health
```

**Step 5: Clear browser cache**
```
# In browser: Ctrl+Shift+Delete
# Or use incognito mode
```

#### Prevention
- Test build output
- Monitor frontend logs
- Implement error boundaries
- Use proper error handling

## Test Issues

### E2E Test Failures

#### Symptom
```
Playwright test failed
Timeout exceeded
Element not found
```

#### Root Cause
- Application not ready
- Timing issues
- Environment differences
- Selector changes

#### Solution

**Step 1: Run tests with debug**
```bash
cd playwright-tests

# Run with debug
npx playwright test --debug

# Run specific test
npx playwright test tests/organizations/create-organization.spec.ts
```

**Step 2: Check test output**
```bash
# View test report
npx playwright show-report

# Check screenshots
ls -la test-results/
open test-results/*/screenshot.png
```

**Step 3: Verify application is ready**
```bash
# Check services
./scripts/status.sh

# Test API
curl http://localhost:8080/actuator/health

# Test frontend
curl http://localhost:5006
```

**Step 4: Increase timeouts**
```typescript
// In playwright.config.ts
timeout: 60000,  // Increase timeout
expect: {
  timeout: 10000
}
```

**Step 5: Update selectors**
```typescript
// Use more stable selectors
await page.getByRole('button', { name: 'Create' }).click();
// Instead of
await page.locator('#create-btn').click();
```

#### Prevention
- Use stable selectors
- Add explicit waits
- Test locally first
- Keep tests isolated

### Coverage Report Errors

#### Symptom
```
Coverage report not generated
JaCoCo error
Jest coverage failed
```

#### Root Cause
- Tests not running
- Coverage thresholds not met
- Configuration error

#### Solution

**Step 1: Generate coverage manually**
```bash
# Backend
cd app/backend
mvn clean test jacoco:report

# Frontend
cd app/frontend
npm test -- --coverage
```

**Step 2: Check coverage thresholds**
```xml
<!-- In pom.xml -->
<limit>
  <counter>LINE</counter>
  <value>COVEREDRATIO</value>
  <minimum>0.80</minimum>  <!-- Check this -->
</limit>
```

**Step 3: View coverage report**
```bash
# Backend
open app/backend/target/site/jacoco/index.html

# Frontend
open app/frontend/coverage/lcov-report/index.html
```

**Step 4: Add missing tests**
```bash
# Identify uncovered code
# Write tests for uncovered classes/functions
```

#### Prevention
- Write tests for new code
- Monitor coverage in CI/CD
- Set realistic thresholds
- Review coverage reports

## Common Error Messages

### "Connection refused"

**Cause**: Service not running or wrong port

**Solution**:
```bash
# Check if service is running
podman ps | grep <service>

# Check port
curl http://localhost:<port>

# Restart service
podman restart <container>
```

### "Out of memory"

**Cause**: Container memory limit exceeded

**Solution**:
```bash
# Check memory usage
podman stats

# Increase memory limit
# Edit podman-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### "Permission denied"

**Cause**: File/volume permission issues

**Solution**:
```bash
# Check permissions
ls -la /path/to/file

# Fix permissions
sudo chown -R $(id -u):$(id -g) /path/to/file
```

### "Image not found"

**Cause**: Container image doesn't exist

**Solution**:
```bash
# List images
podman images

# Pull image
podman pull <image-name>

# Or build image
podman build -t <image-name> .
```

### "Port already in use"

**Cause**: Another service using the port

**Solution**:
```bash
# Find process
sudo lsof -i :<port>

# Kill process
sudo kill -9 <PID>
```

## Getting Additional Help

If you can't resolve the issue:

1. **Check Logs**: `./scripts/logs.sh`
2. **Check Status**: `./scripts/status.sh`
3. **Review Documentation**: [README.md](README.md)
4. **Search Issues**: Check GitHub issues
5. **Ask Community**: Post in forums
6. **Contact Support**: Reach out to team

---

Remember: When in doubt, check the logs!
