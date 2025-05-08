#!/bin/bash
# Entrypoint script for inpit-sqlite-mcp container
# This script fetches data from BigQuery and stores it in SQLite on container startup

set -e

echo "=== Starting inpit-sqlite-mcp with BigQuery data import ==="
echo "$(date): Container started"

# Database paths
DATA_DIR="/app/data"
DB_SUBDIR="$DATA_DIR/db"

echo "Running as $(id -un) ($(id -u):$(id -g))"

# Verify directories and permissions
echo "Verifying directory permissions:"
ls -la $DATA_DIR
ls -la $DB_SUBDIR

# Ensure the db directory exists and has correct permissions
mkdir -p "$DB_SUBDIR"
echo "Setting correct permissions on data directories..."
chown -R $(id -u):$(id -g) "$DATA_DIR" "$DB_SUBDIR" || echo "Warning: Could not change directory ownership"
chmod -R 755 "$DATA_DIR" "$DB_SUBDIR" || echo "Warning: Could not change directory permissions"
echo "After permission changes:"
ls -la $DATA_DIR
ls -la $DB_SUBDIR

# Define database paths - separate paths for GCP and S3 data
# Put them in the subdirectory we created and know we have write access to
GOOGLE_PATENTS_DB_PATH="$DB_SUBDIR/google_patents_gcp.db"
S3_LOCAL_DB_PATH="$DB_SUBDIR/google_patents_s3.db"
S3_BUCKET="ndi-3supervision"
S3_KEY="MIT/demo/GCP/google_patents.db"
S3_SQLITE_DB_PATH="s3://$S3_BUCKET/$S3_KEY"

echo "Database paths:"
echo "- GCP Database: $GOOGLE_PATENTS_DB_PATH"
echo "- S3 Local Database: $S3_LOCAL_DB_PATH"
echo "- S3 Source Path: $S3_SQLITE_DB_PATH"

# Set GCP credentials environment variables for GooglePatentsFetcher class
#export GCP_CREDENTIALS_S3_KEY="MIT/GCPServiceKey/tosapi-bf0ac4918370.json"
export GCP_CREDENTIALS_S3_BUCKET="ndi-3supervision"
export GCP_CREDENTIALS_S3_KEY="MIT/GCPServiceKey/mytest-202601-6d547916bf46.json"

# Note: GCP credentials are automatically downloaded from S3 by the GooglePatentsFetcher class
# using the environment variables defined above

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

# Remove any existing database file to ensure a fresh start
if [ -f "$S3_LOCAL_DB_PATH" ]; then
    echo "Removing existing S3 database file..."
    rm -f "$S3_LOCAL_DB_PATH"
fi

# Download SQLite database from S3
echo "Downloading SQLite database from S3..."
echo "Source: $S3_SQLITE_DB_PATH"
echo "Destination: $S3_LOCAL_DB_PATH"

# Check AWS credentials
echo "Checking AWS credentials..."
aws sts get-caller-identity || echo "AWS credentials issue detected"

# Check if the S3 object exists
echo "Checking if S3 object exists..."
if aws s3 ls "$S3_SQLITE_DB_PATH" 2>/dev/null; then
    echo "S3 object exists, proceeding with download"
else
    echo "ERROR: S3 object does not exist at $S3_SQLITE_DB_PATH"
    # List directory contents to check various common paths
    echo "Searching for the database file in different possible locations..."
    
    echo "Listing contents of ndi-3supervision/MIT/demo/GCP:"
    aws s3 ls "s3://ndi-3supervision/MIT/demo/GCP/" || echo "Path not found or not accessible"
    
    echo "Listing contents of ndi-3supervision/MIT/demo:"
    aws s3 ls "s3://ndi-3supervision/MIT/demo/" || echo "Path not found or not accessible"
    
    echo "Listing contents of ndi-3supervision/MIT:"
    aws s3 ls "s3://ndi-3supervision/MIT/" || echo "Path not found or not accessible"
    
    # Search for files matching the pattern in the bucket
    echo "Searching for files named google_patents.db in the bucket:"
    aws s3 ls --recursive "s3://ndi-3supervision/" | grep "google_patents.db" || echo "No matching files found"
fi

# Check directory permissions before download
echo "Checking directory permissions for $DB_SUBDIR:"
ls -la "$DB_SUBDIR"

# Try to download with verbose output
echo "Attempting download with verbose output..."
aws s3 cp "$S3_SQLITE_DB_PATH" "$S3_LOCAL_DB_PATH" --debug

if [ $? -eq 0 ]; then
    echo "Successfully downloaded SQLite database from S3"
    # Verify file exists and check its size
    ls -la "$S3_LOCAL_DB_PATH"
else
    echo "ERROR: Failed to download SQLite database from S3"
    # Check for common issues
    echo "Possible causes:"
    echo "1. S3 object doesn't exist"
    echo "2. AWS credentials issue"
    echo "3. Permission problems"
    echo "4. Network connectivity"
    
    # Fallback: Create an empty database file to prevent application errors
    echo "Creating a fallback empty SQLite database at $S3_LOCAL_DB_PATH"
    
    # Create an empty SQLite database with basic schema
    sqlite3 "$S3_LOCAL_DB_PATH" <<EOF
CREATE TABLE IF NOT EXISTS publications (
    publication_number TEXT PRIMARY KEY,
    filing_date TEXT,
    publication_date TEXT,
    application_number TEXT,
    assignee_harmonized TEXT,
    assignee_original TEXT,
    title_ja TEXT,
    title_en TEXT,
    abstract_ja TEXT,
    abstract_en TEXT,
    claims TEXT,
    ipc_code TEXT,
    family_id TEXT,
    country_code TEXT,
    kind_code TEXT,
    priority_date TEXT,
    grant_date TEXT,
    priority_claim TEXT,
    status TEXT,
    legal_status TEXT,
    examined TEXT,
    family_size INTEGER
);

CREATE TABLE IF NOT EXISTS patent_families (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_id TEXT,
    application_number TEXT,
    publication_number TEXT,
    country_code TEXT,
    UNIQUE(family_id, application_number)
);

CREATE INDEX IF NOT EXISTS idx_family_id ON publications (family_id);
CREATE INDEX IF NOT EXISTS idx_app_num ON publications (application_number);
CREATE INDEX IF NOT EXISTS idx_assignee_harmonized ON publications (assignee_harmonized);
CREATE INDEX IF NOT EXISTS idx_country_code ON publications (country_code);

CREATE INDEX IF NOT EXISTS idx_family_family_id ON patent_families (family_id);
CREATE INDEX IF NOT EXISTS idx_family_app_num ON patent_families (application_number);
CREATE INDEX IF NOT EXISTS idx_family_pub_num ON patent_families (publication_number);
EOF

    if [ $? -eq 0 ]; then
        echo "Successfully created fallback empty database"
        ls -la "$S3_LOCAL_DB_PATH"
    else
        echo "ERROR: Failed to create fallback database"
    fi
fi

# At this point, both database files should be created and accessible by the current user
# since they're in our writable subdirectory

echo "After database operations, checking file ownership and permissions..."
ls -la "$DB_SUBDIR"

# Start the MCP server
echo "Starting MCP server..."
exec ./start_server.sh
