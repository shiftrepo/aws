#!/bin/bash

source ./.env

# Set error handling
set -e

echo "========================================================"
echo "     Quick Start Trend Analysis Container Script        "
echo "========================================================"

echo "Building trend-analysis container..."
cd app/trend-analysis

# Build the image directly with podman
podman build -t trend-analysis-image .

echo "Running trend-analysis container..."
# First remove any existing container
podman rm -f trend-analysis-service 2>/dev/null || true

# Create and run the container
podman run -d \
  --name trend-analysis-service \
  --network=mcp-network \
  -p 5006:5000 \
  -e DATABASE_API_URL=http://sqlite-db:5000 \
  -e LOG_LEVEL=DEBUG \
  -e MPLCONFIGDIR=/tmp/.matplotlib \
  --tmpfs /tmp:rw,exec,mode=1777 \
  trend-analysis-image

echo "Container started!"
echo "Checking health status..."
sleep 5  # Give it some time to start

# Check if the container is running
if podman ps | grep -q trend-analysis-service; then
  echo "Container is running."
  
  # Try to check health status
  HEALTH_CHECK=$(podman exec trend-analysis-service curl -s http://localhost:5000/health || echo "Failed to connect to health endpoint")
  
  if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo "Health check passed: $HEALTH_CHECK"
  else
    echo "Health check failed or returned unexpected result"
    echo "Output: $HEALTH_CHECK"
    echo "Container logs:"
    podman logs trend-analysis-service
  fi
else
  echo "Container is not running!"
  echo "Container logs:"
  podman logs trend-analysis-service
fi

echo "========================================================"
echo "Service URL: http://localhost:5006"
echo "========================================================"
