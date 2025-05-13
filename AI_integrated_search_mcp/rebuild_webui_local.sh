#!/bin/bash

# Script to rebuild just the webui service using only local build
set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

echo "=== Rebuilding WebUI Service (Local Only) ==="

echo "1. Building web-ui service locally..."
podman-compose build web-ui

echo "2. Stopping the web-ui service..."
podman-compose stop web-ui || true

echo "3. Starting the web-ui service with locally built image..."
# Force using local build and prevent pulling from registry
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 podman-compose up -d --force-recreate --no-deps web-ui

echo "WebUI service has been rebuilt and restarted."
echo "You can check the web-ui logs with:"
echo "podman logs \$(podman ps -qf name=web-ui)"
