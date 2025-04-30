#!/bin/bash

# Inpit SQLite MCP Server Startup Script

echo "Starting Inpit SQLite MCP Server..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    # Activate virtual environment
    source venv/bin/activate
    echo "Activated virtual environment"
else
    echo "Virtual environment not found. Running setup script first..."
    ./setup.sh
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Change to app directory
cd app

# Start the server
echo "Starting MCP server..."
python server.py
