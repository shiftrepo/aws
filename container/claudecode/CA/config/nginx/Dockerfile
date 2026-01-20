FROM docker.io/library/nginx:1.25-alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Create certificate directory
RUN mkdir -p /etc/nginx/certs

# Remove default nginx configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
# (Will be mounted via docker-compose volume)

# Copy test page
# (Will be mounted via docker-compose volume)

# Expose HTTPS port
EXPOSE 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -k -f https://localhost:443/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
