#!/bin/bash
set -e

echo "Starting Patent DWH MCP Server..."

# Run the FastAPI server using Uvicorn
exec uvicorn server:app --host 0.0.0.0 --port 8080
