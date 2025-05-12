#!/bin/bash
# Script to download missing database files for AI Integrated Search MCP

echo "================================================="
echo "Database Download Script for AI Integrated Search MCP"
echo "================================================="

# Set script to exit if any command fails
set -e

# Change to root directory
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Environment variables loaded from .env file"
else
  echo "ERROR: .env file not found"
  exit 1
fi

# Check if AWS credentials are available from environment variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "ERROR: AWS credentials not found in environment variables."
  echo "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_DEFAULT_REGION environment variables before running this script."
  exit 1
fi

echo "AWS region: $AWS_DEFAULT_REGION"

# Create data directory if it doesn't exist
CONTAINER_NAME="${DATABASE_CONTAINER:-sqlite-db}"
DATA_DIR="./db/data"
mkdir -p "$DATA_DIR"
echo "Ensuring data directory exists: $DATA_DIR"

# Download databases directly to the volume
echo "Downloading databases to volume directory..."

# Download Inpit database
INPIT_DB_PATH="$DATA_DIR/inpit.db"
if [ ! -f "$INPIT_DB_PATH" ]; then
  echo "Downloading Inpit database from S3..."
  aws s3 cp "$INPUT_DB_S3_PATH" "$INPIT_DB_PATH"
  if [ $? -eq 0 ]; then
    echo "✓ Inpit database downloaded successfully"
  else
    echo "✗ Failed to download Inpit database"
  fi
else
  echo "Inpit database already exists at $INPIT_DB_PATH"
fi

# Download BigQuery database
BIGQUERY_DB_PATH="$DATA_DIR/google_patents_gcp.db"
if [ ! -f "$BIGQUERY_DB_PATH" ]; then
  echo "Downloading BigQuery database from S3..."
  aws s3 cp "$BIGQUERY_DB_S3_PATH" "$BIGQUERY_DB_PATH"
  if [ $? -eq 0 ]; then
    echo "✓ BigQuery database downloaded successfully"
  else
    echo "✗ Failed to download BigQuery database"
  fi
else
  echo "BigQuery database already exists at $BIGQUERY_DB_PATH"
fi

# Check file existence and set permissions
echo "Checking database files and permissions..."
if [ -f "$INPIT_DB_PATH" ]; then
  echo "✓ Inpit database exists"
  chmod 644 "$INPIT_DB_PATH"
else
  echo "✗ Inpit database does not exist"
fi

if [ -f "$BIGQUERY_DB_PATH" ]; then
  echo "✓ BigQuery database exists"
  chmod 644 "$BIGQUERY_DB_PATH"
else
  echo "✗ BigQuery database does not exist"
fi

# Restart the database container (if it exists) to ensure it recognizes the files
if podman ps -a | grep -q "$CONTAINER_NAME"; then
  echo "Restarting database container to load the database files..."
  podman restart "$CONTAINER_NAME"
else
  echo "Database container '$CONTAINER_NAME' not found. Container will be created in the next step."
fi

echo "================================================="
echo "Database download completed"
echo "================================================="

# Run health check script if available
if [ -f "./scripts/check_health.sh" ]; then
  echo "Running health check script..."
  ./scripts/check_health.sh
fi
