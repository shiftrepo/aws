#!/bin/bash

# This script forcibly removes all containers and images related to our patent analysis system

echo "Forcibly cleaning up all containers..."

# Stop all running containers
echo "Stopping all running containers..."
podman stop -a

# Get all container IDs
ALL_CONTAINERS=$(podman ps -a --format "{{.ID}}")

# Force remove all containers
if [ ! -z "$ALL_CONTAINERS" ]; then
  echo "Force removing all containers..."
  echo "$ALL_CONTAINERS" | xargs podman rm -f
fi

echo "Cleanup completed!"
echo "You can now run ./fix_and_run_patent_analysis.sh to start fresh."
