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

# Define database path
GOOGLE_PATENTS_DB_PATH="/app/data/google_patents.db"
S3_SQLITE_DB_PATH="s3://ndi-3supervision/MIT/demo/GCP/google_patents.db"

# Note: GCP credentials are automatically downloaded from S3 by the GooglePatentsFetcher class
# The S3 path for GCP credentials is defined in google_patents_fetcher.py:
# s3_bucket = os.environ.get('GCP_CREDENTIALS_S3_BUCKET', 'ndi-3supervision')
# s3_key = os.environ.get('GCP_CREDENTIALS_S3_KEY', 'MIT/GCPServiceKey/tosapi-bf0ac4918370.json')

# Check if database already exists and has data
if [ -f "$GOOGLE_PATENTS_DB_PATH" ]; then
    echo "Checking existing database..."
    DB_SIZE=$(stat -c %s "$GOOGLE_PATENTS_DB_PATH" 2>/dev/null || echo "0")
    
    # If database exists and is larger than 10MB, assume it has data
    if [ "$DB_SIZE" -gt 10485760 ]; then
        echo "Database already exists and contains data. Skipping import."
        echo "To force reimport, remove the database file."
    else
        echo "Database exists but appears to be empty or incomplete."
        echo "Attempting to download SQLite database from S3..."
        
        # Create data directory if it doesn't exist
        mkdir -p $(dirname "$GOOGLE_PATENTS_DB_PATH")
        
        # Download SQLite database from S3
        aws s3 cp "$S3_SQLITE_DB_PATH" "$GOOGLE_PATENTS_DB_PATH"
        
        # Check if S3 download was successful
        if [ $? -eq 0 ]; then
            echo "Successfully downloaded SQLite database from S3"
            DB_SIZE=$(stat -c %s "$GOOGLE_PATENTS_DB_PATH" 2>/dev/null || echo "0")
            if [ "$DB_SIZE" -gt 10485760 ]; then
                echo "Downloaded database appears valid. Skipping BigQuery import."
            else
                echo "Downloaded database appears incomplete. Proceeding with BigQuery import..."
                # Import data from BigQuery (GCP credentials will be downloaded from S3 by GooglePatentsFetcher)
                echo "Importing patent data from BigQuery..."
                python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=10000); print(f'Imported {count} patents from BigQuery')"
                
                if [ $? -eq 0 ]; then
                    echo "Successfully imported patent data from BigQuery"
                else
                    echo "Failed to import patent data from BigQuery"
                    # Continue with server startup even if import fails
                fi
            fi
        else
            echo "Failed to download SQLite database from S3. Proceeding with BigQuery import..."
            
            # Import data from BigQuery (GCP credentials will be downloaded from S3 by GooglePatentsFetcher)
            echo "Importing patent data from BigQuery..."
            python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=10000); print(f'Imported {count} patents from BigQuery')"
            
            if [ $? -eq 0 ]; then
                echo "Successfully imported patent data from BigQuery"
            else
                echo "Failed to import patent data from BigQuery"
                # Continue with server startup even if import fails
            fi
        fi
    fi
else
    echo "Database doesn't exist. Attempting to download from S3..."
    
    # Create data directory if it doesn't exist
    mkdir -p $(dirname "$GOOGLE_PATENTS_DB_PATH")
    
    # Download SQLite database from S3
    aws s3 cp "$S3_SQLITE_DB_PATH" "$GOOGLE_PATENTS_DB_PATH"
    
    # Check if S3 download was successful
    if [ $? -eq 0 ]; then
        echo "Successfully downloaded SQLite database from S3"
        DB_SIZE=$(stat -c %s "$GOOGLE_PATENTS_DB_PATH" 2>/dev/null || echo "0")
        if [ "$DB_SIZE" -gt 10485760 ]; then
            echo "Downloaded database appears valid. Skipping BigQuery import."
        else
            echo "Downloaded database appears incomplete. Proceeding with BigQuery import..."
            # Import data from BigQuery (GCP credentials will be downloaded from S3 by GooglePatentsFetcher)
            echo "Importing patent data from BigQuery..."
            python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=10000); print(f'Imported {count} patents from BigQuery')"
            
            if [ $? -eq 0 ]; then
                echo "Successfully imported patent data from BigQuery"
            else
                echo "Failed to import patent data from BigQuery"
                # Continue with server startup even if import fails
            fi
        fi
    else
        echo "Failed to download SQLite database from S3. Attempting BigQuery import instead..."
        
        # Import data from BigQuery (GCP credentials will be downloaded from S3 by GooglePatentsFetcher)
        echo "Importing patent data from BigQuery..."
        python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=10000); print(f'Imported {count} patents from BigQuery')"
        
        if [ $? -eq 0 ]; then
            echo "Successfully imported patent data from BigQuery"
        else
            echo "Failed to import patent data from BigQuery"
            # Continue with server startup even if import fails
        fi
    fi
fi

# Start the MCP server
echo "Starting MCP server..."
exec ./start_server.sh
