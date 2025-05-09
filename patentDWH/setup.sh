#!/bin/bash
set -e

echo "=============================="
echo "patentDWH - Patent Database Setup"
echo "=============================="

# Check for podman or docker
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo "Using Podman for containerization"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker compose"
    echo "Using Docker for containerization"
else
    echo "Error: Neither podman nor docker found. Please install one of them."
    exit 1
fi

echo "Creating necessary directories..."
mkdir -p data/db

echo "Building and starting containers..."
$COMPOSE_CMD build
$COMPOSE_CMD up -d

echo "Waiting for services to start..."
sleep 5

echo "Checking database service..."
if curl -s "http://localhost:5002/health" | grep -q "healthy"; then
    echo "Database service is running!"
else
    echo "Warning: Database service may not be running properly. Please check the logs."
fi

echo "Checking MCP service..."
if curl -s "http://localhost:8080/health" | grep -q "healthy"; then
    echo "MCP service is running!"
else
    echo "Warning: MCP service may not be running properly. Please check the logs."
fi

echo "=============================="
echo "Setup complete!"
echo ""
echo "Access the database UI:   http://localhost:5002/"
echo "Access the MCP API:       http://localhost:8080/"
echo ""
echo "MCP configuration for Claude:"
echo '{
  "serverName": "patentDWH",
  "description": "Patent DWH MCP Server",
  "url": "http://localhost:8080/api/v1/mcp"
}'
echo ""
echo "To view logs:"
echo "$COMPOSE_CMD logs -f"
echo ""
echo "To stop services:"
echo "$COMPOSE_CMD down"
echo "=============================="
