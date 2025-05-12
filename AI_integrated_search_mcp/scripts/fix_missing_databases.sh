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

# Execute the download databases script
echo "Downloading missing databases..."
bash ./scripts/download_databases.sh

echo "Database fix completed. Running health check..."
bash ./scripts/check_health.sh
