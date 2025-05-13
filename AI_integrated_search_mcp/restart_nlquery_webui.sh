#!/bin/bash
# Script to restart the nl-query and web-ui services to apply fixes

echo "Restarting nl-query and web-ui services..."

# Stop the services first
echo "Stopping services..."
podman-compose -f podman-compose.yml stop nl-query-service web-ui

# Start the services again
echo "Starting services..."
podman-compose -f podman-compose.yml up -d nl-query-service web-ui

echo "Services restarted. Check logs with:"
echo "podman-compose -f podman-compose.yml logs -f nl-query-service web-ui"

echo "Done!"
