#!/bin/bash
# Infrastructure Shutdown Script
# This script stops all infrastructure services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Stopping Infrastructure Services"
echo "=========================================="
echo ""

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed"
    exit 1
fi

# Stop services
echo "Stopping all services..."
podman-compose down

echo ""
echo "=========================================="
echo "Services Stopped"
echo "=========================================="
echo ""
echo "All services have been stopped."
echo "Data volumes are preserved."
echo ""
echo "To start again: ./start.sh"
echo "To remove volumes: podman-compose down -v (WARNING: destroys all data)"
echo "=========================================="
