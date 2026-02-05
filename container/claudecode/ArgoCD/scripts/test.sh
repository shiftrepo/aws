#!/bin/bash
#
# test.sh - Test Runner Script
#
# This script runs all tests for the application including:
# - Backend unit tests (Maven/JUnit)
# - Backend integration tests
# - Frontend unit tests (Jest)
# - E2E tests (Playwright)
# - Coverage report generation
#
# Usage: ./test.sh [OPTIONS]
#
# Options:
#   --backend-only        Run only backend tests
#   --frontend-only       Run only frontend tests
#   --e2e-only           Run only E2E tests
#   --skip-backend       Skip backend tests
#   --skip-frontend      Skip frontend tests
#   --skip-e2e           Skip E2E tests
#   --coverage           Generate coverage reports
#   --watch              Run tests in watch mode (frontend only)
#   -h, --help           Show this help message
#

set -e
set -u
set -o pipefail

# ==============================================================================
# INITIALIZATION
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

source "${SCRIPT_DIR}/common.sh"

# ==============================================================================
# CONFIGURATION
# ==============================================================================

BACKEND_ONLY=false
FRONTEND_ONLY=false
E2E_ONLY=false
SKIP_BACKEND=false
SKIP_FRONTEND=false
SKIP_E2E=false
COVERAGE=false
WATCH=false

BACKEND_DIR="${APP_DIR}/backend"
FRONTEND_DIR="${APP_DIR}/frontend"
PLAYWRIGHT_DIR="${PROJECT_ROOT}/playwright-tests"

# Test results
BACKEND_RESULT=0
FRONTEND_RESULT=0
E2E_RESULT=0

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
Test Runner Script

Usage: $(basename "$0") [OPTIONS]

Run all tests for the application with coverage reporting.

Options:
    --backend-only      Run only backend tests
    --frontend-only     Run only frontend tests
    --e2e-only         Run only E2E tests
    --skip-backend     Skip backend tests
    --skip-frontend    Skip frontend tests
    --skip-e2e         Skip E2E tests
    --coverage         Generate coverage reports
    --watch            Run tests in watch mode (frontend only)
    -h, --help         Show this help message

Examples:
    $(basename "$0")                      # Run all tests
    $(basename "$0") --backend-only       # Run only backend tests
    $(basename "$0") --skip-e2e           # Run all except E2E tests
    $(basename "$0") --coverage           # Run all tests with coverage

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                BACKEND_ONLY=true
                SKIP_FRONTEND=true
                SKIP_E2E=true
                shift
                ;;
            --frontend-only)
                FRONTEND_ONLY=true
                SKIP_BACKEND=true
                SKIP_E2E=true
                shift
                ;;
            --e2e-only)
                E2E_ONLY=true
                SKIP_BACKEND=true
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-backend)
                SKIP_BACKEND=true
                shift
                ;;
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --skip-e2e)
                SKIP_E2E=true
                shift
                ;;
            --coverage)
                COVERAGE=true
                shift
                ;;
            --watch)
                WATCH=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# ==============================================================================
# VALIDATE TEST ENVIRONMENT
# ==============================================================================

validate_test_environment() {
    print_header "Validating Test Environment"

    # Check required commands
    local required_commands=()

    if [ "$SKIP_BACKEND" = false ]; then
        required_commands+=("mvn")
    fi

    if [ "$SKIP_FRONTEND" = false ]; then
        required_commands+=("npm")
    fi

    if [ "$SKIP_E2E" = false ]; then
        required_commands+=("npx")
    fi

    if [ ${#required_commands[@]} -gt 0 ]; then
        check_prerequisites "${required_commands[@]}" || die "Missing required dependencies"
    fi

    # Validate directories
    if [ "$SKIP_BACKEND" = false ]; then
        validate_directory "$BACKEND_DIR" "Backend directory not found"
    fi

    if [ "$SKIP_FRONTEND" = false ]; then
        validate_directory "$FRONTEND_DIR" "Frontend directory not found"
    fi

    if [ "$SKIP_E2E" = false ]; then
        validate_directory "$PLAYWRIGHT_DIR" "Playwright tests directory not found"
    fi

    log_success "Test environment validation complete"
}

# ==============================================================================
# BACKEND TESTS
# ==============================================================================

run_backend_tests() {
    if [ "$SKIP_BACKEND" = true ]; then
        log_info "Skipping backend tests"
        return 0
    fi

    print_header "Running Backend Tests"

    cd "$BACKEND_DIR" || die "Failed to change to backend directory"

    log_info "Running Maven test suite..."

    # Build test command
    local test_cmd="mvn clean test"

    if [ "$COVERAGE" = true ]; then
        test_cmd="$test_cmd jacoco:report"
    fi

    # Run tests
    if $test_cmd; then
        log_success "Backend tests passed"
        BACKEND_RESULT=0

        # Check for test results
        if [ -d "target/surefire-reports" ]; then
            local total_tests=$(find target/surefire-reports -name "TEST-*.xml" -exec xmllint --xpath 'string(//testsuite/@tests)' {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
            local failed_tests=$(find target/surefire-reports -name "TEST-*.xml" -exec xmllint --xpath 'string(//testsuite/@failures)' {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
            local error_tests=$(find target/surefire-reports -name "TEST-*.xml" -exec xmllint --xpath 'string(//testsuite/@errors)' {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')

            echo ""
            echo -e "${CYAN}Backend Test Summary:${NC}"
            echo -e "  Total Tests: ${total_tests:-0}"
            echo -e "  Passed: $((${total_tests:-0} - ${failed_tests:-0} - ${error_tests:-0}))"
            echo -e "  Failed: ${failed_tests:-0}"
            echo -e "  Errors: ${error_tests:-0}"
        fi

        # Coverage report
        if [ "$COVERAGE" = true ] && [ -f "target/site/jacoco/index.html" ]; then
            log_info "Coverage report: ${BACKEND_DIR}/target/site/jacoco/index.html"
        fi
    else
        log_error "Backend tests failed"
        BACKEND_RESULT=1
    fi

    echo ""
    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# FRONTEND TESTS
# ==============================================================================

run_frontend_tests() {
    if [ "$SKIP_FRONTEND" = true ]; then
        log_info "Skipping frontend tests"
        return 0
    fi

    print_header "Running Frontend Tests"

    cd "$FRONTEND_DIR" || die "Failed to change to frontend directory"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing dependencies..."
        npm ci
    fi

    log_info "Running Jest test suite..."

    # Build test command
    local test_cmd="npm test"

    if [ "$WATCH" = true ]; then
        test_cmd="$test_cmd -- --watch"
    elif [ "$COVERAGE" = true ]; then
        test_cmd="$test_cmd -- --coverage --run"
    else
        test_cmd="$test_cmd -- --run"
    fi

    # Run tests
    if $test_cmd; then
        log_success "Frontend tests passed"
        FRONTEND_RESULT=0

        # Coverage report
        if [ "$COVERAGE" = true ] && [ -f "coverage/index.html" ]; then
            log_info "Coverage report: ${FRONTEND_DIR}/coverage/index.html"
        fi
    else
        log_error "Frontend tests failed"
        FRONTEND_RESULT=1
    fi

    echo ""
    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# E2E TESTS
# ==============================================================================

run_e2e_tests() {
    if [ "$SKIP_E2E" = true ]; then
        log_info "Skipping E2E tests"
        return 0
    fi

    print_header "Running E2E Tests"

    # Check if Playwright tests exist
    if [ ! -d "$PLAYWRIGHT_DIR" ]; then
        log_warning "Playwright tests directory not found, skipping E2E tests"
        return 0
    fi

    cd "$PLAYWRIGHT_DIR" || die "Failed to change to Playwright directory"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing Playwright dependencies..."
        npm ci
        npx playwright install
    fi

    log_info "Running Playwright test suite..."

    # Check if application is running
    local base_url=${PLAYWRIGHT_BASE_URL:-http://localhost:5006}

    log_info "Testing against: $base_url"

    if ! curl -sf "$base_url" > /dev/null 2>&1; then
        log_warning "Application does not appear to be running at $base_url"
        log_warning "E2E tests may fail. Ensure application is deployed first."
    fi

    # Run tests
    if npx playwright test; then
        log_success "E2E tests passed"
        E2E_RESULT=0

        # Generate HTML report
        log_info "Generating HTML report..."
        npx playwright show-report --host 0.0.0.0 &

        log_info "E2E test report: ${PLAYWRIGHT_DIR}/playwright-report/index.html"
    else
        log_error "E2E tests failed"
        E2E_RESULT=1

        # Show report on failure
        log_info "Opening failure report..."
        npx playwright show-report --host 0.0.0.0 &
    fi

    echo ""
    cd "$PROJECT_ROOT" || die "Failed to return to project root"
}

# ==============================================================================
# GENERATE COMBINED COVERAGE
# ==============================================================================

generate_combined_coverage() {
    if [ "$COVERAGE" = false ]; then
        return 0
    fi

    print_header "Combined Coverage Report"

    log_info "Generating combined coverage report..."

    # Check for backend coverage
    if [ -f "${BACKEND_DIR}/target/site/jacoco/jacoco.xml" ]; then
        log_info "Backend coverage available"
    fi

    # Check for frontend coverage
    if [ -f "${FRONTEND_DIR}/coverage/coverage-final.json" ]; then
        log_info "Frontend coverage available"
    fi

    # Note: Combining coverage from different languages would require additional tooling
    log_info "View individual coverage reports:"
    echo -e "  Backend:  ${CYAN}${BACKEND_DIR}/target/site/jacoco/index.html${NC}"
    echo -e "  Frontend: ${CYAN}${FRONTEND_DIR}/coverage/index.html${NC}"
    echo ""
}

# ==============================================================================
# DISPLAY TEST SUMMARY
# ==============================================================================

display_test_summary() {
    print_header "Test Summary"

    local backend_status="Skipped"
    local frontend_status="Skipped"
    local e2e_status="Skipped"

    if [ "$SKIP_BACKEND" = false ]; then
        if [ $BACKEND_RESULT -eq 0 ]; then
            backend_status="${GREEN}✓ Passed${NC}"
        else
            backend_status="${RED}✗ Failed${NC}"
        fi
    fi

    if [ "$SKIP_FRONTEND" = false ]; then
        if [ $FRONTEND_RESULT -eq 0 ]; then
            frontend_status="${GREEN}✓ Passed${NC}"
        else
            frontend_status="${RED}✗ Failed${NC}"
        fi
    fi

    if [ "$SKIP_E2E" = false ]; then
        if [ $E2E_RESULT -eq 0 ]; then
            e2e_status="${GREEN}✓ Passed${NC}"
        else
            e2e_status="${RED}✗ Failed${NC}"
        fi
    fi

    echo ""
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}  TEST RESULTS${NC}"
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "  Backend Tests:  $backend_status"
    echo -e "  Frontend Tests: $frontend_status"
    echo -e "  E2E Tests:      $e2e_status"
    echo -e "${MAGENTA}========================================${NC}"
    echo ""

    # Determine overall result
    local overall_result=0

    if [ "$SKIP_BACKEND" = false ] && [ $BACKEND_RESULT -ne 0 ]; then
        overall_result=1
    fi

    if [ "$SKIP_FRONTEND" = false ] && [ $FRONTEND_RESULT -ne 0 ]; then
        overall_result=1
    fi

    if [ "$SKIP_E2E" = false ] && [ $E2E_RESULT -ne 0 ]; then
        overall_result=1
    fi

    if [ $overall_result -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    else
        echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    fi

    echo ""

    return $overall_result
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "Test Runner"

    validate_test_environment
    run_backend_tests
    run_frontend_tests
    run_e2e_tests
    generate_combined_coverage
    display_test_summary

    local exit_code=$?
    exit $exit_code
}

main "$@"
