#!/bin/bash
# Start script for AI Integrated Search MCP services

echo "================================================="
echo "Starting AI Integrated Search MCP Services"
echo "================================================="

# Set script to exit if any command fails
set -e

# Change to root directory
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Check if source.aws exists and source it if it does
if [ -f ~/.aws/source.aws ]; then
  echo "Sourcing AWS credentials from ~/.aws/source.aws"
  source ~/.aws/source.aws
  echo "AWS credentials sourced. Region: $AWS_REGION"
else
  echo "Warning: AWS credentials file not found at ~/.aws/source.aws"
  echo "Make sure AWS credentials are properly set in environment variables."
fi

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "ERROR: AWS credentials not found in environment variables."
  echo "Please set them before running this script."
  exit 1
fi

echo "AWS region: $AWS_REGION"
echo "Using podman-compose to start services..."

# Start services with podman-compose
echo "Starting services with podman-compose..."
podman-compose -f podman-compose.yml up -d

# Wait for services to start
echo "Waiting for services to start up..."
sleep 10

# Check if services are running
echo "Checking service status..."

# Check database service
if podman ps | grep -q "${DATABASE_CONTAINER:-sqlite-db}"; then
  echo "✓ Database service is running"
else
  echo "✗ Database service failed to start"
  podman logs "${DATABASE_CONTAINER:-sqlite-db}"
fi

# Check NL query service
if podman ps | grep -q "${NL_QUERY_CONTAINER:-nl-query-service}"; then
  echo "✓ Natural Language Query service is running"
else
  echo "✗ Natural Language Query service failed to start"
  podman logs "${NL_QUERY_CONTAINER:-nl-query-service}"
fi

# Check Web UI service
if podman ps | grep -q "${WEBUI_CONTAINER:-web-ui}"; then
  echo "✓ Web UI service is running"
else
  echo "✗ Web UI service failed to start"
  podman logs "${WEBUI_CONTAINER:-web-ui}"
fi

# Print service endpoints
echo ""
echo "Service endpoints:"
echo "Web UI: http://localhost:${WEBUI_PORT:-5002}"
echo "Database API: http://localhost:${DATABASE_API_PORT:-5003}"
echo "NL Query API: http://localhost:${NL_QUERY_API_PORT:-5004}"
echo ""

echo "================================================="
echo "AI Integrated Search MCP Services Started"
echo "================================================="
