#!/bin/bash
#
# verify-session-management.sh - Verify Redis Session Management Implementation
#
# This script verifies that the Redis session management and system info
# display features are working correctly.
#

set -e
set -u
set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Configuration
BACKEND_URL="${BACKEND_URL:-http://10.0.1.191:8083}"
FRONTEND_URL="${FRONTEND_URL:-http://10.0.1.191:5006}"
TEMP_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test 1: Check Backend Pods
test_backend_pods() {
    print_test "Checking backend pod status..."

    if kubectl get pods -l app=orgmgmt-backend &>/dev/null; then
        POD_COUNT=$(kubectl get pods -l app=orgmgmt-backend --no-headers | wc -l)
        READY_COUNT=$(kubectl get pods -l app=orgmgmt-backend --no-headers | grep -c "Running" || true)

        if [ "$READY_COUNT" -ge 1 ]; then
            print_pass "Backend pods running ($READY_COUNT/$POD_COUNT ready)"
            return 0
        else
            print_fail "No backend pods ready ($READY_COUNT/$POD_COUNT)"
            return 1
        fi
    else
        print_fail "Backend deployment not found"
        return 1
    fi
}

# Test 2: Check Backend Service
test_backend_service() {
    print_test "Checking backend service..."

    if kubectl get svc orgmgmt-backend &>/dev/null; then
        SERVICE_IP=$(kubectl get svc orgmgmt-backend -o jsonpath='{.spec.externalIPs[0]}' 2>/dev/null || echo "")
        SERVICE_PORT=$(kubectl get svc orgmgmt-backend -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "")

        if [ -n "$SERVICE_IP" ] && [ -n "$SERVICE_PORT" ]; then
            print_pass "Backend service found (${SERVICE_IP}:${SERVICE_PORT})"
            return 0
        else
            print_fail "Backend service misconfigured"
            return 1
        fi
    else
        print_fail "Backend service not found"
        return 1
    fi
}

# Test 3: Check Redis Connectivity
test_redis_connectivity() {
    print_test "Checking Redis connectivity..."

    if podman exec argocd-redis redis-cli PING 2>/dev/null | grep -q "PONG"; then
        print_pass "Redis is responding"
        return 0
    else
        print_fail "Redis is not responding"
        return 1
    fi
}

# Test 4: Test System Info Endpoint
test_system_info_endpoint() {
    print_test "Testing system info endpoint..."

    COOKIE_FILE="$TEMP_DIR/cookies.txt"
    RESPONSE=$(curl -s -c "$COOKIE_FILE" "${BACKEND_URL}/api/system/info" 2>/dev/null || echo "")

    if [ -n "$RESPONSE" ]; then
        # Check if response is valid JSON
        if echo "$RESPONSE" | jq . &>/dev/null; then
            print_pass "System info endpoint returns valid JSON"

            # Extract and display fields
            POD_NAME=$(echo "$RESPONSE" | jq -r '.podName // "unknown"')
            SESSION_ID=$(echo "$RESPONSE" | jq -r '.sessionId // "unknown"')
            FLYWAY_VERSION=$(echo "$RESPONSE" | jq -r '.flywayVersion // "unknown"')
            DB_STATUS=$(echo "$RESPONSE" | jq -r '.databaseStatus // "unknown"')

            print_info "  Pod Name: $POD_NAME"
            print_info "  Session ID: ${SESSION_ID:0:16}..."
            print_info "  Flyway Version: $FLYWAY_VERSION"
            print_info "  Database Status: $DB_STATUS"

            return 0
        else
            print_fail "System info endpoint returns invalid JSON"
            print_info "  Response: $RESPONSE"
            return 1
        fi
    else
        print_fail "System info endpoint not responding"
        return 1
    fi
}

# Test 5: Test Session Persistence
test_session_persistence() {
    print_test "Testing session persistence..."

    COOKIE_FILE="$TEMP_DIR/cookies2.txt"

    # First request
    RESPONSE1=$(curl -s -c "$COOKIE_FILE" "${BACKEND_URL}/api/system/info" 2>/dev/null || echo "")
    SESSION_ID1=$(echo "$RESPONSE1" | jq -r '.sessionId // "unknown"' 2>/dev/null)

    if [ "$SESSION_ID1" = "unknown" ] || [ -z "$SESSION_ID1" ]; then
        print_fail "Could not get session ID from first request"
        return 1
    fi

    # Second request with same cookie
    sleep 1
    RESPONSE2=$(curl -s -b "$COOKIE_FILE" "${BACKEND_URL}/api/system/info" 2>/dev/null || echo "")
    SESSION_ID2=$(echo "$RESPONSE2" | jq -r '.sessionId // "unknown"' 2>/dev/null)

    if [ "$SESSION_ID1" = "$SESSION_ID2" ]; then
        print_pass "Session persists across requests"
        print_info "  Session ID: ${SESSION_ID1:0:16}..."
        return 0
    else
        print_fail "Session ID changed between requests"
        print_info "  First:  ${SESSION_ID1:0:16}..."
        print_info "  Second: ${SESSION_ID2:0:16}..."
        return 1
    fi
}

# Test 6: Check Redis Session Keys
test_redis_session_keys() {
    print_test "Checking Redis session keys..."

    KEY_COUNT=$(podman exec argocd-redis redis-cli KEYS "spring:session:orgmgmt:*" 2>/dev/null | wc -l || echo "0")

    if [ "$KEY_COUNT" -gt 0 ]; then
        print_pass "Redis session keys found ($KEY_COUNT keys)"
        return 0
    else
        print_fail "No Redis session keys found"
        print_info "  Expected namespace: spring:session:orgmgmt"
        return 1
    fi
}

# Test 7: Check POD_NAME Environment Variable
test_pod_name_env() {
    print_test "Checking POD_NAME environment variable..."

    POD_NAME=$(kubectl get pods -l app=orgmgmt-backend -o name | head -1)
    if [ -z "$POD_NAME" ]; then
        print_fail "No backend pod found"
        return 1
    fi

    POD_ENV=$(kubectl exec "$POD_NAME" -- env | grep "POD_NAME=" 2>/dev/null || echo "")

    if [ -n "$POD_ENV" ]; then
        print_pass "POD_NAME environment variable is set"
        print_info "  $POD_ENV"
        return 0
    else
        print_fail "POD_NAME environment variable not set"
        return 1
    fi
}

# Test 8: Check Database Connectivity Status
test_database_status() {
    print_test "Checking database connectivity status..."

    RESPONSE=$(curl -s "${BACKEND_URL}/api/system/info" 2>/dev/null || echo "")
    DB_STATUS=$(echo "$RESPONSE" | jq -r '.databaseStatus // "unknown"' 2>/dev/null)

    if [ "$DB_STATUS" = "OK" ]; then
        print_pass "Database connectivity status is OK"
        return 0
    else
        print_fail "Database connectivity status: $DB_STATUS"
        return 1
    fi
}

# Test 9: Check Flyway Version
test_flyway_version() {
    print_test "Checking Flyway version..."

    RESPONSE=$(curl -s "${BACKEND_URL}/api/system/info" 2>/dev/null || echo "")
    FLYWAY_VERSION=$(echo "$RESPONSE" | jq -r '.flywayVersion // "unknown"' 2>/dev/null)

    if [ "$FLYWAY_VERSION" != "unknown" ] && [ "$FLYWAY_VERSION" != "error" ]; then
        print_pass "Flyway version retrieved: $FLYWAY_VERSION"
        return 0
    else
        print_fail "Could not retrieve Flyway version"
        return 1
    fi
}

# Test 10: Check Frontend Access
test_frontend_access() {
    print_test "Checking frontend access..."

    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}" 2>/dev/null || echo "000")

    if [ "$HTTP_STATUS" = "200" ]; then
        print_pass "Frontend is accessible"
        return 0
    else
        print_fail "Frontend returned HTTP $HTTP_STATUS"
        return 1
    fi
}

# Test 11: Check Backend Health
test_backend_health() {
    print_test "Checking backend health endpoint..."

    RESPONSE=$(curl -s "${BACKEND_URL}/actuator/health" 2>/dev/null || echo "")
    HEALTH_STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"' 2>/dev/null)

    if [ "$HEALTH_STATUS" = "UP" ]; then
        print_pass "Backend health status is UP"

        # Check Redis component
        REDIS_STATUS=$(echo "$RESPONSE" | jq -r '.components.redis.status // "unknown"' 2>/dev/null)
        if [ "$REDIS_STATUS" = "UP" ]; then
            print_info "  Redis component: UP"
        else
            print_info "  Redis component: $REDIS_STATUS"
        fi

        return 0
    else
        print_fail "Backend health status: $HEALTH_STATUS"
        return 1
    fi
}

# Test 12: Check Session Affinity
test_session_affinity() {
    print_test "Checking session affinity configuration..."

    SESSION_AFFINITY=$(kubectl get svc orgmgmt-backend -o jsonpath='{.spec.sessionAffinity}' 2>/dev/null || echo "")

    if [ "$SESSION_AFFINITY" = "ClientIP" ]; then
        TIMEOUT=$(kubectl get svc orgmgmt-backend -o jsonpath='{.spec.sessionAffinityConfig.clientIP.timeoutSeconds}' 2>/dev/null || echo "")
        print_pass "Session affinity is configured (ClientIP, ${TIMEOUT}s)"
        return 0
    else
        print_fail "Session affinity not configured correctly (got: $SESSION_AFFINITY)"
        return 1
    fi
}

# Main execution
main() {
    print_header "Redis Session Management Verification"

    print_info "Backend URL: $BACKEND_URL"
    print_info "Frontend URL: $FRONTEND_URL"
    print_info "Temp Directory: $TEMP_DIR"

    print_header "Running Tests"

    # Infrastructure tests
    test_backend_pods
    test_backend_service
    test_redis_connectivity

    # API tests
    test_system_info_endpoint
    test_session_persistence
    test_backend_health

    # Redis tests
    test_redis_session_keys

    # Configuration tests
    test_pod_name_env
    test_session_affinity

    # Data tests
    test_database_status
    test_flyway_version

    # Frontend test
    test_frontend_access

    # Summary
    print_header "Test Summary"

    TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
    echo -e "Total Tests: $TOTAL_TESTS"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All tests passed!${NC}\n"
        return 0
    else
        echo -e "\n${RED}✗ Some tests failed${NC}\n"
        return 1
    fi
}

# Check dependencies
check_dependencies() {
    local missing_deps=()

    for cmd in kubectl podman curl jq; do
        if ! command -v $cmd &>/dev/null; then
            missing_deps+=("$cmd")
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}Error: Missing required dependencies:${NC}"
        printf '%s\n' "${missing_deps[@]}"
        echo -e "\nPlease install missing dependencies and try again."
        exit 1
    fi
}

# Run checks and main
check_dependencies
main
