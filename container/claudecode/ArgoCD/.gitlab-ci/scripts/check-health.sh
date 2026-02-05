#!/bin/bash
set -e

# ============================================================================
# Script: check-health.sh
# Description: Check health status of backend and frontend services
# ============================================================================

echo "=========================================="
echo "Application Health Check"
echo "=========================================="

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5006}"
MAX_ATTEMPTS="${HEALTH_CHECK_ATTEMPTS:-30}"
RETRY_INTERVAL="${HEALTH_CHECK_INTERVAL:-10}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check backend health
check_backend_health() {
    local url="${BACKEND_URL}/actuator/health"
    echo ""
    echo "Checking backend health: ${url}"

    local attempt=1
    while [ ${attempt} -le ${MAX_ATTEMPTS} ]; do
        echo -n "Attempt ${attempt}/${MAX_ATTEMPTS}: "

        # Make the health check request
        response=$(curl -s -o /tmp/backend-health.json -w "%{http_code}" ${url} 2>/dev/null || echo "000")

        if [ "${response}" = "200" ]; then
            if [ -f /tmp/backend-health.json ]; then
                health_status=$(cat /tmp/backend-health.json | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "UNKNOWN")
                if [ "${health_status}" = "UP" ]; then
                    echo -e "${GREEN}Backend is healthy (status: UP)${NC}"
                    cat /tmp/backend-health.json | head -n 5
                    return 0
                else
                    echo -e "${YELLOW}Backend returned status: ${health_status}${NC}"
                fi
            else
                echo -e "${GREEN}Backend is responding (HTTP 200)${NC}"
                return 0
            fi
        elif [ "${response}" = "000" ]; then
            echo -e "${RED}Backend is not reachable${NC}"
        else
            echo -e "${RED}Backend returned HTTP ${response}${NC}"
        fi

        if [ ${attempt} -lt ${MAX_ATTEMPTS} ]; then
            echo "Waiting ${RETRY_INTERVAL}s before retry..."
            sleep ${RETRY_INTERVAL}
        fi

        attempt=$((attempt + 1))
    done

    echo -e "${RED}ERROR: Backend health check failed after ${MAX_ATTEMPTS} attempts${NC}"
    return 1
}

# Function to check frontend health
check_frontend_health() {
    local url="${FRONTEND_URL}"
    echo ""
    echo "Checking frontend health: ${url}"

    local attempt=1
    while [ ${attempt} -le ${MAX_ATTEMPTS} ]; do
        echo -n "Attempt ${attempt}/${MAX_ATTEMPTS}: "

        # Make the health check request
        response=$(curl -s -o /dev/null -w "%{http_code}" ${url} 2>/dev/null || echo "000")

        if [ "${response}" = "200" ]; then
            echo -e "${GREEN}Frontend is accessible (HTTP 200)${NC}"
            return 0
        elif [ "${response}" = "000" ]; then
            echo -e "${RED}Frontend is not reachable${NC}"
        else
            echo -e "${YELLOW}Frontend returned HTTP ${response}${NC}"
            # Consider 301/302 redirects as success
            if [ "${response}" = "301" ] || [ "${response}" = "302" ]; then
                echo -e "${GREEN}Frontend is accessible (redirect)${NC}"
                return 0
            fi
        fi

        if [ ${attempt} -lt ${MAX_ATTEMPTS} ]; then
            echo "Waiting ${RETRY_INTERVAL}s before retry..."
            sleep ${RETRY_INTERVAL}
        fi

        attempt=$((attempt + 1))
    done

    echo -e "${RED}ERROR: Frontend health check failed after ${MAX_ATTEMPTS} attempts${NC}"
    return 1
}

# Function to display service summary
display_summary() {
    echo ""
    echo "=========================================="
    echo "Health Check Summary"
    echo "=========================================="
    echo "Backend URL: ${BACKEND_URL}"
    echo "Frontend URL: ${FRONTEND_URL}"
    echo "Backend Status: $1"
    echo "Frontend Status: $2"
    echo "=========================================="
}

# Main execution
BACKEND_STATUS="UNKNOWN"
FRONTEND_STATUS="UNKNOWN"
EXIT_CODE=0

# Check backend
if check_backend_health; then
    BACKEND_STATUS="${GREEN}HEALTHY${NC}"
else
    BACKEND_STATUS="${RED}UNHEALTHY${NC}"
    EXIT_CODE=1
fi

# Check frontend
if check_frontend_health; then
    FRONTEND_STATUS="${GREEN}HEALTHY${NC}"
else
    FRONTEND_STATUS="${RED}UNHEALTHY${NC}"
    EXIT_CODE=1
fi

# Display summary
display_summary "${BACKEND_STATUS}" "${FRONTEND_STATUS}"

# Additional diagnostics if health check failed
if [ ${EXIT_CODE} -ne 0 ]; then
    echo ""
    echo "=========================================="
    echo "Diagnostics"
    echo "=========================================="

    echo ""
    echo "Checking if services are running..."
    if command -v podman &> /dev/null; then
        echo "Podman containers:"
        podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true
    elif command -v docker &> /dev/null; then
        echo "Docker containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true
    fi

    echo ""
    echo "Network connectivity test:"
    echo -n "Backend: "
    nc -zv localhost 8080 2>&1 || echo "Port 8080 is not accessible"
    echo -n "Frontend: "
    nc -zv localhost 5006 2>&1 || echo "Port 5006 is not accessible"
fi

echo ""
if [ ${EXIT_CODE} -eq 0 ]; then
    echo -e "${GREEN}All health checks passed successfully!${NC}"
else
    echo -e "${RED}Health check failed. See details above.${NC}"
fi

exit ${EXIT_CODE}
