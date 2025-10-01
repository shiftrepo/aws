# DevOps & Deployment Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Database Management](#database-management)
5. [Security Configuration](#security-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Performance Testing](#performance-testing)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Local Development
```bash
# Install dependencies
npm install

# Set up environment
cp config/environments/.env.development .env

# Run migrations
npm run db:migrate

# Start development server
npm run dev
```

### Docker Deployment (Production)
```bash
# Copy and configure environment
cp config/environments/.env.production .env
nano .env  # Edit with your values

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f app
```

## Environment Setup

### Environment Variables

#### Required Variables
```bash
# Authentication (CHANGE THESE!)
BASIC_AUTH_USERNAME=your_admin_username
BASIC_AUTH_PASSWORD=your_strong_password_here
SESSION_SECRET=generate_random_32_char_string_here

# Database
DATABASE_PATH=/app/data/schedule.db
```

#### Optional Variables
```bash
# Application
NODE_ENV=production
APP_PORT=3000
LOG_LEVEL=info

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=900000

# Backup
BACKUP_ENABLED=true
BACKUP_INTERVAL=86400000
BACKUP_RETENTION_DAYS=30

# S3 Backup (Optional)
S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Generating Secure Credentials

```bash
# Generate strong password (Linux/macOS)
openssl rand -base64 32

# Generate session secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# Generate using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Docker Deployment

### Basic Deployment
```bash
# Start application only
docker-compose up -d app

# View logs
docker-compose logs -f app
```

### Production Deployment (with SSL)
```bash
# Start with nginx SSL termination
docker-compose --profile production up -d

# Start with monitoring
docker-compose --profile monitoring up -d
```

### Docker Compose Profiles

| Profile | Description | Services |
|---------|-------------|----------|
| default | Basic app only | app |
| production | App + Nginx + Backup | app, nginx, backup |
| ssl | App + Nginx with SSL | app, nginx |
| monitoring | Add monitoring tools | prometheus, grafana |
| backup | Add backup service | backup |

### Custom Configuration

**Using Custom Data Directory:**
```bash
# In .env file
DATA_PATH=/path/to/your/data

# Start services
docker-compose up -d
```

**Resource Limits:**
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Adjust as needed
      memory: 1G       # Adjust as needed
```

## Database Management

### Migrations

**Run Migrations:**
```bash
# Using npm script
npm run db:migrate

# Using script directly
./devops/scripts/migrate.sh

# In Docker
docker-compose exec app npm run db:migrate
```

**Create New Migration:**
```bash
# Create migration file
cat > migrations/002_add_feature.sql << EOF
-- Add your SQL here
ALTER TABLE teams ADD COLUMN new_field TEXT;
EOF

# Apply migration
npm run db:migrate
```

### Backup & Restore

**Manual Backup:**
```bash
# Local backup
./devops/scripts/backup.sh

# Docker backup
docker-compose exec backup /backup/backup.sh
```

**Restore from Backup:**
```bash
# List available backups
ls -lh /app/backups/

# Restore specific backup
./devops/scripts/restore.sh schedule_20250101_120000.db.gz

# Docker restore
docker-compose exec backup /backup/restore.sh schedule_20250101_120000.db.gz
```

**Automated Backups:**
```bash
# Configure in .env
BACKUP_ENABLED=true
BACKUP_INTERVAL=86400000  # 24 hours in ms
BACKUP_RETENTION_DAYS=30

# Start backup service
docker-compose --profile backup up -d
```

### Database Maintenance

**Optimize Database:**
```bash
sqlite3 data/schedule.db "VACUUM;"
sqlite3 data/schedule.db "ANALYZE;"
```

**Check Integrity:**
```bash
sqlite3 data/schedule.db "PRAGMA integrity_check;"
```

## Security Configuration

### Basic Authentication

**Setting Up Users:**
```bash
# In .env file
BASIC_AUTH_ENABLED=true
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=your_strong_password

# Restart application
docker-compose restart app
```

**Best Practices:**
- Use strong passwords (minimum 12 characters)
- Use unique passwords for each environment
- Rotate credentials regularly
- Never commit credentials to version control

### SSL/TLS Configuration

**Generate Self-Signed Certificate (Development):**
```bash
mkdir -p devops/docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout devops/docker/ssl/key.pem \
  -out devops/docker/ssl/cert.pem
```

**Using Let's Encrypt (Production):**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem devops/docker/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem devops/docker/ssl/key.pem

# Start with SSL
docker-compose --profile ssl up -d
```

### Rate Limiting

**Configure Rate Limits:**
```bash
# Application-level (in .env)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX=100          # Max requests
RATE_LIMIT_WINDOW=900000    # 15 minutes

# Nginx-level (in nginx.conf)
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
```

### Security Headers

Configured in `nginx.conf`:
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (HSTS)
- Referrer-Policy

## Monitoring & Logging

### Application Logs

**View Logs:**
```bash
# Docker logs
docker-compose logs -f app
docker-compose logs --tail=100 app

# Log files
tail -f /app/logs/app.log
```

**Log Levels:**
- `error`: Critical errors only
- `warn`: Warnings and errors
- `info`: General information (default)
- `debug`: Detailed debugging info

### Prometheus & Grafana

**Start Monitoring Stack:**
```bash
docker-compose --profile monitoring up -d
```

**Access Dashboards:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

**Key Metrics:**
- Request rate and latency
- Error rates
- Database query performance
- Memory and CPU usage
- Active connections

### Health Checks

**Endpoints:**
```bash
# Application health
curl http://localhost:3000/health

# Docker health check
docker-compose ps
```

## CI/CD Pipeline

### GitHub Actions Workflow

Pipeline stages:
1. **Lint & Format**: Code quality checks
2. **Unit Tests**: Fast, isolated tests
3. **Integration Tests**: Database and API tests
4. **Security Audit**: Dependency scanning
5. **Build**: Docker image creation
6. **Performance Tests**: Load testing
7. **Deploy**: Automated deployment

### Running Locally

```bash
# Install act (GitHub Actions locally)
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow
act -j test-unit
act -j build
```

### Deployment Environments

| Environment | Branch | Trigger | URL |
|-------------|--------|---------|-----|
| Development | develop | Push | dev.example.com |
| Staging | develop | Push | staging.example.com |
| Production | main | Push | example.com |

## Performance Testing

### k6 Load Testing

**Install k6:**
```bash
# macOS
brew install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**Run Load Test:**
```bash
# Basic test
k6 run tests/performance/k6-load-test.js

# With custom configuration
BASE_URL=https://your-domain.com \
AUTH_USER=admin \
AUTH_PASS=password \
k6 run tests/performance/k6-load-test.js
```

### Artillery Testing

**Install Artillery:**
```bash
npm install -g artillery
```

**Run Tests:**
```bash
# Basic test
artillery run tests/performance/artillery-config.yml

# Generate report
artillery run --output report.json tests/performance/artillery-config.yml
artillery report report.json
```

### Performance Targets

For 30 concurrent users:
- Response time p95: < 500ms
- Response time p99: < 1000ms
- Error rate: < 1%
- Throughput: > 100 req/s

## Troubleshooting

### Common Issues

**1. Database Locked Error**
```bash
# Check for long-running queries
sqlite3 data/schedule.db ".timeout 5000"

# Kill stale connections
docker-compose restart app
```

**2. Permission Errors**
```bash
# Fix data directory permissions
chown -R 1001:1001 ./data
chmod 755 ./data
```

**3. Out of Memory**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml
memory: 1G

# Restart services
docker-compose restart app
```

**4. SSL Certificate Issues**
```bash
# Verify certificate
openssl x509 -in devops/docker/ssl/cert.pem -text -noout

# Check nginx logs
docker-compose logs nginx
```

### Debug Mode

**Enable Debug Logging:**
```bash
# Set in .env
LOG_LEVEL=debug

# Restart application
docker-compose restart app

# View detailed logs
docker-compose logs -f app
```

### Health Checks

**Application:**
```bash
curl http://localhost:3000/health
# Expected: {"status":"ok","timestamp":"..."}
```

**Database:**
```bash
sqlite3 data/schedule.db "SELECT COUNT(*) FROM teams;"
```

**Docker:**
```bash
docker-compose ps
docker stats
```

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **SQLite Best Practices**: https://www.sqlite.org/bestpractice.html
- **k6 Documentation**: https://k6.io/docs/
- **Nginx Documentation**: https://nginx.org/en/docs/

## Support

For issues and questions:
1. Check the logs: `docker-compose logs -f`
2. Review this guide
3. Check GitHub Issues
4. Contact the development team
