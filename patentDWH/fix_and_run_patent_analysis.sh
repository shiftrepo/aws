#!/bin/bash

# This script fixes the patent analysis system issues and runs it

echo "Fixing patent analysis system..."

# 1. Stop and forcefully remove ALL existing containers to avoid conflicts
echo "Forcefully removing all containers..."
podman stop -a 2>/dev/null || true
podman rm -f $(podman ps -a -q) 2>/dev/null || true

# 2. Update the patent analyzer script with the fixed version
echo "Updating patent analyzer script..."
cp ../patent_analysis_container/patent_trend_analyzer.fixed.py ../patent_analysis_container/patent_trend_analyzer.py

# 3. Set proper permissions on output directory
echo "Setting proper permissions on output directory..."
mkdir -p ../patent_analysis_container/output 2>/dev/null || true
chmod 777 ../patent_analysis_container/output

# 4. Run the patent analysis with the fixed docker-compose file
echo "Running patent analysis with fixed configuration..."
podman-compose -f docker-compose.fixed.yml run --rm patent-analysis "$1" "$2"

echo "Patent analysis completed!"
