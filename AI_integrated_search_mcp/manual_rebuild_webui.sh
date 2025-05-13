#!/bin/bash

# Script to manually rebuild and restart the web-ui service
set -e

# Change to the project directory
cd /root/aws.git/AI_integrated_search_mcp

echo "=== Manually Rebuilding WebUI Service ==="

echo "1. Building web-ui service..."
cd app/webui
podman build -t ai_integrated_search_mcp_web-ui:latest .
cd ../../

echo "2. Stopping any existing web-ui container..."
podman stop web-ui || true
podman rm web-ui || true

echo "3. Starting the web-ui service with the newly built image..."
podman run -d --name web-ui \
  --network=ai_integrated_search_mcp_mcp-network \
  -p 5002:5000 \
  -e DATABASE_API_URL=http://sqlite-db:5000 \
  -e NL_QUERY_API_URL=http://nl-query-service:5000 \
  -e LANGCHAIN_QUERY_API_URL=http://langchain-query-service:5000 \
  -e LOG_LEVEL=DEBUG \
  -u "1000:1000" \
  ai_integrated_search_mcp_web-ui:latest

echo "WebUI service has been rebuilt and restarted."
echo "You can check the web-ui logs with:"
echo "podman logs web-ui"
