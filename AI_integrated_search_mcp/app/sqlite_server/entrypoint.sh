#!/bin/bash

set -e

# Enable detailed logging
echo "Starting SQLite Database Service $(date)"

# Create necessary directories
mkdir -p /app/data/db

# Set environment variables if not set
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"ap-northeast-1"}
export S3_DB_BUCKET=${S3_DB_BUCKET:-"your-bucket-name"}
export S3_DB_KEY=${S3_DB_KEY:-"path/to/your/db.sqlite"}

echo "Configured with AWS region: $AWS_DEFAULT_REGION"
echo "S3 Bucket: $S3_DB_BUCKET"
echo "S3 DB Key: $S3_DB_KEY"

# Download the database from S3
echo "Downloading database file from S3: s3://$S3_DB_BUCKET/$S3_DB_KEY"
aws s3 cp s3://$S3_DB_BUCKET/$S3_DB_KEY /app/data/db/database.sqlite || {
    echo "WARNING: Failed to download database from S3. Creating a test database instead."
    echo "Running init_test_db.py to create sample data..."
    python /app/init_test_db.py
    if [ $? -eq 0 ]; then
        echo "Test database created successfully."
    else
        echo "Failed to create test database. Creating an empty database instead."
        touch /app/data/db/database.sqlite
        sqlite3 /app/data/db/database.sqlite "PRAGMA journal_mode=WAL;"
    fi
}

# Set permissions
echo "Setting database file permissions"
chmod 666 /app/data/db/database.sqlite

echo "Database ready. Starting SQLite API server..."

# Start the FastAPI server
exec uvicorn main:app --host 0.0.0.0 --port 5001 --log-level debug
