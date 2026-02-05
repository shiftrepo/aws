# Organization Management System - E2E Tests

Comprehensive end-to-end test suite for the Organization Management System using Playwright.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Test Scenarios](#test-scenarios)
- [Project Structure](#project-structure)
- [CI/CD Integration](#cicd-integration)
- [Reports and Artifacts](#reports-and-artifacts)
- [Troubleshooting](#troubleshooting)

## Overview

This test suite provides comprehensive E2E testing coverage for:
- Organization management (CRUD operations)
- Department management and hierarchy
- User management and assignments
- Error handling and validation
- Network failure scenarios
- Authorization and authentication

**Total Tests:** 100+ comprehensive test scenarios

## Prerequisites

- Node.js 18+ and npm
- Application running at `http://localhost:5006` (or configure via environment)
- Docker (optional, for containerized testing)

## Installation

### Local Installation

```bash
cd playwright-tests
npm install
npx playwright install
npx playwright install-deps
```

### Docker Installation

```bash
cd playwright-tests
docker build -t orgmgmt-e2e-tests .
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key configuration options:

```bash
# Base URL of the application
PLAYWRIGHT_BASE_URL=http://localhost:5006

# Run in headless mode
PLAYWRIGHT_HEADLESS=true

# Browser selection
BROWSER=chromium

# CI mode
CI=false
```

### Playwright Configuration

Edit `playwright.config.ts` to customize:
- Test timeout
- Retries
- Parallel execution
- Browsers to test
- Screenshot/video settings

## Running Tests

### All Tests

```bash
npm test
```

### Headed Mode (with browser UI)

```bash
npm run test:headed
```

### Debug Mode

```bash
npm run test:debug
```

### Interactive UI Mode

```bash
npm run test:ui
```

### Specific Browser

```bash
npm run test:chromium
npm run test:firefox
npm run test:webkit
```

### Specific Test Suite

```bash
npm run test:organizations
npm run test:departments
npm run test:users
npm run test:errors
```

### Single Test File

```bash
npx playwright test tests/organizations/crud.spec.ts
```

### Single Test

```bash
npx playwright test -g "should create new organization"
```

### Generate Tests (Codegen)

```bash
npm run codegen
```

## Test Scenarios

### Organization Tests (20+ tests)

**CRUD Operations** (`tests/organizations/crud.spec.ts`)
- List all organizations with table rendering
- Create new organization with valid data
- Update organization details
- Delete organization with confirmation
- Search organizations by name
- Search organizations by code
- Filter active organizations
- Display pagination controls
- Handle empty search results
- Cancel organization creation

**Tree View** (`tests/organizations/tree-view.spec.ts`)
- View organization tree structure
- Expand departments in tree view
- Collapse departments in tree view
- Navigate through hierarchy levels
- Show organization with departments in tree
- Switch between tree and list views
- Maintain search functionality in tree view

**Search** (`tests/organizations/search.spec.ts`)
- Search by exact organization code
- Search by partial organization name
- Handle case-insensitive search
- Clear search results
- Show no results for non-existent search
- Update search results in real-time
- Preserve search when navigating between pages
- Search by organization description
- Handle special characters in search
- Display search count or results summary

### Department Tests (18+ tests)

**CRUD Operations** (`tests/departments/crud.spec.ts`)
- List departments with table rendering
- Create new department under organization
- Update department information
- Delete department
- Assign parent department
- Display pagination
- Search departments by code
- Search departments by name
- Cancel department creation
- Handle empty search results

**Hierarchy** (`tests/departments/hierarchy.spec.ts`)
- Create sub-department under parent
- Create multiple levels of hierarchy
- Move department to different parent
- View full hierarchy tree
- Expand and collapse hierarchy nodes
- Display department breadcrumb path
- Prevent circular parent-child relationships
- Show hierarchy depth indicator

### User Tests (21+ tests)

**CRUD Operations** (`tests/users/crud.spec.ts`)
- List all users with pagination
- Create new user with required fields
- Update user information
- Delete user with confirmation
- Search users by name
- Search users by username
- Search users by email
- Display user details in table
- Handle empty search results
- Cancel user creation
- Toggle user active status
- Display user count or summary
- Sort users by column

**Assignment** (`tests/users/assignment.spec.ts`)
- Assign user to department
- Change user department
- View users in department
- Unassign user from department
- Assign multiple users to same department
- Filter users by department
- Display department info in user list
- Prevent deletion of department with assigned users

### Error Scenario Tests (40+ tests)

**Validation** (`tests/error-scenarios/validation.spec.ts`)

Organization Validation:
- Empty organization code error
- Empty organization name error
- Duplicate organization code error
- Invalid organization code format
- Organization code length validation

Department Validation:
- Empty department code error
- Empty department name error
- Prevent selecting same department as parent
- Validate required fields on department form

User Validation:
- Empty username error
- Empty email error
- Invalid email format error
- Multiple invalid email formats
- Empty first name error
- Empty last name error
- Validate all required fields
- Username uniqueness validation
- Email uniqueness validation
- Display inline validation errors

**Network** (`tests/error-scenarios/network.spec.ts`)
- Handle API timeout gracefully
- Handle 500 server error
- Handle network failure
- Handle 404 Not Found error
- Handle 400 Bad Request error
- Retry failed requests
- Handle malformed JSON response
- Handle slow API responses
- Handle partial data load failure
- Handle CORS errors
- Handle connection timeout
- Show offline message when network is down
- Handle rate limiting (429 error)
- Handle service unavailable (503 error)

**Authorization** (`tests/error-scenarios/authorization.spec.ts`)
- Handle 401 unauthorized error
- Handle 403 forbidden error
- Redirect to login on authentication failure
- Handle expired session
- Handle insufficient permissions for create
- Handle insufficient permissions for delete
- Handle insufficient permissions for update
- Display error message for token expiration
- Handle missing authentication token
- Handle invalid authentication token
- Handle role-based access control errors
- Handle organization-level access restrictions
- Show login prompt when accessing protected route

## Project Structure

```
playwright-tests/
├── playwright.config.ts          # Playwright configuration
├── package.json                  # Dependencies and scripts
├── tsconfig.json                 # TypeScript configuration
├── .env.example                  # Environment variables template
├── Dockerfile                    # Docker container definition
├── README.md                     # This file
│
├── tests/                        # Test specifications
│   ├── organizations/
│   │   ├── crud.spec.ts         # Organization CRUD tests
│   │   ├── tree-view.spec.ts    # Tree view tests
│   │   └── search.spec.ts       # Search functionality tests
│   ├── departments/
│   │   ├── crud.spec.ts         # Department CRUD tests
│   │   └── hierarchy.spec.ts    # Hierarchy tests
│   ├── users/
│   │   ├── crud.spec.ts         # User CRUD tests
│   │   └── assignment.spec.ts   # Assignment tests
│   └── error-scenarios/
│       ├── validation.spec.ts   # Validation error tests
│       ├── network.spec.ts      # Network error tests
│       └── authorization.spec.ts # Auth error tests
│
├── page-objects/                 # Page Object Models
│   ├── OrganizationPage.ts     # Organization page abstraction
│   ├── DepartmentPage.ts       # Department page abstraction
│   └── UserPage.ts             # User page abstraction
│
├── fixtures/                     # Test data and fixtures
│   └── test-data.ts            # Sample test data
│
└── utils/                        # Utility functions
    ├── screenshot.ts           # Screenshot helpers
    └── coverage.ts             # Coverage helpers
```

## CI/CD Integration

### GitLab CI

```yaml
e2e-tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  script:
    - cd playwright-tests
    - npm ci
    - npm test
  artifacts:
    when: always
    paths:
      - playwright-tests/playwright-report/
      - playwright-tests/test-results/
    expire_in: 30 days
```

### GitHub Actions

```yaml
- name: Run Playwright tests
  run: |
    cd playwright-tests
    npm ci
    npx playwright install --with-deps
    npm test
```

### Docker

```bash
# Build
docker build -t orgmgmt-e2e-tests .

# Run
docker run -e PLAYWRIGHT_BASE_URL=http://host.docker.internal:5006 orgmgmt-e2e-tests

# Run with volume mounts for reports
docker run -v $(pwd)/reports:/tests/playwright-report orgmgmt-e2e-tests
```

## Reports and Artifacts

### HTML Report

After test run:

```bash
npm run report
```

Opens interactive HTML report in browser showing:
- Test results
- Screenshots
- Videos (on failure)
- Traces (on retry)

Report location: `playwright-report/index.html`

### JSON Report

JSON results available at: `test-results.json`

### JUnit Report

XML results for CI integration: `junit-results.xml`

### Screenshots

Screenshots saved to: `screenshots/`
- Captured on failure automatically
- Manual captures during tests
- Named with test name and timestamp

### Videos

Videos saved to: `test-results/`
- Recorded on failure
- Full test execution replay

### Traces

Traces saved to: `test-results/`
- Captured on first retry
- View with: `npx playwright show-trace trace.zip`

## Coverage

### Collecting Coverage

```bash
# Coverage is collected automatically during test runs
# Merge coverage reports
node utils/coverage.js
```

Coverage reports saved to: `coverage/`

## Troubleshooting

### Application Not Running

```
Error: page.goto: net::ERR_CONNECTION_REFUSED
```

**Solution:** Ensure application is running at configured base URL:
```bash
# Check application
curl http://localhost:5006

# Or update PLAYWRIGHT_BASE_URL in .env
```

### Browser Installation Issues

```bash
# Install browsers
npx playwright install

# Install system dependencies
npx playwright install-deps
```

### Port Conflicts

If port 5006 is in use, update configuration:
```bash
export PLAYWRIGHT_BASE_URL=http://localhost:YOUR_PORT
```

### Timeout Issues

Increase timeout in `playwright.config.ts`:
```typescript
timeout: 60000, // 60 seconds
```

### Docker Network Issues

Use host network mode:
```bash
docker run --network host orgmgmt-e2e-tests
```

### Flaky Tests

Enable retries in `playwright.config.ts`:
```typescript
retries: 2
```

### Debug Test Failures

```bash
# Run with debug flag
npm run test:debug

# Run specific test in headed mode
npx playwright test tests/organizations/crud.spec.ts --headed --debug
```

### View Trace

```bash
npx playwright show-trace test-results/path-to-trace.zip
```

## Best Practices

1. **Page Objects:** Use page object models for maintainability
2. **Test Data:** Use fixtures for consistent test data
3. **Waits:** Use explicit waits, avoid hard-coded timeouts
4. **Assertions:** Use Playwright's built-in expect assertions
5. **Cleanup:** Clean up test data after tests (if applicable)
6. **Screenshots:** Capture screenshots for debugging
7. **Isolation:** Each test should be independent
8. **Naming:** Use descriptive test names

## Contributing

1. Follow existing test patterns
2. Use TypeScript
3. Add page objects for new pages
4. Document complex test scenarios
5. Ensure tests are idempotent
6. Add appropriate waits and assertions

## License

ISC

## Support

For issues or questions:
- Check troubleshooting section
- Review Playwright documentation: https://playwright.dev
- Check application logs
- Verify application is running correctly
