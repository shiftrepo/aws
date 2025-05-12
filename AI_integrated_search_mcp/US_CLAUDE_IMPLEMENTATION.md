# US Claude 3.7 Sonnet Implementation

## Overview
This document describes the implementation of cross-region support for the `us.anthropic.claude-3-7-sonnet-20250219-v1:0` model in the AI Integrated Search MCP service.

## Changes Made

### 1. Updated Model ID
The model ID was changed in the `.env` file:

```
BEDROCK_LLM_MODEL=us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

### 2. Cross-Region Client Implementation
The AWS Bedrock client in both services was modified to support cross-region functionality:

- **nl-query service**: Updated `BedrockClient` class to create a cross-region client specifically for Claude 3.7 models
- **langchain-query service**: Updated `BedrockLLM` class to use the appropriate region for Claude 3.7 models

### 3. Support for US-Specific Model ID Format
Added detection for US-specific model IDs (with the `us.` prefix) in addition to the normal Claude 3.7 model ID pattern. This ensures proper region selection regardless of the model ID format.

### 4. AWS Region Configuration
Set the AWS region to `us-west-2` as this is where the Claude 3.7 models are available.

## Implementation Details

### Client Selection Logic
When making API calls, the system now:

1. Detects if the model is Claude 3.7 or a US-specific model
2. Uses a cross-region client pointing to `us-west-2` if needed
3. Falls back to the default region for other models

```python
if "claude-3-7" in model_id or "us.anthropic" in model_id:
    client = cross_region_bedrock  # Uses us-west-2
else:
    client = bedrock  # Uses default region
```

## Running the System

To rebuild and restart all services with the US Claude 3.7 configuration:

```bash
cd /root/aws.git/AI_integrated_search_mcp
chmod +x rebuild_with_us_claude.sh
./rebuild_with_us_claude.sh
```

## Testing
Use the included test script to verify Claude 3.7 integration:

```bash
python3 test_bedrock.py
```

A successful test will show Claude responding properly with no access errors.

## Troubleshooting

If you encounter issues:

1. **Model Access Errors**: Ensure your AWS account has access to the US Claude 3.7 Sonnet model
2. **Region Issues**: Verify the AWS_DEFAULT_REGION is properly set in .env file
3. **Credentials**: Check that AWS credentials have permission to access Bedrock
4. **Inference Profile**: For some Claude models, an inference profile may be required

## Architecture Notes

The cross-region implementation uses conditional client selection rather than creating separate services for each region. This approach:

- Minimizes code duplication
- Keeps configuration centralized
- Handles model-specific requirements transparently
- Preserves backward compatibility with other models
