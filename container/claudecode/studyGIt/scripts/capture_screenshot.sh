#!/bin/bash

# Screenshot capture utility for GitPlayground Docker Visualizer
# This script captures screenshots of the application for documentation and reporting

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCREENSHOT_DIR="../screenshots"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create screenshot directory if it doesn't exist
mkdir -p "$SCREENSHOT_DIR"

echo -e "${BLUE}===== Screenshot Capture Utility =====${NC}"
echo "Current date: $(date)"

# Function to check if application is accessible
check_app() {
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
  
  if [ "$HTTP_CODE" = "200" ]; then
    return 0
  else
    return 1
  fi
}

# Check if Firefox is installed
capture_with_firefox() {
  local url="$1"
  local output="$2"
  
  if command -v firefox >/dev/null 2>&1; then
    firefox --screenshot "$output" "$url" >/dev/null 2>&1
    return $?
  else
    return 1
  fi
}

# Check if Chrome/Chromium is installed
capture_with_chrome() {
  local url="$1"
  local output="$2"
  
  if command -v google-chrome >/dev/null 2>&1; then
    google-chrome --headless --screenshot="$output" "$url" >/dev/null 2>&1
    return $?
  elif command -v chromium >/dev/null 2>&1; then
    chromium --headless --screenshot="$output" "$url" >/dev/null 2>&1
    return $?
  else
    return 1
  fi
}

# Capture screenshot using available tools
capture_screenshot() {
  local url="$1"
  local name="$2"
  local output="${SCREENSHOT_DIR}/${name}_${TIMESTAMP}.png"
  
  echo -e "${BLUE}Capturing screenshot of: ${url}${NC}"
  
  if capture_with_firefox "$url" "$output"; then
    echo -e "${GREEN}Screenshot captured with Firefox: ${output}${NC}"
    return 0
  elif capture_with_chrome "$url" "$output"; then
    echo -e "${GREEN}Screenshot captured with Chrome/Chromium: ${output}${NC}"
    return 0
  else
    echo -e "${RED}Failed to capture screenshot automatically${NC}"
    echo "Please capture a screenshot manually of URL: $url"
    echo "Then save it to: $output"
    return 1
  fi
}

# Check if the application is running
if ! check_app; then
  echo -e "${RED}Error: Application is not accessible at http://localhost:3000${NC}"
  echo "Please make sure the Docker container is running before taking screenshots"
  exit 1
fi

# Capture screenshots of different views
capture_screenshot "http://localhost:3000" "homepage"
capture_screenshot "http://localhost:3000/playground?username=TestUser" "playground"
capture_screenshot "http://localhost:3000/playground?username=TestUser&tab=docker" "docker_view"

echo -e "${BLUE}===== Screenshot Capture Complete =====${NC}"
echo "Screenshots saved to: $SCREENSHOT_DIR"
echo "Use these screenshots in your GitHub issue updates"

# Create a markdown snippet for easy GitHub inclusion
MARKDOWN_FILE="${SCREENSHOT_DIR}/screenshot_links_${TIMESTAMP}.md"
cat > "$MARKDOWN_FILE" << EOF
## Screenshots (${TIMESTAMP})

![Homepage](../screenshots/homepage_${TIMESTAMP}.png)
*Homepage view showing GitPlayground landing page*

![Playground](../screenshots/playground_${TIMESTAMP}.png)
*Main playground interface with Docker tab*

![Docker View](../screenshots/docker_view_${TIMESTAMP}.png)
*Docker Visualizer component showing container relationships*

EOF

echo -e "${GREEN}Markdown snippet created: ${MARKDOWN_FILE}${NC}"
echo "Copy this content to your GitHub issue update"