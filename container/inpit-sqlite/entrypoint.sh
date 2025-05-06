#!/bin/bash
set -e

# Path to SQLite database
DB_PATH="/app/data/inpit.db"
CSV_PATH="/app/data/plidb_bulkdata_202503.csv"

echo "Starting container..."

# Print current user information
echo "Running as $(id -un) (UID: $(id -u), GID: $(id -g))"

# Ensure data directory exists
mkdir -p /app/data

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

# Make sure CSV file is readable
if [ -f "$CSV_PATH" ]; then
    echo "Setting permissions on CSV file"
    # Try to make the CSV file readable by all
    touch "$CSV_PATH" 2>/dev/null || echo "Cannot touch CSV file - continuing anyway"
fi

# Create schema and import data
echo "Creating schema and importing data..."
python /app/schema.py

# Make sure database file is accessible if it exists
if [ -f "$DB_PATH" ]; then
    echo "Setting permissions on database file"
    # Try to make the database file readable and writable by all
    touch "$DB_PATH" 2>/dev/null || echo "Cannot touch DB file - continuing anyway"
fi

# Start SQLite Web UI
echo "Starting SQLite Web UI on port 5001..."
cd /app && python app.py

# This line will not be reached when running Flask directly
# Keep container running
exec "$@"
