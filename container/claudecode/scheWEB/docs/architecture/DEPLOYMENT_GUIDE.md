# Deployment Guide - Team Meeting Scheduler

**Version:** 1.0
**Last Updated:** 2025-10-01

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Initialization](#database-initialization)
6. [SSL/TLS Setup](#ssltls-setup)
7. [Backup & Restore](#backup--restore)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- 1 CPU core
- 2 GB RAM
- 10 GB disk space
- Ubuntu 22.04 LTS or similar Linux distribution

**Recommended:**
- 2 CPU cores
- 4 GB RAM
- 20 GB disk space (for logs and backups)

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- OpenSSL (for certificate generation)
- Optional: Certbot (for Let's Encrypt SSL)

### Installation Commands

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Install Git and OpenSSL
sudo apt install git openssl -y

# Verify installations
docker --version
docker compose version
git --version
```

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourorg/meeting-scheduler.git
cd meeting-scheduler
```

### 2. Create Environment File

```bash
cat > .env << EOF
# Application Configuration
APP_ENV=development
APP_PORT=8000
APP_HOST=0.0.0.0

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_EXPIRY_HOURS=24
BCRYPT_ROUNDS=12

# Database
DATABASE_PATH=/app/data/scheduler.db

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=/app/logs/app.log

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
```

### 3. Create Directory Structure

```bash
mkdir -p data logs nginx/ssl static
```

### 4. Start Development Environment

```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Initialize database
docker-compose exec app python -m src.migrations.init_db

# Create test admin user
docker-compose exec app python -m src.scripts.create_admin \
  --email admin@localhost \
  --password AdminPass123! \
  --name "Admin User"
```

### 5. Verify Development Setup

```bash
# Check container health
docker-compose ps

# Test API health endpoint
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@localhost","password":"AdminPass123!"}'
```

---

## Production Deployment

### 1. Server Preparation

```bash
# Connect to production server
ssh user@your-server.com

# Create application user
sudo useradd -m -s /bin/bash scheduler
sudo usermod -aG docker scheduler

# Create application directory
sudo mkdir -p /opt/meeting-scheduler
sudo chown scheduler:scheduler /opt/meeting-scheduler
```

### 2. Clone and Configure

```bash
# Switch to application user
sudo su - scheduler
cd /opt/meeting-scheduler

# Clone repository
git clone https://github.com/yourorg/meeting-scheduler.git .

# Create production environment file
cat > .env << EOF
# Application Configuration
APP_ENV=production
APP_PORT=8000
APP_HOST=0.0.0.0

# Security (CHANGE THESE!)
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_EXPIRY_HOURS=24
BCRYPT_ROUNDS=12

# Database
DATABASE_PATH=/app/data/scheduler.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# CORS
CORS_ORIGINS=https://scheduler.example.com

# Domain (for SSL)
DOMAIN=scheduler.example.com
ADMIN_EMAIL=admin@example.com
EOF

# Secure environment file
chmod 600 .env
```

### 3. SSL Certificate Setup

**Option A: Let's Encrypt (Recommended)**

```bash
# Install Certbot
sudo apt install certbot -y

# Stop containers if running
docker-compose down

# Obtain certificate
sudo certbot certonly --standalone \
  -d scheduler.example.com \
  -m admin@example.com \
  --agree-tos

# Copy certificates to application directory
sudo cp /etc/letsencrypt/live/scheduler.example.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/scheduler.example.com/privkey.pem nginx/ssl/
sudo chown scheduler:scheduler nginx/ssl/*

# Setup auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

**Option B: Self-Signed Certificate (Development)**

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=scheduler.example.com"
```

### 4. Configure Nginx

```bash
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    upstream app_backend {
        server app:8000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Auth endpoints (stricter rate limiting)
        location /api/auth/ {
            limit_req zone=auth_limit burst=5 nodelay;

            proxy_pass http://app_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://app_backend;
            access_log off;
        }
    }
}
EOF
```

### 5. Production Docker Compose

```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: scheduler-app
    restart: unless-stopped
    environment:
      - DATABASE_PATH=${DATABASE_PATH}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_EXPIRY_HOURS=${JWT_EXPIRY_HOURS}
      - BCRYPT_ROUNDS=${BCRYPT_ROUNDS}
      - LOG_LEVEL=${LOG_LEVEL}
      - APP_ENV=${APP_ENV}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - scheduler-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    container_name: scheduler-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./static:/usr/share/nginx/html:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - app
    networks:
      - scheduler-net
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

networks:
  scheduler-net:
    driver: bridge
EOF
```

### 6. Start Production Environment

```bash
# Build and start containers
docker-compose -f docker-compose.prod.yml up -d --build

# Initialize database
docker-compose -f docker-compose.prod.yml exec app python -m src.migrations.init_db

# Create admin user
docker-compose -f docker-compose.prod.yml exec app python -m src.scripts.create_admin \
  --email admin@example.com \
  --password $(openssl rand -base64 16) \
  --name "Admin User"

# Save the generated password!
```

### 7. Setup Systemd Service

```bash
sudo cat > /etc/systemd/system/scheduler.service << 'EOF'
[Unit]
Description=Meeting Scheduler Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/meeting-scheduler
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=scheduler
Group=scheduler

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable scheduler.service
sudo systemctl start scheduler.service
sudo systemctl status scheduler.service
```

---

## Environment Configuration

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Environment (development/production) | development | No |
| `APP_PORT` | Application port | 8000 | No |
| `JWT_SECRET_KEY` | Secret key for JWT signing | - | **Yes** |
| `JWT_EXPIRY_HOURS` | Token expiry in hours | 24 | No |
| `BCRYPT_ROUNDS` | Password hashing cost factor | 12 | No |
| `DATABASE_PATH` | SQLite database file path | /app/data/scheduler.db | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |
| `LOG_FILE` | Log file path | /app/logs/app.log | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | * | No |

---

## Database Initialization

### Initial Setup

```bash
# Run migration scripts
docker-compose exec app python -m src.migrations.init_db

# Verify database
docker-compose exec app sqlite3 /app/data/scheduler.db ".tables"

# Check schema
docker-compose exec app sqlite3 /app/data/scheduler.db ".schema users"
```

### Seed Data (Optional)

```bash
# Create seed script
cat > scripts/seed_data.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from src.database import db
from src.models import User, Availability
from src.utils.auth import hash_password

# Create sample users
users = [
    {"email": "alice@example.com", "name": "Alice Smith", "password": "Pass123!"},
    {"email": "bob@example.com", "name": "Bob Johnson", "password": "Pass123!"},
]

for user_data in users:
    user = User(
        email=user_data["email"],
        name=user_data["name"],
        password_hash=hash_password(user_data["password"]),
        role="member"
    )
    db.session.add(user)

db.session.commit()
print("Seed data created successfully!")
EOF

# Run seed script
docker-compose exec app python scripts/seed_data.py
```

---

## Backup & Restore

### Automated Backup Script

```bash
# Create backup script
sudo cat > /usr/local/bin/scheduler-backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/backup/scheduler"
APP_DIR="/opt/meeting-scheduler"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

# Backup SQLite database (hot backup)
cd $APP_DIR
docker-compose -f docker-compose.prod.yml exec -T app \
  sqlite3 /app/data/scheduler.db ".backup /app/data/backup_$TIMESTAMP.db"

docker cp scheduler-app:/app/data/backup_$TIMESTAMP.db $BACKUP_DIR/

# Backup environment file
cp $APP_DIR/.env $BACKUP_DIR/.env_$TIMESTAMP

# Compress backup
cd $BACKUP_DIR
tar -czf scheduler_backup_$TIMESTAMP.tar.gz backup_$TIMESTAMP.db .env_$TIMESTAMP
rm backup_$TIMESTAMP.db .env_$TIMESTAMP

# Delete old backups
find $BACKUP_DIR -name "scheduler_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Optional: Upload to S3
# aws s3 cp scheduler_backup_$TIMESTAMP.tar.gz s3://your-bucket/backups/

echo "Backup completed: $BACKUP_DIR/scheduler_backup_$TIMESTAMP.tar.gz"
EOF

sudo chmod +x /usr/local/bin/scheduler-backup.sh

# Setup cron job for daily backups at 2 AM
sudo crontab -e
# Add line:
# 0 2 * * * /usr/local/bin/scheduler-backup.sh >> /var/log/scheduler-backup.log 2>&1
```

### Manual Backup

```bash
# Manual backup
sudo /usr/local/bin/scheduler-backup.sh
```

### Restore from Backup

```bash
# Stop application
docker-compose -f docker-compose.prod.yml down

# Extract backup
cd /backup/scheduler
tar -xzf scheduler_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore database
cp backup_YYYYMMDD_HHMMSS.db /opt/meeting-scheduler/data/scheduler.db

# Restore environment (if needed)
cp .env_YYYYMMDD_HHMMSS /opt/meeting-scheduler/.env

# Restart application
cd /opt/meeting-scheduler
docker-compose -f docker-compose.prod.yml up -d
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl https://scheduler.example.com/health

# Container status
docker-compose ps

# View logs
docker-compose logs -f --tail=100

# Database size
docker-compose exec app ls -lh /app/data/scheduler.db
```

### Log Management

```bash
# View application logs
docker-compose logs app

# View nginx access logs
docker-compose logs nginx

# Setup log rotation
sudo cat > /etc/logrotate.d/scheduler << 'EOF'
/opt/meeting-scheduler/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 scheduler scheduler
    postrotate
        docker-compose -f /opt/meeting-scheduler/docker-compose.prod.yml restart app > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Performance Monitoring

```bash
# Container resource usage
docker stats scheduler-app scheduler-nginx

# Database statistics
docker-compose exec app sqlite3 /app/data/scheduler.db "
  SELECT
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM availability) as availability_slots,
    (SELECT COUNT(*) FROM meetings) as meetings;
"

# API response time test
curl -o /dev/null -s -w "%{time_total}s\n" https://scheduler.example.com/api/auth/me
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs app

# Common fixes:
# - Check environment variables
cat .env

# - Check permissions
ls -l data/ logs/

# - Verify database exists
ls -l data/scheduler.db

# - Rebuild containers
docker-compose down
docker-compose up -d --build
```

#### 2. Database Locked Error

```bash
# Stop all containers
docker-compose down

# Check for stale lock
rm -f data/scheduler.db-wal data/scheduler.db-shm

# Restart
docker-compose up -d
```

#### 3. SSL Certificate Issues

```bash
# Check certificate expiry
openssl x509 -in nginx/ssl/fullchain.pem -noout -enddate

# Renew Let's Encrypt certificate
sudo certbot renew
sudo cp /etc/letsencrypt/live/scheduler.example.com/* nginx/ssl/
docker-compose restart nginx
```

#### 4. High Memory Usage

```bash
# Check container memory
docker stats --no-stream

# Restart containers
docker-compose restart

# Optimize database
docker-compose exec app sqlite3 /app/data/scheduler.db "VACUUM;"
```

### Debug Mode

```bash
# Enable debug logging
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose restart app

# Interactive shell
docker-compose exec app /bin/bash

# Python REPL with app context
docker-compose exec app python -c "from src.app import app; import src.models"
```

---

## Security Checklist

- [ ] Change default JWT secret key
- [ ] Change default admin password
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (allow only 80, 443, SSH)
- [ ] Setup automated backups
- [ ] Enable log rotation
- [ ] Keep Docker and system packages updated
- [ ] Monitor access logs for suspicious activity
- [ ] Implement rate limiting (configured in nginx)
- [ ] Regular security audits

---

## Update Procedure

```bash
# 1. Backup current installation
/usr/local/bin/scheduler-backup.sh

# 2. Pull latest code
cd /opt/meeting-scheduler
git pull origin main

# 3. Rebuild containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Run migrations (if any)
docker-compose -f docker-compose.prod.yml exec app python -m src.migrations.upgrade

# 5. Verify deployment
curl https://scheduler.example.com/health
```

---

## Support & Resources

- **Documentation:** `/docs` directory
- **API Docs:** https://scheduler.example.com/api/docs
- **Issue Tracker:** https://github.com/yourorg/meeting-scheduler/issues
- **Logs:** `/opt/meeting-scheduler/logs`

---

**Deployment Guide Version:** 1.0
**Last Updated:** 2025-10-01
