#!/bin/bash
set -e

echo "======================================"
echo "Classification Analysis API Deployment"
echo "======================================"

# Check for the existing aiimcp-network
NETWORK_EXISTS=$(podman network ls | grep aiimcp-network || true)
if [ -z "$NETWORK_EXISTS" ]; then
  echo "Creating aiimcp-network..."
  podman network create aiimcp-network
else
  echo "Using existing aiimcp-network"
fi

# Stop any existing container
echo "Removing any existing classification-api-service..."
podman rm -f classification-api-service 2>/dev/null || true

# Build the Docker image
echo "Building classification API Docker image..."
podman build -t classification-api-image -f Dockerfile.classification_api .

# Start the service
echo "Starting classification API service..."
podman run -d \
  --name classification-api-service \
  --network aiimcp-network \
  -p 5006:5006 \
  -e DATABASE_API_URL=http://sqlite-db:5000 \
  classification-api-image

echo ""
echo "Classification API service has been started"
echo "API is available at: http://localhost:5006"
echo ""
echo "Available endpoints:"
echo "  - GET /health - Health check endpoint"
echo "  - GET / - API information"
echo "  - POST /analyze_classification - Classification analysis"
echo ""
echo "Example usage:"
echo 'curl -X POST http://localhost:5006/analyze_classification -H "Content-Type: application/json" -d "{"classification_code": "G", "start_year": 2010, "end_year": 2023}"'
echo ""
echo "======================================"
