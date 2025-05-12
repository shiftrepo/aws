#!/bin/bash

# Script to rebuild and restart services with US Claude 3.7 Sonnet configuration

set -e

echo "=== Rebuilding AI Integrated Search MCP Services with US Claude 3.7 Configuration ==="

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

# Load environment variables for the ports
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "1. Stopping all services if they're running..."
podman-compose down || true

echo "2. Creating data directory for database files..."
mkdir -p db/data
chmod 777 db/data

echo "3. Rebuilding all services..."
podman-compose build

echo "4. Starting the database service first to download files..."
podman-compose up -d sqlite-db

echo "5. Waiting for database service to initialize and download files (30s)..."
for i in {1..30}; do
  echo -n "."
  sleep 1
done
echo ""

echo "6. Starting remaining services..."
podman-compose up -d

echo "7. Waiting for all services to initialize (20s)..."
for i in {1..20}; do
  echo -n "."
  sleep 1
done
echo ""

echo "8. Checking AWS Bedrock configuration..."
python3 test_bedrock.py

echo "9. Services status:"
podman-compose ps

echo "All services have been rebuilt and restarted with US Claude 3.7 Sonnet configuration."
echo "Health check URLs:"
echo "Database Service: http://localhost:${DATABASE_API_PORT}/health"
echo "NL Query Service: http://localhost:${NL_QUERY_API_PORT}/health"
echo "LangChain Query Service: http://localhost:${LANGCHAIN_QUERY_API_PORT}/health"
echo "Web UI: http://localhost:${WEBUI_PORT}"
