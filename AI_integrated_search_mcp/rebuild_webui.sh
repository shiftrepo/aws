#!/bin/bash

# Script to rebuild just the webui service
set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

echo "=== Rebuilding WebUI Service ==="

echo "1. Building web-ui service locally..."
podman-compose build web-ui

echo "2. Stopping the web-ui service..."
podman-compose stop web-ui

echo "3. Starting the web-ui service with the newly built image..."
podman-compose up -d web-ui

echo "WebUI service has been rebuilt and restarted."
echo "You can check the web-ui logs with:"
echo "podman logs \$(podman ps -qf name=web-ui)"
