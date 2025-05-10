#!/bin/bash

# Enhanced patentDWH setup script with LangChain support
# This script will set up the enhanced patentDWH system with LangChain support in containers

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== patentDWH 強化版LangChain機能セットアップ（コンテナ版） ===${NC}"
echo ""

# Function to display error message and exit
error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
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

# Create a docker-compose file for enhanced version
echo -e "${BLUE}[INFO] Creating container compose file for enhanced version...${NC}"

cat > docker-compose.enhanced.yml << EOL
version: '3'

services:
  patentdwh-db:
    build:
      context: ./db
    container_name: patentdwh-db
    ports:
      - "5002:5002"
    volumes:
      - ./data:/app/data
    environment:
      - PORT=5002
    restart: unless-stopped

  patentdwh-mcp-enhanced:
    build:
      context: ./app
      dockerfile: Dockerfile.enhanced
    container_name: patentdwh-mcp-enhanced
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - PATENT_DB_URL=http://patentdwh-db:5002
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION:-us-east-1}
    depends_on:
      - patentdwh-db
    restart: unless-stopped
EOL

# Check AWS credentials
echo -e "${BLUE}[INFO] Checking AWS credentials...${NC}"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}[WARNING] AWS credentials not set in environment.${NC}"
    echo "To use Bedrock services, please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION."
    echo "Example:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_REGION=us-east-1"
else
    echo -e "${GREEN}[INFO] AWS credentials found in environment.${NC}"
fi

# Build and start containers
echo -e "${BLUE}[INFO] Building enhanced containers...${NC}"
$COMPOSE_CMD -f docker-compose.enhanced.yml build
if [ $? -ne 0 ]; then
    error_exit "Failed to build containers. Check the error messages above."
fi
echo -e "${GREEN}[INFO] Container build successful${NC}"

echo -e "${BLUE}[INFO] Starting enhanced containers...${NC}"
$COMPOSE_CMD -f docker-compose.enhanced.yml up -d
if [ $? -ne 0 ]; then
    error_exit "Failed to start containers. Check the error messages above."
fi
echo -e "${GREEN}[INFO] Enhanced containers started successfully${NC}"

echo -e "${BLUE}[INFO] Container status:${NC}"
$COMPOSE_CMD -f docker-compose.enhanced.yml ps

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
    $COMPOSE_CMD -f docker-compose.enhanced.yml ps
    $COMPOSE_CMD -f docker-compose.enhanced.yml logs --tail 50 patentdwh-db
fi

# Check MCP service
echo -e "${BLUE}[INFO] Checking enhanced MCP service...${NC}"
MCP_HEALTH=$(curl -s -w "%{http_code}" -o /tmp/mcp_response.txt "http://localhost:8080/health")
if [ "$MCP_HEALTH" = "200" ] && grep -q "healthy" /tmp/mcp_response.txt; then
    echo -e "${GREEN}[SUCCESS] Enhanced MCP service is running!${NC}"
    echo -e "  - Response: $(cat /tmp/mcp_response.txt)"
else
    echo -e "${RED}[WARNING] Enhanced MCP service may not be running properly.${NC}"
    echo -e "  - HTTP status: $MCP_HEALTH"
    if [ -f /tmp/mcp_response.txt ]; then
        echo -e "  - Response: $(cat /tmp/mcp_response.txt)"
    else
        echo -e "  - No response received"
    fi
    $COMPOSE_CMD -f docker-compose.enhanced.yml logs --tail 50 patentdwh-mcp-enhanced
fi

# Summary
echo -e "${BLUE}==============================${NC}"
if [ "$DB_HEALTH" = "200" ] && [ "$MCP_HEALTH" = "200" ]; then
    echo -e "${GREEN}[SUCCESS] Enhanced setup complete!${NC}"
else
    echo -e "${YELLOW}[WARNING] Setup completed with warnings!${NC}"
fi
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Setup finished${NC}"
echo ""
echo -e "${BOLD}Access Information:${NC}"
echo -e "  - Database UI:   ${GREEN}http://localhost:5002/${NC}"
echo -e "  - Enhanced MCP API: ${GREEN}http://localhost:8080/${NC}"
echo ""
echo -e "${BOLD}MCP configuration for Claude:${NC}"
echo '{
  "serverName": "patentDWH",
  "description": "Enhanced Patent DWH MCP Server with LangChain",
  "url": "http://localhost:8080/api/v1/mcp"
}'
echo ""
echo -e "${BOLD}Example API usage:${NC}"
echo -e "curl -X POST http://localhost:8080/api/nl-query \\"
echo -e "  -H \"Content-Type: application/json\" \\"
echo -e "  -d '{\"query\": \"2020年以降に出願された人工知能に関する特許を教えてください\", \"db_type\": \"inpit\", \"use_langchain_first\": true}' | jq"
echo ""
echo -e "${BOLD}Useful Commands:${NC}"
echo -e "  - View logs:               ${BLUE}$COMPOSE_CMD -f docker-compose.enhanced.yml logs -f${NC}"
echo -e "  - View specific container: ${BLUE}$COMPOSE_CMD -f docker-compose.enhanced.yml logs -f [patentdwh-db|patentdwh-mcp-enhanced]${NC}"
echo -e "  - Stop services:           ${BLUE}$COMPOSE_CMD -f docker-compose.enhanced.yml down${NC}"
echo -e "  - Restart services:        ${BLUE}$COMPOSE_CMD -f docker-compose.enhanced.yml restart${NC}"
echo -e "${BLUE}==============================${NC}"
echo ""
echo -e "${GREEN}For more details, see ENHANCED_LANGCHAIN_USAGE.md${NC}"
echo ""

exit 0
