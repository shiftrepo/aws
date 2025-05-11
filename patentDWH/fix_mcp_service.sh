#!/bin/bash

# Fix and restart the patentDWH MCP enhanced service
# Addresses issues with LangChain compatibility and networking

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Fixing and restarting patentDWH MCP enhanced service"

# Change to the patentDWH directory
cd "$(dirname "$0")"

# Stop the running containers
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Stopping existing containers"
podman-compose -f docker-compose.consolidated.yml stop patentdwh-mcp-enhanced

# Rebuild the enhanced MCP container
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Rebuilding the enhanced MCP container with updated requirements"
podman-compose -f docker-compose.consolidated.yml build --no-cache patentdwh-mcp-enhanced

# Restart the enhanced MCP service
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting the enhanced MCP service"
podman-compose -f docker-compose.consolidated.yml up -d patentdwh-mcp-enhanced

# Wait for service to start
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Waiting for service to start"
sleep 5

# Check service status
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking service status"
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health || echo "failed")
  
  if [ "$RESPONSE" = "200" ]; then
    SUCCESS=true
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP service is now running successfully"
    curl -s http://localhost:8080/health | jq '.'
  else
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Waiting for service to become available (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
  fi
done

if [ "$SUCCESS" = false ]; then
  echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - MCP service failed to start properly after $MAX_RETRIES attempts"
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Check logs with: podman-compose -f docker-compose.consolidated.yml logs -f patentdwh-mcp-enhanced"
  exit 1
fi

# Check database connectivity
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Testing database connectivity"
RESPONSE=$(curl -s http://localhost:8080/health | jq -r '.database_connected')

if [ "$RESPONSE" = "true" ]; then
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Database connectivity confirmed"
else
  echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Database connectivity issue detected. The MCP service is running but may have trouble connecting to the database."
fi

# Check AWS configuration
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking AWS configuration"
RESPONSE=$(curl -s http://localhost:8080/api/aws-status)
AWS_CONFIGURED=$(echo "$RESPONSE" | jq -r '.success')

if [ "$AWS_CONFIGURED" = "true" ]; then
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - AWS credentials correctly configured for Bedrock services"
else
  echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - AWS credentials not properly configured. Natural language queries will not work correctly."
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Please ensure AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION environment variables are correctly set."
fi

echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Fix process completed."
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You can access the MCP service at: http://localhost:8080/"
