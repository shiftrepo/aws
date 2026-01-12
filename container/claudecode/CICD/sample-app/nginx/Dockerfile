# ========================================================================
# Nginx Dockerfile - Multi-Stage Build
# Stage 1: Build React frontend
# Stage 2: Nginx server with built frontend + reverse proxy
# ========================================================================

# Stage 1: Build frontend
FROM docker.io/library/node:20-alpine AS frontend-builder

WORKDIR /app

# Copy frontend package files (cache dependencies layer)
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Nginx server
FROM docker.io/library/nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Expose port 80 (published as host port 80)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1

# Nginx runs in foreground by default
CMD ["nginx", "-g", "daemon off;"]
