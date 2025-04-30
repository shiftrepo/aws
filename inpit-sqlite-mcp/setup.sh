#!/bin/bash

# Inpit SQLite MCP Server Setup Script
# This script sets up the Inpit SQLite MCP Server for use with Claude

echo "Setting up Inpit SQLite MCP Server..."

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv || python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r app/requirements.txt

# Make server.py executable
chmod +x app/server.py

echo "Setup complete!"
echo ""
echo "To run the server:"
echo "1. Ensure the Inpit SQLite service is running (default: http://localhost:5001)"
echo "2. Configure environment variables (optional):"
echo "   export INPIT_API_URL=http://localhost:5001  # Change if your Inpit SQLite service is at a different URL"
echo "   export PORT=8000                          # Change if you want to run the MCP server on a different port"
echo "3. Start the server:"
echo "   source venv/bin/activate"
echo "   cd app && python server.py"
echo ""
echo "For Claude integration:"
echo "Update your Claude configuration to include this MCP server."
