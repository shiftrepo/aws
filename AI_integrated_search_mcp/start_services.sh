#!/bin/bash

# AI Integrated Search MCP - Start Services Script
# This script starts all the containers for the AI SQLite search system

set -e

echo "===== AI Integrated Search MCP ====="
echo "Starting services at $(date)"

# Check if running as root, as required for podman
if [ "$(id -u)" -ne 0 ]; then
    echo "WARNING: This script needs to be run as root for podman"
    echo "Adding 'sudo' to commands"
    SUDO="sudo"
else
    SUDO=""
fi

# Check if AWS environment variables are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "ERROR: AWS credentials not found in environment variables"
    echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
    echo "For example:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key_id"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_access_key"
    echo "  export AWS_DEFAULT_REGION=ap-northeast-1"
    exit 1
fi

echo "AWS credentials found in environment variables"
echo "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-ap-northeast-1}"
echo ""

# Check if S3 bucket and key are set
if [ -z "$S3_DB_BUCKET" ] || [ -z "$S3_DB_KEY" ]; then
    echo "WARNING: S3 database location not specified"
    echo "Using default values, which may not work properly"
    echo "To set specific S3 location:"
    echo "  export S3_DB_BUCKET=your-s3-bucket"
    echo "  export S3_DB_KEY=path/to/your/db.sqlite"
    echo ""
fi

# Create the necessary directories
mkdir -p data/sqlite data/nl_query data/web_ui

# Check if podman-compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "ERROR: podman-compose is not installed"
    echo "Please install podman-compose first"
    exit 1
fi

echo "Starting containers using podman-compose..."
$SUDO podman-compose -f podman-compose.yml up --build -d

echo "Waiting for services to be ready..."
sleep 5

echo "Checking service health..."

# Function to check if service is up
check_service() {
    local name=$1
    local url=$2
    local max_attempts=$3
    local attempt=1

    echo -n "Checking $name... "
    while [ $attempt -le $max_attempts ]; do
        if $SUDO podman-compose -f podman-compose.yml exec web-ui curl -s -o /dev/null -w "%{http_code}" $url | grep -q "200"; then
            echo "UP"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "DOWN"
    return 1
}

# Check each service
check_service "SQLite API" "http://sqlite-db:5001/health" 10
check_service "NL Query MCP API" "http://nl-query-mcp:8000/health" 10
check_service "Web UI" "http://web-ui:5002/health" 5

echo ""
echo "Services are running!"
echo "Web UI is available at: http://localhost:5002"
echo ""
echo "To stop services, run: ./stop_services.sh"
