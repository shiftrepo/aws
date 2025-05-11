#!/bin/bash
set -ex

# Function for logging with timestamp
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [patentDWH-DB] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [patentDWH-DB] [ERROR] $1" >&2
}

log_msg "==== Patent DWH Database Server Starting ===="
log_msg "Running as user: $(id)"
log_msg "Environment variables:"
log_msg "  - SKIP_DATA_DOWNLOAD: ${SKIP_DATA_DOWNLOAD}"
log_msg "  - AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}"
# Check if AWS keys are set without printing the actual values
log_msg "  - AWS keys set: $(if [ -n "${AWS_ACCESS_KEY_ID}" ] && [ -n "${AWS_SECRET_ACCESS_KEY}" ]; then echo "Yes"; else echo "No"; fi)"

# Set up proper permissions for data directory
log_msg "Creating data directory with proper permissions"
mkdir -p /app/data
chmod 777 /app/data
log_msg "Data directory permissions set: $(ls -ld /app/data)"

# Check if we should skip data download
if [ "${SKIP_DATA_DOWNLOAD}" != "true" ]; then
    log_msg "Downloading data from S3..."
    # Execute download_data.py and capture its output and exit code
    set +e
    python /app/download_data.py 2>&1 | while IFS= read -r line; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [download_data] $line"
    done
    download_exit_code=${PIPESTATUS[0]}
    set -e
    
    if [ $download_exit_code -ne 0 ]; then
        log_error "Data download failed with exit code $download_exit_code"
        log_error "Checking for existing database files:"
        for db_file in /app/data/inpit.db /app/data/google_patents_gcp.db /app/data/google_patents_s3.db; do
            if [ -f "$db_file" ]; then
                log_msg "  - $db_file exists ($(du -h "$db_file" | cut -f1) size)"
            else
                log_error "  - $db_file does not exist"
            fi
        done
    else
        log_msg "Data download completed successfully"
        log_msg "Database files:"
        for db_file in /app/data/inpit.db /app/data/google_patents_gcp.db /app/data/google_patents_s3.db; do
            if [ -f "$db_file" ]; then
                log_msg "  - $db_file ($(du -h "$db_file" | cut -f1) size)"
            else
                log_error "  - $db_file does not exist after download"
            fi
        done
    fi
else
    log_msg "Skipping data download (SKIP_DATA_DOWNLOAD=true)"
    log_msg "Checking for existing database files:"
    for db_file in /app/data/inpit.db /app/data/google_patents_gcp.db /app/data/google_patents_s3.db; do
        if [ -f "$db_file" ]; then
            log_msg "  - $db_file exists ($(du -h "$db_file" | cut -f1) size)"
        else
            log_error "  - $db_file does not exist"
        fi
    done
fi

# Start the web server
log_msg "Starting Flask web server..."
exec python /app/app.py 2>&1 | while IFS= read -r line; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [flask] $line"
done
