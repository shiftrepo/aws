#!/bin/bash

# Patent Analysis MCP Server startup script
# This script starts the FastAPI-based patent analysis MCP server that uses SQLite and LLM

# Display banner
echo "======================================================"
echo "  Patent Analysis MCP Server Startup"
echo "======================================================"
echo ""

# Podman-compose前提でセットアップ
CONTAINER_RUNTIME="podman"
COMPOSE_CMD="podman-compose"
COMPOSE_FILE="podman-compose.yml"
echo "Using Podman and podman-compose with $COMPOSE_FILE"

# podman-composeが利用可能か確認
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed or not in PATH"
    echo "Please install podman-compose first"
    exit 1
fi

# podmanが利用可能か確認
if ! command -v podman &> /dev/null; then
    echo "ERROR: podman is not installed or not in PATH"
    echo "Please install podman first"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p ./output
chmod 777 ./output

# Create data directory for SQLite if it doesn't exist
mkdir -p ../app/patent_system/data
chmod 777 ../app/patent_system/data

# Clean up any previous container instances 
echo "Cleaning up any previous container instances..."
$CONTAINER_RUNTIME stop patent-analysis-mcp 2>/dev/null || true
$CONTAINER_RUNTIME rm -f patent-analysis-mcp 2>/dev/null || true

# If the compose command is not available, fall back to direct container commands
if ! command -v $COMPOSE_CMD &> /dev/null; then
    echo "WARNING: $COMPOSE_CMD not found, will use direct $CONTAINER_RUNTIME commands"
    COMPOSE_CMD=""
fi

if [ -n "$COMPOSE_CMD" ]; then
    $COMPOSE_CMD -f docker-compose.mcp.yml down 2>/dev/null || true
fi

# Make sure required environment variables are set (without exposing values)
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "WARNING: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY environment variables are not set."
    echo "These are required for the server to function properly."
    echo "Please set these environment variables before starting the server:"
    echo "export AWS_ACCESS_KEY_ID=your_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "export AWS_DEFAULT_REGION=your_region  # Optional, defaults to us-east-1"
fi

# Build the container with the latest changes
echo "Building the Patent Analysis MCP server..."
$COMPOSE_CMD -f $COMPOSE_FILE build

# ネットワークの確認と作成
echo "Checking for required networks..."
if ! $CONTAINER_RUNTIME network ls | grep -q "patentdwh_default"; then
    echo "Creating patentdwh_default network..."
    $CONTAINER_RUNTIME network create patentdwh_default
    echo "Network patentdwh_default created."
else
    echo "Network patentdwh_default already exists."
fi

# Start the MCP server
echo "Starting the Patent Analysis MCP server with podman-compose..."
$COMPOSE_CMD -f $COMPOSE_FILE up -d

# Check if the server started correctly
if [ $? -eq 0 ]; then
    echo ""
    echo "Patent Analysis MCP Server is starting..."
    echo "API is available at: http://localhost:8000"
    echo ""
    echo "Available endpoints:"
    echo "  - GET  /                           - Health check"
    echo "  - GET  /docs                       - Swagger API documentation"
    echo "  - GET  /openapi.json               - OpenAPI schema for Dify integration"
    echo "  - POST /api/v1/mcp                 - MCP compatible endpoint"
    echo "  - POST /api/tools/execute          - Dify compatible endpoint"
    echo "  - POST /api/analyze                - Analyze patent trends (JSON)"
    echo "  - GET  /api/report/{applicant_name} - Get report in markdown format"
    echo "  - GET  /api/report/{applicant_name}/zip - Get report as zip file"
    echo ""
    echo "コンテナ接続性テストを実行するには:"
    echo "./test_container_connectivity.sh"
    echo ""
    echo "詳細なPodman使用ガイドは以下を参照してください:"
    echo "README_PODMAN_USAGE.md"
    echo ""
    echo "Example CURL commands:"
    echo "  curl -X POST http://localhost:8000/api/v1/mcp -H 'Content-Type: application/json' \\"
    echo "      -d '{\"tool_name\":\"analyze_patent_trends\",\"tool_input\":{\"applicant_name\":\"トヨタ\"}}'"
    echo ""
    echo "  curl -X POST http://localhost:8000/api/tools/execute -H 'Content-Type: application/json' \\"
    echo "      -d '{\"tool_name\":\"analyze_patent_trends\",\"arguments\":{\"applicant_name\":\"トヨタ\"}}'"
    echo ""
    echo "  curl -X GET http://localhost:8000/api/report/トヨタ/zip -o toyota_report.zip"
    echo ""
    echo "NOTE: Please ensure the SQLite database at ../app/patent_system/data/patents.db"
    echo "contains patent data before using the API."
else
    echo ""
    echo "ERROR: Failed to start the Patent Analysis MCP server"
    echo "Check the logs for more information:"
    echo "  $COMPOSE_CMD -f $COMPOSE_FILE logs"
    exit 1
fi

exit 0
