#!/bin/bash

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================${NC}"
echo -e "${BOLD}patentDWH - AWS Credentials Fix${NC}"
echo -e "${BLUE}==============================${NC}"
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Starting implementation${NC}"

# Determine container command (podman or docker)
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo -e "${GREEN}[INFO] Using Podman for containerization${NC}"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}[INFO] Using Docker for containerization${NC}"
    if command -v docker-compose &> /dev/null && ! docker compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    fi
else
    echo -e "${RED}[ERROR] Neither podman nor docker found. Please install one of them.${NC}"
    exit 1
fi

# Check if the patched files exist
echo -e "${BLUE}[INFO] Checking patched files...${NC}"
if [ ! -f "app/patched_nl_query_processor.py" ] || [ ! -f "app/patched_server.py" ]; then
    echo -e "${RED}[ERROR] Patched files not found. Please ensure you have created:${NC}"
    echo -e "${RED}  - app/patched_nl_query_processor.py${NC}"
    echo -e "${RED}  - app/patched_server.py${NC}"
    exit 1
fi

# Back up original files
echo -e "${BLUE}[INFO] Backing up original files...${NC}"
if [ -f "app/nl_query_processor.py" ]; then
    cp -f "app/nl_query_processor.py" "app/nl_query_processor.py.bak"
    echo -e "${GREEN}[INFO] Backed up nl_query_processor.py${NC}"
fi

if [ -f "app/server.py" ]; then
    cp -f "app/server.py" "app/server.py.bak"
    echo -e "${GREEN}[INFO] Backed up server.py${NC}"
fi

# Deploy the patched files
echo -e "${BLUE}[INFO] Deploying patched files...${NC}"
cp -f "app/patched_nl_query_processor.py" "app/nl_query_processor.py"
cp -f "app/patched_server.py" "app/server.py"
echo -e "${GREEN}[INFO] Deployed patched files successfully${NC}"

# Set AWS credentials environment variables for the container
echo -e "${BLUE}[INFO] Setting up AWS credentials in environment...${NC}"
# Note: AWS_REGIONは使わず、AWS_DEFAULT_REGIONを利用すること。
export AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-dummy_access_key}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-dummy_secret_key}

echo -e "${GREEN}[INFO] Using the following AWS credentials:${NC}"
echo -e "  - AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
echo -e "  - AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:4}...${AWS_ACCESS_KEY_ID:(-4)}"
echo -e "  - AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:0:4}...${AWS_SECRET_ACCESS_KEY:(-4)}"

# Restart the MCP server container
echo -e "${BLUE}[INFO] Restarting MCP server container...${NC}"
$COMPOSE_CMD restart patentdwh-mcp
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Failed to restart patentdwh-mcp container.${NC}"
    echo -e "${YELLOW}[INFO] Attempting alternative restart approach...${NC}"
    $COMPOSE_CMD down
    $COMPOSE_CMD up -d
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to restart containers.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}[INFO] MCP server restarted successfully${NC}"

# Wait for service to start
echo -e "${BLUE}[INFO] Waiting for service to initialize...${NC}"
sleep 5

# Check if the service is running
echo -e "${BLUE}[INFO] Checking if service is available...${NC}"
curl -s http://localhost:8080/api/aws-status > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Service may not be fully available yet.${NC}"
    echo -e "${YELLOW}[WARNING] Waiting a few more seconds...${NC}"
    sleep 5
fi

# Check AWS credentials status
echo -e "${BLUE}[INFO] Checking AWS credentials status...${NC}"
AWS_STATUS=$(curl -s http://localhost:8080/api/aws-status)
echo -e "${GREEN}[INFO] AWS credentials status: ${NC}"
echo $AWS_STATUS | python3 -m json.tool

# Summary
echo -e "${BLUE}==============================${NC}"
echo -e "${GREEN}[SUCCESS] Implementation complete!${NC}"
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Implementation finished${NC}"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo -e "  1. You can now test natural language queries with the patched system."
echo -e "  2. If using real AWS credentials, make sure to update them in your environment."
echo -e "  3. To test a query, try: ${BLUE}curl -X POST -H \"Content-Type: application/json\" -d '{\"tool_name\": \"patent_nl_query\", \"tool_input\": {\"query\": \"ソニーが出願した人工知能関連の特許を教えてください\", \"db_type\": \"google_patents_gcp\"}}' http://localhost:8080/api/v1/mcp${NC}"
echo ""
echo -e "${BOLD}Useful commands:${NC}"
echo -e "  - Check logs:          ${BLUE}$COMPOSE_CMD logs -f patentdwh-mcp${NC}"
echo -e "  - Check AWS status:    ${BLUE}curl http://localhost:8080/api/aws-status${NC}"
echo -e "  - Check service health: ${BLUE}curl http://localhost:8080/health${NC}"
echo -e "  - Restore backups:     ${BLUE}mv app/nl_query_processor.py.bak app/nl_query_processor.py && mv app/server.py.bak app/server.py${NC}"
echo -e "${BLUE}==============================${NC}"
