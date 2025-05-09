#!/bin/bash

# Test script for Natural Language Query MCP endpoints
# This script demonstrates how to query the patent databases using natural language

# Set the base URL for the server
BASE_URL="http://localhost:8000"

# 1. Get help information about Inpit database NL querying
echo "Getting INPIT database natural language query help..."
curl -s "$BASE_URL/nl-query/help/inpit" | python -m json.tool

echo -e "\n\n"

# 2. Get help information about Google Patents database NL querying
echo "Getting Google Patents database natural language query help..."
curl -s "$BASE_URL/nl-query/help/google-patents" | python -m json.tool

echo -e "\n\n"

# 3. Execute a natural language query against INPIT database
echo "Executing natural language query against INPIT database..."
curl -s -X POST "$BASE_URL/nl-query/inpit" \
  -d "query=トヨタによる自動車関連の特許を5件表示して" \
  | python -m json.tool

echo -e "\n\n"

# 4. Execute a natural language query against INPIT database with JSON
echo "Executing natural language query against INPIT database with JSON..."
curl -s -X POST "$BASE_URL/nl-query/inpit/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "ソニーの2019年以降のカメラ技術に関する特許"}' \
  | python -m json.tool

echo -e "\n\n"

# 5. Execute a natural language query against Google Patents database
echo "Executing natural language query against Google Patents database..."
curl -s -X POST "$BASE_URL/nl-query/google-patents" \
  -d "query=Show me 5 recent patents about electric vehicles from Toyota" \
  | python -m json.tool

echo -e "\n\n"

# 6. Execute a natural language query against Google Patents database with JSON
echo "Executing natural language query against Google Patents database with JSON..."
curl -s -X POST "$BASE_URL/nl-query/google-patents/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find patents related to semiconductor technology published after 2020"}' \
  | python -m json.tool

echo -e "\n\n"

# Make the script executable
# chmod +x nl_query_examples.sh
