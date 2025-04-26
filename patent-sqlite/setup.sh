#!/bin/bash

# Setup script for patent-sqlite container system

# Create necessary directories
mkdir -p service-key data

# Download GCP service account key from S3
echo "Attempting to download GCP service account key from S3..."
aws s3 cp s3://ndi-3supervision/MIT/GCPServiceKey/tosapi-bd19ecc6f5bb.json ./service-key/tosapi-bd19ecc6f5bb.json

# Check if download was successful
if [ $? -ne 0 ]; then
    echo "WARNING: Could not download GCP service account key from S3."
    echo "You will need to place the service account key manually in ./service-key/tosapi-bd19ecc6f5bb.json"
    echo "Using dummy key file for demonstration purposes..."
    # No need to copy dummy key as we already created it in service-key directory
else
    echo "Service account key downloaded successfully."
fi

# Check for container management tools and build/start the container
echo "Building and starting containers..."

# Use docker compose which is available on this system (uses podman-compose under the hood)
docker compose up -d --build
CONTAINER_EXIT_CODE=$?

# If it fails, try alternative commands
if [ $CONTAINER_EXIT_CODE -ne 0 ]; then
    echo "Trying alternative container commands..."
    
    # Check if podman-compose is available directly
    if command -v podman-compose &> /dev/null; then
        podman-compose up -d --build
        CONTAINER_EXIT_CODE=$?
    # Check if docker-compose is available
    elif command -v docker-compose &> /dev/null; then
        docker-compose up -d --build
        CONTAINER_EXIT_CODE=$?
    else
        echo "ERROR: Failed to find a working container composition tool."
        echo "Please install either podman-compose or docker-compose to continue."
        exit 1
    fi
fi

# Check if container was started successfully
if [ $CONTAINER_EXIT_CODE -ne 0 ]; then
    echo "ERROR: Failed to start containers."
    exit 1
fi

# Wait for the application to start
echo "Waiting for the application to start..."
sleep 5

# Initialize the database
echo "Initializing the patent database..."
curl -s http://localhost:5000/init

echo ""
echo "Setup complete! Your patent SQLite container is now running."
echo ""
echo "To import patent data, use:"
echo "  curl -X POST http://localhost:5000/import -H \"Content-Type: application/json\" -d '{\"theme\": \"G06F\"}'"
echo ""
echo "To query patent data, use:"
echo "  curl \"http://localhost:5000/patents?theme=G06F\""
echo ""
echo "To check database status, use:"
echo "  curl http://localhost:5000/status"
echo ""
