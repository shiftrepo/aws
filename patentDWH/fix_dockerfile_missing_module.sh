#!/bin/bash

# Fix script for missing base_nl_query_processor.py module in Docker build
# This script addresses the ModuleNotFoundError: No module named 'base_nl_query_processor'
# by ensuring the file is included in the Dockerfile.enhanced COPY instructions

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting Dockerfile missing module fix"

# Path to the Dockerfile
DOCKERFILE="./app/Dockerfile.enhanced"

if [ ! -f "$DOCKERFILE" ]; then
  echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Dockerfile not found at $DOCKERFILE"
  exit 1
fi

# Create a backup
cp "$DOCKERFILE" "${DOCKERFILE}.bak"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Created backup at ${DOCKERFILE}.bak"

# Check if base_nl_query_processor.py is already included in the Dockerfile
if grep -q "COPY base_nl_query_processor.py" "$DOCKERFILE"; then
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - base_nl_query_processor.py is already included in the Dockerfile"
else
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Adding base_nl_query_processor.py to Dockerfile"
  
  # Add the missing file to the COPY instructions
  sed -i '/# Copy application files/,/COPY server_with_enhanced_nl.py/ s/COPY enhanced_nl_query_processor.py/COPY base_nl_query_processor.py .\nCOPY enhanced_nl_query_processor.py/' "$DOCKERFILE"
  
  # Verify the change
  if grep -q "COPY base_nl_query_processor.py" "$DOCKERFILE"; then
    echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - Successfully added base_nl_query_processor.py to Dockerfile"
  else
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Failed to add base_nl_query_processor.py to Dockerfile"
    exit 1
  fi
fi

# Check if the base_nl_query_processor.py file exists
if [ ! -f "./app/base_nl_query_processor.py" ]; then
  echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - base_nl_query_processor.py file not found in ./app/"
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Looking for the file in other locations..."
  
  # Try to find the file
  FOUND_FILE=$(find ./ -name "base_nl_query_processor.py" 2>/dev/null | head -n 1)
  
  if [ -n "$FOUND_FILE" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Found the file at $FOUND_FILE"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Copying to ./app/ directory"
    cp "$FOUND_FILE" "./app/base_nl_query_processor.py"
    echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - File copied successfully"
  else
    echo "[ERROR] $(date +"%Y-%m-%d %H:%M:%S") - Could not find base_nl_query_processor.py in the project directory"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You may need to create this file manually or restore it from a backup"
    exit 1
  fi
fi

echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Dockerfile missing module fix completed"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You need to rebuild the container for this fix to take effect"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Run: cd patentDWH && ./stop_all_services.sh && ./start_all_services.sh"
