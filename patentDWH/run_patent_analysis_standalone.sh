#!/bin/bash
# Comprehensive script to run patent analysis system standalone
# Usage: ./run_patent_analysis_standalone.sh "トヨタ" inpit

# Get command line arguments
APPLICANT_NAME="$1"
DB_TYPE="${2:-inpit}"

echo "===== Patent Analysis System: Standalone Mode ====="
echo "Applicant: $APPLICANT_NAME"
echo "Database type: $DB_TYPE"

# Step 1: Clean up environment
echo "Cleaning up existing containers..."
podman stop -a 2>/dev/null || true
sleep 2
podman rm -f $(podman ps -a -q) 2>/dev/null || true
sleep 2

# Step 2: Make sure we're using the fixed patent analyzer script
echo "Installing fixed patent analyzer script..."
cp ../patent_analysis_container/patent_trend_analyzer.fixed.py ../patent_analysis_container/patent_trend_analyzer.py

# Step 3: Set proper permissions for output directory
echo "Setting output directory permissions..."
mkdir -p ../patent_analysis_container/output 2>/dev/null || true
chmod 777 ../patent_analysis_container/output

# Step 4: Start the DB container first
echo "Starting DB container..."
podman run -d \
  --name patentdwh-db \
  -v "$(pwd)/data:/app/data:z" \
  -e PORT=5002 \
  -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
  -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
  -e AWS_DEFAULT_REGION="${AWS_REGION:-ap-northeast-1}" \
  -e SKIP_DATA_DOWNLOAD=false \
  -u root:root \
  --network=host \
  $(podman build -q ./db)

# Wait for DB to be ready
echo "Waiting for DB to initialize..."
sleep 5

# Step 5: Start the MCP Enhanced container
echo "Starting MCP Enhanced container..."
podman run -d \
  --name patentdwh-mcp-enhanced \
  -v "$(pwd)/data:/app/data:z" \
  -v "$(pwd)/data/db:/app/data/db:z" \
  -e PORT=8080 \
  -e PATENT_DB_URL=http://localhost:5002 \
  -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
  -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
  -e AWS_REGION="${AWS_REGION:-us-east-1}" \
  -e GCP_CREDENTIALS_S3_BUCKET=ndi-3supervision \
  -e GCP_CREDENTIALS_S3_KEY=MIT/GCPServiceKey/tosapi-bf0ac4918370.json \
  -u root:root \
  --network=host \
  $(podman build -q -f app/Dockerfile.enhanced app)

# Wait for MCP to be ready
echo "Waiting for MCP Enhanced to initialize..."
sleep 10

# Step 6: Build and run the patent analysis container
echo "Building patent analysis container..."
cd ../patent_analysis_container
PATENT_ANALYSIS_IMAGE=$(podman build -q .)

echo "Running patent analysis..."
podman run --rm \
  -v "$(pwd)/output:/app/output:z" \
  -e MCP_URL=http://localhost:8080/api/v1/mcp \
  -e DB_URL=http://localhost:5002/api/sql-query \
  -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
  -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
  -e AWS_REGION="${AWS_REGION:-us-east-1}" \
  -u root:root \
  --network=host \
  --name patent-analysis \
  $PATENT_ANALYSIS_IMAGE "$APPLICANT_NAME" "$DB_TYPE"

echo "===== Patent Analysis Completed ====="
echo "Check the output directory: ../patent_analysis_container/output/"

# Optionally stop the supporting containers
read -p "Do you want to stop the DB and MCP containers? (y/n): " STOP_CONTAINERS
if [[ $STOP_CONTAINERS == "y" || $STOP_CONTAINERS == "Y" ]]; then
  echo "Stopping containers..."
  podman stop patentdwh-mcp-enhanced patentdwh-db
fi
