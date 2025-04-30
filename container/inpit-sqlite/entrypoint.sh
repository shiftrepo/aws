#!/bin/bash
set -e

# Path to SQLite database
DB_PATH="/app/data/inpit.db"
CSV_PATH="/app/data/plidb_bulkdata_202503.csv"

echo "Starting container..."

# Ensure data directory has proper permissions
mkdir -p /app/data
chmod 777 /app/data

# Check if the data file needs to be copied from the mounted volume
if [ -f "/app/data/plidb_bulkdata_202503.csv" ]; then
    echo "CSV file found in data directory"
else
    # Try to download data from S3
    echo "Attempting to download data from S3..."
    python /app/download_data.py
    
    # Check if download was successful
    if [ ! -f "/app/data/plidb_bulkdata_202503.csv" ]; then
        echo "Failed to download data from S3. Exiting."
        exit 1
    fi
fi

# Create schema and import data
echo "Creating schema and importing data..."
chmod 666 "$CSV_PATH" || true

python /app/schema.py

# Ensure database file is accessible
chmod 666 "$DB_PATH" || true

# Start SQLite Web UI
echo "Starting SQLite Web UI on port 5001..."
cd /app && python app.py

# This line will not be reached when running Flask directly
# Keep container running
exec "$@"
