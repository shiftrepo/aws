#!/bin/bash
# Build script for Java Test Specification Generator

echo "Building Java Test Specification Generator..."

# Use Docker to build the project
docker run --rm \
  -v "$(pwd)":/workspace \
  -w /workspace \
  maven:3.9-eclipse-temurin-17 \
  sh -c "mvn clean compile && mvn test && mvn package -DskipTests"

echo "Build complete. Checking for output..."
ls -la target/*.jar