#!/bin/bash
# Infrastructure Startup Script
# This script starts all infrastructure services using podman-compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Starting Infrastructure Services"
echo "=========================================="
echo ""

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed"
    echo "Please install it first: pip3 install podman-compose"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Copying .env.example to .env"
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env and update the passwords before using in production!"
    echo ""
fi

# Create gitops directory if it doesn't exist
if [ ! -d gitops ]; then
    echo "Creating gitops directory for ArgoCD..."
    mkdir -p gitops
fi

# Start services
echo "Starting all services..."
podman-compose up -d

echo ""
echo "=========================================="
echo "Services Starting..."
echo "=========================================="
echo ""
echo "This may take several minutes, especially on first run."
echo "GitLab can take 5-10 minutes to fully initialize."
echo ""

# Wait a few seconds
sleep 5

# Show status
echo "Service Status:"
podman-compose ps

echo ""
echo "=========================================="
echo "Access Information"
echo "=========================================="
echo ""
echo "PostgreSQL:    localhost:5432"
echo "pgAdmin:       http://localhost:5050"
echo "Nexus:         http://localhost:8081"
echo "GitLab:        http://localhost:5003"
echo "ArgoCD:        http://localhost:5010"
echo ""
echo "Default credentials are in the .env file"
echo ""
echo "To view logs: podman-compose logs -f"
echo "To stop:      podman-compose down"
echo ""
echo "For more information, see README.md"
echo "=========================================="
