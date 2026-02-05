#!/bin/bash
set -e

# ============================================================================
# Script: deploy-nexus-npm.sh
# Description: Deploy NPM/Frontend artifacts to Nexus Repository
# ============================================================================

echo "=========================================="
echo "Deploying Frontend Artifact to Nexus"
echo "=========================================="

# Configuration
NEXUS_URL="${NEXUS_URL:-http://nexus:8081}"
NEXUS_USERNAME="${NEXUS_USERNAME:-admin}"
NEXUS_PASSWORD="${NEXUS_PASSWORD:-admin123}"
NPM_REPO="${NPM_REPO:-npm-hosted}"
VERSION="${VERSION:-latest}"
FRONTEND_DIR="${CI_PROJECT_DIR}/app/frontend"

echo "Nexus URL: ${NEXUS_URL}"
echo "NPM Repository: ${NPM_REPO}"
echo "Version: ${VERSION}"
echo "Frontend Directory: ${FRONTEND_DIR}"

# Navigate to frontend directory
cd "${FRONTEND_DIR}"

# Find the tarball
TARBALL=$(find . -name "frontend-*.tgz" -type f | head -n 1)
if [ -z "${TARBALL}" ]; then
    echo "ERROR: Frontend tarball not found"
    echo "Looking for: frontend-*.tgz"
    ls -la
    exit 1
fi

echo "Found tarball: ${TARBALL}"
TARBALL_NAME=$(basename "${TARBALL}")

# Display tarball information
echo ""
echo "Tarball Information:"
echo "  Name: ${TARBALL_NAME}"
echo "  Size: $(du -h "${TARBALL}" | cut -f1)"
echo "  Path: ${TARBALL}"

# Upload to Nexus using raw repository upload
echo ""
echo "Uploading to Nexus..."
UPLOAD_URL="${NEXUS_URL}/repository/${NPM_REPO}/${TARBALL_NAME}"

HTTP_CODE=$(curl -u "${NEXUS_USERNAME}:${NEXUS_PASSWORD}" \
    --upload-file "${TARBALL}" \
    -w "%{http_code}" \
    -o /tmp/nexus-response.txt \
    -s \
    "${UPLOAD_URL}")

echo "HTTP Response Code: ${HTTP_CODE}"

# Check response
if [ "${HTTP_CODE}" -eq 201 ] || [ "${HTTP_CODE}" -eq 200 ]; then
    echo ""
    echo "=========================================="
    echo "Frontend artifact uploaded successfully!"
    echo "URL: ${UPLOAD_URL}"
    echo "=========================================="
else
    echo "ERROR: Upload failed with HTTP code ${HTTP_CODE}"
    if [ -f /tmp/nexus-response.txt ]; then
        echo "Response:"
        cat /tmp/nexus-response.txt
    fi
    exit 1
fi

# Verify upload by checking if file exists
echo ""
echo "Verifying upload..."
VERIFY_CODE=$(curl -u "${NEXUS_USERNAME}:${NEXUS_PASSWORD}" \
    -s -o /dev/null \
    -w "%{http_code}" \
    "${UPLOAD_URL}")

if [ "${VERIFY_CODE}" -eq 200 ]; then
    echo "Verification successful: Artifact is accessible"
else
    echo "WARNING: Verification failed with HTTP code ${VERIFY_CODE}"
fi

echo ""
echo "Frontend deployment completed successfully"
exit 0
