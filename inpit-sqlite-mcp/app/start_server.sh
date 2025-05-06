#!/bin/bash
# Script to start the inpit-sqlite-mcp server with proper encoding handling

echo "Starting Inpit SQLite MCP Server..."
echo "This version supports direct use of non-ASCII characters in URLs"
echo "For example: http://localhost:8000/applicant/テック株式会社"
echo ""

# Set environment variables if needed
# export INPIT_API_URL=http://localhost:5001

# Start the server
cd /app
python server.py
