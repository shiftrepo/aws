#!/bin/bash

echo "Rebuilding SQLite Database Service"
echo "=================================="

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print status messages
status() {
  echo -e "${YELLOW}[STATUS]${NC} $1"
}

success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Make sure the database files exist and have correct permissions
status "Ensuring database files exist and have correct permissions"
chmod 644 db/data/*.db || echo "Could not set permissions, continuing anyway"

# Step 2: Stop the current database container
status "Stopping the current database container"
podman stop sqlite-db || echo "No container to stop"

# Step 3: Remove the container
status "Removing the container"
podman rm sqlite-db || echo "No container to remove"

# Step 4: Rebuild the service
status "Rebuilding the database service"
podman-compose build sqlite-db
success "Database service rebuilt"

# Step 5: Start the service
status "Starting the database service"
podman-compose up -d sqlite-db
success "Database service started"

# Step 6: Wait for container to start
status "Waiting for container to start up..."
sleep 10

# Step 7: Apply fix script inside container
status "Applying fix script inside container"
podman exec sqlite-db python /app/fix_db_paths.py || echo "Failed to run fix script, but continuing"

# Step 8: Check container health
status "Checking container status"
CONTAINER_STATUS=$(podman inspect sqlite-db --format '{{.State.Status}}')
echo "Container status: $CONTAINER_STATUS"

# Step 9: Test health endpoint
status "Testing health endpoint"
echo "Attempting to connect to health endpoint..."
sleep 3
curl -v http://localhost:5003/health

echo "=================================="
echo "Database service rebuild completed"
echo "Run the health check script to verify all services are working:"
echo "./scripts/check_health.sh"
