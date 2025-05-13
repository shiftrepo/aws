# Database Connection Fix Guide

This document provides guidance on resolving database connection issues in the AI Integrated Search MCP system.

## Problem Description

The health check reported the following issues:

- Database container is running but health endpoint is not responding
- Missing or inaccessible database files
- Inter-container connectivity issues - other services cannot connect to the database service

## Root Causes

1. **Volume Mount Issues**: Database files exist on the host but are not properly accessible within the container due to permissions or mount issues.
2. **Database File Permission Problems**: Even when files exist, they may have incorrect permissions preventing the container from reading them.
3. **Container Health Check Failure**: The health check endpoint is failing due to database connectivity issues.

## Solution

We've implemented several fixes to address these issues:

1. **Improved Database File Detection**: Enhanced the app to better detect and verify database files on startup
2. **Permission Fixes**: Added code to ensure proper permissions are set on database files
3. **Enhanced Health Check**: Improved the health check endpoint to provide more detailed diagnostics
4. **Startup Verification**: Added a check-and-fix routine that runs on service startup

## Fixing the Issue

We've provided several scripts to help diagnose and fix database connection issues:

### 1. Debug Script

Run the debug script to diagnose issues without making changes:

```bash
cd AI_integrated_search_mcp
./scripts/debug_db_container.sh
```

This script will:
- Check if the container is running
- Verify database files exist in the container
- Test the health endpoint from inside and outside the container
- Check environment variables and AWS configuration
- Test network connectivity

### 2. Fix Script

Run the fix script to attempt automatic repair of database issues:

```bash
cd AI_integrated_search_mcp
./scripts/fix_db_container.sh
```

This script will:
- Verify database files on the host
- Fix permissions on database files
- Force copy database files into the container
- Set proper ownership and permissions inside the container
- Restart the container

### 3. Rebuild Script

For a complete rebuild of the database service:

```bash
cd AI_integrated_search_mcp
./scripts/rebuild_db_service.sh
```

This script will:
- Stop and remove the existing container
- Rebuild the database service from scratch 
- Start a fresh instance
- Apply all fixes
- Verify the service is working properly

## Manual Fixes

If the scripts don't resolve the issue, you can try these manual steps:

1. Ensure database files exist on the host:
   ```bash
   ls -la AI_integrated_search_mcp/db/data/
   ```

2. Fix permissions on database files:
   ```bash
   chmod 644 AI_integrated_search_mcp/db/data/*.db
   ```

3. Restart the database container:
   ```bash
   cd AI_integrated_search_mcp
   podman stop sqlite-db
   podman rm sqlite-db
   podman-compose up -d sqlite-db
   ```

4. Force copy database files into container:
   ```bash
   cd AI_integrated_search_mcp
   podman cp db/data/inpit.db sqlite-db:/app/data/inpit.db
   podman cp db/data/google_patents_gcp.db sqlite-db:/app/data/google_patents_gcp.db
   podman exec sqlite-db chown -R ec2-user:ec2-user /app/data
   podman exec sqlite-db chmod 644 /app/data/*.db
   ```

5. Restart the entire stack:
   ```bash
   cd AI_integrated_search_mcp
   podman-compose down
   podman-compose up -d
   ```

## Verifying the Fix

Run the health check script to verify all services are working properly:

```bash
cd AI_integrated_search_mcp
./scripts/check_health.sh
```

The output should show that all services are running and healthy.
