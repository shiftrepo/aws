#!/bin/bash
set -ex

# Function for logging with timestamp
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [patentDWH-MCP] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [patentDWH-MCP] [ERROR] $1" >&2
}

log_msg "==== Patent DWH MCP Server Starting ===="
log_msg "Running as user: $(id)"

# Log environment and configuration
log_msg "Environment variables:"
log_msg "  - PATENT_DB_URL: ${PATENT_DB_URL:-http://patentdwh-db:5002}"
log_msg "  - AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION:-not set}"
log_msg "  - AWS keys set: $(if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then echo "Yes"; else echo "No"; fi)"
log_msg "  - GCP credentials variables set: $(if [ -n "$GCP_CREDENTIALS_S3_BUCKET" ] && [ -n "$GCP_CREDENTIALS_S3_KEY" ]; then echo "Yes"; else echo "No"; fi)"

# Check if we can access the database server
log_msg "Checking connection to database server..."
set +e
for i in $(seq 1 10); do
    log_msg "Connection attempt $i to ${PATENT_DB_URL:-http://patentdwh-db:5002}/health"
    response=$(curl -s -w "%{http_code}" -o /tmp/db_response.txt "${PATENT_DB_URL:-http://patentdwh-db:5002}/health")
    exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ "$response" = "200" ]; then
        log_msg "Successfully connected to database server"
        log_msg "Response: $(cat /tmp/db_response.txt)"
        break
    else
        if [ $i -eq 10 ]; then
            log_error "Failed to connect to database server after 10 attempts"
            if [ $exit_code -ne 0 ]; then
                log_error "Curl exit code: $exit_code (connection failed)"
            else
                log_error "HTTP response code: $response"
                log_error "Response body: $(cat /tmp/db_response.txt 2>/dev/null || echo 'Empty response')"
            fi
        else
            log_msg "Could not connect to database server, retrying in 3 seconds..."
            sleep 3
        fi
    fi
done
set -e

# Check data volumes
log_msg "Checking data volumes:"
log_msg "  - /app/data directory: $(if [ -d "/app/data" ]; then echo "exists"; else echo "does not exist"; fi)"
log_msg "  - /app/data/db directory: $(if [ -d "/app/data/db" ]; then echo "exists"; else echo "does not exist"; fi)"

# Check for database files in the volume
log_msg "Checking database files in volume:"
for db_file in /app/data/inpit.db /app/data/google_patents_gcp.db /app/data/google_patents_s3.db; do
    if [ -f "$db_file" ]; then
        log_msg "  - $db_file exists ($(du -h "$db_file" | cut -f1) size)"
    else
        log_error "  - $db_file does not exist"
    fi
done

# Launch the FastAPI server
log_msg "Starting FastAPI server with Uvicorn..."
log_msg "Server will be available at http://0.0.0.0:8080"

exec uvicorn server:app --host 0.0.0.0 --port 8080 --log-level info 2>&1 | while IFS= read -r line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [uvicorn] $line"
done
