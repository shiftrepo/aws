#!/bin/bash
set -e

# ============================================================================
# Script: deploy-nexus-maven.sh
# Description: Deploy Maven artifacts to Nexus Repository
# ============================================================================

echo "=========================================="
echo "Deploying Maven Artifact to Nexus"
echo "=========================================="

# Configuration
NEXUS_URL="${NEXUS_URL:-http://nexus:8081}"
NEXUS_USERNAME="${NEXUS_USERNAME:-admin}"
NEXUS_PASSWORD="${NEXUS_PASSWORD:-admin123}"
MAVEN_REPO="${MAVEN_REPO:-maven-snapshots}"
BACKEND_DIR="${CI_PROJECT_DIR}/app/backend"

echo "Nexus URL: ${NEXUS_URL}"
echo "Maven Repository: ${MAVEN_REPO}"
echo "Backend Directory: ${BACKEND_DIR}"

# Navigate to backend directory
cd "${BACKEND_DIR}"

# Verify settings.xml exists
if [ ! -f /root/.m2/settings.xml ]; then
    echo "ERROR: Maven settings.xml not found at /root/.m2/settings.xml"
    exit 1
fi

echo "Maven settings.xml configured successfully"

# Update pom.xml distribution management URLs with environment variables
echo "Updating distribution management URLs..."
sed -i "s|http://localhost:8081|${NEXUS_URL}|g" pom.xml

# Display Maven version
mvn --version

# Deploy to Nexus
echo ""
echo "Deploying artifact to Nexus ${MAVEN_REPO} repository..."
mvn deploy -DskipTests \
    -Dmaven.repo.local=${CI_PROJECT_DIR}/.m2/repository \
    -DaltDeploymentRepository=nexus::default::${NEXUS_URL}/repository/${MAVEN_REPO}/

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Maven artifact deployed successfully!"
    echo "Repository: ${NEXUS_URL}/repository/${MAVEN_REPO}/"
    echo "=========================================="
else
    echo "ERROR: Maven deployment failed"
    exit 1
fi

# Verify deployment
echo ""
echo "Verifying deployment..."
JAR_FILE=$(find target -name "*.jar" -type f ! -name "*-sources.jar" ! -name "*-javadoc.jar" | head -n 1)
if [ -z "${JAR_FILE}" ]; then
    echo "WARNING: Could not find JAR file for verification"
else
    JAR_NAME=$(basename "${JAR_FILE}")
    echo "Deployed artifact: ${JAR_NAME}"
    echo "Size: $(du -h "${JAR_FILE}" | cut -f1)"
fi

echo ""
echo "Maven deployment completed successfully"
exit 0
