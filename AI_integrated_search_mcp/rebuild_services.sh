#!/bin/bash

# Script to rebuild and restart services with updated dependencies

set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

# Load environment variables for the ports
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "=== AI Integrated Search MCP Service Rebuild ==="
echo "This script will rebuild services with updated dependencies and restore proper functionality."

echo "1. Stopping all services if they're running..."
podman-compose down || true

echo "2. Rebuilding sqlite-db service..."
podman-compose build sqlite-db

echo "3. Rebuilding nl-query-service with updated boto3..."
podman-compose build nl-query-service

echo "4. Rebuilding langchain-query-service with updated boto3..."
podman-compose build langchain-query-service

echo "5. Creating data directory for database files..."
mkdir -p db/data
chmod 777 db/data

echo "6. Starting the database service first to download files..."
podman-compose up -d sqlite-db

echo "7. Waiting for database service to initialize and download files (30s)..."
for i in {1..30}; do
  echo -n "."
  sleep 1
done
echo ""

echo "8. Starting remaining services..."
podman-compose up -d

echo "9. Waiting for all services to initialize (20s)..."
for i in {1..20}; do
  echo -n "."
  sleep 1
done
echo ""

echo "10. Checking service status..."
echo "Database service logs:"
podman logs $(podman ps -qf name=sqlite-db) | tail -n 20
echo ""

echo "NL Query service logs:"
podman logs $(podman ps -qf name=nl-query-service) | tail -n 20
echo ""

echo "All services have been rebuilt and restarted with updated boto3 and botocore versions."

echo "Health check URLs:"
echo "Database Service: http://localhost:${DATABASE_API_PORT}/health"
echo "NL Query Service: http://localhost:${NL_QUERY_API_PORT}/health"
echo "LangChain Query Service: http://localhost:${LANGCHAIN_QUERY_API_PORT}/health"
echo "Web UI: http://localhost:${WEBUI_PORT}"

echo "You can run the health check script to verify all services:"
echo "./scripts/check_health.sh"
