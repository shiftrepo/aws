#!/bin/bash

# Script to just restart the webui service
set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

echo "=== Restarting WebUI Service ==="

echo "1. Stopping the web-ui service..."
podman-compose stop web-ui

echo "2. Starting the web-ui service..."
podman-compose up -d web-ui

echo "WebUI service has been restarted."
echo "You can check the web-ui logs with:"
echo "podman logs \$(podman ps -qf name=web-ui)"
