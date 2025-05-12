#!/bin/bash
# Script to verify the database connectivity fix

echo "===== Verifying Database Fix ====="

# Function for logging with timestamp
log_msg() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Detect container runtime
if command -v podman &> /dev/null; then
  CONTAINER_RUNTIME="podman"
  log_msg "Using podman as container runtime"
elif command -v docker &> /dev/null; then
  CONTAINER_RUNTIME="docker"
  log_msg "Using docker as container runtime"
else
  log_msg "Error: No container runtime (podman or docker) found"
  exit 1
fi

# Check if patentdwh-db container is running
log_msg "Checking if patentdwh-db container is running..."
if ! $CONTAINER_RUNTIME ps | grep -q "patentdwh-db"; then
  log_msg "patentdwh-db container is not running!"
  exit 1
fi

# Verify database tables
log_msg "Checking database tables..."
TABLE_CHECK=$($CONTAINER_RUNTIME exec patentdwh-db sqlite3 /app/data/inpit.db ".tables" 2>&1)
if echo "$TABLE_CHECK" | grep -q "inpit_data"; then
  log_msg "✅ inpit_data table exists"
else
  log_msg "❌ inpit_data table does not exist"
fi

# Check for sample data
log_msg "Checking for sample data..."
DATA_CHECK=$($CONTAINER_RUNTIME exec patentdwh-db sqlite3 /app/data/inpit.db "SELECT COUNT(*) FROM inpit_data" 2>&1)
if [[ "$DATA_CHECK" =~ ^[0-9]+$ ]]; then
  if [ "$DATA_CHECK" -gt 0 ]; then
    log_msg "✅ inpit_data table contains $DATA_CHECK records"
  else
    log_msg "⚠️ inpit_data table exists but contains no records"
  fi
else
  log_msg "❌ Error querying data: $DATA_CHECK"
fi

# Check direct database access
log_msg "Testing direct database access..."
DB_TEST=$($CONTAINER_RUNTIME exec patentdwh-db sqlite3 /app/data/inpit.db "SELECT * FROM inpit_data LIMIT 1" 2>&1)

if [ $? -eq 0 ]; then
  log_msg "✅ Direct database access is working correctly"
  echo "$DB_TEST"
else
  log_msg "❌ Direct database access failed"
  echo "$DB_TEST"
fi

# Check MCP container if running
if $CONTAINER_RUNTIME ps | grep -q "patent-analysis-mcp"; then
  log_msg "Testing MCP container connectivity to database container..."
  # Use ping instead of curl
  MCP_TEST=$($CONTAINER_RUNTIME exec patent-analysis-mcp ping -c 2 patentdwh-db 2>&1)
    
  if [ $? -eq 0 ]; then
    log_msg "✅ MCP container can connect to database container"
    echo "$MCP_TEST" | grep "bytes from"
  else
    log_msg "❌ MCP container cannot connect to database container"
    echo "$MCP_TEST"
  fi
else
  log_msg "⚠️ patent-analysis-mcp container is not running, skipping MCP connectivity test"
fi

# Check database service is running
log_msg "Checking if database service is up and running..."
# Use ps inside container to check if Python process is running
PS_TEST=$($CONTAINER_RUNTIME exec patentdwh-db ps aux | grep -v grep | grep "python /app/app.py" 2>&1)

if [ $? -eq 0 ]; then
  log_msg "✅ Database service is running"
  echo "$PS_TEST"
else
  log_msg "❌ Database service may not be running correctly"
  log_msg "You may need to check service logs with: podman logs patentdwh-db"
fi

echo ""
log_msg "Verification completed. If all checks have passed, the database fix was successful."
echo ""
echo "If issues persist, try restarting all services:"
echo "cd /root/aws.git/patentDWH"
echo "./stop_all_services.sh"
echo "./start_all_services.sh"
