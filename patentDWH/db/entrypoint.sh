#!/bin/bash
set -e

# Set up proper permissions for data directory
mkdir -p /app/data
chmod 777 /app/data

echo "Starting Patent DWH Database server..."

# Check if we should skip data download
if [ "${SKIP_DATA_DOWNLOAD}" != "true" ]; then
    echo "Downloading data from S3..."
    python /app/download_data.py
else
    echo "Skipping data download (SKIP_DATA_DOWNLOAD=true)"
fi

# Start the web server
echo "Starting Flask web server..."
exec python /app/app.py
