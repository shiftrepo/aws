#!/bin/bash
# Infrastructure Status Script
# This script checks the status of all infrastructure services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Infrastructure Service Status"
echo "=========================================="
echo ""

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed"
    exit 1
fi

# Show container status
echo "Container Status:"
echo "----------------------------------------"
podman-compose ps
echo ""

# Check individual service health
echo "Service Health Checks:"
echo "----------------------------------------"

# PostgreSQL
if podman exec orgmgmt-postgres pg_isready -U orgmgmt_user &> /dev/null; then
    echo "✓ PostgreSQL:  HEALTHY"
else
    echo "✗ PostgreSQL:  UNHEALTHY or not running"
fi

# Redis
if podman exec argocd-redis redis-cli ping &> /dev/null; then
    echo "✓ Redis:       HEALTHY"
else
    echo "✗ Redis:       UNHEALTHY or not running"
fi

# ArgoCD Server
if curl -sf http://localhost:5010/healthz &> /dev/null; then
    echo "✓ ArgoCD:      HEALTHY"
else
    echo "✗ ArgoCD:      UNHEALTHY or not ready"
fi

# GitLab
if curl -sf http://localhost:5003/-/health &> /dev/null; then
    echo "✓ GitLab:      HEALTHY"
else
    echo "✗ GitLab:      UNHEALTHY or not ready (may still be initializing)"
fi

# Nexus
if curl -sf http://localhost:8081/service/rest/v1/status &> /dev/null; then
    echo "✓ Nexus:       HEALTHY"
else
    echo "✗ Nexus:       UNHEALTHY or not ready"
fi

# pgAdmin (just check if port is responding)
if curl -sf http://localhost:5050 &> /dev/null; then
    echo "✓ pgAdmin:     HEALTHY"
else
    echo "✗ pgAdmin:     UNHEALTHY or not running"
fi

echo ""
echo "=========================================="
echo "Access URLs:"
echo "----------------------------------------"
echo "PostgreSQL:    localhost:5432"
echo "pgAdmin:       http://localhost:5050"
echo "Nexus:         http://localhost:8081"
echo "GitLab:        http://localhost:5003"
echo "ArgoCD:        http://localhost:5010"
echo "=========================================="
echo ""
echo "To view logs: podman-compose logs -f [service-name]"
echo ""
