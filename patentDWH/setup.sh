#!/bin/bash

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to display error message and exit
error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

# Function to show logs when issues occur
show_service_logs() {
    local service=$1
    echo -e "${YELLOW}[INFO] Showing last 50 lines of logs for $service...${NC}"
    $COMPOSE_CMD logs --tail 50 $service
}

# Function to check port availability
check_port() {
    local port=$1
    if command -v netstat &>/dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            echo -e "${YELLOW}[WARNING] Port $port is already in use. This might cause conflicts.${NC}"
        fi
    elif command -v ss &>/dev/null; then
        if ss -tuln | grep -q ":$port "; then
            echo -e "${YELLOW}[WARNING] Port $port is already in use. This might cause conflicts.${NC}"
        fi
    else
        echo -e "${YELLOW}[WARNING] Cannot check if port $port is available (netstat/ss not found).${NC}"
    fi
}

echo -e "${BLUE}==============================${NC}"
echo -e "${BOLD}patentDWH - Patent Database Setup${NC}"
echo -e "${BLUE}==============================${NC}"
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Starting setup${NC}"

# Check for root privileges (requested in task)
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Not running as root. Some operations might fail.${NC}"
    echo -e "${YELLOW}[WARNING] Consider running with 'sudo su -' as specified.${NC}"
fi

# Environment check
echo -e "${BLUE}[INFO] System Information:${NC}"
echo -e "  - Hostname: $(hostname)"
echo -e "  - OS: $(uname -s)"
echo -e "  - Kernel: $(uname -r)"
echo -e "  - User: $(id)"

# Check for podman or docker
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo -e "${GREEN}[INFO] Using Podman for containerization${NC}"
    echo -e "  - Podman version: $(podman --version)"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}[INFO] Using Docker for containerization${NC}"
    echo -e "  - Docker version: $(docker --version)"
    if command -v docker-compose &> /dev/null && ! command -v "docker compose" &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        echo -e "${YELLOW}[INFO] Using docker-compose command${NC}"
    fi
    echo -e "  - Docker Compose version: $($COMPOSE_CMD --version)"
else
    error_exit "Neither podman nor docker found. Please install one of them."
fi

# Check required ports
echo -e "${BLUE}[INFO] Checking required ports...${NC}"
check_port 5002
check_port 8080

# Creating directories
echo -e "${BLUE}[INFO] Creating necessary directories...${NC}"
mkdir -p data/db
if [ $? -ne 0 ]; then
    error_exit "Failed to create data directories."
fi
echo -e "${GREEN}[INFO] Created data directories successfully${NC}"

# Checking AWS credentials if needed
echo -e "${BLUE}[INFO] Checking AWS credentials...${NC}"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}[WARNING] AWS credentials not set as environment variables.${NC}"
    echo -e "${YELLOW}[WARNING] Data download from S3 may fail. Consider setting AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.${NC}"
else
    echo -e "${GREEN}[INFO] AWS credentials are set${NC}"
fi

# Building and starting containers with error handling
echo -e "${BLUE}[INFO] Building containers...${NC}"
$COMPOSE_CMD build
if [ $? -ne 0 ]; then
    error_exit "Failed to build containers. Check the error messages above."
fi
echo -e "${GREEN}[INFO] Container build successful${NC}"

echo -e "${BLUE}[INFO] Starting containers...${NC}"
$COMPOSE_CMD up -d
if [ $? -ne 0 ]; then
    error_exit "Failed to start containers. Check the error messages above."
fi
echo -e "${GREEN}[INFO] Containers started successfully${NC}"

echo -e "${BLUE}[INFO] Container status:${NC}"
$COMPOSE_CMD ps

# Wait for services to start with progress indicator
echo -e "${BLUE}[INFO] Waiting for services to start...${NC}"
for i in {1..15}; do
    echo -ne "\r  - Progress: ${i}/15"
    sleep 1
done
echo -e "\r  - Waited 15 seconds for services to initialize          "

# Check database service with more detailed diagnostics
echo -e "${BLUE}[INFO] Checking database service...${NC}"
DB_HEALTH=$(curl -s -w "%{http_code}" -o /tmp/db_response.txt "http://localhost:5002/health")
if [ "$DB_HEALTH" = "200" ] && grep -q "healthy" /tmp/db_response.txt; then
    echo -e "${GREEN}[SUCCESS] Database service is running!${NC}"
    echo -e "  - Response: $(cat /tmp/db_response.txt)"
else
    echo -e "${RED}[WARNING] Database service may not be running properly.${NC}"
    echo -e "  - HTTP status: $DB_HEALTH"
    if [ -f /tmp/db_response.txt ]; then
        echo -e "  - Response: $(cat /tmp/db_response.txt)"
    else
        echo -e "  - No response received"
    fi
    echo -e "${YELLOW}[INFO] Checking if containers are running...${NC}"
    $COMPOSE_CMD ps
    show_service_logs "patentdwh-db"
fi

# Check MCP service
echo -e "${BLUE}[INFO] Checking MCP service...${NC}"
MCP_HEALTH=$(curl -s -w "%{http_code}" -o /tmp/mcp_response.txt "http://localhost:8080/health")
if [ "$MCP_HEALTH" = "200" ] && grep -q "healthy" /tmp/mcp_response.txt; then
    echo -e "${GREEN}[SUCCESS] MCP service is running!${NC}"
    echo -e "  - Response: $(cat /tmp/mcp_response.txt)"
else
    echo -e "${RED}[WARNING] MCP service may not be running properly.${NC}"
    echo -e "  - HTTP status: $MCP_HEALTH"
    if [ -f /tmp/mcp_response.txt ]; then
        echo -e "  - Response: $(cat /tmp/mcp_response.txt)"
    else
        echo -e "  - No response received"
    fi
    show_service_logs "patentdwh-mcp"
fi

# Check database content (if services are running)
if [ "$DB_HEALTH" = "200" ] && [ "$MCP_HEALTH" = "200" ]; then
    echo -e "${BLUE}[INFO] Checking database contents via API...${NC}"
    DB_INFO=$(curl -s "http://localhost:8080/api/status")
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[INFO] Database information:${NC}"
        echo "$DB_INFO" | grep -o '"record_count":[^,}]*' || echo "  - No record count information available"
    else
        echo -e "${YELLOW}[WARNING] Could not retrieve database information${NC}"
    fi
fi

# Summary
echo -e "${BLUE}==============================${NC}"
if [ "$DB_HEALTH" = "200" ] && [ "$MCP_HEALTH" = "200" ]; then
    echo -e "${GREEN}[SUCCESS] Setup complete!${NC}"
else
    echo -e "${YELLOW}[WARNING] Setup completed with warnings!${NC}"
fi
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Setup finished${NC}"
echo ""
echo -e "${BOLD}Access Information:${NC}"
echo -e "  - Database UI:   ${GREEN}http://localhost:5002/${NC}"
echo -e "  - MCP API:       ${GREEN}http://localhost:8080/${NC}"
echo ""
echo -e "${BOLD}MCP configuration for Claude:${NC}"
echo '{
  "serverName": "patentDWH",
  "description": "Patent DWH MCP Server",
  "url": "http://localhost:8080/api/v1/mcp"
}'
echo ""
echo -e "${BOLD}Useful Commands:${NC}"
echo -e "  - View logs:               ${BLUE}$COMPOSE_CMD logs -f${NC}"
echo -e "  - View specific container: ${BLUE}$COMPOSE_CMD logs -f [patentdwh-db|patentdwh-mcp]${NC}"
echo -e "  - Stop services:           ${BLUE}$COMPOSE_CMD down${NC}"
echo -e "  - Restart services:        ${BLUE}$COMPOSE_CMD restart${NC}"
echo -e "  - Start shell in DB:       ${BLUE}$COMPOSE_CMD exec patentdwh-db /bin/bash${NC}"
echo -e "${BLUE}==============================${NC}"
