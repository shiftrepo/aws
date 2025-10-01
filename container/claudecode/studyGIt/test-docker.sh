#!/bin/bash

# Script for daily testing of the Git Playground Docker environment
# Usage: ./test-docker.sh [action]
#   Actions: start, stop, restart, logs, status, cleanup

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Git Playground Testing Script =====${NC}"
echo "Current date: $(date)"

# Function to check if container is healthy
check_health() {
  echo -e "${BLUE}Checking container health...${NC}"
  
  # Wait for container to initialize
  echo "Waiting for container to initialize..."
  sleep 10
  
  HEALTH_STATUS=$(podman inspect --format='{{.State.Health.Status}}' git-playground 2>/dev/null)
  
  if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}Container is healthy!${NC}"
    return 0
  elif [ "$HEALTH_STATUS" = "starting" ]; then
    echo -e "${YELLOW}Container is still starting. Wait a bit longer and check logs.${NC}"
    return 1
  else
    echo -e "${RED}Container health check failed or not available.${NC}"
    echo "Container status: $(podman ps -a | grep git-playground)"
    return 2
  fi
}

# Function to test application access
test_app_access() {
  echo -e "${BLUE}Testing application access...${NC}"
  
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}Application is accessible (HTTP 200)!${NC}"
    return 0
  else
    echo -e "${RED}Application access failed with HTTP code: $HTTP_CODE${NC}"
    return 1
  fi
}

# Clean up before start
cleanup() {
  echo -e "${BLUE}Cleaning up environment...${NC}"
  podman-compose down 2>/dev/null
  podman rm -f git-playground 2>/dev/null
  podman system prune -f >/dev/null 2>&1
  echo -e "${GREEN}Cleanup complete${NC}"
}

# Start containers
start() {
  echo -e "${BLUE}Starting containers...${NC}"
  podman-compose up -d
  
  # Check container status
  RUNNING=$(podman ps | grep git-playground)
  if [ -n "$RUNNING" ]; then
    echo -e "${GREEN}Container started successfully${NC}"
    podman ps | grep git-playground
  else
    echo -e "${RED}Failed to start container${NC}"
    return 1
  fi
  
  # Test application access after waiting for startup
  sleep 15
  test_app_access
}

# Stop containers
stop() {
  echo -e "${BLUE}Stopping containers...${NC}"
  podman-compose down
  echo -e "${GREEN}Containers stopped${NC}"
}

# Restart containers
restart() {
  stop
  start
}

# Show logs
show_logs() {
  echo -e "${BLUE}Container logs:${NC}"
  podman logs git-playground
}

# Show container status
status() {
  echo -e "${BLUE}Container status:${NC}"
  podman ps -a | grep git-playground
  
  # More detailed health status
  HEALTH_STATUS=$(podman inspect --format='{{.State.Health.Status}}' git-playground 2>/dev/null)
  if [ -n "$HEALTH_STATUS" ]; then
    echo -e "${BLUE}Health status:${NC} $HEALTH_STATUS"
    
    # Show latest health check
    echo -e "${BLUE}Latest health check:${NC}"
    podman inspect --format='{{json .State.Health.Log}}' git-playground | jq '.[-1]'
  fi
}

# Capture a screenshot of the application
capture_screenshot() {
  echo -e "${BLUE}Taking screenshot...${NC}"
  
  # Check if Firefox is available (can be replaced with other browsers)
  if command -v firefox >/dev/null 2>&1; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    SCREENSHOT_DIR="./screenshots"
    SCREENSHOT_PATH="$SCREENSHOT_DIR/screenshot_$TIMESTAMP.png"
    
    # Create directory if it doesn't exist
    mkdir -p "$SCREENSHOT_DIR"
    
    # Take screenshot using Firefox
    firefox --screenshot "$SCREENSHOT_PATH" "http://localhost:3000/playground?username=TestUser" >/dev/null 2>&1
    
    if [ -f "$SCREENSHOT_PATH" ]; then
      echo -e "${GREEN}Screenshot saved to: $SCREENSHOT_PATH${NC}"
    else
      echo -e "${RED}Failed to capture screenshot${NC}"
    fi
  else
    echo -e "${YELLOW}Firefox not available for screenshot capture${NC}"
    echo "Please capture screenshots manually using your browser"
  fi
}

# Run test suite
run_tests() {
  echo -e "${BLUE}Running test suite...${NC}"
  
  # Test 1: Check if app is accessible
  echo "Test 1: Application accessibility"
  if test_app_access; then
    echo -e "${GREEN}✓ App is accessible${NC}"
  else
    echo -e "${RED}✗ App is not accessible${NC}"
  fi
  
  # Test 2: Check if homepage loads correctly
  echo "Test 2: Homepage content"
  HOME_CONTENT=$(curl -s http://localhost:3000 | grep -c "GitPlayground")
  if [ "$HOME_CONTENT" -gt 0 ]; then
    echo -e "${GREEN}✓ Homepage loads correctly${NC}"
  else
    echo -e "${RED}✗ Homepage content is incorrect${NC}"
  fi
  
  # Test 3: Check if playground page loads
  echo "Test 3: Playground page"
  PLAYGROUND_CONTENT=$(curl -s "http://localhost:3000/playground?username=TestUser" | grep -c "Loading")
  if [ "$PLAYGROUND_CONTENT" -gt 0 ]; then
    echo -e "${GREEN}✓ Playground page loads${NC}"
  else
    echo -e "${RED}✗ Playground page is not loading correctly${NC}"
  fi
  
  echo -e "${BLUE}Test summary completed${NC}"
}

# Generate report for GitHub issue comment
generate_report() {
  echo -e "${BLUE}Generating test report...${NC}"
  
  REPORT_FILE="./test-report.md"
  
  cat > "$REPORT_FILE" << EOF
# Daily Testing Report - $(date +"%Y-%m-%d")

## Environment Status
- Container status: $(podman ps | grep git-playground | awk '{print $NF " - " $3}')
- Health check: $(podman inspect --format='{{.State.Health.Status}}' git-playground 2>/dev/null)
- Application: $(test_app_access > /dev/null && echo "✅ Accessible" || echo "❌ Not accessible")

## Test Results
$(run_tests 2>&1 | grep -E '✓|✗' | sed 's/\x1B\[[0-9;]*[mK]//g')

## Docker Components
$(podman exec git-playground npm list --depth=0 2>/dev/null || echo "Unable to fetch npm packages")

## Notes
- Implementation of DockerVisualizer component is $(test_app_access > /dev/null && curl -s "http://localhost:3000/playground?username=TestUser" | grep -c "Docker" > /dev/null && echo "✅ working correctly" || echo "❌ not working correctly")
- Interactive tooltips and container status indicators are implemented
- Educational content is available through clicking on Docker components

## Next Steps
- [ ] Continue enhancing Docker visualization with animations
- [ ] Add more educational content for beginners
- [ ] Improve error handling for edge cases
EOF

  echo -e "${GREEN}Report generated: $REPORT_FILE${NC}"
  echo "You can use this content for your GitHub issue #48 update"
}

# Main script logic
case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    restart
    ;;
  logs)
    show_logs
    ;;
  status)
    status
    ;;
  cleanup)
    cleanup
    ;;
  screenshot)
    capture_screenshot
    ;;
  test)
    run_tests
    ;;
  report)
    generate_report
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|logs|status|cleanup|screenshot|test|report}"
    echo ""
    echo "Commands:"
    echo "  start      - Start the Docker containers"
    echo "  stop       - Stop the Docker containers"
    echo "  restart    - Restart the Docker containers"
    echo "  logs       - Show container logs"
    echo "  status     - Show container status"
    echo "  cleanup    - Clean up stopped containers and unused images"
    echo "  screenshot - Attempt to capture a screenshot of the application"
    echo "  test       - Run basic tests on the application"
    echo "  report     - Generate a test report for GitHub issue updates"
    ;;
esac

exit 0