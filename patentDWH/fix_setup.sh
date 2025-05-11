#!/bin/bash

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================${NC}"
echo -e "${BOLD}patentDWH - Fix Setup Script${NC}"
echo -e "${BLUE}==============================${NC}"
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Starting fix${NC}"

# Check for podman or docker
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo -e "${GREEN}[INFO] Using Podman for containerization${NC}"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}[INFO] Using Docker for containerization${NC}"
    if command -v docker-compose &> /dev/null && ! command -v "docker compose" &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    fi
else
    echo -e "${RED}[ERROR] Neither podman nor docker found. Please install one of them.${NC}"
    exit 1
fi

# 1. Stop and clean up existing containers
echo -e "${YELLOW}[INFO] Stopping and removing existing containers...${NC}"
$CONTAINER_CMD stop -a 2>/dev/null || true
$CONTAINER_CMD rm -f $($CONTAINER_CMD ps -a -q) 2>/dev/null || true

# 2. Create a patched docker-compose file with explicit network configuration
echo -e "${YELLOW}[INFO] Creating patched compose file...${NC}"
cat > docker-compose.patched.yml << EOL
version: '3'

services:
  patentdwh-db:
    image: patentdwh-db:latest
    container_name: patentdwh-db
    build:
      context: ./db
      dockerfile: Dockerfile
    ports:
      - "5002:5002"
    environment:
      - AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=ap-northeast-1
      - SKIP_DATA_DOWNLOAD=false
    volumes:
      - ./data:/app/data:z
    user: "root:root"
    restart: unless-stopped
    networks:
      - patent-network

  patentdwh-mcp:
    build:
      context: ./app
      dockerfile: Dockerfile
    container_name: patentdwh-mcp
    environment:
      - PATENT_DB_URL=http://patentdwh-db:5002
      - AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=ap-northeast-1
      - GCP_CREDENTIALS_S3_BUCKET=ndi-3supervision
      - GCP_CREDENTIALS_S3_KEY=MIT/GCPServiceKey/tosapi-bf0ac4918370.json
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data:z
      - ./data/db:/app/data/db:z
    user: "root:root"
    depends_on:
      - patentdwh-db
    restart: unless-stopped
    networks:
      - patent-network

  patentdwh-mcp-enhanced:
    build:
      context: ./app
      dockerfile: Dockerfile.enhanced
    container_name: patentdwh-mcp-enhanced
    environment:
      - PATENT_DB_URL=http://patentdwh-db:5002
      - AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=ap-northeast-1
      - GCP_CREDENTIALS_S3_BUCKET=ndi-3supervision
      - GCP_CREDENTIALS_S3_KEY=MIT/GCPServiceKey/tosapi-bf0ac4918370.json
    ports:
      - "8080"
    volumes:
      - ./data:/app/data:z
      - ./data/db:/app/data/db:z
    user: "root:root"
    depends_on:
      - patentdwh-db
    networks:
      - patent-network

networks:
  patent-network:
    driver: bridge
EOL

# 3. Build and start containers with the patched config
echo -e "${YELLOW}[INFO] Building containers with patched config...${NC}"
$COMPOSE_CMD -f docker-compose.patched.yml build

echo -e "${YELLOW}[INFO] Starting containers with patched config...${NC}"
$COMPOSE_CMD -f docker-compose.patched.yml up -d

# 4. Wait for services to start
echo -e "${YELLOW}[INFO] Waiting 20 seconds for services to initialize...${NC}"
for i in $(seq 1 20); do
    echo -ne "\r  - Progress: $i/20"
    sleep 1
done
echo -e "\r  - Waited 20 seconds for services to initialize          "

# 5. Check services
echo -e "${YELLOW}[INFO] Checking services...${NC}"
$COMPOSE_CMD -f docker-compose.patched.yml ps

echo -e "${GREEN}[SUCCESS] Setup fix completed!${NC}"
echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S') Fix completed${NC}"
echo -e "${YELLOW}[INFO] You can now access:${NC}"
echo -e "  - Database UI:   ${GREEN}http://localhost:5002/${NC}"
echo -e "  - MCP API:       ${GREEN}http://localhost:8080/${NC}"
echo ""
echo -e "${YELLOW}[INFO] To view logs, run:${NC}"
echo -e "  ${BLUE}cd patentDWH && $COMPOSE_CMD -f docker-compose.patched.yml logs -f${NC}"
