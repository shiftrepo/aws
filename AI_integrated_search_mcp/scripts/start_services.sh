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

# Check if AWS credentials are available from environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "ERROR: AWS credentials not found in environment variables."
  echo "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION environment variables before running this script."
  exit 1
fi

echo "AWS region: $AWS_DEFAULT_REGION"

# Add AWS region to .env file if not already there
if ! grep -q "^AWS_DEFAULT_REGION=" .env; then
  echo "AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION" >> .env
fi

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Environment variables loaded from .env file"
fi

# Stop and remove any existing containers with the same names
echo "Cleaning up any existing containers..."
for CONTAINER in "${DATABASE_CONTAINER:-sqlite-db}" "${NL_QUERY_CONTAINER:-nl-query-service}" "${WEBUI_CONTAINER:-web-ui}"
do
  if podman ps -a | grep -q "$CONTAINER"; then
    echo "Removing existing container: $CONTAINER"
    podman rm -f "$CONTAINER" 2>/dev/null || true
  fi
done

# Define data directory path
DATA_DIR="$ROOT_DIR/db/data"

# Download databases if needed
echo "Checking for database files..."
bash ./scripts/download_databases.sh

# Ensure data directory exists and has proper permissions
if [ ! -d "$DATA_DIR" ]; then
  echo "Creating data directory: $DATA_DIR"
  mkdir -p "$DATA_DIR"
fi

# Set directory permissions more carefully
echo "Setting directory permissions..."
# Only change permissions for directories and files we can actually modify
find "$DATA_DIR" -type d -exec chmod 755 {} \; 2>/dev/null || true
find "$DATA_DIR" -type f -name "*.db" -exec chmod 644 {} \; 2>/dev/null || true

# Create a dedicated network for the containers if it doesn't exist
echo "Ensuring dedicated container network exists..."
podman network exists mcp-network 2>/dev/null || podman network create mcp-network

# Skip podman-compose build which was causing issues
echo "Building images directly instead of using podman-compose..."

echo "Building and running containers individually to avoid dependency issues..."

# Build individual images directly without using local registry
echo "Building database image..."
podman build -t sqlite-db-image:latest "$ROOT_DIR/db"

echo "Starting database container..."
podman run -d --name "${DATABASE_CONTAINER:-sqlite-db}" \
  --network mcp-network \
  -p "${DATABASE_API_PORT:-5003}:5000" \
  -v "$ROOT_DIR/db/data:/app/data:Z" \
  --user "$(id -u):$(id -g)" \
  -e "INPUT_DB_S3_PATH=${INPUT_DB_S3_PATH}" \
  -e "BIGQUERY_DB_S3_PATH=${BIGQUERY_DB_S3_PATH}" \
  -e "LOG_LEVEL=DEBUG" \
  -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \
  sqlite-db-image:latest

echo "Waiting for database container to initialize (15s)..."
sleep 15

# Build NL Query image
echo "Building NL Query image..."
podman build -t nl-query-image:latest "$ROOT_DIR/app/nl-query"

# Start NL Query container
echo "Starting NL Query container..."
podman run -d --name "${NL_QUERY_CONTAINER:-nl-query-service}" \
  --network mcp-network \
  -p "${NL_QUERY_API_PORT:-5004}:5000" \
  --user "$(id -u):$(id -g)" \
  -e "DATABASE_API_URL=http://${DATABASE_CONTAINER:-sqlite-db}:5000" \
  -e "LOG_LEVEL=DEBUG" \
  -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \
  nl-query-image:latest

# Build Web UI image
echo "Building Web UI image..."
podman build -t web-ui-image:latest "$ROOT_DIR/app/webui"

# Start Web UI container
echo "Starting Web UI container..."
podman run -d --name "${WEBUI_CONTAINER:-web-ui}" \
  --network mcp-network \
  -p "${WEBUI_PORT:-5002}:5000" \
  --user "$(id -u):$(id -g)" \
  -e "DATABASE_API_URL=http://${DATABASE_CONTAINER:-sqlite-db}:5000" \
  -e "NL_QUERY_API_URL=http://${NL_QUERY_CONTAINER:-nl-query-service}:5000" \
  -e "LOG_LEVEL=DEBUG" \
  -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \
  -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \
  -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \
  web-ui-image:latest

# Build Trend Analysis image
echo "Building Trend Analysis image..."
podman build -t trend-analysis-image:latest "$ROOT_DIR/app/trend-analysis"

# Create credentials directory if it doesn't exist
echo "Setting up credentials directory for Trend Analysis..."
mkdir -p "$ROOT_DIR/app/trend-analysis/credentials"

# Start Trend Analysis container
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
echo "Running health check..."
bash "$ROOT_DIR/scripts/check_health.sh"
