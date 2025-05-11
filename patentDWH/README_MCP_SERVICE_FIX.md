# MCP Service Fix Documentation

This document explains the fixes applied to the `patentdwh-mcp-enhanced` service to resolve connectivity and LangChain compatibility issues.

## Problem Analysis

Based on the logs, the following issues were identified:

1. The MCP service starts successfully and the Uvicorn server is running on port 8080, but the health check fails.
2. There are multiple "Connection refused" errors when trying to connect to the database service.
3. The LangChain initialization appears to succeed, but there may be compatibility issues between the LangChain version and LangChain Community version.

## Applied Fixes

### 1. LangChain Version Compatibility

The previous requirements used incompatible versions:
- `langchain==0.0.267`
- `langchain-community==0.0.5`

These versions are not compatible with each other. LangChain underwent a major restructuring where the core package was split into multiple packages. We've updated the versions to compatible ones:

```
langchain>=0.1.0
langchain-community>=0.0.13
```

### 2. Import Handling

The LangChain import path has been updated with a fallback mechanism to handle different versions:

```python
try:
    from langchain_community.llms.bedrock import Bedrock
except ImportError:
    # Fall back to old import path if needed
    try:
        from langchain.llms.bedrock import Bedrock
    except ImportError:
        logging.error("Failed to import Bedrock from langchain. Ensure langchain and langchain-community are properly installed.")
```

### 3. Improved Health Check Endpoint

The health check has been enhanced to:
- Check database connectivity with a longer timeout
- Initialize the NL processor if needed
- Return more detailed status information

### 4. Proper Error Handling

Additional error handling has been added to gracefully handle connection issues.

## How to Apply the Fix

1. The changes have been applied to the following files:
   - `patentDWH/app/requirements_enhanced.txt`
   - `patentDWH/app/enhanced_nl_query_processor.py`
   - `patentDWH/app/server_with_enhanced_nl.py`

2. A script has been created to apply these fixes and restart the service:
   ```
   ./fix_mcp_service.sh
   ```

The script performs the following actions:
- Stops the existing MCP service
- Rebuilds the container with the updated requirements
- Starts the service and verifies it's running correctly
- Checks database connectivity and AWS credential configuration

## Verification

After running the fix script, verify that:

1. The MCP service is running and accessible at http://localhost:8080/
2. The health check endpoint returns a successful response
3. Database connectivity is established
4. AWS credentials are properly configured (if needed for NL queries)

## Troubleshooting

If issues persist:
- Check the logs with: `podman-compose -f docker-compose.consolidated.yml logs -f patentdwh-mcp-enhanced`
- Verify network connectivity between containers
- Ensure AWS credentials are properly set in the environment if using NL features

## AWS Credentials

For natural language processing features to work correctly, the following environment variables must be properly set:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION` (preferably set to a region with Bedrock services, e.g., "us-east-1")
