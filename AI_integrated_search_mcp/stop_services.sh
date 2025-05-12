#!/bin/bash

# AI Integrated Search MCP - Stop Services Script
# This script stops all the containers for the AI SQLite search system

set -e

echo "===== AI Integrated Search MCP ====="
echo "Stopping services at $(date)"

# Check if running as root, as required for podman
if [ "$(id -u)" -ne 0 ]; then
    echo "WARNING: This script needs to be run as root for podman"
    echo "Adding 'sudo' to commands"
    SUDO="sudo"
else
    SUDO=""
fi

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed"
    echo "Please install podman-compose first"
    exit 1
fi

echo "Stopping containers..."
$SUDO podman-compose -f podman-compose.yml down

echo "Checking for remaining containers..."
if $SUDO podman ps -a | grep -q "ai-"; then
    echo "Force removing any remaining containers..."
    $SUDO podman ps -a | grep "ai-" | awk '{print $1}' | xargs -r $SUDO podman rm -f
fi

echo ""
echo "All services stopped successfully!"
echo ""
echo "To start services again, run: ./start_services.sh"
