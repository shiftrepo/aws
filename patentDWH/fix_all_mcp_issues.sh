#!/bin/bash

# Comprehensive fix script for patentDWH MCP service startup issues
# This script addresses:
# 1. Network connectivity between containers
# 2. LangChain compatibility issues
# 3. AWS credential configuration

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting comprehensive MCP service fix"

# Detect container runtime
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Using Podman as container runtime"
    
    if command -v podman-compose &> /dev/null; then
        COMPOSE_CMD="podman-compose"
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Found podman-compose command"
    else
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - podman-compose not found, will use native podman commands"
        COMPOSE_CMD=""
    fi
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Found docker-compose command"
    else
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - docker-compose not found, will use native docker commands"
        COMPOSE_CMD=""
    fi
else
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Neither Docker nor Podman is installed or in PATH"
    exit 1
fi

# Step 1: Stop all services
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Stopping all services"
./stop_all_services.sh

# Step 2: Fix network issues
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for required network"
NETWORK_NAME="patent-network"
EXTERNAL_NETWORK_NAME="patentdwh_default"

if ! $CONTAINER_RUNTIME network exists $EXTERNAL_NETWORK_NAME &>/dev/null; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Creating network $EXTERNAL_NETWORK_NAME"
    $CONTAINER_RUNTIME network create $EXTERNAL_NETWORK_NAME
    if [ $? -ne 0 ]; then
        echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Failed to create network $EXTERNAL_NETWORK_NAME"
        exit 1
    fi
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Network $EXTERNAL_NETWORK_NAME created successfully"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Using existing network $EXTERNAL_NETWORK_NAME"
fi

# Step 3: Check AWS credentials
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking AWS credentials"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - AWS credentials not set in environment variables"
    
    # Try to load from ~/.aws/credentials
    if [ -f ~/.aws/credentials ]; then
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Found AWS credentials file, attempting to load"
        export AWS_ACCESS_KEY_ID=$(grep -m 1 'aws_access_key_id' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ')
        export AWS_SECRET_ACCESS_KEY=$(grep -m 1 'aws_secret_access_key' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ')
        export AWS_DEFAULT_REGION=$(grep -m 1 'region' ~/.aws/config 2>/dev/null | cut -d '=' -f 2 | tr -d ' ' || echo "us-east-1")
        
        if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
            echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Successfully loaded AWS credentials"
        else
            echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Could not load AWS credentials"
            echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Natural language query features may not work properly"
            echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Continuing without AWS credentials"
        fi
    else
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - No AWS credentials file found"
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Natural language query features may not work properly"
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Continuing without AWS credentials"
    fi
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - AWS credentials are set in environment variables"
fi

# Make sure AWS_DEFAULT_REGION is set - required by some components
if [ -z "$AWS_DEFAULT_REGION" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Setting AWS_DEFAULT_REGION to us-east-1"
    export AWS_DEFAULT_REGION="us-east-1"
fi

# Step 4: Apply FastAPI middleware import fix
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for FastAPI middleware import issue"

if [ -f "./fix_fastapi_middleware_import.sh" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Applying FastAPI middleware import fix..."
    ./fix_fastapi_middleware_import.sh || echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - FastAPI middleware fix failed but continuing"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for FastAPI middleware import in server_with_enhanced_nl.py"
    if grep -q "from fastapi.middleware.base import BaseHTTPMiddleware" "./app/server_with_enhanced_nl.py"; then
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Applying manual middleware import fix"
        cp "./app/server_with_enhanced_nl.py" "./app/server_with_enhanced_nl.py.bak"
        sed -i 's/from fastapi\.middleware\.base import BaseHTTPMiddleware/from starlette.middleware.base import BaseHTTPMiddleware/' "./app/server_with_enhanced_nl.py"
        
        # Add starlette to requirements if not present
        if ! grep -q "starlette>=" "./app/requirements_enhanced.txt"; then
            echo "starlette>=0.27.0" >> "./app/requirements_enhanced.txt"
        fi
        
        echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - Fixed FastAPI middleware import"
    else
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - No FastAPI middleware import issue detected"
    fi
fi

# Step 5: Apply LangChain fix
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for LangChain compatibility in requirements_enhanced.txt"

# Make sure the requirements file has the correct versions
LANGCHAIN_VERSIONS_OK=false
if grep -q "langchain>=0.1.0" ./app/requirements_enhanced.txt && \
   grep -q "langchain-community>=0.0.13" ./app/requirements_enhanced.txt; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - LangChain versions are correctly set"
    LANGCHAIN_VERSIONS_OK=true
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Updating LangChain versions in requirements_enhanced.txt"
    # Create a backup
    cp ./app/requirements_enhanced.txt ./app/requirements_enhanced.txt.bak
    
    # Update the requirements file
    sed -i 's/^langchain==.*$/langchain>=0.1.0/' ./app/requirements_enhanced.txt
    sed -i 's/^langchain-community==.*$/langchain-community>=0.0.13/' ./app/requirements_enhanced.txt
    
    # Add the packages if they don't exist
    if ! grep -q "langchain" ./app/requirements_enhanced.txt; then
        echo "langchain>=0.1.0" >> ./app/requirements_enhanced.txt
    fi
    
    if ! grep -q "langchain-community" ./app/requirements_enhanced.txt; then
        echo "langchain-community>=0.0.13" >> ./app/requirements_enhanced.txt
    fi
fi

# Step 5: Apply Dockerfile missing module fix
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for Dockerfile missing module issue"

if [ -f "./fix_dockerfile_missing_module.sh" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Applying Dockerfile missing module fix..."
    ./fix_dockerfile_missing_module.sh || echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Dockerfile missing module fix failed but continuing"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - No Dockerfile missing module fix script found"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking if base_nl_query_processor.py is missing from Dockerfile.enhanced"
    
    if [ -f "./app/Dockerfile.enhanced" ]; then
        if ! grep -q "COPY base_nl_query_processor.py" "./app/Dockerfile.enhanced"; then
            echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Adding base_nl_query_processor.py to Dockerfile.enhanced"
            # Create backup
            cp "./app/Dockerfile.enhanced" "./app/Dockerfile.enhanced.bak"
            # Add missing file to COPY instructions
            sed -i '/# Copy application files/,/COPY server_with_enhanced_nl.py/ s/COPY enhanced_nl_query_processor.py/COPY base_nl_query_processor.py .\nCOPY enhanced_nl_query_processor.py/' "./app/Dockerfile.enhanced"
            echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - Updated Dockerfile.enhanced to include base_nl_query_processor.py"
        else
            echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - base_nl_query_processor.py is already in Dockerfile.enhanced"
        fi
    else
        echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Dockerfile.enhanced not found, skipping"
    fi
fi

# Step 6: Apply circular import fix
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for circular import issues"

if [ -f "./fix_mcp_circular_import.sh" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Applying circular import fix..."
    ./fix_mcp_circular_import.sh || echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Circular import fix failed but continuing"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - No circular import fix script found, skipping"
fi

# Step 6: Apply import fallback fix in enhanced_nl_query_processor.py
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking for import fallback mechanism"

if grep -q "try:" ./app/enhanced_nl_query_processor.py && \
   grep -q "from langchain_community.llms.bedrock import Bedrock" ./app/enhanced_nl_query_processor.py && \
   grep -q "except ImportError:" ./app/enhanced_nl_query_processor.py; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Import fallback mechanism is already in place"
else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Adding import fallback mechanism to enhanced_nl_query_processor.py"
    # Create a backup
    cp ./app/enhanced_nl_query_processor.py ./app/enhanced_nl_query_processor.py.bak
    
    # Replace the import statement
    sed -i 's/from langchain.llms.bedrock import Bedrock/try:\n    from langchain_community.llms.bedrock import Bedrock\nexcept ImportError:\n    # Fall back to old import path if needed\n    try:\n        from langchain.llms.bedrock import Bedrock\n    except ImportError:\n        logging.error("Failed to import Bedrock from langchain. Ensure langchain and langchain-community are properly installed.")/' ./app/enhanced_nl_query_processor.py
fi

# Step 6: Rebuild and restart the patentdwh-mcp-enhanced service
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Rebuilding and starting patentdwh-mcp-enhanced service"

if [ -n "$COMPOSE_CMD" ]; then
    # Use docker-compose or podman-compose
    $COMPOSE_CMD -f docker-compose.consolidated.yml build --no-cache patentdwh-mcp-enhanced
    $COMPOSE_CMD -f docker-compose.consolidated.yml up -d patentdwh-db
    sleep 5  # Give the DB time to start
    $COMPOSE_CMD -f docker-compose.consolidated.yml up -d patentdwh-mcp-enhanced
else
    # Manual commands if compose is not available
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - No compose command available, manual rebuild may be incomplete"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Please use docker-compose or podman-compose for better reliability"
    
    # Try to do our best with direct container commands
    $CONTAINER_RUNTIME build -t patentdwh-mcp-enhanced ./app -f ./app/Dockerfile.enhanced
    
    # Start the DB service first
    $CONTAINER_RUNTIME run -d --name patentdwh-db \
        --network $EXTERNAL_NETWORK_NAME \
        -p 5002:5002 \
        -e PORT=5002 \
        -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
        -e SKIP_DATA_DOWNLOAD=false \
        -v "./data:/app/data:z" \
        --restart unless-stopped \
        patentdwh-db
    
    sleep 5  # Give the DB time to start
    
    # Start the MCP service
    $CONTAINER_RUNTIME run -d --name patentdwh-mcp-enhanced \
        --network $EXTERNAL_NETWORK_NAME \
        -e PORT=8080 \
        -e PATENT_DB_URL=http://patentdwh-db:5002 \
        -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
        -v "./data:/app/data:z" \
        -v "./data/db:/app/data/db:z" \
        --restart unless-stopped \
        patentdwh-mcp-enhanced
fi

# Step 7: Wait and check if the service is running
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Waiting for MCP service to start"
MAX_RETRIES=30
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
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Check logs with: $COMPOSE_CMD logs -f patentdwh-mcp-enhanced"
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Last 20 lines of logs:"
  $CONTAINER_RUNTIME logs --tail 20 patentdwh-mcp-enhanced
  exit 1
fi

# Step 8: Fix and start patent-analysis-mcp container
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Fixing and starting patent-analysis-mcp container"
cd ../patent_analysis_container && ./fix_mcp_container.sh
cd ../patentDWH

# Step 9: Test connectivity
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Testing container connectivity"
cd ../patent_analysis_container && ./test_container_connectivity.sh
cd ../patentDWH

echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Fix process completed successfully"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You can access the MCP service at: http://localhost:8080/"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You can access the Patent Analysis MCP API at: http://localhost:8000/"
