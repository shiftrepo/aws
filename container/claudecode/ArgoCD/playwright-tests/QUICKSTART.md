# Playwright E2E Tests - Quick Start Guide

Get up and running with E2E tests in 5 minutes!

## Prerequisites

- Node.js 18+
- Application running at http://localhost:5006

## Quick Setup

### 1. Install Dependencies

```bash
cd playwright-tests
npm install
npx playwright install
```

### 2. Run Tests

```bash
# Run all tests (headless)
npm test

# Run with browser visible
npm run test:headed

# Run specific suite
npm run test:organizations
npm run test:departments
npm run test:users
```

### 3. View Results

```bash
npm run report
```

## Test Execution Options

### Using npm scripts

```bash
npm test                    # All tests, headless
npm run test:headed         # Show browser
npm run test:debug          # Debug mode
npm run test:ui             # Interactive UI
npm run test:chromium       # Chrome only
npm run test:firefox        # Firefox only
npm run test:webkit         # Safari only
```

### Using run script

```bash
# Basic usage
./run-tests.sh

# With options
./run-tests.sh --mode headed --browser chromium
./run-tests.sh --suite organizations --mode debug
./run-tests.sh --clean --report
```

## Common Tasks

### Run Specific Test File

```bash
npx playwright test tests/organizations/crud.spec.ts
```

### Run Single Test

```bash
npx playwright test -g "should create new organization"
```

### Debug Failed Test

```bash
npx playwright test tests/organizations/crud.spec.ts --debug
```

### Generate New Tests

```bash
npm run codegen
```

## Environment Configuration

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
PLAYWRIGHT_BASE_URL=http://localhost:5006
PLAYWRIGHT_HEADLESS=true
```

## Docker

### Build

```bash
docker build -t orgmgmt-e2e-tests .
```

### Run

```bash
docker run -e PLAYWRIGHT_BASE_URL=http://host.docker.internal:5006 orgmgmt-e2e-tests
```

## Test Structure

```
tests/
├── organizations/    # Organization CRUD, tree, search
├── departments/      # Department CRUD, hierarchy
├── users/           # User CRUD, assignments
└── error-scenarios/ # Validation, network, auth errors
```

## Troubleshooting

### Application not running

```bash
# Start application first
cd ../frontend
npm run dev

# Or check if running
curl http://localhost:5006
```

### Browser issues

```bash
# Reinstall browsers
npx playwright install --force
```

### Port conflicts

Update `.env`:
```bash
PLAYWRIGHT_BASE_URL=http://localhost:YOUR_PORT
```

## Next Steps

- Read full [README.md](README.md) for comprehensive documentation
- Customize `playwright.config.ts` for your needs
- Add new tests in appropriate directories
- Use Page Object Models for new pages

## Help

```bash
./run-tests.sh --help
npx playwright test --help
```

## Test Coverage

- 100+ test scenarios
- 3 browsers (Chrome, Firefox, Safari)
- Complete CRUD operations
- Error handling
- Network failures
- Authorization flows

Happy Testing!
