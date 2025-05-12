#!/bin/bash
# Script to fix database connectivity issues and initialize required tables
# 
# このスクリプトは通常、「no such table: inpit_data」エラーが発生した場合に1回だけ実行する必要があります。
# 通常の運用では毎回実行する必要はありません。
#
# This script only needs to be run ONCE when you encounter the "no such table: inpit_data" error.
# It is NOT necessary to run this script during normal operation.
set -e

echo "===== Patent DWH Database Connectivity Fix ====="
echo ""
echo "注意：このスクリプトは「no such table: inpit_data」エラーを修正するためのものです。"
echo "通常の運用では実行する必要はありません。"
echo ""
echo "NOTE: This script fixes the 'no such table: inpit_data' error."
echo "It does not need to be run during normal operation."
echo ""

# Function for logging with timestamp
log_msg() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Default network name for podman/docker
NETWORK_NAME="patentdwh_default"

# Detect container runtime
if command -v podman &> /dev/null; then
  CONTAINER_RUNTIME="podman"
  log_msg "Using podman as container runtime"
elif command -v docker &> /dev/null; then
  CONTAINER_RUNTIME="docker"
  log_msg "Using docker as container runtime"
else
  log_msg "Error: No container runtime (podman or docker) found"
  exit 1
fi

# Step 1: Check if required network exists, create if missing
log_msg "Checking for $NETWORK_NAME network..."
if ! $CONTAINER_RUNTIME network ls | grep -q "$NETWORK_NAME"; then
  log_msg "Network $NETWORK_NAME does not exist, creating..."
  $CONTAINER_RUNTIME network create $NETWORK_NAME
  log_msg "Network created successfully"
else
  log_msg "Network $NETWORK_NAME already exists"
fi

# Step 2: Check container status
log_msg "Checking container status..."
if ! $CONTAINER_RUNTIME ps | grep -q "patentdwh-db"; then
  log_msg "patentdwh-db container is not running!"
  log_msg "Make sure to start it with: cd /root/aws.git/patentDWH && ./start_all_services.sh"
  exit 1
fi

# Step 3: Create a script to initialize the database inside the container
log_msg "Creating database initialization script..."
cat > init_inpit_table.py << 'EOF'
#!/usr/bin/env python3
"""
Script to initialize the inpit_data table if it doesn't exist
"""

import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database file path
INPIT_DB_PATH = "/app/data/inpit.db"

def initialize_inpit_table():
    """Create inpit_data table if it doesn't exist"""
    try:
        # Check if database file exists
        if not os.path.exists(INPIT_DB_PATH):
            logger.info(f"Creating new database file at {INPIT_DB_PATH}")
            # Make sure directory exists
            os.makedirs(os.path.dirname(INPIT_DB_PATH), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(INPIT_DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inpit_data'")
        if cursor.fetchone():
            logger.info("inpit_data table already exists")
            # Count rows in table
            cursor.execute("SELECT COUNT(*) FROM inpit_data")
            count = cursor.fetchone()[0]
            logger.info(f"Table contains {count} rows")
        else:
            logger.info("Creating inpit_data table")
            # Create empty inpit data table with essential columns
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS inpit_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                open_patent_info_number TEXT,
                title TEXT,
                open_patent_info_registration_date TEXT,
                latest_update_date TEXT,
                application_number TEXT,
                application_date TEXT,
                applicant TEXT,
                publication_number TEXT,
                registration_number TEXT,
                patent_owner TEXT,
                invention_name TEXT,
                technical_field1 TEXT,
                technical_field2 TEXT,
                technical_field3 TEXT,
                function1 TEXT,
                function2 TEXT,
                function3 TEXT,
                applicable_products TEXT,
                purpose TEXT,
                effect TEXT,
                technical_overview TEXT,
                implementation_record_status TEXT,
                licensing_record_status TEXT,
                patent_right_transfer TEXT
            )
            ''')
            
            # Insert a sample record for testing
            cursor.execute('''
            INSERT INTO inpit_data (
                open_patent_info_number, title, application_number, 
                application_date, applicant, publication_number
            ) VALUES (
                'SAMPLE-001', 'サンプル特許', 'APP-2023-001',
                '2023-01-01', 'テック株式会社', 'PUB-2023-001'
            )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_num ON inpit_data (application_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pub_num ON inpit_data (publication_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_applicant ON inpit_data (applicant)')
            
            conn.commit()
            logger.info("Sample data inserted successfully")
        
        # Set appropriate permissions
        conn.close()
        try:
            os.chmod(INPIT_DB_PATH, 0o666)
            logger.info("Database permissions set to 666 (readable/writable by all)")
        except Exception as e:
            logger.warning(f"Could not set permissions on database file: {e}")
            
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    if initialize_inpit_table():
        print("Database initialization completed successfully")
    else:
        print("Database initialization failed")
EOF

# Step 4: Copy the script into the container and execute it
log_msg "Copying database initialization script into the container..."
$CONTAINER_RUNTIME cp init_inpit_table.py patentdwh-db:/app/init_inpit_table.py

log_msg "Executing database initialization script..."
$CONTAINER_RUNTIME exec patentdwh-db python /app/init_inpit_table.py

# Step 5: Clean up
rm -f init_inpit_table.py

# Step 6: Test database connectivity directly with sqlite3
log_msg "Testing database connectivity with sqlite3..."
$CONTAINER_RUNTIME exec patentdwh-db sqlite3 /app/data/inpit.db "SELECT COUNT(*) FROM inpit_data"

# Step 7: Check if MCP container is running
log_msg "Checking MCP server status..."
if $CONTAINER_RUNTIME ps | grep -q "patent-analysis-mcp"; then
  log_msg "patent-analysis-mcp container is running"
  log_msg "To manually test connectivity: podman exec patent-analysis-mcp ping -c 2 patentdwh-db"
else
  log_msg "patent-analysis-mcp container is not running, skipping MCP connectivity test"
  log_msg "Start it with: cd /root/aws.git/patent_analysis_container && ./start_mcp_server.sh"
fi

log_msg "Database connectivity fix completed"
echo ""
echo "To verify the fix, try accessing the API again. If issues persist,"
echo "run the network troubleshooting script:"
echo "cd /root/aws.git/patent_analysis_container && ./test_container_connectivity.sh"
