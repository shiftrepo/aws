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

# Check if source.aws exists and source it if it does
if [ -f ~/.aws/source.aws ]; then
  echo "Sourcing AWS credentials from ~/.aws/source.aws"
  source ~/.aws/source.aws
  echo "AWS credentials sourced. Region: $AWS_REGION"
else
  echo "Warning: AWS credentials file not found at ~/.aws/source.aws"
  echo "Make sure AWS credentials are properly set in environment variables."
fi

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "ERROR: AWS credentials not found in environment variables."
  echo "Please set them before running this script."
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

# Restart the database container to ensure it recognizes the files
echo "Restarting database container to load the database files..."
podman restart "$CONTAINER_NAME"

echo "================================================="
echo "Database download completed"
echo "================================================="

# Run health check script if available
if [ -f "./scripts/check_health.sh" ]; then
  echo "Running health check script..."
  ./scripts/check_health.sh
fi
