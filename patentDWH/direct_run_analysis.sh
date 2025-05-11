#!/bin/bash

# This script directly runs the patent analyzer with fixed issues
# Usage: ./direct_run_analysis.sh "Company Name" [db_type]

APPLICANT_NAME="$1"
DB_TYPE="${2:-inpit}"

echo "Direct patent analysis for: $APPLICANT_NAME using $DB_TYPE database"

# Stop and remove any existing containers
echo "Cleaning up existing containers..."
podman stop -a 2>/dev/null || true
podman rm -f $(podman ps -a -q) 2>/dev/null || true

# Make sure we're using the fixed patent analyzer script
echo "Updating patent analyzer script..."
cp ../patent_analysis_container/patent_trend_analyzer.fixed.py ../patent_analysis_container/patent_trend_analyzer.py

# Set proper permissions for output directory
echo "Setting output directory permissions..."
mkdir -p ../patent_analysis_container/output 2>/dev/null || true
chmod 777 ../patent_analysis_container/output

# Build the patent analysis container directly (uses the updated script)
echo "Building patent analysis container..."
cd ../patent_analysis_container
podman build -t patent-analysis:latest .

# Run the patent analysis directly
echo "Running patent analysis..."
podman run --rm \
  -v "$(pwd)/output:/app/output:z" \
  -e MCP_URL=http://localhost:8080/api/v1/mcp \
  -e DB_URL=http://localhost:5002/api/sql-query \
  --name patent-analysis \
  patent-analysis:latest "$APPLICANT_NAME" "$DB_TYPE"

echo "Analysis completed. Check ../patent_analysis_container/output/ for results."
