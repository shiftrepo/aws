#!/bin/bash

set -e

# Enable detailed logging
echo "Starting Web UI Service $(date)"

# Create necessary directories
mkdir -p /app/data/cache

# Log configuration
echo "SQLite API URL: $SQLITE_API_URL"
echo "MCP API URL: $MCP_API_URL"

# Wait for SQLite API to be ready
echo "Waiting for SQLite API to be available at $SQLITE_API_URL"
until $(curl --output /dev/null --silent --head --fail $SQLITE_API_URL/health); do
    echo "Waiting for SQLite API..."
    sleep 5
done

# Wait for MCP API to be ready
echo "Waiting for MCP API to be available at $MCP_API_URL"
until $(curl --output /dev/null --silent --head --fail $MCP_API_URL/health); do
    echo "Waiting for MCP API..."
    sleep 5
done

echo "All required services are available. Starting Web UI..."

# Start the FastAPI server for Web UI
exec uvicorn main:app --host 0.0.0.0 --port 5002 --log-level debug
