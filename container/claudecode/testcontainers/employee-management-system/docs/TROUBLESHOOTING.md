# Troubleshooting Guide - Employee Management System

Comprehensive troubleshooting guide for common issues, performance problems, and debugging techniques.

## 🚨 Quick Diagnosis

### System Health Check
```bash
#!/bin/bash
# Quick health check script

echo "=== Employee Management System Health Check ==="
echo

echo "1. Checking container status..."
podman-compose ps

echo -e "\n2. Checking database connectivity..."
podman-compose exec postgres pg_isready -U postgres -d employee_db

echo -e "\n3. Checking application health..."
curl -s http://localhost:8080/actuator/health | jq '.' || echo "Application not responding"

echo -e "\n4. Checking disk space..."
df -h

echo -e "\n5. Checking memory usage..."
free -h

echo -e "\n6. Checking container logs for errors..."
podman-compose logs --tail=10 postgres | grep -i error || echo "No PostgreSQL errors"
podman-compose logs --tail=10 app | grep -i error || echo "No application errors"

echo -e "\nHealth check completed!"
```

## 🔧 Container Issues

### Container Won't Start

#### Symptom
```bash
$ podman-compose up -d
ERROR: Service 'postgres' failed to build
```

#### Diagnosis
```bash
# Check if ports are already in use
sudo netstat -tulpn | grep -E ':5432|:8080|:5050'

# Check available system resources
df -h
free -h

# Check for conflicting containers
podman ps -a
podman container list --all
```

#### Solutions

**Port Conflicts:**
```bash
# Option 1: Stop conflicting services
sudo systemctl stop postgresql
sudo killall -9 postgres

# Option 2: Change ports in podman-compose.yml
# Edit postgres service:
services:
  postgres:
    ports:
      - "5433:5432"  # Change host port
```

**Resource Issues:**
```bash
# Free up disk space
podman system prune -a
podman volume prune -f

# Free up memory
sudo systemctl restart docker  # or podman
```

**Permission Issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x docker/postgres/init.sql

# Fix SELinux issues (if applicable)
sudo setsebool -P container_manage_cgroup true
```

### Container Keeps Restarting

#### Symptom
```bash
$ podman-compose ps
NAME              STATUS
employee_postgres Restarting...
```

#### Diagnosis
```bash
# Check container logs
podman-compose logs postgres
podman-compose logs app

# Check container resource limits
podman stats $(podman-compose ps -q)

# Check for OOM kills
dmesg | grep -i "killed process"
```

#### Solutions

**Memory Issues:**
```yaml
# In podman-compose.yml, increase memory limits
services:
  postgres:
    mem_limit: 1g
    memswap_limit: 1g
  app:
    mem_limit: 2g
    memswap_limit: 2g
```

**Database Corruption:**
```bash
# Remove corrupted database volume
podman-compose down -v
podman volume rm $(podman volume ls -q | grep postgres)
podman-compose up -d
```

**Configuration Issues:**
```bash
# Reset to default configuration
git checkout -- podman-compose.yml
git checkout -- .env
podman-compose up -d
```

## 🗄️ Database Issues

### Connection Problems

#### Symptom
```
org.postgresql.util.PSQLException: Connection to localhost:5432 refused
```

#### Diagnosis
```bash
# Check if PostgreSQL container is running
podman-compose ps postgres

# Test database connectivity
podman-compose exec postgres pg_isready -U postgres

# Check database logs
podman-compose logs postgres | tail -20

# Test connection from application container
podman-compose exec app nc -zv postgres 5432
```

#### Solutions

**Container Not Running:**
```bash
# Restart PostgreSQL service
podman-compose restart postgres

# Check for startup errors
podman-compose logs postgres
```

**Wrong Connection Parameters:**
```bash
# Verify connection parameters in application.yml
podman-compose exec app cat src/main/resources/application.yml | grep -A 5 datasource

# Test with correct parameters
podman-compose exec app psql -h postgres -p 5432 -U postgres -d employee_db
```

**Network Issues:**
```bash
# Check container network
podman network ls
podman network inspect $(podman-compose ps -q | head -1)

# Recreate network
podman-compose down
podman network prune -f
podman-compose up -d
```

### Database Performance Issues

#### Symptom
Slow query execution, timeouts, or high CPU usage.

#### Diagnosis
```bash
# Check database performance stats
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT * FROM pg_stat_activity WHERE state = 'active';
"

# Check slow queries
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY total_time DESC LIMIT 10;
"

# Check database size and table stats
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
  FROM pg_stat_user_tables;
"
```

#### Solutions

**Query Optimization:**
```sql
-- Add missing indexes
CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_department_active ON employees(department_id, active);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.active = true;
```

**Database Configuration:**
```bash
# Increase shared memory (in podman-compose.yml)
services:
  postgres:
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c shared_buffers=256MB
      -c max_connections=100
      -c work_mem=4MB
```

**Connection Pool Tuning:**
```yaml
# In application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
```

### Data Corruption or Inconsistency

#### Symptoms
- Foreign key constraint violations
- Unexpected NULL values
- Missing or duplicate records

#### Diagnosis
```bash
# Check database integrity
podman-compose exec postgres psql -U postgres -d employee_db -c "
  -- Check for orphaned employees
  SELECT e.id, e.email, e.department_id
  FROM employees e
  LEFT JOIN departments d ON e.department_id = d.id
  WHERE e.department_id IS NOT NULL AND d.id IS NULL;
"

# Check constraint violations
podman-compose exec postgres psql -U postgres -d employee_db -c "
  -- Check email uniqueness
  SELECT email, COUNT(*)
  FROM employees
  GROUP BY email
  HAVING COUNT(*) > 1;
"
```

#### Solutions

**Fix Orphaned Records:**
```sql
-- Option 1: Remove orphaned employees
DELETE FROM employees
WHERE department_id NOT IN (SELECT id FROM departments);

-- Option 2: Set orphaned employees to NULL department
UPDATE employees
SET department_id = NULL
WHERE department_id NOT IN (SELECT id FROM departments);
```

**Reset Database:**
```bash
# Complete database reset (destroys all data)
podman-compose down -v
podman volume rm $(podman volume ls -q | grep postgres)
podman-compose up -d

# Wait for initialization
sleep 30
podman-compose logs postgres | grep "ready to accept connections"
```

## ☕ Application Issues

### Application Won't Start

#### Symptom
```
Error starting ApplicationContext
```

#### Diagnosis
```bash
# Check application logs
podman-compose logs app | tail -50

# Check Java version and environment
podman-compose exec app java -version
podman-compose exec app env | grep -E 'JAVA|SPRING'

# Check for missing dependencies
podman-compose exec app mvn dependency:tree | grep -i missing
```

#### Solutions

**Maven Dependencies:**
```bash
# Clean and rebuild
podman-compose exec app mvn clean install -DskipTests

# Update dependencies
podman-compose exec app mvn versions:display-dependency-updates
```

**Configuration Issues:**
```bash
# Check application configuration
podman-compose exec app cat src/main/resources/application.yml

# Validate configuration
podman-compose exec app mvn validate
```

**Port Conflicts:**
```yaml
# Change application port in podman-compose.yml
services:
  app:
    ports:
      - "8081:8080"  # Use different host port
    environment:
      - SERVER_PORT=8080  # Keep container port same
```

### Memory Issues (OutOfMemoryError)

#### Symptoms
```
java.lang.OutOfMemoryError: Java heap space
```

#### Diagnosis
```bash
# Check JVM memory settings
podman-compose exec app jps -v

# Monitor memory usage
podman stats $(podman-compose ps -q app)

# Check heap dump (if available)
podman-compose exec app jcmd $(pidof java) GC.run_finalization
```

#### Solutions

**Increase Heap Size:**
```yaml
# In podman-compose.yml
services:
  app:
    environment:
      - JAVA_OPTS=-Xmx2g -Xms1g -XX:+UseG1GC
```

**Memory Leak Detection:**
```bash
# Enable heap dump on OOM
services:
  app:
    environment:
      - JAVA_OPTS=-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heapdump.hprof
```

**Profile Memory Usage:**
```bash
# Use JProfiler or similar tools
podman-compose exec app java -XX:+UnlockCommercialFeatures -XX:+FlightRecorder -XX:StartFlightRecording=duration=60s,filename=/tmp/recording.jfr YourApp
```

## 🧪 Test Issues

### Tests Failing

#### Symptom
```
Tests run: 50, Failures: 5, Errors: 2, Skipped: 0
```

#### Diagnosis
```bash
# Run tests with detailed logging
podman-compose exec app mvn test -X

# Run specific failing test
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest#shouldFindByEmail"

# Check test database state
podman-compose exec postgres psql -U postgres -d employee_db -c "\dt"
```

#### Solutions

**Test Data Issues:**
```bash
# Validate test data
podman-compose exec app mvn test -Dtestdata.validate-only=true

# Refresh test data
podman-compose exec app mvn test -Dtestdata.refresh=true

# Clean test database
podman-compose exec app mvn clean test
```

**TestContainers Issues:**
```bash
# Check Docker/Podman connectivity
podman info | grep -E "Rootless|Version"

# Clean TestContainers
export TESTCONTAINERS_REUSE_ENABLE=false
podman-compose exec app mvn clean test

# Enable TestContainer logs
export TESTCONTAINERS_LOG_LEVEL=DEBUG
```

**Transaction/Isolation Issues:**
```java
// In test classes, ensure proper transaction management
@Transactional
@Rollback
public class EmployeeServiceTest {
    // Test methods
}
```

### Flaky Tests

#### Symptoms
Tests pass sometimes and fail other times.

#### Diagnosis
```bash
# Run test multiple times
for i in {1..10}; do
  podman-compose exec app mvn test -Dtest="FlakyTest" || echo "FAILED on iteration $i"
done

# Check for timing dependencies
podman-compose exec app mvn test -Dtest="FlakyTest" -X | grep -i time
```

#### Solutions

**Add Proper Wait Conditions:**
```java
// Instead of Thread.sleep()
@Test
public void shouldWaitForAsyncOperation() {
    // Start async operation
    service.asyncMethod();

    // Wait for condition
    await().atMost(Duration.ofSeconds(10))
           .until(() -> service.isCompleted());
}
```

**Fix Race Conditions:**
```java
// Use proper synchronization
@Test
@Transactional
public void shouldHandleConcurrentAccess() {
    // Ensure proper isolation level
}
```

### Test Performance Issues

#### Symptoms
Tests taking too long to execute.

#### Diagnosis
```bash
# Profile test execution
podman-compose exec app mvn test -Dtest.profile=true

# Check database connection pool
podman-compose logs postgres | grep -i connection

# Monitor container resources during tests
podman stats $(podman-compose ps -q) &
podman-compose exec app mvn test
```

#### Solutions

**Optimize TestContainers:**
```bash
# Reuse containers
export TESTCONTAINERS_REUSE_ENABLE=true

# Use faster database initialization
# In test configuration, disable Flyway and use direct SQL
```

**Parallel Test Execution:**
```xml
<!-- In pom.xml -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-surefire-plugin</artifactId>
  <configuration>
    <forkCount>2</forkCount>
    <reuseForks>true</reuseForks>
  </configuration>
</plugin>
```

## 🌐 Network and Connectivity Issues

### Can't Access Services

#### Symptoms
- pgAdmin not accessible on http://localhost:5050
- API not responding on http://localhost:8080

#### Diagnosis
```bash
# Check port bindings
podman-compose ps
podman port $(podman-compose ps -q postgres)
podman port $(podman-compose ps -q app)

# Test connectivity
curl -I http://localhost:8080/actuator/health
curl -I http://localhost:5050

# Check if services are listening
podman-compose exec app netstat -tlnp
podman-compose exec postgres netstat -tlnp
```

#### Solutions

**Port Binding Issues:**
```yaml
# Ensure proper port mapping in podman-compose.yml
services:
  postgres:
    ports:
      - "5432:5432"  # host:container
  app:
    ports:
      - "8080:8080"
  pgladmin:
    ports:
      - "5050:80"    # pgAdmin runs on port 80 inside container
```

**Firewall Issues:**
```bash
# Check firewall rules (Linux)
sudo iptables -L | grep -E '5432|8080|5050'

# Temporarily disable firewall for testing
sudo ufw disable  # Ubuntu/Debian
sudo systemctl stop firewalld  # CentOS/RHEL

# Add permanent rules
sudo ufw allow 5432
sudo ufw allow 8080
sudo ufw allow 5050
```

**Container Network Issues:**
```bash
# Recreate network
podman-compose down
podman network prune -f
podman-compose up -d

# Check container IP addresses
podman-compose exec app ip addr show
podman-compose exec postgres ip addr show
```

## 📊 Performance Troubleshooting

### High CPU Usage

#### Diagnosis
```bash
# Monitor container CPU usage
podman stats

# Check Java thread usage
podman-compose exec app jstack $(pidof java)

# Check database queries
podman-compose exec postgres psql -U postgres -d employee_db -c "
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query
  FROM pg_stat_activity
  WHERE state = 'active'
  ORDER BY duration DESC;
"
```

#### Solutions

**Application Optimization:**
```yaml
# Tune JVM garbage collection
services:
  app:
    environment:
      - JAVA_OPTS=-XX:+UseG1GC -XX:MaxGCPauseMillis=200 -Xmx2g
```

**Database Query Optimization:**
```sql
-- Identify slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Add missing indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employees_search
ON employees USING gin(to_tsvector('english', first_name || ' ' || last_name));
```

### High Memory Usage

#### Diagnosis
```bash
# Check memory usage by container
podman stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Java heap analysis
podman-compose exec app jstat -gc $(pidof java)

# Database memory usage
podman-compose exec postgres psql -U postgres -c "
  SELECT * FROM pg_stat_database WHERE datname = 'employee_db';
"
```

#### Solutions

**JVM Memory Tuning:**
```yaml
services:
  app:
    environment:
      - JAVA_OPTS=-Xmx1g -Xms512m -XX:+UseG1GC -XX:MaxMetaspaceSize=256m
    mem_limit: 2g
```

**PostgreSQL Memory Tuning:**
```yaml
services:
  postgres:
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=4MB
      -c max_connections=50
```

## 🛠️ Debugging Tools and Commands

### Container Inspection
```bash
# Get detailed container information
podman inspect $(podman-compose ps -q app)

# Execute commands in running containers
podman-compose exec app bash
podman-compose exec postgres bash

# Copy files from containers
podman cp $(podman-compose ps -q app):/workspace/target/logs ./app-logs
```

### Log Analysis
```bash
# Follow logs in real-time
podman-compose logs -f app | grep -E "ERROR|WARN|Exception"

# Search logs for patterns
podman-compose logs app | grep -i "connection"

# Save logs to file
podman-compose logs app > app.log 2>&1
```

### Database Debugging
```bash
# Connect to database
podman-compose exec postgres psql -U postgres -d employee_db

# Useful PostgreSQL debugging queries
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_locks;
SHOW all;
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM employees;
```

### Application Debugging
```bash
# Enable debug mode
podman-compose exec app mvn spring-boot:run -Dspring.profiles.active=dev -Ddebug=true

# Remote debugging setup
services:
  app:
    environment:
      - JAVA_OPTS=-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
    ports:
      - "5005:5005"  # Debug port
```

## 🆘 Emergency Recovery

### Complete System Reset
```bash
#!/bin/bash
# Nuclear option - complete reset (destroys all data)

echo "WARNING: This will destroy all data!"
read -p "Are you sure? (type 'yes' to continue): " confirm

if [ "$confirm" = "yes" ]; then
    echo "Stopping all services..."
    podman-compose down -v

    echo "Cleaning up containers and volumes..."
    podman system prune -a -f
    podman volume prune -f

    echo "Rebuilding and starting services..."
    podman-compose build --no-cache
    podman-compose up -d

    echo "Waiting for services to start..."
    sleep 30

    echo "Running health check..."
    ./scripts/health-check.sh

    echo "System reset completed!"
else
    echo "Reset cancelled."
fi
```

### Backup and Restore
```bash
# Create backup before major changes
podman-compose exec postgres pg_dump -U postgres employee_db > backup-$(date +%Y%m%d).sql

# Restore from backup
podman-compose exec -T postgres psql -U postgres employee_db < backup-20240115.sql
```

## 📞 Getting Help

### Information to Collect for Support
```bash
#!/bin/bash
# Support information collection script

echo "Employee Management System - Support Information" > support-info.txt
echo "=================================================" >> support-info.txt
date >> support-info.txt
echo "" >> support-info.txt

echo "System Information:" >> support-info.txt
uname -a >> support-info.txt
echo "" >> support-info.txt

echo "Container Status:" >> support-info.txt
podman-compose ps >> support-info.txt
echo "" >> support-info.txt

echo "Container Logs:" >> support-info.txt
podman-compose logs >> support-info.txt
echo "" >> support-info.txt

echo "System Resources:" >> support-info.txt
free -h >> support-info.txt
df -h >> support-info.txt
echo "" >> support-info.txt

echo "Network Configuration:" >> support-info.txt
podman network ls >> support-info.txt

echo "Support information collected in support-info.txt"
```

### Common Support Scenarios

| Issue | First Action | Documentation |
|-------|-------------|---------------|
| Container won't start | Check logs: `podman-compose logs` | [Container Issues](#🔧-container-issues) |
| Database connection fails | Verify PostgreSQL: `podman-compose exec postgres pg_isready` | [Database Issues](#🗄️-database-issues) |
| Tests failing | Run with debug: `mvn test -X` | [Test Issues](#🧪-test-issues) |
| High resource usage | Monitor: `podman stats` | [Performance](#📊-performance-troubleshooting) |
| API not responding | Check health: `curl localhost:8080/actuator/health` | [Application Issues](#☕-application-issues) |

---

**Remember**: Most issues can be resolved by checking logs, verifying configuration, and ensuring all services are healthy. When in doubt, start with the health check script and work through the diagnosis steps systematically.