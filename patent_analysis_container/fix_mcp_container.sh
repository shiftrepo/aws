#!/bin/bash

# This script fixes the patent-analysis-mcp container by ensuring it properly connects
# to the patentDWH services network.

echo "======================================================"
echo "  Patent Analysis MCP Container Fix Script"
echo "======================================================"
echo ""

# Detect container runtime (Docker or Podman)
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
    echo "Using Podman as container runtime"
    
    if command -v podman-compose &> /dev/null; then
        COMPOSE_CMD="podman-compose"
        echo "Found podman-compose command"
    else
        echo "podman-compose not found, will use native podman commands"
        COMPOSE_CMD=""
    fi
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        echo "Found docker-compose command"
    else
        echo "docker-compose not found, will use native docker commands"
        COMPOSE_CMD=""
    fi
else
    echo "ERROR: Neither Docker nor Podman is installed or in PATH"
    echo "Please install Docker or Podman first"
    exit 1
fi

# Create necessary directories
mkdir -p ./output
chmod 777 ./output

# Make sure required environment variables are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "WARNING: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY environment variables are not set."
    echo "These are required for the server to function properly."
    echo "Please set these environment variables before starting the server."
    
    # Load AWS credentials if they're in the standard ~/.aws/credentials file
    if [ -f ~/.aws/credentials ]; then
        echo "Found AWS credentials file. Attempting to load credentials..."
        export AWS_ACCESS_KEY_ID=$(grep -m 1 'aws_access_key_id' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ')
        export AWS_SECRET_ACCESS_KEY=$(grep -m 1 'aws_secret_access_key' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ')
        export AWS_DEFAULT_REGION=$(grep -m 1 'region' ~/.aws/credentials | cut -d '=' -f 2 | tr -d ' ' || echo "us-east-1")
        
        if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
            echo "Successfully loaded AWS credentials from ~/.aws/credentials"
        fi
    fi
fi

# 必要なネットワークを確認・作成
NETWORK_NAME="patentdwh_default"
if ! $CONTAINER_RUNTIME network exists $NETWORK_NAME &>/dev/null; then
    echo "ネットワーク $NETWORK_NAME が存在しないため、作成します"
    $CONTAINER_RUNTIME network create $NETWORK_NAME
    if [ $? -ne 0 ]; then
        echo "ネットワーク $NETWORK_NAME の作成に失敗しました"
        exit 1
    fi
    echo "ネットワーク $NETWORK_NAME を作成しました"
else
    echo "既存のネットワーク $NETWORK_NAME を使用します"
fi

# Stop and remove the current container
echo "Stopping and removing the current container..."
$CONTAINER_RUNTIME stop patent-analysis-mcp 2>/dev/null || true
$CONTAINER_RUNTIME rm -f patent-analysis-mcp 2>/dev/null || true
$COMPOSE_CMD -f docker-compose.mcp.yml down 2>/dev/null || true

# Rebuild and start the container with the updated configuration
echo "Building and starting the container with the updated network configuration..."

if [ -n "$COMPOSE_CMD" ]; then
    # If we have a compose command, use it
    $COMPOSE_CMD -f docker-compose.mcp.yml up -d --build
else
    # If no compose command is available, do manual container creation
    echo "No compose command available, using direct container commands..."
    
    # Make sure we have an image
    if [ -n "$(podman images | grep patent-analysis-mcp)" ]; then
        echo "Using existing image for patent-analysis-mcp"
    else
        echo "Building image from Dockerfile.mcp..."
        $CONTAINER_RUNTIME build -t patent-analysis-mcp -f Dockerfile.mcp .
    fi
    
    echo "Creating and starting container..."
    
    # Check if the patentdwh_default network exists
    if $CONTAINER_RUNTIME network exists patentdwh_default &>/dev/null; then
        echo "Using existing patentdwh_default network"
        $CONTAINER_RUNTIME run -d --name patent-analysis-mcp \
            --network patentdwh_default \
            -e LLM_SERVICE_URL=http://patentdwh-mcp-enhanced:8080/api/v1/mcp \
            -e DB_URL=http://patentdwh-db:5002/api/sql-query \
            -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
            -e HOST=0.0.0.0 -e PORT=8000 \
            -e OUTPUT_DIR=/app/output \
            -e DATABASE_PATH=/app/app/patent_system/data/patents.db \
            -p 8000:8000 \
            -v "$PWD/output:/app/output" \
            --restart unless-stopped \
            patent-analysis-mcp
    else
        echo "patentdwh_default network doesn't exist, creating standalone container"
        $CONTAINER_RUNTIME run -d --name patent-analysis-mcp \
            -e LLM_SERVICE_URL=http://patentdwh-mcp-enhanced:8080/api/v1/mcp \
            -e DB_URL=http://patentdwh-db:5002/api/sql-query \
            -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
            -e HOST=0.0.0.0 -e PORT=8000 \
            -e OUTPUT_DIR=/app/output \
            -e DATABASE_PATH=/app/app/patent_system/data/patents.db \
            -p 8000:8000 \
            -v "$PWD/output:/app/output" \
            --restart unless-stopped \
            patent-analysis-mcp
    fi
fi

# Check if the container started successfully
if $CONTAINER_RUNTIME ps | grep patent-analysis-mcp | grep -q "Up "; then
    echo ""
    echo "SUCCESS: Patent Analysis MCP Container is now running properly!"
    echo "API is available at: http://localhost:8000"
    echo ""
    echo "To test the API, you can use:"
    echo "  curl http://localhost:8000/"
    echo ""
    echo "To run an analysis:"
    echo "  curl -X POST http://localhost:8000/api/v1/mcp -H 'Content-Type: application/json' \\"
    echo "      -d '{\"tool_name\":\"analyze_patent_trends\",\"tool_input\":{\"applicant\":\"トヨタ\"}}'"
    echo ""
else
    echo ""
    echo "ERROR: Failed to start the Patent Analysis MCP Container"
    echo "Check the logs for more information:"
    echo "  $CONTAINER_RUNTIME logs patent-analysis-mcp"
    exit 1
fi

exit 0
