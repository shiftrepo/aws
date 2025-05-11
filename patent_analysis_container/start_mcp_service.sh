#!/bin/bash

# Patent Analysis MCP Server startup script
# This script starts the FastAPI-based patent analysis MCP server that uses SQLite and LLM

# Display banner
echo "======================================================"
echo "  Patent Analysis MCP Server Startup"
echo "======================================================"
echo ""

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "ERROR: Podman is not installed or not in PATH"
    echo "Please install Podman first"
    exit 1
fi

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed or not in PATH"
    echo "Please install podman-compose first"
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
podman-compose -f docker-compose.mcp.yml down 2>/dev/null || true
podman rm -f patent-analysis-mcp 2>/dev/null || true

# Build the container with the latest changes
echo "Building the Patent Analysis MCP server..."
podman-compose -f docker-compose.mcp.yml build

# Start the MCP server
echo "Starting the Patent Analysis MCP server..."
podman-compose -f docker-compose.mcp.yml up -d

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
    echo "  podman-compose -f docker-compose.mcp.yml logs"
    exit 1
fi

exit 0
