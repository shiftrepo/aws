#!/bin/bash

# Fix script for FastAPI middleware import issues in patentDWH
# This script addresses the ModuleNotFoundError: No module named 'fastapi.middleware.base'
# by updating imports to use starlette.middleware.base instead

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting FastAPI middleware import fix"

# Directory containing server files
APP_DIR="./app"
FILES_TO_CHECK=(
  "${APP_DIR}/server.py"
  "${APP_DIR}/server_with_enhanced_nl.py"
)

# Check for each potential file
for file in "${FILES_TO_CHECK[@]}"; do
  if [ -f "$file" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Checking $file for FastAPI middleware imports"
    
    # Create backup
    cp "$file" "${file}.bak"
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Created backup at ${file}.bak"
    
    # Replace the import statement
    if grep -q "from fastapi.middleware.base import BaseHTTPMiddleware" "$file"; then
      echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Replacing middleware import in $file"
      sed -i 's/from fastapi\.middleware\.base import BaseHTTPMiddleware/from starlette.middleware.base import BaseHTTPMiddleware/' "$file"
      echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - Updated middleware import in $file"
    else
      echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - No middleware import to fix in $file"
    fi
  else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - File $file does not exist, skipping"
  fi
done

# Add starlette to requirements if not already present
REQUIREMENTS_FILE="${APP_DIR}/requirements_enhanced.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Ensuring starlette is in requirements file"
  
  if ! grep -q "starlette>=" "$REQUIREMENTS_FILE"; then
    # Get the line number of the fastapi requirement
    FASTAPI_LINE=$(grep -n "fastapi" "$REQUIREMENTS_FILE" | head -n 1 | cut -d: -f1)
    
    if [ -n "$FASTAPI_LINE" ]; then
      # Insert starlette requirement after fastapi line
      sed -i "${FASTAPI_LINE}a starlette>=0.27.0" "$REQUIREMENTS_FILE"
      echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - Added starlette to requirements"
    else
      # Add to the top if fastapi not found
      sed -i '1i starlette>=0.27.0' "$REQUIREMENTS_FILE"
      echo "[SUCCESS] $(date +"%Y-%m-%d %H:%M:%S") - Added starlette to requirements (at top)"
    fi
  else
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - starlette already in requirements"
  fi
else
  echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - Requirements file not found at $REQUIREMENTS_FILE"
fi

echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - FastAPI middleware import fix completed"
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - You should rebuild and restart the container for changes to take effect"
