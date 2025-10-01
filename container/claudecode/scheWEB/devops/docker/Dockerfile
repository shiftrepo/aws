# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

# Install build dependencies
RUN apk add --no-cache python3 make g++ sqlite

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with production optimizations
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application code
COPY src ./src
COPY public ./public

# Build application (if using TypeScript/build step)
# RUN npm run build

# Production stage
FROM node:18-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    sqlite \
    wget \
    tini \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app

# Copy from builder
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --chown=appuser:appgroup src ./src
COPY --chown=appuser:appgroup public ./public
COPY --chown=appuser:appgroup package*.json ./

# Create directories with proper permissions
RUN mkdir -p /app/data /app/backups /app/logs && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Use tini for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start application
CMD ["node", "src/server.js"]
