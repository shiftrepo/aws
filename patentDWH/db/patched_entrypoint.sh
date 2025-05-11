#!/bin/bash

# Patched entrypoint script for the database service
# Applies MCP endpoint patch before starting the service

set -e
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting patched entrypoint script"

# Directory containing the application code
APP_DIR=/app

# Apply MCP endpoint patch if the patch file exists
MCP_PATCH_FILE="${APP_DIR}/mcp_endpoint_patch.py"
if [ -f "$MCP_PATCH_FILE" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Found MCP endpoint patch, applying it..."
    
    # Add import and initialization for MCP endpoint in app.py
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Patching app.py to add MCP endpoint"
    
    # Check if the patch has already been applied
    if grep -q "add_mcp_endpoint" ${APP_DIR}/app.py; then
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP endpoint patch already applied"
    else
        # Add import for mcp_endpoint_patch at the top after existing imports
        sed -i '/^import/a import mcp_endpoint_patch' ${APP_DIR}/app.py
        
        # Add initialization before app.run()
        sed -i 's/if __name__ == .main.:/\
# Apply MCP endpoint patch\
mcp_endpoint_patch.add_mcp_endpoint(app)\
\
if __name__ == "__main__":/' ${APP_DIR}/app.py
        
        echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - MCP endpoint patch applied successfully"
    fi
else
    echo "[WARNING] $(date +"%Y-%m-%d %H:%M:%S") - MCP endpoint patch file not found"
fi

# Initialize the database if needed (reuse existing initialization logic)
if [ -f "${APP_DIR}/init_db.py" ]; then
    echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Initializing database"
    python ${APP_DIR}/init_db.py
fi

# Start the Flask application
echo "[INFO] $(date +"%Y-%m-%d %H:%M:%S") - Starting Flask application"
exec python ${APP_DIR}/app.py
