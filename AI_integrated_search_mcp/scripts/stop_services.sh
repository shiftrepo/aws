#!/bin/bash
# Stop script for AI Integrated Search MCP services

echo "================================================="
echo "Stopping AI Integrated Search MCP Services"
echo "================================================="

# Change to root directory
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Stop services with podman-compose
echo "Stopping services with podman-compose..."
podman-compose -f podman-compose.yml down

# Check if any of our containers are still running
echo "Checking for any remaining containers..."

# Define container names (use defaults if not set)
DATABASE_CONTAINER=${DATABASE_CONTAINER:-sqlite-db}
NL_QUERY_CONTAINER=${NL_QUERY_CONTAINER:-nl-query-service}
WEBUI_CONTAINER=${WEBUI_CONTAINER:-web-ui}
TREND_ANALYSIS_CONTAINER=${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}

for container in "$DATABASE_CONTAINER" "$NL_QUERY_CONTAINER" "$WEBUI_CONTAINER" "$TREND_ANALYSIS_CONTAINER"; do
  if podman ps -a | grep -q "$container"; then
    echo "Found container $container, forcing stop and removal..."
    podman stop "$container" 2>/dev/null || true
    podman rm "$container" 2>/dev/null || true
  fi
done

# Check if any containers are still running on our ports
for port in "${WEBUI_PORT:-5002}" "${DATABASE_API_PORT:-5003}" "${NL_QUERY_API_PORT:-5004}"; do
  if podman ps | grep -q ":$port->"; then
    echo "Warning: There's still a container running on port $port"
  fi
done

echo "================================================="
echo "AI Integrated Search MCP Services Stopped"
echo "================================================="
