#!/bin/bash
# Health check script for AI Integrated Search MCP services

echo "================================================="
echo "Health Check for AI Integrated Search MCP Services"
echo "================================================="

# Change to root directory
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Define container names and ports
DATABASE_CONTAINER=${DATABASE_CONTAINER:-sqlite-db}
NL_QUERY_CONTAINER=${NL_QUERY_CONTAINER:-nl-query-service}
WEBUI_CONTAINER=${WEBUI_CONTAINER:-web-ui}
TREND_ANALYSIS_CONTAINER=${TREND_ANALYSIS_CONTAINER:-trend-analysis-service}

DATABASE_API_PORT=${DATABASE_API_PORT:-5003}
NL_QUERY_API_PORT=${NL_QUERY_API_PORT:-5004}
WEBUI_PORT=${WEBUI_PORT:-5002}
TREND_ANALYSIS_API_PORT=${TREND_ANALYSIS_API_PORT:-5006}

# Function for color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

pass() {
  echo -e "${GREEN}✓ PASS:${NC} $1"
}

fail() {
  echo -e "${RED}✗ FAIL:${NC} $1"
}

warn() {
  echo -e "${YELLOW}! WARN:${NC} $1"
}

# Check if containers are running
echo "Checking if containers are running..."

running_containers=$(podman ps --format "{{.Names}}")

check_container() {
  local container=$1
  if echo "$running_containers" | grep -q "$container"; then
    pass "Container $container is running"
    return 0
  else
    fail "Container $container is not running"
    return 1
  fi
}

check_container "$DATABASE_CONTAINER"
db_running=$?

check_container "$NL_QUERY_CONTAINER"
nl_running=$?

check_container "$WEBUI_CONTAINER"
ui_running=$?

check_container "$TREND_ANALYSIS_CONTAINER"
trend_running=$?

echo ""
echo "Checking container health endpoints..."

# Check health endpoints
check_health_endpoint() {
  local container=$1
  local port=$2
  local endpoint="/health"
  
  # Try direct HTTP request first
  if curl -s -f "http://localhost:$port$endpoint" > /dev/null; then
    pass "Health endpoint for container $container is accessible"
    return 0
  else
    fail "Health endpoint for container $container is not responding"
    return 1
  fi
}

if [ $db_running -eq 0 ]; then
  check_health_endpoint "$DATABASE_CONTAINER" "$DATABASE_API_PORT"
  db_healthy=$?
else
  db_healthy=1
fi

if [ $nl_running -eq 0 ]; then
  check_health_endpoint "$NL_QUERY_CONTAINER" "$NL_QUERY_API_PORT"
  nl_healthy=$?
else
  nl_healthy=1
fi

# Check Trend Analysis service health
if [ $trend_running -eq 0 ]; then
  check_health_endpoint "$TREND_ANALYSIS_CONTAINER" "$TREND_ANALYSIS_API_PORT"
  trend_healthy=$?
else
  trend_healthy=1
fi

# Web UI health can be checked through a simple HTTP request
if [ $ui_running -eq 0 ]; then
  if curl -s -f "http://localhost:$WEBUI_PORT/" > /dev/null; then
    pass "Web UI is accessible"
    ui_healthy=0
  else
    fail "Web UI is not responding"
    ui_healthy=1
  fi
else
  ui_healthy=1
fi

echo ""
echo "Testing inter-container connectivity..."

# Test connectivity between containers
if [ $db_running -eq 0 ] && [ $nl_running -eq 0 ]; then
  if podman exec -it "$NL_QUERY_CONTAINER" curl -s -f "http://$DATABASE_CONTAINER:5000/health" > /dev/null; then
    pass "NL Query Service can connect to Database Service"
  else
    fail "NL Query Service cannot connect to Database Service"
  fi
fi

if [ $ui_running -eq 0 ] && [ $db_running -eq 0 ]; then
  if podman exec -it "$WEBUI_CONTAINER" curl -s -f "http://$DATABASE_CONTAINER:5000/health" > /dev/null; then
    pass "Web UI can connect to Database Service"
  else
    fail "Web UI cannot connect to Database Service"
  fi
fi

if [ $ui_running -eq 0 ] && [ $nl_running -eq 0 ]; then
  if podman exec -it "$WEBUI_CONTAINER" curl -s -f "http://$NL_QUERY_CONTAINER:5000/health" > /dev/null; then
    pass "Web UI can connect to NL Query Service"
  else
    fail "Web UI cannot connect to NL Query Service"
  fi
fi

echo ""
echo "Database file status:"

# Check database files
if [ $db_running -eq 0 ]; then
  echo "Checking if database files exist in container..."
  
  if podman exec -it "$DATABASE_CONTAINER" test -f /app/data/inpit.db; then
    file_size=$(podman exec -it "$DATABASE_CONTAINER" stat -c%s /app/data/inpit.db)
    pass "Inpit Database exists (Size: $file_size bytes)"
  else
    fail "Inpit Database does not exist"
  fi
  
  if podman exec -it "$DATABASE_CONTAINER" test -f /app/data/google_patents_gcp.db; then
    file_size=$(podman exec -it "$DATABASE_CONTAINER" stat -c%s /app/data/google_patents_gcp.db)
    pass "BigQuery Database exists (Size: $file_size bytes)"
  else
    fail "BigQuery Database does not exist"
  fi
fi

echo ""
# Check Trend Analysis service
if [ $trend_running -eq 0 ]; then
  check_health_endpoint "$TREND_ANALYSIS_CONTAINER" "$TREND_ANALYSIS_API_PORT"
  trend_healthy=$?
  
  # Test connectivity with database
  if [ $db_running -eq 0 ]; then
    if podman exec -it "$TREND_ANALYSIS_CONTAINER" curl -s -f "http://$DATABASE_CONTAINER:5000/health" > /dev/null; then
      pass "Trend Analysis Service can connect to Database Service"
    else
      fail "Trend Analysis Service cannot connect to Database Service"
    fi
  fi
else
  trend_healthy=1
fi

echo ""
echo "Overall system status:"

if [ $db_healthy -eq 0 ] && [ $nl_healthy -eq 0 ] && [ $ui_healthy -eq 0 ] && [ $trend_healthy -eq 0 ]; then
  echo -e "${GREEN}All systems are running and healthy${NC}"
else
  echo -e "${RED}Some services are not running or not healthy${NC}"
fi

echo ""
echo "Service endpoints:"
echo "Web UI: http://localhost:$WEBUI_PORT"
echo "Database API: http://localhost:$DATABASE_API_PORT"
echo "NL Query API: http://localhost:$NL_QUERY_API_PORT"
echo "Trend Analysis API: http://localhost:$TREND_ANALYSIS_API_PORT"
echo ""

echo "================================================="
echo "Health check completed"
echo "================================================="
