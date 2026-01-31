# Employee Management System

A comprehensive containerized employee management system demonstrating PostgreSQL database integration with Spring Boot and extensive testing strategies.

## 🚀 Quick Start

```bash
# Start the complete environment
podman-compose up -d

# Verify services are running
podman-compose ps

# Access the application
curl http://localhost:8080/api/v1/employees
```

## 📋 Overview

This project implements a complete employee and department management system designed for **comprehensive database testing education**. It demonstrates:

- **Containerized Development Environment**: PostgreSQL + pgAdmin + Java development container
- **Three-Tier Testing Strategy**: Repository → Service → Controller testing levels
- **Maintainable Test Data**: YAML-based test data that can be modified without code changes
- **Real-World Scenarios**: Complex queries, transactions, and business logic testing

## 🏗️ Architecture

### Technology Stack
- **Backend**: Spring Boot 3.x with Spring Data JPA
- **Database**: PostgreSQL 15 with full-text search capabilities
- **Testing**: JUnit 5 + TestContainers + comprehensive test utilities
- **Container Management**: podman-compose for complete environment orchestration
- **Build Tool**: Maven with integrated testing and coverage reporting

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   REST API      │    │   Service Layer  │    │  Repository     │
│   Controllers   │◄──►│  Business Logic  │◄──►│  Data Access    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   PostgreSQL    │
                                                │    Database     │
                                                └─────────────────┘
```

## 🎯 Testing Strategy

### Three-Level Testing Approach

#### 1. **Repository Layer Tests** (Beginner Level)
- Basic CRUD operations testing
- JPA query method validation
- Custom query verification
- Database constraint testing

#### 2. **Service Layer Tests** (Intermediate Level)
- Business logic validation
- Transaction management testing
- Error handling verification
- Mock integration testing

#### 3. **Controller Layer Tests** (Advanced Level)
- REST API endpoint testing
- JSON serialization/deserialization
- HTTP status code validation
- Integration test scenarios

### Test Data Management
- **YAML-Based Configuration**: Modify test data without changing code
- **Scenario-Specific Datasets**: Different data sets for different test types
- **Automatic Cleanup**: Tests clean up after themselves
- **Regression Testing**: Compare results with baseline data

## 🛠️ Setup and Installation

### Prerequisites
- **podman** and **podman-compose** installed
- **Java 17+** (for local development)
- **Maven 3.6+** (for local development)

### Environment Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd employee-management-system
   ```

2. **Start All Services**
   ```bash
   podman-compose up -d
   ```

3. **Verify Installation**
   ```bash
   # Check all services are running
   podman-compose ps

   # Test database connection
   podman-compose exec postgres pg_isready -U postgres

   # Access pgAdmin (http://localhost:5050)
   # Email: admin@example.com, Password: admin
   ```

### Service Endpoints
- **Application**: http://localhost:8080
- **pgAdmin**: http://localhost:5050
- **PostgreSQL**: localhost:5432

## 🧪 Running Tests

### Basic Test Execution
```bash
# All tests
podman-compose exec app mvn test

# Specific test levels
podman-compose exec app mvn test -Dtest="*Repository*"  # Repository tests
podman-compose exec app mvn test -Dtest="*Service*"    # Service tests
podman-compose exec app mvn test -Dtest="*Controller*" # Controller tests
```

### Advanced Test Scenarios
```bash
# Test with specific data profile
podman-compose exec app mvn test -Dtestdata.profile=medium

# Run regression tests
podman-compose exec app mvn test -Dtest.suite=regression

# Generate coverage report
podman-compose exec app mvn test jacoco:report
```

### Test Data Profiles
- **`basic`**: Minimal dataset for quick testing
- **`medium`**: Moderate dataset for comprehensive testing
- **`large`**: Large dataset for performance testing
- **`integration`**: Complete dataset for end-to-end testing

## 📊 Database Schema

### Core Entities

#### Departments
```sql
CREATE TABLE departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    budget DECIMAL(12,2) NOT NULL,
    description VARCHAR(500),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0
);
```

#### Employees
```sql
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hire_date DATE NOT NULL,
    phone_number VARCHAR(15),
    address VARCHAR(200),
    active BOOLEAN NOT NULL DEFAULT true,
    department_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0,
    CONSTRAINT fk_employee_department FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

## 🔧 Development Workflow

### 1. Modify Test Data
Edit YAML files directly - no code changes needed:
```bash
# Edit test data
vi src/test/resources/testdata/employees.yml
vi src/test/resources/testdata/departments.yml

# Run tests with new data
podman-compose exec app mvn test
```

### 2. Add New Tests
```bash
# Create new test class
vi src/test/java/com/example/employee/repository/MyNewRepositoryTest.java

# Run specific test
podman-compose exec app mvn test -Dtest="MyNewRepositoryTest"
```

### 3. Database Inspection
```bash
# Connect to database directly
podman-compose exec postgres psql -U postgres -d employee_db

# Or use pgAdmin web interface
# http://localhost:5050
```

## 📚 API Documentation

### Departments API

#### GET /api/v1/departments
```bash
# Get all departments
curl http://localhost:8080/api/v1/departments

# Get active departments only
curl http://localhost:8080/api/v1/departments?activeOnly=true
```

#### POST /api/v1/departments
```bash
curl -X POST http://localhost:8080/api/v1/departments \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "New Department",
    "code": "NEW",
    "budget": 1000000.00,
    "description": "A new department"
  }'
```

### Employees API

#### GET /api/v1/employees
```bash
# Get all employees
curl http://localhost:8080/api/v1/employees

# Search employees
curl "http://localhost:8080/api/v1/employees/search?term=John"

# Get employees by department
curl http://localhost:8080/api/v1/employees/department/1
```

#### POST /api/v1/employees
```bash
curl -X POST http://localhost:8080/api/v1/employees \\
  -H "Content-Type: application/json" \\
  -d '{
    "firstName": "New",
    "lastName": "Employee",
    "email": "new.employee@company.com",
    "hireDate": "2024-01-15",
    "departmentId": 1
  }'
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL is running
podman-compose ps postgres

# Check database logs
podman-compose logs postgres

# Test connection manually
podman-compose exec postgres pg_isready -U postgres
```

#### Test Failures
```bash
# Run tests with detailed logging
podman-compose exec app mvn test -Dtest.log.level=DEBUG

# Check test database state
podman-compose exec postgres psql -U postgres -d employee_db -c "\\dt"
```

#### Container Issues
```bash
# Restart all services
podman-compose down && podman-compose up -d

# Rebuild containers
podman-compose build --no-cache

# Clean volumes (WARNING: deletes all data)
podman-compose down -v
```

## 📈 Performance Monitoring

### JaCoCo Coverage Reports
```bash
# Generate coverage report
podman-compose exec app mvn test jacoco:report

# View report
open target/site/jacoco/index.html
```

### Database Performance
```bash
# Check database statistics
podman-compose exec postgres psql -U postgres -d employee_db \\
  -c "SELECT * FROM pg_stat_user_tables;"

# Monitor active connections
podman-compose exec postgres psql -U postgres -d employee_db \\
  -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes and add tests**
4. **Ensure all tests pass**: `podman-compose exec app mvn test`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**

### Testing Guidelines
- All new features must include tests at all three levels (Repository, Service, Controller)
- Test data should be added to appropriate YAML files
- Maintain test isolation - tests should not depend on each other
- Follow existing naming conventions for test methods

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spring Boot Team** for the excellent framework
- **TestContainers** for making integration testing seamless
- **PostgreSQL Community** for the robust database platform
- **podman Community** for container orchestration capabilities

---

**Built for comprehensive database testing education and real-world development practices.**