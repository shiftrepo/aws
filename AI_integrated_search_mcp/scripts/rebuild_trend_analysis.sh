#!/bin/bash
# Script to rebuild the Trend Analysis container

echo "================================================="
echo "Rebuilding Trend Analysis Container"
echo "================================================="

# Change to root directory
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Environment variables loaded from .env file"
fi

# Set default values for container name and port if not set in .env
TREND_ANALYSIS_CONTAINER=${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}
TREND_ANALYSIS_API_PORT=${TREND_ANALYSIS_API_PORT:-5006}

echo "Building Trend Analysis container..."
podman build -t trend-analysis-image:latest "$ROOT_DIR/app/trend-analysis"

echo "================================================="
echo "Trend Analysis container rebuild complete"
echo "================================================="

echo ""
echo "To start the container, run ./scripts/start_services.sh or use the rebuild_trend_analysis.sh script in the root directory."
echo ""
