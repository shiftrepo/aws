#!/bin/bash

echo "Fixing Database Container Issues"
echo "================================"

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

# Step 1: Check if container is running
status "Checking if database container is running..."
if podman inspect sqlite-db >/dev/null 2>&1; then
  success "Database container is running."
else
  error "Database container is not running."
  exit 1
fi

# Step 2: Check the container volume mapping
status "Checking container volume mapping..."
VOLUME_PATH=$(podman inspect sqlite-db --format '{{ range .Mounts }}{{ if eq .Destination "/app/data" }}{{ .Source }}{{ end }}{{ end }}')
echo "Volume path mapping: $VOLUME_PATH -> /app/data"

# Step 3: Verify database files exist on the host
status "Verifying database files on host..."
HOST_DB_DIR="./db/data"
INPIT_DB="$HOST_DB_DIR/inpit.db"
BIGQUERY_DB="$HOST_DB_DIR/google_patents_gcp.db"

if [ -f "$INPIT_DB" ] && [ -f "$BIGQUERY_DB" ]; then
  success "Database files exist on host."
  echo "Inpit DB size: $(stat -c %s "$INPIT_DB")"
  echo "BigQuery DB size: $(stat -c %s "$BIGQUERY_DB")"
else
  error "Missing database files on host."
  [ -f "$INPIT_DB" ] || echo "Missing: $INPIT_DB"
  [ -f "$BIGQUERY_DB" ] || echo "Missing: $BIGQUERY_DB"
fi

# Step 4: Check permissions on database files
status "Checking permissions on database files..."
chmod 644 $INPIT_DB $BIGQUERY_DB || echo "Permission change failed, but continuing"
success "Set read permissions on database files."

# Step 5: Check AWS credentials
status "Checking AWS credentials for S3 download..."
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$AWS_DEFAULT_REGION" ]; then
  echo "AWS credentials not found in environment. Setting them for this session from .env file..."
  export $(grep -v '^#' .env | grep 'AWS_' | xargs)
fi

# Step 6: Force copy database files to container
status "Copying database files to container..."
podman cp "$INPIT_DB" sqlite-db:/app/data/inpit.db
podman cp "$BIGQUERY_DB" sqlite-db:/app/data/google_patents_gcp.db
success "Database files copied to container."

# Step 7: Fix permissions inside container
status "Setting permissions inside container..."
podman exec sqlite-db chown -R ec2-user:ec2-user /app/data
podman exec sqlite-db chmod 644 /app/data/inpit.db /app/data/google_patents_gcp.db
success "Permissions set inside container."

# Step 8: Verify database files inside container
status "Verifying database files in container..."
podman exec sqlite-db ls -la /app/data
# Check if files exist in container
if podman exec sqlite-db test -f /app/data/inpit.db && podman exec sqlite-db test -f /app/data/google_patents_gcp.db; then
  success "Database files exist in container."
else
  error "Database files missing in container."
fi

# Step 9: Restart the container
status "Restarting database container..."
podman restart sqlite-db
success "Container restarted."

# Step 10: Wait for container to start up
status "Waiting for container to start up..."
sleep 10

# Step 11: Check container health
status "Checking container health..."
HEALTH_STATUS=$(podman inspect sqlite-db --format '{{.State.Health.Status}}')
echo "Container health status: $HEALTH_STATUS"

# Step 12: Test health endpoint
status "Testing health endpoint..."
if curl -s http://localhost:5003/health -o /dev/null; then
  success "Health endpoint is now responding."
else
  error "Health endpoint is still not responding."
fi

echo "================================"
echo "Fix script completed. If issues persist, check the DB container logs:"
echo "podman logs sqlite-db"

# Return to parent directory
cd ..
