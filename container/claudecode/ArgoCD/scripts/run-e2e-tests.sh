#!/bin/bash
#
# run-e2e-tests.sh - E2E Test Runner Script
#
# This script runs Playwright E2E tests including:
# - Deployment health checks
# - Playwright test execution
# - Screenshot capture on failure
# - HTML report generation
# - Test artifact archival
#
# Usage: ./run-e2e-tests.sh [OPTIONS]
#
# Options:
#   --environment ENV     Target environment (dev/staging/prod, default: dev)
#   --headed             Run tests in headed mode (visible browser)
#   --debug              Run tests in debug mode
#   --ui                 Run tests in UI mode
#   --project PROJECT    Run specific project (chromium/firefox/webkit)
#   --grep PATTERN       Run tests matching pattern
#   --skip-health        Skip health checks
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

ENVIRONMENT="dev"
HEADED=false
DEBUG=false
UI=false
PROJECT=""
GREP_PATTERN=""
SKIP_HEALTH=false

PLAYWRIGHT_DIR="${PROJECT_ROOT}/playwright-tests"
ARCHIVE_DIR="${PROJECT_ROOT}/test-results"

# ==============================================================================
# USAGE
# ==============================================================================

show_usage() {
    cat << EOF
E2E Test Runner Script

Usage: $(basename "$0") [OPTIONS]

Run Playwright E2E tests against the deployed application.

Options:
    --environment ENV    Target environment (dev/staging/prod, default: dev)
    --headed            Run tests in headed mode (visible browser)
    --debug             Run tests in debug mode
    --ui                Run tests in UI mode
    --project PROJECT   Run specific project (chromium/firefox/webkit)
    --grep PATTERN      Run tests matching pattern
    --skip-health       Skip health checks
    -h, --help          Show this help message

Examples:
    $(basename "$0")                                # Run all E2E tests on dev
    $(basename "$0") --environment prod             # Run tests on prod
    $(basename "$0") --headed --debug               # Run in debug mode
    $(basename "$0") --project chromium             # Run only Chromium tests
    $(basename "$0") --grep "login"                 # Run tests matching "login"

EOF
}

# ==============================================================================
# ARGUMENT PARSING
# ==============================================================================

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --headed)
                HEADED=true
                shift
                ;;
            --debug)
                DEBUG=true
                shift
                ;;
            --ui)
                UI=true
                shift
                ;;
            --project)
                PROJECT="$2"
                shift 2
                ;;
            --grep)
                GREP_PATTERN="$2"
                shift 2
                ;;
            --skip-health)
                SKIP_HEALTH=true
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

    # Validate environment
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        die "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod."
    fi
}

# ==============================================================================
# CHECK DEPLOYMENT HEALTH
# ==============================================================================

check_deployment_health() {
    if [ "$SKIP_HEALTH" = true ]; then
        log_info "Skipping health checks"
        return 0
    fi

    print_header "Checking Deployment Health"

    # Get service ports based on environment
    local backend_port frontend_port

    case "$ENVIRONMENT" in
        dev)
            backend_port=8080
            frontend_port=5006
            ;;
        staging)
            backend_port=8081
            frontend_port=5007
            ;;
        prod)
            backend_port=8082
            frontend_port=5008
            ;;
    esac

    # Check frontend
    print_step 1 "Checking frontend at http://localhost:${frontend_port}"

    if curl -sf "http://localhost:${frontend_port}" > /dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        die "Frontend is not accessible. Please deploy the application first."
    fi

    # Check backend
    print_step 2 "Checking backend at http://localhost:${backend_port}"

    if curl -sf "http://localhost:${backend_port}/actuator/health" > /dev/null 2>&1; then
        local health_status=$(curl -s "http://localhost:${backend_port}/actuator/health" | jq -r '.status')

        if [ "$health_status" = "UP" ]; then
            log_success "Backend is healthy"
        else
            log_warning "Backend health status: $health_status"
        fi
    else
        die "Backend is not accessible. Please deploy the application first."
    fi

    log_success "Deployment health checks passed"
}

# ==============================================================================
# SETUP TEST ENVIRONMENT
# ==============================================================================

setup_test_environment() {
    print_header "Setting Up Test Environment"

    # Validate Playwright directory
    validate_directory "$PLAYWRIGHT_DIR" "Playwright tests directory not found"

    cd "$PLAYWRIGHT_DIR" || die "Failed to change to Playwright directory"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing Playwright dependencies..."
        npm ci

        log_info "Installing Playwright browsers..."
        npx playwright install
    else
        log_info "Dependencies already installed"
    fi

    # Set base URL based on environment
    local frontend_port

    case "$ENVIRONMENT" in
        dev)
            frontend_port=5006
            ;;
        staging)
            frontend_port=5007
            ;;
        prod)
            frontend_port=5008
            ;;
    esac

    export PLAYWRIGHT_BASE_URL="http://localhost:${frontend_port}"

    log_info "Base URL: $PLAYWRIGHT_BASE_URL"
    log_success "Test environment setup complete"
}

# ==============================================================================
# RUN PLAYWRIGHT TESTS
# ==============================================================================

run_playwright_tests() {
    print_header "Running Playwright Tests"

    log_info "Executing test suite..."

    # Build test command
    local test_cmd="npx playwright test"

    # Add options
    if [ "$HEADED" = true ]; then
        test_cmd="$test_cmd --headed"
    fi

    if [ "$DEBUG" = true ]; then
        test_cmd="$test_cmd --debug"
    fi

    if [ "$UI" = true ]; then
        test_cmd="$test_cmd --ui"
    fi

    if [ -n "$PROJECT" ]; then
        test_cmd="$test_cmd --project=$PROJECT"
    fi

    if [ -n "$GREP_PATTERN" ]; then
        test_cmd="$test_cmd --grep \"$GREP_PATTERN\""
    fi

    log_info "Running: $test_cmd"
    echo ""

    # Run tests
    local test_result=0

    if eval $test_cmd; then
        log_success "All E2E tests passed"
        test_result=0
    else
        log_error "Some E2E tests failed"
        test_result=1
    fi

    echo ""
    return $test_result
}

# ==============================================================================
# GENERATE HTML REPORT
# ==============================================================================

generate_html_report() {
    print_header "Generating HTML Report"

    log_info "Creating test report..."

    # Check if report exists
    if [ -d "playwright-report" ]; then
        log_success "Report generated at: ${PLAYWRIGHT_DIR}/playwright-report/index.html"

        # Optionally open report in browser
        if [ -t 0 ] && check_command xdg-open; then
            read -p "$(echo -e ${YELLOW}Open report in browser? [y/N]: ${NC})" -n 1 -r
            echo ""

            if [[ $REPLY =~ ^[Yy]$ ]]; then
                xdg-open "${PLAYWRIGHT_DIR}/playwright-report/index.html" &
            fi
        fi
    else
        log_warning "Report directory not found"
    fi
}

# ==============================================================================
# COLLECT TEST ARTIFACTS
# ==============================================================================

collect_test_artifacts() {
    print_header "Collecting Test Artifacts"

    # Create archive directory
    mkdir -p "$ARCHIVE_DIR"

    local timestamp=$(date +%Y%m%d-%H%M%S)
    local archive_name="e2e-tests-${ENVIRONMENT}-${timestamp}"
    local archive_path="${ARCHIVE_DIR}/${archive_name}"

    log_info "Creating test artifact archive..."

    # Create archive directory
    mkdir -p "$archive_path"

    # Copy test results
    if [ -d "test-results" ]; then
        log_info "Copying test results..."
        cp -r test-results "$archive_path/"
    fi

    # Copy screenshots
    if [ -d "screenshots" ]; then
        log_info "Copying screenshots..."
        cp -r screenshots "$archive_path/"
    fi

    # Copy HTML report
    if [ -d "playwright-report" ]; then
        log_info "Copying HTML report..."
        cp -r playwright-report "$archive_path/"
    fi

    # Copy videos if available
    if [ -d "videos" ]; then
        log_info "Copying test videos..."
        cp -r videos "$archive_path/"
    fi

    # Create tarball
    log_info "Creating tarball..."

    cd "$ARCHIVE_DIR" || die "Failed to change to archive directory"

    tar -czf "${archive_name}.tar.gz" "$archive_name"

    if [ $? -eq 0 ]; then
        log_success "Test artifacts archived: ${ARCHIVE_DIR}/${archive_name}.tar.gz"

        # Calculate size
        local size=$(du -h "${archive_name}.tar.gz" | cut -f1)
        log_info "Archive size: $size"

        # Clean up uncompressed directory
        rm -rf "$archive_name"
    else
        log_warning "Failed to create tarball"
    fi

    cd "$PLAYWRIGHT_DIR" || die "Failed to return to Playwright directory"
}

# ==============================================================================
# DISPLAY TEST SUMMARY
# ==============================================================================

display_test_summary() {
    local test_result=$1

    print_summary \
        "Environment:${ENVIRONMENT}" \
        "Base URL:${PLAYWRIGHT_BASE_URL}" \
        "Test Mode:$([ "$HEADED" = true ] && echo "Headed" || echo "Headless")" \
        "Project:${PROJECT:-All}" \
        "Result:$([ $test_result -eq 0 ] && echo "Passed" || echo "Failed")"

    if [ $test_result -eq 0 ]; then
        echo -e "${GREEN}✓ E2E tests completed successfully!${NC}"
    else
        echo -e "${RED}✗ E2E tests failed. Check the report for details.${NC}"
    fi

    echo ""
    echo -e "${YELLOW}Test Artifacts:${NC}"
    echo -e "  Report: ${CYAN}${PLAYWRIGHT_DIR}/playwright-report/index.html${NC}"
    echo -e "  Screenshots: ${CYAN}${PLAYWRIGHT_DIR}/test-results/${NC}"

    if [ -d "${ARCHIVE_DIR}" ]; then
        local latest_archive=$(ls -t "${ARCHIVE_DIR}"/*.tar.gz 2>/dev/null | head -1)
        if [ -n "$latest_archive" ]; then
            echo -e "  Archive: ${CYAN}${latest_archive}${NC}"
        fi
    fi

    echo ""
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    parse_arguments "$@"

    print_header "E2E Test Runner - Environment: ${ENVIRONMENT}"

    check_deployment_health
    setup_test_environment

    local test_result=0
    run_playwright_tests || test_result=$?

    generate_html_report
    collect_test_artifacts
    display_test_summary $test_result

    cd "$PROJECT_ROOT" || die "Failed to return to project root"

    exit $test_result
}

main "$@"
