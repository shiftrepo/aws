#!/bin/bash

# Script to rebuild just the webui service following the architecture in README.md
set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

echo "=== Rebuilding WebUI Service ==="

echo "1. Building web-ui service from local Dockerfile..."
cd app/webui
podman build -t ai_integrated_search_mcp_web-ui:local .
cd ../../

echo "2. Stopping any existing web-ui container..."
podman stop web-ui || true
podman rm web-ui || true

echo "3. Starting the web-ui service with the newly built image..."
podman run -d --name web-ui \
  --network=$(podman network ls | grep mcp-network | head -1 | awk '{print $2}') \
  -p 5002:5000 \
  -e DATABASE_API_URL=http://sqlite-db:5000 \
  -e NL_QUERY_API_URL=http://nl-query-service:5000 \
  -e LANGCHAIN_QUERY_API_URL=http://langchain-query-service:5000 \
  -e LOG_LEVEL=DEBUG \
  $(env | grep "AWS_" | sed 's/^/-e /') \
  -u "1000:1000" \
  localhost/ai_integrated_search_mcp_web-ui:local

echo "WebUI service has been rebuilt and restarted."
echo "You can access the Web UI at http://localhost:5002"
echo "You can check the web-ui logs with:"
echo "podman logs web-ui"
