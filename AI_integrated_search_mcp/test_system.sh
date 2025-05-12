#!/bin/bash

# AI Integrated Search MCP - System Test Script
# This script tests the functionality of the system components

set -e

echo "===== AI Integrated Search MCP ====="
echo "Starting system test at $(date)"

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "ERROR: curl is not installed"
    echo "Please install curl to run this test"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "WARNING: jq is not installed"
    echo "Some test results will not be formatted nicely"
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Get base URL from environment or use default
SQLITE_API_URL=${SQLITE_API_URL:-"http://localhost:5001"}
MCP_API_URL=${MCP_API_URL:-"http://localhost:8000"}
WEB_UI_URL=${WEB_UI_URL:-"http://localhost:5002"}

# Test functions
test_sqlite_api() {
    echo ""
    echo "Testing SQLite API at $SQLITE_API_URL"
    echo "------------------------------------"

    # Test health endpoint
    echo "Testing health endpoint..."
    health_response=$(curl -s $SQLITE_API_URL/health)
    echo "Response: $health_response"
    
    # Test tables endpoint
    echo ""
    echo "Testing tables endpoint..."
    tables_response=$(curl -s $SQLITE_API_URL/tables)
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Tables found: $(echo $tables_response | jq -r '.tables | join(", ")')"
    else
        echo "Response: $tables_response"
    fi
    
    # Test query execution
    echo ""
    echo "Testing SQL execution - user count query..."
    user_count_response=$(curl -s -X POST $SQLITE_API_URL/execute \
        -H "Content-Type: application/json" \
        -d '{"query": "SELECT COUNT(*) as user_count FROM users"}')
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "User count: $(echo $user_count_response | jq -r '.rows[0].user_count')"
    else
        echo "Response: $user_count_response"
    fi
    
    # Test sample queries endpoint
    echo ""
    echo "Testing sample queries endpoint..."
    sample_queries_response=$(curl -s $SQLITE_API_URL/sample_queries)
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Sample queries found: $(echo $sample_queries_response | jq -r '.sample_queries | length')"
        echo "First query: $(echo $sample_queries_response | jq -r '.sample_queries[0].name')"
    else
        echo "Response: Sample queries received"
    fi
}

test_nl_query_api() {
    echo ""
    echo "Testing NL Query API at $MCP_API_URL"
    echo "------------------------------------"
    
    # Test health endpoint
    echo "Testing health endpoint..."
    health_response=$(curl -s $MCP_API_URL/health)
    echo "Response: $health_response"
    
    # Test natural language query
    echo ""
    echo "Testing natural language query execution..."
    nl_query_response=$(curl -s -X POST $MCP_API_URL/query \
        -H "Content-Type: application/json" \
        -d '{"query": "How many users are in the database?", "max_results": 5}')
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Generated SQL: $(echo $nl_query_response | jq -r '.generated_sql')"
        echo "Confidence score: $(echo $nl_query_response | jq -r '.confidence_score')"
    else
        echo "Response: NL query processed"
    fi
}

test_web_ui() {
    echo ""
    echo "Testing Web UI at $WEB_UI_URL"
    echo "------------------------------------"
    
    # Test health endpoint
    echo "Testing health endpoint..."
    health_response=$(curl -s $WEB_UI_URL/health)
    echo "Response: $health_response"
    
    # Test main page load
    echo ""
    echo "Testing main page load..."
    main_page_response=$(curl -s -o /dev/null -w "%{http_code}" $WEB_UI_URL/)
    echo "HTTP Status: $main_page_response"
    
    # Test schema page load
    echo ""
    echo "Testing schema page load..."
    schema_page_response=$(curl -s -o /dev/null -w "%{http_code}" $WEB_UI_URL/schema)
    echo "HTTP Status: $schema_page_response"
    
    # Test NL query page load
    echo ""
    echo "Testing NL query page load..."
    nl_page_response=$(curl -s -o /dev/null -w "%{http_code}" $WEB_UI_URL/nl-query)
    echo "HTTP Status: $nl_page_response"
}

# Function to run all tests
run_tests() {
    # Test SQLite API
    test_sqlite_api
    
    # Test NL Query API
    test_nl_query_api
    
    # Test Web UI
    test_web_ui
}

# Check services availability
echo "Checking if services are available..."
echo ""

if curl -s $SQLITE_API_URL/health > /dev/null; then
    echo "✓ SQLite API is running"
else
    echo "✗ SQLite API is not running"
    echo "Make sure you've started the services using ./start_services.sh"
    exit 1
fi

if curl -s $MCP_API_URL/health > /dev/null; then
    echo "✓ NL Query API is running"
else
    echo "✗ NL Query API is not running"
    echo "Make sure you've started the services using ./start_services.sh"
    exit 1
fi

if curl -s $WEB_UI_URL/health > /dev/null; then
    echo "✓ Web UI is running"
else
    echo "✗ Web UI is not running"
    echo "Make sure you've started the services using ./start_services.sh"
    exit 1
fi

echo ""
echo "All services are running. Starting tests..."
run_tests

echo ""
echo "All tests completed at $(date)"
echo ""
echo "To access the Web UI, open a browser and navigate to:"
echo "$WEB_UI_URL"
