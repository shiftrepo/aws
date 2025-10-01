# Deployment Guide

## Quick Start Deployment

### Prerequisites
- Docker and Docker Compose installed
- Basic understanding of command line
- 2GB+ RAM available
- 10GB+ disk space

### 5-Minute Deployment

```bash
# 1. Clone repository
git clone <repository-url>
cd schedule-system

# 2. Configure environment
cp config/environments/.env.production .env
nano .env  # Edit credentials

# 3. Deploy
docker-compose up -d

# 4. Verify
curl http://localhost:3000/health
```

**Access the application:** http://localhost:3000

## Deployment Options

### Option 1: Basic Deployment (Recommended for Small Teams)

**Features:**
- Application only
- SQLite database
- Local backups
- No SSL (use reverse proxy)

```bash
# Start application
docker-compose up -d app

# View logs
docker-compose logs -f app
```

**Requirements:**
- 512MB RAM
- 1 CPU core
- 5GB disk

### Option 2: Production Deployment

**Features:**
- Application + Nginx
- SSL/TLS termination
- Automated backups
- Log management

```bash
# Start with production profile
docker-compose --profile production up -d

# View all services
docker-compose ps
```

**Requirements:**
- 1GB RAM
- 2 CPU cores
- 10GB disk

### Option 3: Full Stack (with Monitoring)

**Features:**
- All production features
- Prometheus monitoring
- Grafana dashboards
- Performance metrics

```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

**Requirements:**
- 2GB RAM
- 2 CPU cores
- 20GB disk

## Environment Configuration

### Critical Variables (MUST CHANGE)

```bash
# .env file
BASIC_AUTH_USERNAME=your_admin_username    # Change this!
BASIC_AUTH_PASSWORD=your_strong_password   # Change this!
SESSION_SECRET=generate_32_char_random     # Change this!
```

### Generate Secure Credentials

```bash
# Generate strong password
openssl rand -base64 32

# Generate session secret
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Optional Configuration

```bash
# Application
APP_PORT=3000
LOG_LEVEL=info

# Backups
BACKUP_ENABLED=true
BACKUP_INTERVAL=86400000        # 24 hours
BACKUP_RETENTION_DAYS=30

# S3 Backup (Optional)
S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## SSL/TLS Setup

### Option A: Using Nginx (Included)

**1. Generate SSL Certificate (Let's Encrypt):**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem devops/docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem devops/docker/ssl/key.pem
sudo chmod 644 devops/docker/ssl/*.pem
```

**2. Start with SSL:**
```bash
docker-compose --profile ssl up -d
```

### Option B: External Reverse Proxy

If using Cloudflare, AWS ALB, or external Nginx:

```bash
# Start app only (no nginx)
docker-compose up -d app

# Configure your reverse proxy to forward to localhost:3000
```

## Database Management

### Initial Setup

Database is created automatically on first start. No manual setup required.

### Migrations

```bash
# Run migrations
docker-compose exec app npm run db:migrate

# Or manually
docker-compose exec app node -e "require('./src/database').migrate()"
```

### Backup

**Manual Backup:**
```bash
# Create backup
docker-compose exec app /backup/backup.sh

# List backups
docker-compose exec app ls -lh /app/backups/
```

**Automated Backups:**
```bash
# Enable in .env
BACKUP_ENABLED=true
BACKUP_INTERVAL=86400000  # Daily

# Start backup service
docker-compose --profile backup up -d
```

**S3 Backups (Recommended for Production):**
```bash
# Configure in .env
S3_BUCKET=my-schedule-backups
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Backups will automatically upload to S3
```

### Restore

```bash
# List available backups
docker-compose exec app ls /app/backups/

# Restore from backup
docker-compose exec app /backup/restore.sh schedule_20250101_120000.db.gz

# Restart application
docker-compose restart app
```

## Scaling & Performance

### For 10-20 Users (Default)

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

### For 20-30 Users

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
```

### Database Optimization

```bash
# Regular optimization
docker-compose exec app sqlite3 /app/data/schedule.db "VACUUM; ANALYZE;"

# Schedule via cron
0 2 * * 0 docker-compose exec app sqlite3 /app/data/schedule.db "VACUUM;"
```

## Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:3000/health

# Docker health
docker-compose ps
docker stats
```

### Logs

```bash
# Application logs
docker-compose logs -f app

# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100 app
```

### Prometheus & Grafana (Optional)

```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Prometheus
open http://localhost:9090

# Access Grafana
open http://localhost:3001
# Default credentials: admin/admin
```

**Key Metrics to Monitor:**
- Request rate and latency
- Error rates
- CPU and memory usage
- Database query time
- Active connections

## Maintenance

### Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f app
```

### Database Cleanup

```bash
# Delete old schedules (90+ days)
docker-compose exec app node -e "
const db = require('./src/database');
db.run(\`DELETE FROM schedules WHERE date < datetime('now', '-90 days')\`);
"
```

### Log Rotation

```bash
# Configure in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs app

# Check database permissions
ls -la ./data/

# Reset and restart
docker-compose down
docker-compose up -d
```

### Can't Access Application

```bash
# Check if running
docker-compose ps

# Check firewall
sudo ufw status

# Check port binding
netstat -tlnp | grep 3000
```

### Database Locked Errors

```bash
# Restart application
docker-compose restart app

# If persists, check for orphaned processes
ps aux | grep schedule
```

### High Memory Usage

```bash
# Check stats
docker stats

# Reduce memory limit
# Edit docker-compose.yml memory: 256M

# Restart
docker-compose restart app
```

### SSL Certificate Issues

```bash
# Verify certificate
openssl x509 -in devops/docker/ssl/cert.pem -text -noout

# Check expiry
openssl x509 -enddate -noout -in devops/docker/ssl/cert.pem

# Renew Let's Encrypt
sudo certbot renew
```

## Security Checklist

Before going live:

- [ ] Changed default credentials
- [ ] Generated strong session secret
- [ ] Configured firewall rules
- [ ] Enabled HTTPS/SSL
- [ ] Set up regular backups
- [ ] Configured rate limiting
- [ ] Reviewed nginx security headers
- [ ] Updated all dependencies
- [ ] Tested backup restoration
- [ ] Documented access procedures

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Backups configured and tested
- [ ] Monitoring set up
- [ ] Firewall rules configured
- [ ] Log rotation enabled
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations

## Common Deployment Scenarios

### Scenario 1: Single Server (Most Common)

**Setup:**
- One server (2GB RAM, 2 CPUs)
- Docker Compose
- Let's Encrypt SSL
- Daily backups to S3

**Commands:**
```bash
docker-compose --profile production up -d
```

### Scenario 2: Behind Corporate Proxy

**Setup:**
- Internal network
- Corporate SSL termination
- Local backups only

**Commands:**
```bash
# Start app only
docker-compose up -d app

# Configure proxy to forward to :3000
```

### Scenario 3: High Availability

**Setup:**
- Load balancer
- Multiple app instances
- Shared database volume
- External monitoring

**docker-compose.override.yml:**
```yaml
services:
  app:
    deploy:
      replicas: 2
```

## Support Resources

- **Documentation**: See /docs folder
- **Logs**: `docker-compose logs -f`
- **Health Check**: http://localhost:3000/health
- **GitHub Issues**: <repository-url>/issues

## Next Steps

1. **Configure Environment**: Edit .env with your values
2. **Deploy**: Run docker-compose up -d
3. **Verify**: Check health endpoint
4. **Create Users**: Add team members
5. **Test**: Create test schedules
6. **Monitor**: Review logs and metrics
7. **Backup**: Verify backups are working

---

For detailed guides, see:
- [DevOps Guide](./DEVOPS_GUIDE.md)
- [Security Guide](./SECURITY.md)
- [Testing Strategy](./TESTING_STRATEGY.md)
