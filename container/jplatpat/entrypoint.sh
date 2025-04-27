#!/bin/bash

# Start Xvfb for headless Chrome
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
export DISPLAY=:99

# Wait a moment for Xvfb to initialize
sleep 1

# Handle SQL command separately
if [[ "$1" == "sql" ]]; then
    shift
    /app/sql.sh "$@"
else
    # Use the wrapper module to handle all other commands
    python /app/wrapper.py "$@"
fi
