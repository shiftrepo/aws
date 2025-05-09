#!/bin/bash
set -e

# Path to SQLite database
DB_PATH="/app/data/inpit.db"
CSV_PATH="/app/data/plidb_bulkdata_202503.csv"
GOOGLE_PATENTS_GCP_DB_PATH="/app/data/google_patents_gcp.db"
GOOGLE_PATENTS_S3_DB_PATH="/app/data/google_patents_s3.db"

echo "Starting container..."

# Print current user information
echo "Running as $(id -un) (UID: $(id -u), GID: $(id -g))"

# Ensure data directory exists
mkdir -p /app/data

# Define S3 source paths for Google Patents databases
S3_BUCKET="ndi-3supervision"
S3_KEY="MIT/demo/GCP/bak/google_patents.db"
S3_SQLITE_DB_PATH="s3://$S3_BUCKET/$S3_KEY"

echo "Database paths:"
echo "- Inpit Database: $DB_PATH"
echo "- GCP Database: $GOOGLE_PATENTS_GCP_DB_PATH"
echo "- S3 Local Database: $GOOGLE_PATENTS_S3_DB_PATH"
echo "- S3 Source Path: $S3_SQLITE_DB_PATH"

# Download all necessary data from S3
echo "Downloading data from S3..."
python /app/download_data.py

# Check if the INPIT CSV file was downloaded successfully
if [ ! -f "/app/data/plidb_bulkdata_202503.csv" ]; then
    echo "Failed to download INPIT data from S3."
    # Continue anyway as we might still have the Google Patents databases
fi

# Verify Google Patents database files
echo "Checking Google Patents database files:"
if [ -f "$GOOGLE_PATENTS_S3_DB_PATH" ]; then
    echo "- S3 database file exists: $GOOGLE_PATENTS_S3_DB_PATH"
    ls -la "$GOOGLE_PATENTS_S3_DB_PATH"
else
    echo "- S3 database file missing: $GOOGLE_PATENTS_S3_DB_PATH"
fi

if [ -f "$GOOGLE_PATENTS_GCP_DB_PATH" ]; then
    echo "- GCP database file exists: $GOOGLE_PATENTS_GCP_DB_PATH"
    ls -la "$GOOGLE_PATENTS_GCP_DB_PATH"
else
    echo "- GCP database file missing: $GOOGLE_PATENTS_GCP_DB_PATH"
fi

# Make sure all data files are readable
if [ -f "$CSV_PATH" ]; then
    echo "Setting permissions on CSV file"
    # Try to make the CSV file readable by all
    touch "$CSV_PATH" 2>/dev/null || echo "Cannot touch CSV file - continuing anyway"
fi

# Set permissions on database files to ensure they're accessible by the web UI
for db_file in "$GOOGLE_PATENTS_GCP_DB_PATH" "$GOOGLE_PATENTS_S3_DB_PATH"; do
    if [ -f "$db_file" ]; then
        echo "Setting permissions on database file: $db_file"
        chmod 666 "$db_file" 2>/dev/null || echo "Cannot set permissions on database file: $db_file - continuing anyway"
    fi
done

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
