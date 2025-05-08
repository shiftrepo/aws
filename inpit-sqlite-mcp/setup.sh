#!/bin/bash

# Inpit SQLite MCP Server Setup Script
# This script sets up the Inpit SQLite MCP Server for use with Claude

echo "Setting up Inpit SQLite MCP Server..."

# Check for required AWS environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "ERROR: AWS credentials not found in environment variables."
    echo "Please set the following environment variables:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "Setup aborted."
    exit 1
fi

echo "AWS credentials found in environment variables."

# Create necessary directories before running podman-compose
echo "Creating required directories..."
mkdir -p ./data-inpit-sqlite/db
mkdir -p ./data-inpit-sqlite-mcp/db

# Set correct ownership and permissions for container user (ec2-user)
echo "Setting proper permissions on data directories..."
chown -R ec2-user:ec2-user ./data-inpit-sqlite
chown -R ec2-user:ec2-user ./data-inpit-sqlite-mcp
chmod -R 775 ./data-inpit-sqlite
chmod -R 775 ./data-inpit-sqlite-mcp

# Run podman-compose to build and start the containers
echo "Starting services with podman-compose..."
podman-compose -f podman-compose.yml up -d

echo "Setup complete!"
echo ""
echo "The MCP server is now running in containers:"
echo "- inpit-sqlite: http://localhost:5001"
echo "- inpit-sqlite-mcp: http://localhost:8000"
echo ""
echo "All library installations and application executions are performed inside the containers."
echo "No additional setup is required on the host system."
echo ""
echo "For Claude integration:"
echo "Update your Claude configuration to include this MCP server."
