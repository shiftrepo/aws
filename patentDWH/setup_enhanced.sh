#!/bin/bash

# Enhanced patentDWH setup script with LangChain support
# This script will set up the enhanced patentDWH system with LangChain support

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== patentDWH 強化版LangChain機能セットアップ ===${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found.${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not found.${NC}"
    echo "Please install pip3 and try again."
    exit 1
fi

# Create a virtual environment if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        echo "Please install the venv module and try again."
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists. Using existing one.${NC}"
fi

# Activate the virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install the required packages
echo -e "${YELLOW}Installing required packages...${NC}"
pip3 install -r app/requirements_enhanced.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install required packages.${NC}"
    echo "Please check your internet connection and try again."
    exit 1
fi
echo -e "${GREEN}Required packages installed successfully.${NC}"

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${YELLOW}Warning: AWS credentials not set in environment.${NC}"
    echo "To use Bedrock services, please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION."
    echo "Example:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_REGION=us-east-1"
else
    echo -e "${GREEN}AWS credentials found in environment.${NC}"
fi

# Print instructions
echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo ""
echo -e "${YELLOW}Instructions to start the enhanced server:${NC}"
echo ""
echo "1. Make sure AWS credentials are set if not already:"
echo "   export AWS_ACCESS_KEY_ID=your_access_key"
echo "   export AWS_SECRET_ACCESS_KEY=your_secret_key"
echo "   export AWS_REGION=us-east-1"
echo ""
echo "2. Ensure the database service is running:"
echo "   podman-compose up -d patentdwh-db"
echo "   # Or with docker:"
echo "   docker compose up -d patentdwh-db"
echo ""
echo "3. Start the enhanced server:"
echo "   python3 app/server_with_enhanced_nl.py"
echo ""
echo "4. The server will be available at http://localhost:8080"
echo ""
echo -e "${YELLOW}Example API usage:${NC}"
echo ""
echo "curl -X POST http://localhost:8080/api/nl-query \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"query\": \"2020年以降に出願された人工知能に関する特許を教えてください\", \"db_type\": \"inpit\", \"use_langchain_first\": true}'"
echo ""
echo -e "${GREEN}For more details, see ENHANCED_LANGCHAIN_USAGE.md${NC}"
echo ""

# Deactivate the virtual environment
deactivate

exit 0
