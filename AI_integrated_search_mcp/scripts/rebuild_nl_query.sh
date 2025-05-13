#!/bin/bash

# Script to rebuild just the nl-query service following the architecture in README.md
set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

echo "=== Rebuilding NL Query Service ==="

echo "1. Building nl-query service from local Dockerfile..."
cd app/nl-query
podman build -t ai_integrated_search_mcp_nl-query:local .
cd ../../

echo "2. Stopping any existing nl-query service container..."
podman stop nl-query-service || true
podman rm nl-query-service || true

echo "3. Starting the nl-query service with the newly built image..."
podman run -d --name nl-query-service \
  --network=$(podman network ls | grep mcp-network | head -1 | awk '{print $2}') \
  -p 5004:5000 \
  -e DATABASE_API_URL=http://sqlite-db:5000 \
  -e LOG_LEVEL=DEBUG \
  $(env | grep "AWS_" | sed 's/^/-e /') \
  -u "1000:1000" \
  localhost/ai_integrated_search_mcp_nl-query:local

echo "NL Query service has been rebuilt and restarted."
echo "You can access the NL Query API at http://localhost:5004"
echo "You can check the nl-query logs with:"
echo "podman logs nl-query-service"
