#!/bin/bash

# This script uses the existing Docker container to generate sample patent reports
# without relying on database access.

echo "===== Patent Sample Report Generator ====="
echo "Applicant: $1"

# Step 1: Make sure output directory exists
echo "Setting output directory permissions..."
mkdir -p ../patent_analysis_container/output 2>/dev/null || true
chmod 777 ../patent_analysis_container/output

# Step 2: Copy the report generator script to the container image build context
echo "Preparing sample report generator..."
cp ../patent_analysis_container/generate_sample_report.py ../patent_analysis_container/

# Step 3: Create Dockerfile for the report generator
cat > ../patent_analysis_container/Dockerfile.report <<EOF
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir pandas matplotlib

# Copy report generator script
COPY generate_sample_report.py .

# Create output directory
RUN mkdir -p output
RUN chmod 777 output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
ENTRYPOINT ["python", "generate_sample_report.py"]
EOF

# Step 4: Build the report generator container
echo "Building report generator container..."
cd ../patent_analysis_container
REPORT_GENERATOR_IMAGE=$(podman build -q -f Dockerfile.report .)

# Step 5: Run the container
echo "Running report generator..."
podman run --rm \
  -v "$(pwd)/output:/app/output:z" \
  --name patent-report-generator \
  $REPORT_GENERATOR_IMAGE "$1"

echo "===== Sample Report Generation Completed ====="
echo "Check the output directory: ../patent_analysis_container/output/"

# Display the generated files
echo "Generated files:"
ls -l ../patent_analysis_container/output/ | grep $(echo "$1" | sed 's/ /_/g')
