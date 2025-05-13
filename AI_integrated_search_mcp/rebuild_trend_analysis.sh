#!/bin/bash
# Script to rebuild and restart the Trend Analysis service

echo "================================================="
echo "Rebuilding and Restarting Trend Analysis Service"
echo "================================================="

# Set script to exit if any command fails
set -e

# Change to root directory
cd "$(dirname "$0")"
ROOT_DIR=$(pwd)

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Environment variables loaded from .env file"
fi

# Check if AWS credentials are available from environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "ERROR: AWS credentials not found in environment variables."
  echo "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION environment variables before running this script."
  exit 1
fi

# Check if container is running and stop it
echo "Checking for existing Trend Analysis container..."
if podman ps -a | grep -q "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}"; then
  echo "Stopping and removing existing Trend Analysis container..."
  podman stop "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}" 2>/dev/null || true
  podman rm "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}" 2>/dev/null || true
fi

# Rebuild the image
echo "Building Trend Analysis image..."
podman build -t trend-analysis-image:latest "$ROOT_DIR/app/trend-analysis"

# Create credentials directory if it doesn't exist
echo "Setting up credentials directory..."
mkdir -p "$ROOT_DIR/app/trend-analysis/credentials"

# Check for network
echo "Ensuring dedicated container network exists..."
podman network exists mcp-network 2>/dev/null || podman network create mcp-network

# Run the container
echo "Starting Trend Analysis container..."
podman run -d --name "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}" \
  --network mcp-network \
  -p "${TREND_ANALYSIS_API_PORT:-5006}:5000" \
  --user "$(id -u):$(id -g)" \
  -v "$ROOT_DIR/app/trend-analysis/credentials:/app/credentials:Z" \
  -e "DATABASE_API_URL=http://${DATABASE_CONTAINER:-sqlite-db}:5000" \
  -e "LOG_LEVEL=DEBUG" \
  -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \
  -e "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" \
  trend-analysis-image:latest

echo "Waiting for service to start..."
sleep 5

# Check if the service is running
if podman ps | grep -q "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}"; then
  echo "✓ Trend Analysis service is running"
  
  # Check if the service is responding
  if curl -s -f "http://localhost:${TREND_ANALYSIS_API_PORT:-5006}/health" > /dev/null; then
    echo "✓ Trend Analysis service is responding correctly"
  else
    echo "✗ Trend Analysis service is not responding"
    podman logs "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}"
  fi
else
  echo "✗ Trend Analysis service failed to start"
  podman logs "${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}"
fi

echo ""
echo "Service endpoint:"
echo "Trend Analysis API: http://localhost:${TREND_ANALYSIS_API_PORT:-5006}"
echo ""

echo "================================================="
echo "Trend Analysis Service Rebuild Completed"
echo "================================================="
