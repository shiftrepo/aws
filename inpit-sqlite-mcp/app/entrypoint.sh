#!/bin/bash
# Entrypoint script for inpit-sqlite-mcp container
# This script fetches data from BigQuery and stores it in SQLite on container startup

set -e

echo "=== Starting inpit-sqlite-mcp with BigQuery data import ==="
echo "$(date): Container started"

# Define database path
GOOGLE_PATENTS_DB_PATH="/app/data/google_patents.db"

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
        echo "Proceeding with BigQuery data import..."
        
        # Import data from BigQuery
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
    echo "Database doesn't exist. Importing data from BigQuery..."
    
    # Create data directory if it doesn't exist
    mkdir -p $(dirname "$GOOGLE_PATENTS_DB_PATH")
    
    # Import data from BigQuery
    echo "Importing patent data from BigQuery..."
    python -c "from google_patents_fetcher import GooglePatentsFetcher; fetcher = GooglePatentsFetcher(db_path='$GOOGLE_PATENTS_DB_PATH'); count = fetcher.fetch_japanese_patents(limit=10000); print(f'Imported {count} patents from BigQuery')"
    
    if [ $? -eq 0 ]; then
        echo "Successfully imported patent data from BigQuery"
    else
        echo "Failed to import patent data from BigQuery"
        # Continue with server startup even if import fails
    fi
fi

# Start the MCP server
echo "Starting MCP server..."
exec ./start_server.sh
