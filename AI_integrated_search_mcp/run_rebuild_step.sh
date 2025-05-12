#!/bin/bash

cd /root/aws.git/AI_integrated_search_mcp

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Step 1: Stop any running containers
echo "Stopping any running containers..."
podman-compose down || true

# Step 2: Build the database service
echo "Building sqlite-db service..."
podman-compose build sqlite-db
if [ $? -ne 0 ]; then
  echo "Failed to build sqlite-db service"
  exit 1
fi

# Step 3: Build nl-query-service
echo "Building nl-query-service..."
podman-compose build nl-query-service
if [ $? -ne 0 ]; then
  echo "Failed to build nl-query-service"
  exit 1
fi

# Step 4: Build langchain-query-service
echo "Building langchain-query-service..."
podman-compose build langchain-query-service
if [ $? -ne 0 ]; then
  echo "Failed to build langchain-query-service"
  exit 1
fi

# Step 5: Start database service
echo "Starting database service..."
podman-compose up -d sqlite-db
if [ $? -ne 0 ]; then
  echo "Failed to start sqlite-db service"
  exit 1
fi

echo "Waiting 30 seconds for database service to initialize..."
sleep 30

# Step 6: Start remaining services
echo "Starting remaining services..."
podman-compose up -d
if [ $? -ne 0 ]; then
  echo "Failed to start all services"
  exit 1
fi

echo "All services have been rebuilt and started."
echo "Database service: http://localhost:${DATABASE_API_PORT}/health"
echo "NL Query service: http://localhost:${NL_QUERY_API_PORT}/health"
echo "LangChain Query service: http://localhost:${LANGCHAIN_QUERY_API_PORT}/health"
echo "Web UI: http://localhost:${WEBUI_PORT}"

exit 0
