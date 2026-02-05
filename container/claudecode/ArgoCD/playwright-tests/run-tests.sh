#!/bin/bash

# Playwright E2E Test Runner Script
# Usage: ./run-tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MODE="headless"
BROWSER="chromium"
SUITE="all"
BASE_URL="http://localhost:5006"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [options]

Options:
    -h, --help              Display this help message
    -m, --mode MODE         Test mode: headless, headed, debug, ui (default: headless)
    -b, --browser BROWSER   Browser: chromium, firefox, webkit, all (default: chromium)
    -s, --suite SUITE       Test suite: all, organizations, departments, users, errors (default: all)
    -u, --url URL           Base URL (default: http://localhost:5006)
    -i, --install           Install dependencies and browsers
    -c, --clean             Clean previous test results
    -r, --report            Open HTML report after tests

Examples:
    $0 --mode headed --browser chromium
    $0 --suite organizations --mode debug
    $0 --install
    $0 --clean --suite all
    $0 --browser firefox --url http://localhost:8080

EOF
    exit 0
}

# Function to check if application is running
check_app_running() {
    print_info "Checking if application is running at $BASE_URL..."

    if curl -s --head --fail "$BASE_URL" > /dev/null 2>&1; then
        print_success "Application is running at $BASE_URL"
        return 0
    else
        print_warning "Cannot connect to application at $BASE_URL"
        print_info "Please ensure the application is running before running tests"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Tests aborted"
            exit 1
        fi
    fi
}

# Function to install dependencies
install_deps() {
    print_info "Installing npm dependencies..."
    npm install

    print_info "Installing Playwright browsers..."
    npx playwright install

    print_info "Installing system dependencies..."
    npx playwright install-deps

    print_success "Installation completed"
}

# Function to clean previous results
clean_results() {
    print_info "Cleaning previous test results..."

    rm -rf playwright-report/
    rm -rf test-results/
    rm -f test-results.json
    rm -f junit-results.xml

    print_success "Cleanup completed"
}

# Function to run tests
run_tests() {
    export PLAYWRIGHT_BASE_URL="$BASE_URL"

    local cmd="npx playwright test"

    # Add suite filter
    case $SUITE in
        organizations)
            cmd="$cmd tests/organizations"
            ;;
        departments)
            cmd="$cmd tests/departments"
            ;;
        users)
            cmd="$cmd tests/users"
            ;;
        errors)
            cmd="$cmd tests/error-scenarios"
            ;;
        all)
            # Run all tests
            ;;
        *)
            print_error "Unknown suite: $SUITE"
            exit 1
            ;;
    esac

    # Add browser filter
    if [ "$BROWSER" != "all" ]; then
        cmd="$cmd --project=$BROWSER"
    fi

    # Add mode flags
    case $MODE in
        headed)
            cmd="$cmd --headed"
            ;;
        debug)
            cmd="$cmd --debug"
            ;;
        ui)
            cmd="$cmd --ui"
            ;;
        headless)
            # Default mode
            ;;
        *)
            print_error "Unknown mode: $MODE"
            exit 1
            ;;
    esac

    print_info "Running tests with command: $cmd"
    print_info "Mode: $MODE | Browser: $BROWSER | Suite: $SUITE"
    echo ""

    # Run tests
    if $cmd; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Some tests failed!"
        return 1
    fi
}

# Function to open report
open_report() {
    print_info "Opening HTML report..."
    npx playwright show-report
}

# Parse command line arguments
INSTALL=false
CLEAN=false
OPEN_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -b|--browser)
            BROWSER="$2"
            shift 2
            ;;
        -s|--suite)
            SUITE="$2"
            shift 2
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -i|--install)
            INSTALL=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -r|--report)
            OPEN_REPORT=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Main execution
print_info "Playwright E2E Test Runner"
print_info "=========================="
echo ""

# Install dependencies if requested
if [ "$INSTALL" = true ]; then
    install_deps
    exit 0
fi

# Clean previous results if requested
if [ "$CLEAN" = true ]; then
    clean_results
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Dependencies not installed. Installing..."
    install_deps
fi

# Check if application is running
check_app_running

# Run tests
if run_tests; then
    TEST_RESULT=0
else
    TEST_RESULT=1
fi

echo ""
print_info "=========================="

# Open report if requested
if [ "$OPEN_REPORT" = true ]; then
    open_report
fi

# Print summary
if [ $TEST_RESULT -eq 0 ]; then
    print_success "Test execution completed successfully"
else
    print_error "Test execution completed with failures"
fi

print_info "Reports available at:"
print_info "  - HTML: playwright-report/index.html"
print_info "  - JSON: test-results.json"
print_info "  - JUnit: junit-results.xml"

exit $TEST_RESULT
