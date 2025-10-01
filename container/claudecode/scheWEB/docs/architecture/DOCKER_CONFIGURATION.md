# Docker Configuration - Team Schedule Management System

## Container Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Docker Host                           │
│                                                            │
│  ┌──────────────────────────────────────────────────┐     │
│  │              nginx-proxy                         │     │
│  │  Image: nginx:1.25-alpine                        │     │
│  │  Port: 80:80, 443:443                            │     │
│  │  - SSL Termination                               │     │
│  │  - Static File Serving                           │     │
│  │  - API Reverse Proxy                             │     │
│  │  - Gzip Compression                              │     │
│  └──────────────────────────────────────────────────┘     │
│                          │                                 │
│         ┌────────────────┴────────────────┐               │
│         │                                  │               │
│         ▼                                  ▼               │
│  ┌──────────────┐                 ┌──────────────┐        │
│  │   frontend   │                 │   backend    │        │
│  │  Image:      │                 │  Image:      │        │
│  │  node:20     │                 │  node:20     │        │
│  │  Port: 3000  │                 │  Port: 3001  │        │
│  │              │                 │              │        │
│  │  - React SPA │                 │  - Express   │        │
│  │  - Vite Dev  │                 │  - REST API  │        │
│  └──────────────┘                 └──────────────┘        │
│                                            │               │
│                                            │               │
│                                            ▼               │
│                                   ┌──────────────┐        │
│                                   │   Volume:    │        │
│                                   │   db-data    │        │
│                                   │              │        │
│                                   │  SQLite DB   │        │
│                                   └──────────────┘        │
│                                                            │
│  Networks:                                                │
│  - app-network (internal)                                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Docker Compose Configuration

### docker-compose.yml (Production)

```yaml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:1.25-alpine
    container_name: schedule-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - backend
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Backend API Service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
    container_name: schedule-backend
    restart: unless-stopped
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - PORT=3001
      - DATABASE_PATH=/data/schedule.db
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRES_IN=24h
      - CORS_ORIGIN=http://localhost
      - LOG_LEVEL=info
    volumes:
      - db-data:/data
      - backend-logs:/app/logs
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Frontend Development Service (optional, for development)
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: schedule-frontend-dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:3001
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - app-network
    profiles:
      - dev

networks:
  app-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16

volumes:
  db-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data
  backend-logs:
    driver: local
  nginx-logs:
    driver: local
```

### docker-compose.dev.yml (Development Override)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    environment:
      - NODE_ENV=development
      - LOG_LEVEL=debug
    volumes:
      - ./backend:/app
      - /app/node_modules
    command: npm run dev

  frontend:
    profiles:
      - dev
    environment:
      - NODE_ENV=development
    command: npm run dev
```

## Dockerfile Configurations

### Backend Dockerfile (Production)

```dockerfile
# backend/Dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Development stage
FROM base AS dev
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Run any build steps (if needed)
# RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 scheduleapp

# Copy production dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy application code
COPY --chown=scheduleapp:nodejs . .

# Create data directory with correct permissions
RUN mkdir -p /data && \
    chown -R scheduleapp:nodejs /data

# Switch to non-root user
USER scheduleapp

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start application
CMD ["node", "src/server.js"]
```

### Backend Dockerfile.dev (Development)

```dockerfile
# backend/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Install development dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3001

# Start with nodemon for hot-reload
CMD ["npm", "run", "dev"]
```

### Frontend Dockerfile (Production)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

# Build stage
FROM base AS builder
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage - serve with nginx
FROM nginx:1.25-alpine AS runner

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Frontend Dockerfile.dev (Development)

```dockerfile
# frontend/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

## Nginx Configuration

### nginx/nginx.conf (Main Configuration)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Include additional configs
    include /etc/nginx/conf.d/*.conf;
}
```

### nginx/conf.d/default.conf (Site Configuration)

```nginx
# Upstream backend
upstream backend {
    server backend:3001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP Server
server {
    listen 80;
    server_name localhost;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # API proxy
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;

        # Cache static assets
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Security: Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# HTTPS Server (optional, requires SSL certificates)
# server {
#     listen 443 ssl http2;
#     server_name localhost;
#
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
#     ssl_prefer_server_ciphers on;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#
#     # Include same locations as HTTP
#     include /etc/nginx/conf.d/locations.conf;
# }
```

## Environment Variables

### .env.example

```bash
# Application
NODE_ENV=production
PORT=3001

# Database
DATABASE_PATH=/data/schedule.db

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h

# CORS
CORS_ORIGIN=http://localhost

# Logging
LOG_LEVEL=info

# Email (future)
# SMTP_HOST=smtp.example.com
# SMTP_PORT=587
# SMTP_USER=noreply@example.com
# SMTP_PASS=password

# Frontend (build time)
VITE_API_URL=http://localhost:3001
```

## Docker Commands

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Start specific service
docker-compose up backend

# View logs
docker-compose logs -f backend

# Execute commands in container
docker-compose exec backend npm run migrate
docker-compose exec backend sh

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production Commands

```bash
# Build images
docker-compose build --no-cache

# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Scale services (if needed in future)
docker-compose up -d --scale backend=2

# Backup database
docker-compose exec backend sh -c 'sqlite3 /data/schedule.db ".backup /data/backup-$(date +%Y%m%d).db"'

# Health check
docker-compose ps
```

## Health Checks

### Backend Health Endpoint

```javascript
// backend/src/routes/health.js
app.get('/health', (req, res) => {
  const db = require('./database');

  try {
    // Check database connection
    const result = db.prepare('SELECT 1').get();

    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      database: 'connected',
      memory: process.memoryUsage()
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});
```

## Volume Management

### Database Backup Strategy

```bash
#!/bin/bash
# scripts/backup-db.sh

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="schedule-${TIMESTAMP}.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T backend sqlite3 /data/schedule.db ".backup '/data/backup.db'"
docker cp schedule-backend:/data/backup.db "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 30 backups
ls -t $BACKUP_DIR/*.gz | tail -n +31 | xargs -r rm

echo "Backup completed: $BACKUP_FILE.gz"
```

### Database Restore

```bash
#!/bin/bash
# scripts/restore-db.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <backup-file>"
  exit 1
fi

BACKUP_FILE=$1

# Stop backend
docker-compose stop backend

# Restore database
gunzip -c "$BACKUP_FILE" > /tmp/restore.db
docker cp /tmp/restore.db schedule-backend:/data/schedule.db

# Start backend
docker-compose start backend

echo "Restore completed from: $BACKUP_FILE"
```

## Deployment Workflow

### CI/CD Pipeline Example (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build images
        run: docker-compose build

      - name: Run tests
        run: docker-compose run backend npm test

      - name: Deploy to production
        if: success()
        run: |
          docker-compose down
          docker-compose up -d
          docker-compose exec backend npm run migrate
```

## Resource Limits

### Production Resource Constraints

```yaml
# Add to docker-compose.yml services
services:
  backend:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  nginx:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
        reservations:
          cpus: '0.25'
          memory: 64M
```

## Monitoring

### Docker Stats

```bash
# Real-time resource usage
docker stats schedule-backend schedule-nginx

# Export metrics (Prometheus format)
docker-compose exec backend wget -qO- localhost:3001/metrics
```
