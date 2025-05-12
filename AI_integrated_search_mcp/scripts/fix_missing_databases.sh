#!/bin/bash
# Script to fix missing databases in already running services

echo "================================================="
echo "Fixing Missing Databases for AI Integrated Search MCP"
echo "================================================="

# Set script to exit if any command fails
set -e

# Change to root directory
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Source environment variables
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

# Execute the download databases script
echo "Downloading missing databases..."
bash ./scripts/download_databases.sh

# Check if database container exists and is running
CONTAINER_NAME="${DATABASE_CONTAINER:-sqlite-db}"
if ! podman ps | grep -q "$CONTAINER_NAME"; then
  echo "Database container '$CONTAINER_NAME' is not running."
  echo "Starting services using start_services.sh script..."
  bash ./scripts/start_services.sh
else
  echo "Database container '$CONTAINER_NAME' is running. Running health check..."
  bash ./scripts/check_health.sh
fi
