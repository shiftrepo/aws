#!/bin/bash

# Start the patent MCP server
# This script starts the FastAPI server using uvicorn

echo "Starting Patent MCP Server..."

# Check if we're in the correct directory
if [ ! -f "app/server.py" ]; then
    echo "Error: app/server.py not found. Make sure you're in the patent-mcp-server directory."
    exit 1
fi

# Export Python path to include parent directory for imports
export PYTHONPATH=$PYTHONPATH:$(dirname $(pwd))

# Start the server using uvicorn
echo "Launching server on http://localhost:8000"
cd app
python3 server.py

# Note: If the above doesn't work, try:
# cd app
# uvicorn server:app --host 0.0.0.0 --port 8000 --reload
