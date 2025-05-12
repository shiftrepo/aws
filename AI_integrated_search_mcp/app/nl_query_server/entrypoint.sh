#!/bin/bash

set -e

# Enable detailed logging
echo "Starting Natural Language Query MCP Service $(date)"

# Create necessary directories
mkdir -p /app/data/cache

# Set environment variables if not set
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-"ap-northeast-1"}
export LLM_MODEL=${LLM_MODEL:-"us.anthropic.claude-3-7-sonnet-20250219-v1:0"}
export EMBED_MODEL=${EMBED_MODEL:-"amazon.titan-embed-text-v2:0"}
export RERANK_MODEL=${RERANK_MODEL:-"amazon.rerank-v1:0"}

echo "Configured with AWS region: $AWS_DEFAULT_REGION"
echo "LLM Model: $LLM_MODEL"
echo "Embedding Model: $EMBED_MODEL"
echo "Reranking Model: $RERANK_MODEL"
echo "SQLite API URL: $SQLITE_API_URL"

# Wait for SQLite API to be ready
echo "Waiting for SQLite API to be available at $SQLITE_API_URL"
until $(curl --output /dev/null --silent --head --fail $SQLITE_API_URL/health); do
    echo "Waiting for SQLite API..."
    sleep 5
done

echo "SQLite API is available. Starting MCP server..."

# Start the FastAPI server with MCP protocol
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
