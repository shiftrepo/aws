#!/bin/bash

echo "Debugging Database Container"
echo "==========================="

echo "1. Checking container is running"
podman inspect sqlite-db --format '{{.State.Status}}' || echo "Container not running"

echo "2. Checking database files in container"
podman exec sqlite-db ls -la /app/data

echo "3. Testing health endpoint inside container"
podman exec sqlite-db curl -v http://localhost:5000/health

echo "4. Checking environment variables inside container"
podman exec sqlite-db env | grep -E "AWS_|DB_|S3_PATH"

echo "5. Checking AWS CLI configuration inside container"
podman exec sqlite-db aws configure list

echo "6. Testing health endpoint from host"
curl -v http://localhost:5003/health

echo "7. Checking container logs"
podman logs sqlite-db | tail -n 50

echo "8. Checking container processes"
podman exec sqlite-db ps aux

echo "9. Checking container network connectivity"
podman exec sqlite-db ping -c 2 s3.amazonaws.com

echo "==========================="
echo "Debug complete"
