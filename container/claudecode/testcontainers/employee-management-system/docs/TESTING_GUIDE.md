# Testing Guide - Employee Management System

Comprehensive testing strategies demonstrating three-tier database testing with PostgreSQL integration.

## 🎯 Testing Philosophy

This system implements a **progressive complexity testing approach** designed for learning database testing strategies:

1. **Repository Layer (Beginner)**: Database access patterns and JPA functionality
2. **Service Layer (Intermediate)**: Business logic, transactions, and error handling
3. **Controller Layer (Advanced)**: REST API integration and end-to-end scenarios

## 🏗️ Test Architecture

### Testing Stack
- **Test Framework**: JUnit 5 with Spring Boot Test
- **Database**: TestContainers with PostgreSQL
- **Test Data**: YAML-based configuration (editable without code changes)
- **Coverage**: JaCoCo with baseline comparison
- **Assertions**: AssertJ for fluent assertions

### Test Data Management
```yaml
# src/test/resources/testdata/employees.yml
employees:
  - firstName: "John"
    lastName: "Doe"
    email: "john.doe@test.com"
    hireDate: "2023-01-15"
    departmentId: 1
```

**Key Benefit**: Modify test data by editing YAML files - no code changes required!

## 🧪 Test Execution

### Basic Test Commands

#### Run All Tests
```bash
# Complete test suite
podman-compose exec app mvn test

# With coverage report
podman-compose exec app mvn test jacoco:report
```

#### Run by Test Level
```bash
# Repository layer tests (Beginner)
podman-compose exec app mvn test -Dtest="*Repository*"

# Service layer tests (Intermediate)
podman-compose exec app mvn test -Dtest="*Service*"

# Controller layer tests (Advanced)
podman-compose exec app mvn test -Dtest="*Controller*"

# Integration tests (Advanced)
podman-compose exec app mvn test -Dtest="*Integration*"
```

### Test Data Profiles

#### Available Profiles
```bash
# Basic dataset (5 employees, 3 departments)
podman-compose exec app mvn test -Dtestdata.profile=basic

# Medium dataset (20 employees, 5 departments)
podman-compose exec app mvn test -Dtestdata.profile=medium

# Large dataset (100+ employees, multiple departments)
podman-compose exec app mvn test -Dtestdata.profile=large

# Integration dataset (realistic relationships)
podman-compose exec app mvn test -Dtestdata.profile=integration
```

#### Custom Test Data
```bash
# Use custom CSV file
podman-compose exec app mvn test -Dtestdata.source=csv -Dtestdata.file=my-data.csv

# Validate test data only
podman-compose exec app mvn test -Dtestdata.validate-only=true
```

## 📊 Test Levels Explained

### Level 1: Repository Layer Tests (Beginner)

**Purpose**: Learn database access patterns and JPA query testing

#### Key Test Scenarios
```java
@DataJpaTest
class EmployeeRepositoryTest {

    // Basic CRUD operations
    @Test
    void shouldSaveAndFindEmployee() {
        // Test basic save/find operations
    }

    // Query method testing
    @Test
    void shouldFindEmployeesByDepartment() {
        // Test derived query methods
    }

    // Custom query testing
    @Test
    void shouldFindEmployeesWithComplexCriteria() {
        // Test @Query annotations
    }
}
```

#### What You Learn
- JPA entity mapping and relationships
- Repository query method testing
- Database constraint validation
- Custom query verification
- Transaction boundaries

#### Example Tests
```bash
# Run repository tests
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest"
podman-compose exec app mvn test -Dtest="DepartmentRepositoryTest"
```

### Level 2: Service Layer Tests (Intermediate)

**Purpose**: Test business logic, transactions, and service orchestration

#### Key Test Scenarios
```java
@SpringBootTest
@Transactional
class EmployeeServiceTest {

    // Business logic testing
    @Test
    void shouldCalculateEmployeeYearsOfService() {
        // Test business calculations
    }

    // Transaction testing
    @Test
    @Rollback(false)
    void shouldHandleTransactionalOperations() {
        // Test transaction management
    }

    // Error handling
    @Test
    void shouldThrowExceptionForInvalidData() {
        // Test error scenarios
    }
}
```

#### What You Learn
- Business logic validation
- Transaction management testing
- Error handling strategies
- Service layer mocking
- Data transformation testing

#### Advanced Scenarios
```bash
# Test with mock dependencies
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldHandleDepartmentTransfer"

# Test transaction rollback
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldRollbackOnError"
```

### Level 3: Controller Layer Tests (Advanced)

**Purpose**: Test REST API endpoints and end-to-end integration

#### Key Test Scenarios
```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class EmployeeControllerTest {

    // REST endpoint testing
    @Test
    void shouldCreateEmployeeViaRestAPI() {
        // Test HTTP POST with JSON
    }

    // Integration testing
    @Test
    void shouldPerformCompleteEmployeeWorkflow() {
        // Test full user scenario
    }

    // Error response testing
    @Test
    void shouldReturn400ForInvalidData() {
        // Test error responses
    }
}
```

#### What You Learn
- REST API endpoint testing
- JSON serialization/deserialization
- HTTP status code validation
- End-to-end workflow testing
- Error response handling

## 🎮 Interactive Testing Scenarios

### Scenario 1: Basic Employee Management
```bash
# Test basic CRUD operations
podman-compose exec app mvn test -Dtest="*Repository*" -Dtestdata.profile=basic

# Inspect test results
cat target/surefire-reports/TEST-*.xml | grep -E "(testcase|failure)"
```

### Scenario 2: Department Transfers
```bash
# Test complex business logic
podman-compose exec app mvn test -Dtest="*Service*" -Dtestdata.profile=medium

# View detailed logs
podman-compose exec app mvn test -Dtest="DepartmentServiceTest#shouldTransferAllEmployees" -X
```

### Scenario 3: API Integration
```bash
# Test complete REST API workflows
podman-compose exec app mvn test -Dtest="*Controller*" -Dtestdata.profile=integration

# Test specific API endpoint
podman-compose exec app mvn test -Dtest="EmployeeControllerTest#shouldSearchEmployees"
```

## 🔧 Test Data Customization

### Editing Test Data Files

#### Employee Test Data
```yaml
# src/test/resources/testdata/employees.yml
employees:
  - firstName: "Alice"           # ← Edit directly
    lastName: "Johnson"          # ← No code changes needed
    email: "alice@company.com"   # ← Just modify YAML
    hireDate: "2024-01-15"      # ← Save and run tests
    departmentId: 1
    active: true
```

#### Department Test Data
```yaml
# src/test/resources/testdata/departments.yml
departments:
  - name: "Engineering"          # ← Modify department names
    code: "ENG"                 # ← Change codes
    budget: 2500000.00          # ← Adjust budgets
    description: "Software Development"
    active: true
```

### Creating Custom Scenarios
```yaml
# src/test/resources/testdata/scenarios/my-scenario.yml
departments:
  - name: "Custom Department"
    code: "CUSTOM"
    budget: 1000000.00
    active: true

employees:
  - firstName: "Test"
    lastName: "User"
    email: "test@example.com"
    hireDate: "2024-01-01"
    departmentId: 1
```

```bash
# Run with custom scenario
podman-compose exec app mvn test -Dtestdata.profile=my-scenario
```

## 📈 Coverage and Quality Metrics

### Generate Coverage Reports
```bash
# Run tests with coverage
podman-compose exec app mvn clean test jacoco:report

# Copy report to host (for viewing)
podman cp $(podman-compose ps -q app):/workspace/target/site/jacoco ./coverage-report

# Open in browser
open coverage-report/index.html
```

### Coverage Targets
- **Repository Layer**: 95%+ coverage
- **Service Layer**: 90%+ coverage
- **Controller Layer**: 85%+ coverage
- **Overall Project**: 90%+ coverage

### Quality Gates
```bash
# Run with quality gate enforcement
podman-compose exec app mvn test -Dquality.gate=true

# This will fail the build if coverage is below targets
```

## 🎯 Regression Testing

### Baseline Comparison
```bash
# Run tests and compare with baseline
podman-compose exec app mvn test -Dregression.compare=true

# Generate new baseline (after confirming results are correct)
podman-compose exec app mvn test -Dregression.update-baseline=true
```

### Automated Regression Detection
```bash
# Run full regression suite
podman-compose exec app mvn test -Dtest.suite=regression

# Check for performance regressions
podman-compose exec app mvn test -Dtest.suite=performance
```

## 🐛 Debugging Tests

### Debug Mode Execution
```bash
# Run tests with debug logging
podman-compose exec app mvn test -X -Dtest.log.level=DEBUG

# Run specific test with SQL logging
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest" -DTEST_SHOW_SQL=true
```

### Database State Inspection
```bash
# Connect to test database during test execution
podman-compose exec postgres psql -U postgres -d employee_db

# View test data
SELECT e.first_name, e.last_name, d.name as department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;
```

### Test Failure Analysis
```bash
# Detailed test failure reports
cat target/surefire-reports/TEST-*.xml

# View test execution timeline
cat target/surefire-reports/*.txt | grep -E "(Test|FAILURE|ERROR)"
```

## 🎪 Advanced Testing Features

### Performance Testing
```bash
# Run performance test suite
podman-compose exec app mvn test -Dtest="*Performance*" -Dtestdata.profile=large

# Monitor database performance during tests
podman-compose exec postgres psql -U postgres -d employee_db \\
  -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

### Concurrent Testing
```bash
# Run tests in parallel (faster execution)
podman-compose exec app mvn test -DforkCount=2 -DreuseForks=true

# Test concurrent database access
podman-compose exec app mvn test -Dtest="*Concurrent*"
```

### Data Migration Testing
```bash
# Test database schema migrations
podman-compose exec app mvn flyway:migrate
podman-compose exec app mvn test -Dtest="*Migration*"
```

## 📚 Learning Path

### Beginner Track
1. Start with Repository layer tests
2. Understand JPA and database mapping
3. Learn query method testing
4. Practice with basic test data

```bash
# Follow this progression
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest#shouldFindByEmail"
podman-compose exec app mvn test -Dtest="EmployeeRepositoryTest#shouldFindActiveEmployees"
podman-compose exec app mvn test -Dtest="DepartmentRepositoryTest#shouldFindByCode"
```

### Intermediate Track
1. Move to Service layer testing
2. Learn transaction management
3. Practice business logic testing
4. Understand error handling

```bash
# Service layer progression
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldCreateEmployee"
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldTransferEmployee"
podman-compose exec app mvn test -Dtest="EmployeeServiceTest#shouldHandleInvalidData"
```

### Advanced Track
1. Master Controller layer testing
2. Learn REST API testing patterns
3. Practice integration testing
4. Understand end-to-end workflows

```bash
# Advanced testing progression
podman-compose exec app mvn test -Dtest="EmployeeControllerTest#shouldCreateEmployeeAPI"
podman-compose exec app mvn test -Dtest="EmployeeManagementIntegrationTest"
```

## 🔍 Troubleshooting Tests

### Common Test Issues

#### Test Data Problems
```bash
# Validate test data format
podman-compose exec app mvn test -Dtestdata.validate-only=true

# Refresh test data
podman-compose exec app mvn test -Dtestdata.refresh=true
```

#### Database Connection Issues
```bash
# Check TestContainer database status
podman-compose logs postgres

# Verify test database connectivity
podman-compose exec postgres pg_isready -U postgres
```

#### Flaky Tests
```bash
# Run flaky test multiple times
for i in {1..5}; do
  podman-compose exec app mvn test -Dtest="FlakyTest" || break
done

# Enable test retry
podman-compose exec app mvn test -Dsurefire.rerunFailingTestsCount=2
```

### Performance Issues
```bash
# Profile test execution
podman-compose exec app mvn test -Dtest.profile=true

# Optimize TestContainer startup
export TESTCONTAINERS_REUSE_ENABLE=true
podman-compose exec app mvn test
```

## 📊 Test Reporting

### Generate Comprehensive Reports
```bash
# All test reports
podman-compose exec app mvn clean test site

# Individual reports
podman-compose exec app mvn surefire-report:report      # Test results
podman-compose exec app mvn jacoco:report               # Coverage
podman-compose exec app mvn pmd:pmd                     # Code quality
```

### View Reports
```bash
# Copy all reports to host
podman cp $(podman-compose ps -q app):/workspace/target/site ./test-reports

# Open main report
open test-reports/index.html
```

---

**Next Steps**: After mastering the testing strategies, explore the [API Documentation](API_DOCUMENTATION.md) to understand the REST endpoints being tested.