# Quick Start Guide

## Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0

## Installation

```bash
# Install pnpm globally (if not already installed)
npm install -g pnpm@8.10.0

# Install project dependencies
pnpm install

# Install Playwright browsers
pnpm playwright:install
```

## Development

```bash
# Start development server (http://localhost:3000)
pnpm dev
```

The application will be available at `http://localhost:3000`.

## Testing

### Unit Tests

```bash
# Run all unit tests
pnpm test

# Run tests in watch mode
pnpm test --watch

# Run tests with coverage
pnpm test --coverage
```

### E2E Tests

```bash
# Run E2E tests
pnpm test:e2e

# Run E2E tests with UI
pnpm test:e2e --ui

# Run E2E tests with coverage
pnpm test:coverage
```

## Coverage Reports

```bash
# Generate coverage report
pnpm coverage:report

# View HTML report
open coverage/index.html
```

Coverage is collected from both unit tests and E2E tests, then merged into a single report.

## Linting

```bash
# Run ESLint (includes architecture checks)
pnpm lint

# Fix auto-fixable issues
pnpm lint:fix

# TypeScript type checking
pnpm type-check
```

## Build

```bash
# Build all modules
pnpm build

# Build web app only
pnpm build:web

# Preview production build
pnpm preview
```

## Project Structure

```
sampleJS/
├── apps/
│   └── web/              # Web application
├── modules/
│   ├── domain/           # Domain models (no dependencies)
│   ├── application/      # Use cases (depends on domain)
│   ├── api/              # API client (depends on domain, application)
│   ├── ui/               # UI components (depends on domain, application, util)
│   └── util/             # Utilities (no dependencies)
├── tests/
│   └── e2e/              # E2E tests with Playwright
├── scripts/
│   └── collect-coverage.js  # Coverage aggregation
└── azure-pipelines.yml   # CI/CD pipeline
```

## Architecture Rules

The project enforces strict dependency rules via ESLint:

- **domain**: No dependencies ✓
- **util**: No dependencies ✓
- **application**: Can only depend on `domain` ✓
- **api**: Can depend on `domain`, `application` ✓
- **ui**: Can depend on `domain`, `application`, `util` ✓
- **web**: Can depend on all modules ✓

Any violation of these rules will cause a lint error:

```bash
❌ Error: domain cannot depend on application
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build all modules |
| `pnpm build:web` | Build web app only |
| `pnpm test` | Run unit tests |
| `pnpm test:e2e` | Run E2E tests |
| `pnpm test:coverage` | Run E2E with coverage |
| `pnpm coverage:report` | Generate coverage report |
| `pnpm lint` | Run ESLint |
| `pnpm lint:fix` | Fix ESLint errors |
| `pnpm type-check` | Run TypeScript checks |
| `pnpm preview` | Preview production build |
| `pnpm clean` | Clean all build artifacts |

## Features

- ✅ Employee CRUD operations
- ✅ Form validation
- ✅ Responsive design
- ✅ Data-testid attributes for testing
- ✅ Error handling
- ✅ Loading states

## API Mocking

For development and testing, the application uses MSW (Mock Service Worker) to mock API endpoints:

- `GET /api/employees` - List all employees
- `GET /api/employees/:id` - Get employee by ID
- `POST /api/employees` - Create employee
- `PUT /api/employees/:id` - Update employee
- `DELETE /api/employees/:id` - Delete employee

## CI/CD

The project includes a complete Azure DevOps pipeline with the following stages:

1. **Install** - Dependencies installation
2. **Lint** - Code quality checks
3. **UnitTest** - Unit test execution
4. **Build** - Production build
5. **E2ETest** - E2E test execution
6. **Coverage** - Coverage report generation
7. **SonarQube** - Code analysis (optional)
8. **Deploy** - Deployment (optional)

## Troubleshooting

### Port 3000 already in use

```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9
```

### Playwright browser not installed

```bash
pnpm playwright:install
```

### Dependencies out of sync

```bash
pnpm install --frozen-lockfile
```

### Clear all build artifacts

```bash
pnpm clean
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Run development server
3. ✅ Make changes to the code
4. ✅ Run tests
5. ✅ Check coverage
6. ✅ Commit changes

## Documentation

- [README.md](./README.md) - Full project documentation
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Implementation details

## Support

For issues or questions, please check:

1. The README.md file
2. The IMPLEMENTATION_SUMMARY.md file
3. TypeScript/ESLint error messages
4. Test output and coverage reports
