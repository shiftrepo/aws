#!/bin/bash

# Fix for circular import in NL Query Processor modules
echo "=== MCP CIRCULAR IMPORT FIX ==="
echo "Fixing circular import issues in Natural Language Query Processor modules..."

# Check if running in the correct directory
if [[ ! -d "patentDWH/app" ]]; then
  echo "Error: This script should be run from the project root directory containing patentDWH folder."
  exit 1
fi

# Make sure we have the updated code files
if [[ ! -f "patentDWH/app/base_nl_query_processor.py" ]] || \
   [[ ! -f "patentDWH/app/nl_query_processor.py" ]] || \
   [[ ! -f "patentDWH/app/patched_nl_query_processor.py" ]] || \
   [[ ! -f "patentDWH/app/enhanced_nl_query_processor.py" ]]; then
  echo "Error: Required NL query processor Python modules not found."
  exit 1
fi

# Check if the docker-compose service is running
if ! docker ps | grep -q patentdwh-mcp-enhanced; then
  echo "The patentdwh-mcp-enhanced container doesn't appear to be running."
  echo "Starting the MCP service..."
  
  # Check if there's a docker-compose file with enhanced service
  if [[ -f "patentDWH/docker-compose.enhanced.yml" ]]; then
    cd patentDWH && docker-compose -f docker-compose.enhanced.yml up -d
  elif [[ -f "patentDWH/docker-compose.consolidated.yml" ]]; then
    cd patentDWH && docker-compose -f docker-compose.consolidated.yml up -d
  else
    echo "Error: Could not find appropriate docker-compose file to start the service."
    exit 1
  fi
else
  echo "The patentdwh-mcp-enhanced container is already running."
  
  # Copy the fixed files into the running container
  echo "Copying fixed files into the container..."
  docker cp patentDWH/app/base_nl_query_processor.py patentdwh-mcp-enhanced:/app/
  docker cp patentDWH/app/nl_query_processor.py patentdwh-mcp-enhanced:/app/
  docker cp patentDWH/app/patched_nl_query_processor.py patentdwh-mcp-enhanced:/app/
  docker cp patentDWH/app/enhanced_nl_query_processor.py patentdwh-mcp-enhanced:/app/
  
  # Restart the container to apply changes
  echo "Restarting the patentdwh-mcp-enhanced container..."
  docker restart patentdwh-mcp-enhanced
fi

echo "Waiting for service to start..."
sleep 5

# Check if the service is responding to health checks
echo "Checking MCP service health..."
for i in {1..10}; do
  if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo "MCP service is now running and healthy!"
    exit 0
  elif [ $i -eq 10 ]; then
    echo "MCP service health check failed after multiple attempts."
    echo "Check container logs for more information:"
    echo "  docker logs patentdwh-mcp-enhanced"
    exit 1
  else
    echo "Waiting for service to become healthy... (attempt $i)"
    sleep 3
  fi
done
