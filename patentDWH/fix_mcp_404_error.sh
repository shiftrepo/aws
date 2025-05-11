#!/bin/bash

# Fix script for patentDWH MCP service 404 errors
# This script addresses the 404 errors seen when accessing /api/v1/mcp endpoint

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting fix for MCP 404 errors"

# First, let's stop all services to ensure a clean state
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Stopping all services"
./stop_all_services.sh || true

# Detect container runtime and compose command
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
    COMPOSE_CMD="podman-compose"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
    COMPOSE_CMD="docker-compose"
else
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - No container runtime found (docker or podman)"
    exit 1
fi

# Ensure network exists
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Ensuring network exists"
$CONTAINER_RUNTIME network exists patentdwh_default &>/dev/null || $CONTAINER_RUNTIME network create patentdwh_default

# Start the database service first
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting database service"
$COMPOSE_CMD -f docker-compose.consolidated.patched.yml up -d patentdwh-db

# Give the database time to initialize
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Waiting for database to initialize"
sleep 5

# Check if database is accessible
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Testing database connectivity"
if curl -s "http://localhost:5002/health" | grep -q "healthy"; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Database is running and responding to health checks"
else
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Database may not be fully initialized, continuing anyway"
fi

# Make sure LangChain requirements are properly set
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking LangChain requirements"
if grep -q "langchain>=0.1.0" ./app/requirements_enhanced.txt && \
   grep -q "langchain-community>=0.0.13" ./app/requirements_enhanced.txt; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - LangChain requirements look good"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Updating LangChain requirements"
    sed -i 's/langchain==.*/langchain>=0.1.0/' ./app/requirements_enhanced.txt
    sed -i 's/langchain-community==.*/langchain-community>=0.0.13/' ./app/requirements_enhanced.txt
    
    # Add entries if they don't exist
    grep -q "langchain" ./app/requirements_enhanced.txt || echo "langchain>=0.1.0" >> ./app/requirements_enhanced.txt
    grep -q "langchain-community" ./app/requirements_enhanced.txt || echo "langchain-community>=0.0.13" >> ./app/requirements_enhanced.txt
    
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - LangChain requirements updated"
fi

# Make sure we're using the proper import fallback in the enhanced_nl_query_processor.py
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for import fallback mechanism"
if grep -q "try:" ./app/enhanced_nl_query_processor.py && \
   grep -q "from langchain_community.llms.bedrock import Bedrock" ./app/enhanced_nl_query_processor.py && \
   grep -q "except ImportError:" ./app/enhanced_nl_query_processor.py; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Import fallback mechanism is already in place"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Adding import fallback mechanism"
    # Create a backup
    cp ./app/enhanced_nl_query_processor.py ./app/enhanced_nl_query_processor.py.bak
    
    # Replace the import statement
    sed -i 's/from langchain.llms.bedrock import Bedrock/try:\n    from langchain_community.llms.bedrock import Bedrock\nexcept ImportError:\n    # Fall back to old import path if needed\n    try:\n        from langchain.llms.bedrock import Bedrock\n    except ImportError:\n        logging.error("Failed to import Bedrock from langchain. Ensure langchain and langchain-community are properly installed.")/' ./app/enhanced_nl_query_processor.py
    
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Import fallback mechanism added"
fi

# Start the MCP service
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting MCP enhanced service"
$COMPOSE_CMD -f docker-compose.consolidated.patched.yml up -d patentdwh-mcp-enhanced

# Give it some time to start
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Waiting for MCP service to start"
sleep 10

# Check if MCP service is running
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking MCP service status"
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" = false ]; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health || echo "failed")
  
  if [ "$RESPONSE" = "200" ]; then
    SUCCESS=true
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP service is now running successfully"
    curl -s http://localhost:8080/health
  else
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Waiting for service to become available (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
  fi
done

if [ "$SUCCESS" = false ]; then
  echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - MCP service failed to start properly after $MAX_RETRIES attempts"
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Check the logs with: $COMPOSE_CMD -f docker-compose.consolidated.patched.yml logs -f patentdwh-mcp-enhanced"
  $COMPOSE_CMD -f docker-compose.consolidated.patched.yml logs --tail 20 patentdwh-mcp-enhanced
else
  # Start the patent analysis MCP service
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting patent analysis MCP service"
  $COMPOSE_CMD -f docker-compose.consolidated.patched.yml up -d patent-analysis-mcp
  
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Fix applied successfully"
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You can access the MCP service at: http://localhost:8080/"
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You can access the Patent Analysis MCP API at: http://localhost:8000/"
fi
