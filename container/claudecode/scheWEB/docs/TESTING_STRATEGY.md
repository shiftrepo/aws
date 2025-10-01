# Testing Strategy

## Overview

Comprehensive testing strategy for the Team Schedule Management System covering unit, integration, and performance testing.

## Testing Pyramid

```
                    /\
                   /  \
                  / E2E \         (10% - Manual/Automated)
                 /______\
                /        \
               / Integration\      (30% - API/Database)
              /____________\
             /              \
            /   Unit Tests   \    (60% - Business Logic)
           /__________________\
```

## Test Coverage Goals

| Test Type | Coverage Target | Priority |
|-----------|----------------|----------|
| Unit Tests | 80%+ | High |
| Integration Tests | 70%+ | High |
| E2E Tests | Critical paths | Medium |
| Performance Tests | All APIs | High |

## Unit Testing

### Scope
- Business logic
- Utility functions
- Data validation
- Error handling

### Framework: Jest

**Configuration:** `tests/unit/jest.config.js`

**Running Tests:**
```bash
# All unit tests
npm run test:unit

# Watch mode
npm run test:unit:watch

# Coverage report
npm run test:unit:coverage
```

### Test Structure

```javascript
describe('TeamService', () => {
  describe('createTeam', () => {
    it('should create a team with valid data', () => {
      // Arrange
      const teamData = {
        name: 'Engineering',
        color: '#FF5733'
      };

      // Act
      const result = teamService.createTeam(teamData);

      // Assert
      expect(result).toBeDefined();
      expect(result.name).toBe('Engineering');
      expect(result.color).toBe('#FF5733');
    });

    it('should throw error with invalid data', () => {
      // Arrange
      const invalidData = { name: '' };

      // Act & Assert
      expect(() => teamService.createTeam(invalidData))
        .toThrow('Team name is required');
    });
  });
});
```

### Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **One assertion per test** (when possible)
3. **Descriptive test names**
4. **Test edge cases**
5. **Mock external dependencies**
6. **No test interdependencies**

## Integration Testing

### Scope
- API endpoints
- Database operations
- Authentication/Authorization
- Error responses

### Framework: Jest + Supertest

**Configuration:** `tests/integration/jest.config.js`

**Running Tests:**
```bash
# All integration tests
npm run test:integration

# Specific test file
npm run test:integration -- teams.test.js
```

### Test Structure

```javascript
const request = require('supertest');
const app = require('../../src/app');
const db = require('../../src/database');

describe('Teams API', () => {
  beforeAll(async () => {
    // Set up test database
    await db.migrate();
  });

  afterAll(async () => {
    // Clean up
    await db.close();
  });

  beforeEach(async () => {
    // Reset database state
    await db.truncate('teams');
  });

  describe('POST /api/teams', () => {
    it('should create a team', async () => {
      const response = await request(app)
        .post('/api/teams')
        .auth('admin', 'password')
        .send({
          name: 'Engineering',
          color: '#FF5733'
        })
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe('Engineering');
    });

    it('should return 401 without authentication', async () => {
      await request(app)
        .post('/api/teams')
        .send({ name: 'Engineering' })
        .expect(401);
    });

    it('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/teams')
        .auth('admin', 'password')
        .send({ color: '#FF5733' })
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });
  });
});
```

### Test Database

**Setup:**
```javascript
// tests/integration/setup.js
const db = require('../../src/database');

beforeAll(async () => {
  // Use in-memory database for tests
  process.env.DATABASE_PATH = ':memory:';
  await db.migrate();
});

afterAll(async () => {
  await db.close();
});
```

## Performance Testing

### Scope
- API response times
- Concurrent user handling
- Resource utilization
- Scalability limits

### Tools

#### k6 (Primary)
- Load testing
- Stress testing
- Spike testing

#### Artillery (Alternative)
- Scenario-based testing
- Complex user flows

### Test Scenarios

**1. Baseline Performance**
```bash
# Normal load (10 users)
k6 run --vus 10 --duration 5m tests/performance/k6-load-test.js
```

**2. Peak Load**
```bash
# Maximum users (30)
k6 run --vus 30 --duration 10m tests/performance/k6-load-test.js
```

**3. Stress Test**
```bash
# Beyond capacity (50 users)
k6 run --vus 50 --duration 5m tests/performance/k6-load-test.js
```

**4. Spike Test**
```bash
# Sudden traffic spike
k6 run --stage 0s:10,30s:100,1m:100,1m30s:10 tests/performance/k6-load-test.js
```

### Performance Targets

| Metric | Target | Max Acceptable |
|--------|--------|----------------|
| Response Time (p95) | < 500ms | < 1000ms |
| Response Time (p99) | < 1000ms | < 2000ms |
| Error Rate | < 0.1% | < 1% |
| Throughput | > 100 req/s | > 50 req/s |
| Concurrent Users | 30 | 50 |
| CPU Usage | < 60% | < 80% |
| Memory Usage | < 400MB | < 512MB |

### Running Performance Tests

```bash
# k6 tests
npm run test:performance:k6

# Artillery tests
npm run test:performance:artillery

# Generate report
npm run test:performance:report
```

### Analyzing Results

**k6 Output:**
```
     ✓ health check status is 200
     ✓ get teams response time < 500ms
     ✓ create team status is 201

     checks.........................: 98.50%
     http_req_duration..............: avg=245ms min=23ms med=198ms max=987ms p(95)=456ms p(99)=789ms
     http_req_failed................: 1.50%
     http_reqs......................: 15420
     vus............................: 30
     vus_max........................: 30
```

**Key Metrics to Monitor:**
- `http_req_duration`: Response time distribution
- `http_req_failed`: Error rate
- `checks`: Validation success rate
- `http_reqs`: Total requests

## Security Testing

### Scope
- Authentication bypass
- SQL injection
- XSS vulnerabilities
- CSRF protection
- Rate limiting
- Input validation

### Tools
- OWASP ZAP
- npm audit
- Snyk
- SQLMap (controlled)

### Security Test Cases

```javascript
describe('Security Tests', () => {
  describe('SQL Injection Protection', () => {
    it('should prevent SQL injection in team name', async () => {
      const maliciousInput = "'; DROP TABLE teams; --";

      const response = await request(app)
        .post('/api/teams')
        .auth('admin', 'password')
        .send({ name: maliciousInput })
        .expect(400);

      // Verify table still exists
      const teams = await db.all('SELECT * FROM teams');
      expect(teams).toBeDefined();
    });
  });

  describe('Authentication', () => {
    it('should reject invalid credentials', async () => {
      await request(app)
        .get('/api/teams')
        .auth('admin', 'wrongpassword')
        .expect(401);
    });

    it('should require authentication', async () => {
      await request(app)
        .get('/api/teams')
        .expect(401);
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits', async () => {
      // Make 101 requests (limit is 100)
      const requests = Array(101).fill().map(() =>
        request(app)
          .get('/api/teams')
          .auth('admin', 'password')
      );

      const responses = await Promise.all(requests);
      const rateLimited = responses.filter(r => r.status === 429);

      expect(rateLimited.length).toBeGreaterThan(0);
    });
  });
});
```

## Test Data Management

### Test Fixtures

```javascript
// tests/fixtures/teams.js
module.exports = {
  validTeam: {
    name: 'Engineering',
    color: '#FF5733'
  },

  invalidTeams: [
    { name: '', color: '#FF5733' },
    { name: 'Engineering', color: 'invalid' },
    { name: null, color: '#FF5733' },
  ],

  sampleTeams: [
    { name: 'Engineering', color: '#FF5733' },
    { name: 'Design', color: '#33FF57' },
    { name: 'Product', color: '#3357FF' },
  ]
};
```

### Database Seeding

```javascript
// tests/helpers/seed.js
async function seedDatabase() {
  await db.run('DELETE FROM teams');
  await db.run('DELETE FROM schedules');

  const teams = await Promise.all([
    db.run('INSERT INTO teams (name, color) VALUES (?, ?)', ['Engineering', '#FF5733']),
    db.run('INSERT INTO teams (name, color) VALUES (?, ?)', ['Design', '#33FF57']),
  ]);

  return { teams };
}

module.exports = { seedDatabase };
```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Pull requests
- Pushes to main/develop
- Manual trigger

**Workflow:** `.github/workflows/ci-cd.yml`

### Local Pre-commit

```bash
# Install husky
npm install --save-dev husky

# Set up pre-commit hook
npx husky install
npx husky add .husky/pre-commit "npm test"
```

## Test Maintenance

### Regular Tasks

**Weekly:**
- Review test failures
- Update test data
- Check coverage reports

**Monthly:**
- Review performance benchmarks
- Update test scenarios
- Refactor slow tests

**Quarterly:**
- Security testing review
- Performance baseline update
- Test strategy review

### Test Quality Metrics

| Metric | Target | Action |
|--------|--------|--------|
| Test execution time | < 5 min | Optimize slow tests |
| Flaky test rate | < 1% | Fix or remove |
| Coverage decrease | 0% | Investigate |
| Failed tests | 0 | Fix immediately |

## Best Practices

### General

1. **Write tests first** (TDD approach)
2. **Keep tests independent**
3. **Use descriptive names**
4. **Test one thing at a time**
5. **Keep tests fast**
6. **Avoid test duplication**
7. **Document complex tests**

### Performance Testing

1. **Establish baseline** before changes
2. **Test in production-like environment**
3. **Monitor during tests**
4. **Test peak and off-peak scenarios**
5. **Document test conditions**

### Security Testing

1. **Never use production data**
2. **Test common vulnerabilities**
3. **Automate security scans**
4. **Document security requirements**
5. **Regular penetration testing**

## Troubleshooting

### Common Issues

**1. Tests Timing Out**
```javascript
// Increase timeout
jest.setTimeout(30000);

// Or per test
it('slow test', async () => {
  // test code
}, 30000);
```

**2. Database Conflicts**
```javascript
// Use separate database per test
beforeEach(async () => {
  const testDb = `:memory:`;
  await db.connect(testDb);
});
```

**3. Flaky Tests**
```javascript
// Add retries for network-dependent tests
jest.retryTimes(3);
```

## Resources

- **Jest Documentation**: https://jestjs.io/docs/getting-started
- **Supertest**: https://github.com/visionmedia/supertest
- **k6 Documentation**: https://k6.io/docs/
- **Artillery**: https://www.artillery.io/docs
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/

## Next Steps

1. Implement missing test cases
2. Set up continuous performance monitoring
3. Automate security scanning
4. Establish testing culture
5. Regular test review sessions
