#!/bin/bash

# Apply MCP fix for the 404 errors in patentDWH service
# This script applies all the necessary changes to fix the MCP 404 errors

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting MCP 404 fix application"

# First, make sure all scripts are executable
chmod +x fix_mcp_404_error.sh
chmod +x db/patched_entrypoint.sh

# Check if patch files are in the right places
if [ ! -f "db/mcp_endpoint_patch.py" ]; then
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - MCP endpoint patch file is missing"
    exit 1
fi

if [ ! -f "db/patched_entrypoint.sh" ]; then
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Patched entrypoint script is missing"
    exit 1
fi

if [ ! -f "docker-compose.consolidated.patched.yml" ]; then
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Patched docker-compose file is missing"
    exit 1
fi

# Determine which container runtime to use
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
    COMPOSE_CMD="podman-compose"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
    COMPOSE_CMD="docker-compose"
else
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Neither Docker nor Podman is installed"
    exit 1
fi

# Stop all services
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Stopping all services"
./stop_all_services.sh

# Ensure AWS credentials are set properly
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking AWS credentials"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - AWS credentials not found in environment"
    
    # Try to load from ~/.aws/credentials
    if [ -f ~/.aws/credentials ]; then
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Loading AWS credentials from ~/.aws/credentials"
        export AWS_ACCESS_KEY_ID=$(grep -m 1 'aws_access_key_id' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ')
        export AWS_SECRET_ACCESS_KEY=$(grep -m 1 'aws_secret_access_key' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ')
        export AWS_DEFAULT_REGION=$(grep -m 1 'region' ~/.aws/config 2>/dev/null | cut -d '=' -f 2 | tr -d ' ' || echo "us-east-1")
    else
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - No AWS credentials found"
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Some functionality may be limited"
    fi
fi

# Make sure AWS_DEFAULT_REGION is set
if [ -z "$AWS_DEFAULT_REGION" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Setting default AWS region to us-east-1"
    export AWS_DEFAULT_REGION="us-east-1"
fi

# Check LangChain versions in requirements file
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking LangChain requirements"
if grep -q "langchain>=0.1.0" ./app/requirements_enhanced.txt && \
   grep -q "langchain-community>=0.0.13" ./app/requirements_enhanced.txt; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - LangChain requirements are properly set"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Updating LangChain requirements"
    sed -i 's/^langchain==.*$/langchain>=0.1.0/' ./app/requirements_enhanced.txt
    sed -i 's/^langchain-community==.*$/langchain-community>=0.0.13/' ./app/requirements_enhanced.txt
    
    # Add entries if they don't exist
    if ! grep -q "langchain" ./app/requirements_enhanced.txt; then
        echo "langchain>=0.1.0" >> ./app/requirements_enhanced.txt
    fi
    if ! grep -q "langchain-community" ./app/requirements_enhanced.txt; then
        echo "langchain-community>=0.0.13" >> ./app/requirements_enhanced.txt
    fi
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - LangChain requirements updated"
fi

# Run the MCP fix script
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Running the MCP fix script"
./fix_mcp_404_error.sh

# Check if services are running
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking service status"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health | grep -q "200"; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP service is running successfully"
else
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - MCP service may not be running properly"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking logs"
    $COMPOSE_CMD -f docker-compose.consolidated.patched.yml logs --tail 20 patentdwh-mcp-enhanced
fi

# Test the MCP endpoint directly
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Testing MCP endpoint"
MCP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" \
    -d '{"tool_name":"get_schema_info","tool_input":{"db_type":"inpit"}}' \
    http://localhost:5002/api/v1/mcp)

if [ "$MCP_RESPONSE" = "200" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Database MCP endpoint is working correctly"
else
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Database MCP endpoint may not be working, status: $MCP_RESPONSE"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - This might need further troubleshooting"
fi

echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP fix application completed"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You can access the services at:"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP service: http://localhost:8080/"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Patent Analysis MCP API: http://localhost:8000/"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Database web interface: http://localhost:5002/"
