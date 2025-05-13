#!/bin/bash
# Script to rebuild nl-query and web-ui services from Dockerfile and restart

echo "Rebuilding and restarting nl-query and web-ui services..."

# Stop the services first
echo "Stopping services..."
podman-compose -f podman-compose.yml stop nl-query-service web-ui

# Build the services from Dockerfile
echo "Building services from Dockerfile..."
podman-compose -f podman-compose.yml build nl-query-service web-ui

# Start the services again
echo "Starting services..."
podman-compose -f podman-compose.yml up -d nl-query-service web-ui

echo "Services rebuilt and restarted. Check logs with:"
echo "podman-compose -f podman-compose.yml logs -f nl-query-service web-ui"

echo "Done!"
