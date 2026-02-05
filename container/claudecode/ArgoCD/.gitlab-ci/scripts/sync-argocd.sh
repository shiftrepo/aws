#!/bin/bash
set -e

# ============================================================================
# Script: sync-argocd.sh
# Description: Trigger ArgoCD application sync and wait for completion
# Usage: ./sync-argocd.sh <environment>
# Example: ./sync-argocd.sh dev
# ============================================================================

echo "=========================================="
echo "ArgoCD Application Sync"
echo "=========================================="

# Check arguments
if [ $# -eq 0 ]; then
    echo "ERROR: Environment argument required"
    echo "Usage: $0 <environment>"
    echo "Example: $0 dev"
    exit 1
fi

ENVIRONMENT=$1

# Configuration
ARGOCD_SERVER="${ARGOCD_URL:-localhost:5010}"
ARGOCD_USERNAME="${ARGOCD_USERNAME:-admin}"
ARGOCD_PASSWORD="${ARGOCD_PASSWORD:-admin123}"
APP_NAME="orgmgmt-${ENVIRONMENT}"
SYNC_TIMEOUT="${ARGOCD_SYNC_TIMEOUT:-300}"

echo "ArgoCD Server: ${ARGOCD_SERVER}"
echo "Application: ${APP_NAME}"
echo "Environment: ${ENVIRONMENT}"
echo "Sync Timeout: ${SYNC_TIMEOUT}s"

# Function to check ArgoCD server availability
check_argocd_server() {
    echo ""
    echo "Checking ArgoCD server availability..."
    local max_attempts=10
    local attempt=1

    while [ ${attempt} -le ${max_attempts} ]; do
        if argocd version --server ${ARGOCD_SERVER} --insecure --grpc-web 2>/dev/null; then
            echo "ArgoCD server is available"
            return 0
        fi
        echo "Attempt ${attempt}/${max_attempts}: ArgoCD server not ready, waiting..."
        sleep 5
        attempt=$((attempt + 1))
    done

    echo "ERROR: ArgoCD server is not available after ${max_attempts} attempts"
    return 1
}

# Check if ArgoCD server is available
if ! check_argocd_server; then
    echo "WARNING: Proceeding anyway, login might fail"
fi

# Login to ArgoCD
echo ""
echo "Logging in to ArgoCD..."
argocd login ${ARGOCD_SERVER} \
    --username ${ARGOCD_USERNAME} \
    --password ${ARGOCD_PASSWORD} \
    --insecure \
    --grpc-web

if [ $? -ne 0 ]; then
    echo "ERROR: ArgoCD login failed"
    exit 1
fi

echo "Successfully logged in to ArgoCD"

# Check if application exists
echo ""
echo "Checking if application exists..."
if ! argocd app get ${APP_NAME} --server ${ARGOCD_SERVER} --insecure --grpc-web >/dev/null 2>&1; then
    echo "ERROR: Application '${APP_NAME}' not found in ArgoCD"
    echo "Available applications:"
    argocd app list --server ${ARGOCD_SERVER} --insecure --grpc-web
    exit 1
fi

echo "Application '${APP_NAME}' found"

# Get current application status
echo ""
echo "Current application status:"
argocd app get ${APP_NAME} \
    --server ${ARGOCD_SERVER} \
    --insecure \
    --grpc-web \
    --refresh

# Trigger sync
echo ""
echo "Triggering sync for application '${APP_NAME}'..."
argocd app sync ${APP_NAME} \
    --server ${ARGOCD_SERVER} \
    --insecure \
    --grpc-web \
    --prune \
    --async

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to trigger sync"
    exit 1
fi

echo "Sync triggered successfully"

# Wait for sync to complete
echo ""
echo "Waiting for sync to complete (timeout: ${SYNC_TIMEOUT}s)..."
argocd app wait ${APP_NAME} \
    --server ${ARGOCD_SERVER} \
    --insecure \
    --grpc-web \
    --timeout ${SYNC_TIMEOUT} \
    --health

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Sync failed or timed out"
    echo "Application status:"
    argocd app get ${APP_NAME} --server ${ARGOCD_SERVER} --insecure --grpc-web
    exit 1
fi

# Display final status
echo ""
echo "=========================================="
echo "Sync completed successfully!"
echo "=========================================="
echo ""
echo "Final application status:"
argocd app get ${APP_NAME} \
    --server ${ARGOCD_SERVER} \
    --insecure \
    --grpc-web

# Display sync history
echo ""
echo "Recent sync history:"
argocd app history ${APP_NAME} \
    --server ${ARGOCD_SERVER} \
    --insecure \
    --grpc-web \
    --output wide

echo ""
echo "ArgoCD sync completed successfully"
exit 0
