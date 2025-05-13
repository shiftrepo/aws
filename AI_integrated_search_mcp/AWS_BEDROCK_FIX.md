# AWS Bedrock Integration Fix

## Problem Statement

The system encountered a 403 error when attempting to use AWS Bedrock:

```
2025-05-13 02:08:08,499 - urllib3.connectionpool - DEBUG - https://bedrock-runtime.us-east-1.amazonaws.com:443 "POST /model/anthropic.claude-3-sonnet-20240229-v1%3A0/invoke HTTP/1.1" 403 77
```

This error was caused by multiple issues:

1. Hardcoded fallback model values in code that didn't match the model specified in `.env`
2. Environment variables not being properly passed to containers
3. No error handling for missing environment variables

## Issues Identified

### 1. Hardcoded Model IDs

Several files had hardcoded fallback model IDs that were different from what was specified in the `.env` file:

- In `test_bedrock.py`, there were multiple occurrences of hardcoded model IDs:
  - `model_id = os.environ.get("BEDROCK_LLM_MODEL", "amazon.titan-text-lite-v1")`
  - `model_id = os.environ.get("BEDROCK_LLM_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")`
  - `model_id = os.environ.get("BEDROCK_LLM_MODEL", "amazon.titan-text-express-v1")`

- In `app/nl-query/app.py`:
  - `self.llm_model_id = os.environ.get("BEDROCK_LLM_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")`
  - `self.embedding_model_id = os.environ.get("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")`
  - `self.rerank_model_id = os.environ.get("BEDROCK_RERANK_MODEL", "amazon.rerank-v1:0")`

- In `app/langchain-query/app.py`:
  - `self.llm_model_id = os.environ.get("BEDROCK_LLM_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")`

### 2. Missing Environment Variable Passing

The `podman-compose.yml` file wasn't passing the Bedrock model environment variables to the containers:

- Missing in `nl-query-service` environment section:
  - `BEDROCK_LLM_MODEL`
  - `BEDROCK_EMBEDDING_MODEL`
  - `BEDROCK_RERANK_MODEL`

- Missing in `langchain-query-service` environment section:
  - `BEDROCK_LLM_MODEL`
  - `BEDROCK_EMBEDDING_MODEL`
  - `BEDROCK_RERANK_MODEL`

## Fixes Applied

### 1. Removed Hardcoded Model IDs

Modified all files to not use fallback values for model IDs, but instead fail with a clear error if the environment variables are not set:

- Updated `test_bedrock.py`:
  ```python
  model_id = os.environ.get("BEDROCK_LLM_MODEL")
  if not model_id:
      logger.error("BEDROCK_LLM_MODEL not found in environment variables")
      return False
  ```

- Updated `app/nl-query/app.py`:
  ```python
  self.llm_model_id = os.environ.get("BEDROCK_LLM_MODEL")
  if not self.llm_model_id:
      logger.error("BEDROCK_LLM_MODEL not found in environment variables")
      raise ValueError("BEDROCK_LLM_MODEL not found in environment variables")
  ```

- Updated `app/langchain-query/app.py` in a similar way.

### 2. Updated podman-compose.yml

Added the missing environment variables to the container definitions:

```yaml
environment:
  - DATABASE_API_URL=http://sqlite-db:5000
  - LOG_LEVEL=DEBUG
  - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
  - BEDROCK_LLM_MODEL=${BEDROCK_LLM_MODEL}
  - BEDROCK_EMBEDDING_MODEL=${BEDROCK_EMBEDDING_MODEL}
  - BEDROCK_RERANK_MODEL=${BEDROCK_RERANK_MODEL}
```

## Verification

After applying these fixes, the system will:

1. Properly use the model specified in the `.env` file: `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
2. Fail with a clear error message if any of the required environment variables are missing
3. Pass the correct model IDs to the containers when using podman-compose

To verify the fix, rebuild and restart the services:

```bash
cd /root/aws.git/AI_integrated_search_mcp
./rebuild_services.sh
```

## Notes

- AWS credentials are still only sourced from host OS environment variables, not from the `.env` file
- Bedrock model configurations are sourced from the `.env` file
- The containers must have the required environment variables set before they will work properly
