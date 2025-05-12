# AI Integrated Search MCP Service Fix

## Issues

### 1. AWS Bedrock Service Error
The application was failing with the following error:
```
Failed to initialize Bedrock client: Unknown service: 'bedrock-runtime'. Valid service names are: [long list of services]
```

### 2. Database Connectivity Issues
Health checks showed multiple database-related issues:
- Database health endpoint not responding
- Missing database files (inpit.db and google_patents_gcp.db)
- Inter-container connectivity issues between services

## Causes

### AWS Bedrock Issue
The error occurs because the boto3 version (1.26.135) is too old to support the AWS Bedrock service. The `bedrock-runtime` service was added in a newer version of the AWS SDK.

### Database Connectivity Issues
- Database files not being properly downloaded from S3 during container startup
- Permissions issues with the data directory
- Services starting before the database is fully initialized

## Solutions

### 1. AWS Bedrock Fix
Updated the boto3 and botocore versions in both the nl-query and langchain-query services:
- Changed boto3 from 1.26.135 to 1.34.21
- Changed botocore from 1.29.135 to 1.34.21

These versions are compatible with the AWS Bedrock service and include support for the `bedrock-runtime` endpoint.

### 2. Database Connectivity Fix
- Added proper setup for database data directory with appropriate permissions
- Modified service startup sequence to ensure database service initializes first
- Added appropriate wait times between service startups to ensure proper initialization

## How to Apply the Fixes

1. The requirements.txt files have been updated with the new versions:
   - `AI_integrated_search_mcp/app/nl-query/requirements.txt`
   - `AI_integrated_search_mcp/app/langchain-query/requirements.txt`

2. A comprehensive rebuild script has been created to address all issues:
   ```bash
   cd /root/aws.git/AI_integrated_search_mcp
   chmod +x rebuild_services.sh
   ./rebuild_services.sh
   ```

3. The rebuild script will:
   - Stop running containers
   - Rebuild all services with updated dependencies
   - Create and set proper permissions on the data directory
   - Start the database service first and wait for it to download files
   - Start remaining services in the correct order
   - Display service logs to verify the fixes work

4. After restarting, verify the health of all services:
   ```bash
   ./scripts/check_health.sh
   ```

This will check:
   - Container status
   - Health endpoints
   - Database file existence
   - Inter-container connectivity

## Note on AWS Credentials
Remember that AWS credentials must be properly configured in the environment variables:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION

These are already properly configured in the podman-compose.yml file to be passed to the containers.
