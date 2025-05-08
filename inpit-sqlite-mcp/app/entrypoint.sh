#!/bin/bash
# Entrypoint script for inpit-sqlite-mcp container
# This script fetches data from BigQuery and stores it in SQLite on container startup

set -e

echo "=== Starting inpit-sqlite-mcp with BigQuery data import ==="
echo "$(date): Container started"

# Ensure proper permissions for data directory
DATA_DIR="/app/data"
mkdir -p $DATA_DIR
# If running as root, change ownership to ec2-user
if [ "$(id -u)" = "0" ]; then
    echo "Running as root, setting proper permissions for ec2-user"
    chown -R 1000:1000 $DATA_DIR
    # Run the remaining script as ec2-user
    exec su -c "bash $0" ec2-user
    exit 0
fi

echo "Running as $(id -un) ($(id -u):$(id -g))"

# Define database paths - separate paths for GCP and S3 data
GOOGLE_PATENTS_DB_PATH="/app/data/google_patents_gcp.db"
S3_LOCAL_DB_PATH="/app/data/google_patents_s3.db"
S3_SQLITE_DB_PATH="s3://ndi-3supervision/MIT/demo/GCP/google_patents.db"

# Set GCP credentials environment variables for GooglePatentsFetcher class
#export GCP_CREDENTIALS_S3_KEY="MIT/GCPServiceKey/tosapi-bf0ac4918370.json"
export GCP_CREDENTIALS_S3_BUCKET="ndi-3supervision"
export GCP_CREDENTIALS_S3_KEY="MIT/GCPServiceKey/mytest-202601-6d547916bf46.json"

# Note: GCP credentials are automatically downloaded from S3 by the GooglePatentsFetcher class
# using the environment variables defined above

# Create data directory if it doesn't exist
mkdir -p $(dirname "$GOOGLE_PATENTS_DB_PATH")

# Always fetch fresh GCP data on container startup
echo "Creating/Refreshing GCP database on container startup..."

# Remove any existing database file to ensure a fresh start
if [ -f "$GOOGLE_PATENTS_DB_PATH" ]; then
    echo "Removing existing GCP database file..."
    rm -f "$GOOGLE_PATENTS_DB_PATH"
fi

# Import data from BigQuery (GCP credentials will be downloaded from S3 by GooglePatentsFetcher)
echo "Importing patent data from BigQuery..."
python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=5000); print(f'Imported {count} patents from BigQuery')"

if [ $? -eq 0 ]; then
    echo "Successfully imported patent data from BigQuery"
else
    echo "Failed to import patent data from BigQuery"
    # Continue with server startup even if import fails
fi

# Always download fresh SQLite database from S3
echo "Creating/Refreshing S3 database on container startup..."

# Create data directory if it doesn't exist
mkdir -p $(dirname "$S3_LOCAL_DB_PATH")

# Remove any existing database file to ensure a fresh start
if [ -f "$S3_LOCAL_DB_PATH" ]; then
    echo "Removing existing S3 database file..."
    rm -f "$S3_LOCAL_DB_PATH"
fi

# Download SQLite database from S3
echo "Downloading SQLite database from S3..."
aws s3 cp "$S3_SQLITE_DB_PATH" "$S3_LOCAL_DB_PATH"

if [ $? -eq 0 ]; then
    echo "Successfully downloaded SQLite database from S3"
else
    echo "Failed to download SQLite database from S3"
fi

# Start the MCP server
echo "Starting MCP server..."
exec ./start_server.sh
