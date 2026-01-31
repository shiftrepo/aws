# API Documentation - Employee Management System

Complete REST API documentation for the Employee Management System with comprehensive examples and testing scenarios.

## 🔗 Base URL

```
http://localhost:8080/api/v1
```

## 📋 API Overview

The Employee Management System provides RESTful APIs for managing employees and departments with comprehensive CRUD operations, search capabilities, and business logic endpoints.

### Authentication
Currently, the API operates without authentication for educational purposes. In production environments, implement appropriate authentication mechanisms.

### Response Format
All API responses follow a consistent JSON structure:

```json
{
  "id": 1,
  "name": "Resource Name",
  "createdAt": "2024-01-15T10:30:00Z",
  "modifiedAt": "2024-01-15T10:30:00Z"
}
```

### Error Handling
Error responses include detailed information:

```json
{
  "error": "Bad Request",
  "message": "Employee email already exists",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/employees"
}
```

## 👥 Employees API

### Core Operations

#### GET /api/v1/employees
Retrieve all employees with optional filtering.

**Parameters:**
- `activeOnly` (boolean, optional): Filter for active employees only

```bash
# Get all employees
curl http://localhost:8080/api/v1/employees

# Get active employees only
curl http://localhost:8080/api/v1/employees?activeOnly=true
```

**Response:**
```json
[
  {
    "id": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@company.com",
    "hireDate": "2023-01-15",
    "phoneNumber": "+1-555-0101",
    "address": "123 Main St, City, State",
    "active": true,
    "departmentId": 1,
    "departmentName": "Human Resources",
    "departmentCode": "HR",
    "fullName": "John Doe",
    "yearsOfService": 1,
    "isNewEmployee": false,
    "isVeteranEmployee": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "modifiedAt": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /api/v1/employees/{id}
Retrieve a specific employee by ID.

```bash
curl http://localhost:8080/api/v1/employees/1
```

**Response:** Single employee object (same structure as above)

#### GET /api/v1/employees/email/{email}
Retrieve an employee by email address.

```bash
curl http://localhost:8080/api/v1/employees/email/john.doe@company.com
```

#### POST /api/v1/employees
Create a new employee.

```bash
curl -X POST http://localhost:8080/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@company.com",
    "hireDate": "2024-01-15",
    "phoneNumber": "+1-555-0102",
    "address": "456 Oak Ave, City, State",
    "departmentId": 2
  }'
```

**Validation Rules:**
- `firstName`: Required, 1-50 characters
- `lastName`: Required, 1-50 characters
- `email`: Required, valid email format, unique
- `hireDate`: Required, not in future
- `phoneNumber`: Optional, valid phone format
- `address`: Optional, max 200 characters

#### PUT /api/v1/employees/{id}
Update an existing employee.

```bash
curl -X PUT http://localhost:8080/api/v1/employees/1 \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Updated",
    "email": "john.updated@company.com",
    "hireDate": "2023-01-15",
    "phoneNumber": "+1-555-0199",
    "address": "999 Updated St, City, State",
    "departmentId": 2,
    "active": true
  }'
```

#### DELETE /api/v1/employees/{id}
Delete an employee (soft delete by setting active=false).

```bash
curl -X DELETE http://localhost:8080/api/v1/employees/1
```

### Department Operations

#### PATCH /api/v1/employees/{id}/department/{departmentId}
Assign employee to a department.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/department/2
```

#### PATCH /api/v1/employees/{id}/remove-department
Remove employee from their current department.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/remove-department
```

#### POST /api/v1/employees/{id}/transfer/{newDepartmentId}
Transfer employee to a new department with business rule validation.

```bash
curl -X POST http://localhost:8080/api/v1/employees/1/transfer/3
```

### Status Operations

#### PATCH /api/v1/employees/{id}/activate
Activate an employee.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/activate
```

#### PATCH /api/v1/employees/{id}/deactivate
Deactivate an employee.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/1/deactivate
```

### Search and Filtering

#### GET /api/v1/employees/search
Advanced employee search with multiple criteria.

**Parameters:**
- `term` (string): Search in names and emails
- `hiredAfter` (date): Filter by hire date after
- `hiredBefore` (date): Filter by hire date before
- `hiredInYear` (integer): Filter by specific hire year
- `minYearsOfService` (integer): Minimum years of service
- `minDepartmentBudget` (decimal): Minimum department budget
- `fullText` (boolean): Enable PostgreSQL full-text search

```bash
# Search by name
curl "http://localhost:8080/api/v1/employees/search?term=John"

# Search by hire date range
curl "http://localhost:8080/api/v1/employees/search?hiredAfter=2023-01-01&hiredBefore=2023-12-31"

# Search by years of service
curl "http://localhost:8080/api/v1/employees/search?minYearsOfService=5"

# Full-text search (PostgreSQL specific)
curl "http://localhost:8080/api/v1/employees/search?term=manager&fullText=true"
```

#### Department-Based Queries

```bash
# Get employees by department ID
curl http://localhost:8080/api/v1/employees/department/1

# Get employees by department code
curl http://localhost:8080/api/v1/employees/department/code/HR

# Get employees without department
curl http://localhost:8080/api/v1/employees/without-department

# Get employees in active departments only
curl http://localhost:8080/api/v1/employees/in-active-departments
```

#### Special Categories

```bash
# Get new employees (hired within last year)
curl http://localhost:8080/api/v1/employees/new-employees

# Get veteran employees (5+ years of service)
curl http://localhost:8080/api/v1/employees/veteran-employees
```

### Statistics and Analytics

#### GET /api/v1/employees/statistics
Get employee statistics and analytics.

```bash
curl http://localhost:8080/api/v1/employees/statistics
```

**Response:**
```json
{
  "totalActiveEmployees": 25,
  "hiringStatisticsByYear": [
    [2023, 15],
    [2024, 10]
  ],
  "departmentEmployeeCounts": [
    ["IT", 8],
    ["HR", 5],
    ["Finance", 4]
  ]
}
```

#### GET /api/v1/employees/statistics/department/{departmentId}
Get statistics for a specific department.

```bash
curl http://localhost:8080/api/v1/employees/statistics/department/1
```

### Validation Endpoints

#### GET /api/v1/employees/email/{email}/unique
Check if an email is unique.

**Parameters:**
- `excludeId` (integer, optional): Exclude specific employee from check

```bash
curl "http://localhost:8080/api/v1/employees/email/new@company.com/unique"
curl "http://localhost:8080/api/v1/employees/email/existing@company.com/unique?excludeId=1"
```

**Response:**
```json
{
  "unique": true
}
```

#### GET /api/v1/employees/{id}/active
Check if employee is active.

```bash
curl http://localhost:8080/api/v1/employees/1/active
```

#### GET /api/v1/employees/{id}/can-delete
Check if employee can be deleted.

```bash
curl http://localhost:8080/api/v1/employees/1/can-delete
```

#### GET /api/v1/employees/{employeeId}/can-assign/{departmentId}
Check if employee can be assigned to department.

```bash
curl http://localhost:8080/api/v1/employees/1/can-assign/2
```

### Batch Operations

#### PATCH /api/v1/employees/batch/activate
Activate multiple employees.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/batch/activate \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3, 4, 5]'
```

**Response:**
```json
{
  "activated": 5
}
```

#### PATCH /api/v1/employees/batch/deactivate
Deactivate multiple employees.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/batch/deactivate \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3]'
```

#### PATCH /api/v1/employees/batch/transfer/{newDepartmentId}
Transfer multiple employees to a new department.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/batch/transfer/2 \
  -H "Content-Type: application/json" \
  -d '[1, 3, 5]'
```

#### PATCH /api/v1/employees/department/{departmentId}/remove-all
Remove all employees from a department.

```bash
curl -X PATCH http://localhost:8080/api/v1/employees/department/1/remove-all
```

## 🏢 Departments API

### Core Operations

#### GET /api/v1/departments
Retrieve all departments with optional filtering.

**Parameters:**
- `activeOnly` (boolean, optional): Filter for active departments only

```bash
# Get all departments
curl http://localhost:8080/api/v1/departments

# Get active departments only
curl http://localhost:8080/api/v1/departments?activeOnly=true
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Human Resources",
    "code": "HR",
    "budget": 1200000.00,
    "description": "Human Resources Department",
    "active": true,
    "employeeCount": 5,
    "createdAt": "2024-01-15T10:30:00Z",
    "modifiedAt": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /api/v1/departments/{id}
Retrieve a specific department by ID.

```bash
curl http://localhost:8080/api/v1/departments/1
```

#### GET /api/v1/departments/code/{code}
Retrieve a department by code.

```bash
curl http://localhost:8080/api/v1/departments/code/HR
```

#### GET /api/v1/departments/with-employee-count
Get all departments with employee counts.

```bash
curl http://localhost:8080/api/v1/departments/with-employee-count
```

#### POST /api/v1/departments
Create a new department.

```bash
curl -X POST http://localhost:8080/api/v1/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Department",
    "code": "NEW",
    "budget": 1500000.00,
    "description": "A new department for testing"
  }'
```

**Validation Rules:**
- `name`: Required, 2-100 characters
- `code`: Required, 2-10 characters, unique
- `budget`: Required, positive number
- `description`: Optional, max 500 characters

#### PUT /api/v1/departments/{id}
Update an existing department.

```bash
curl -X PUT http://localhost:8080/api/v1/departments/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated HR Department",
    "code": "HR",
    "budget": 1300000.00,
    "description": "Updated Human Resources Department",
    "active": true
  }'
```

#### DELETE /api/v1/departments/{id}
Delete a department (only if no active employees).

```bash
curl -X DELETE http://localhost:8080/api/v1/departments/1
```

### Status Operations

#### PATCH /api/v1/departments/{id}/activate
Activate a department.

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/1/activate
```

#### PATCH /api/v1/departments/{id}/deactivate
Deactivate a department.

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/1/deactivate
```

### Search Operations

#### GET /api/v1/departments/search
Advanced department search.

**Parameters:**
- `name` (string): Search by name pattern
- `minBudget` (decimal): Minimum budget filter
- `maxBudget` (decimal): Maximum budget filter
- `minEmployees` (integer): Minimum employee count

```bash
# Search by name
curl "http://localhost:8080/api/v1/departments/search?name=Tech"

# Search by budget range
curl "http://localhost:8080/api/v1/departments/search?minBudget=1000000&maxBudget=2000000"

# Search by minimum employee count
curl "http://localhost:8080/api/v1/departments/search?minEmployees=5"
```

#### GET /api/v1/departments/above-average-budget
Get departments with above-average budget.

```bash
curl http://localhost:8080/api/v1/departments/above-average-budget
```

### Statistics Operations

#### GET /api/v1/departments/statistics
Get department statistics.

```bash
curl http://localhost:8080/api/v1/departments/statistics
```

**Response:**
```json
{
  "totalActiveDepartments": 5,
  "totalActiveBudget": 9500000.00,
  "averageActiveBudget": 1900000.00
}
```

### Business Operations

#### POST /api/v1/departments/{fromId}/transfer-employees/{toId}
Transfer all employees from one department to another.

```bash
curl -X POST http://localhost:8080/api/v1/departments/1/transfer-employees/2
```

**Response:**
```json
{
  "success": true
}
```

### Validation Endpoints

#### GET /api/v1/departments/code/{code}/unique
Check if department code is unique.

**Parameters:**
- `excludeId` (integer, optional): Exclude specific department from check

```bash
curl "http://localhost:8080/api/v1/departments/code/NEW/unique"
curl "http://localhost:8080/api/v1/departments/code/HR/unique?excludeId=1"
```

#### GET /api/v1/departments/{id}/can-delete
Check if department can be deleted.

```bash
curl http://localhost:8080/api/v1/departments/1/can-delete
```

**Response:**
```json
{
  "canDelete": false
}
```

### Batch Operations

#### PATCH /api/v1/departments/batch/activate
Activate multiple departments.

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/batch/activate \
  -H "Content-Type: application/json" \
  -d '[1, 2, 3]'
```

#### PATCH /api/v1/departments/batch/deactivate
Deactivate multiple departments.

```bash
curl -X PATCH http://localhost:8080/api/v1/departments/batch/deactivate \
  -H "Content-Type: application/json" \
  -d '[4, 5]'
```

#### DELETE /api/v1/departments/cleanup/inactive-without-employees
Delete all inactive departments that have no employees.

```bash
curl -X DELETE http://localhost:8080/api/v1/departments/cleanup/inactive-without-employees
```

**Response:**
```json
{
  "deleted": 2
}
```

## 🔐 Error Responses

### Standard Error Codes

| Code | Description | Example |
|------|-------------|---------|
| 200  | Success | Request completed successfully |
| 201  | Created | Resource created successfully |
| 204  | No Content | Resource deleted successfully |
| 400  | Bad Request | Invalid input data |
| 404  | Not Found | Resource not found |
| 409  | Conflict | Resource constraint violation |
| 500  | Internal Server Error | Unexpected server error |

### Error Response Examples

#### Validation Error (400)
```json
{
  "error": "Bad Request",
  "message": "Employee email already exists: john.doe@company.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/employees"
}
```

#### Not Found Error (404)
```json
{
  "error": "Not Found",
  "message": "Employee not found with ID: 999",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/employees/999"
}
```

#### Conflict Error (409)
```json
{
  "error": "Conflict",
  "message": "Cannot delete department with active employees",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/v1/departments/1"
}
```

## 🧪 API Testing Examples

### Complete Workflow Example

```bash
#!/bin/bash
# Complete employee management workflow

echo "1. Create a department"
DEPT_ID=$(curl -s -X POST http://localhost:8080/api/v1/departments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering",
    "code": "ENG",
    "budget": 2500000.00,
    "description": "Software Engineering Department"
  }' | jq -r '.id')

echo "Department created with ID: $DEPT_ID"

echo "2. Create an employee"
EMP_ID=$(curl -s -X POST http://localhost:8080/api/v1/employees \
  -H "Content-Type: application/json" \
  -d "{
    \"firstName\": \"Alice\",
    \"lastName\": \"Engineer\",
    \"email\": \"alice.engineer@company.com\",
    \"hireDate\": \"2024-01-15\",
    \"departmentId\": $DEPT_ID
  }" | jq -r '.id')

echo "Employee created with ID: $EMP_ID"

echo "3. Get employee details"
curl -s http://localhost:8080/api/v1/employees/$EMP_ID | jq '.'

echo "4. Transfer employee to different department"
curl -s -X POST http://localhost:8080/api/v1/employees/$EMP_ID/transfer/1 | jq '.'

echo "5. Get department statistics"
curl -s http://localhost:8080/api/v1/departments/statistics | jq '.'

echo "6. Search employees"
curl -s "http://localhost:8080/api/v1/employees/search?term=Alice" | jq '.'

echo "Workflow completed successfully!"
```

### Performance Testing

```bash
#!/bin/bash
# Performance testing script

echo "Creating multiple employees for performance testing..."

for i in {1..100}; do
  curl -s -X POST http://localhost:8080/api/v1/employees \
    -H "Content-Type: application/json" \
    -d "{
      \"firstName\": \"Employee$i\",
      \"lastName\": \"Test\",
      \"email\": \"employee$i@perf.com\",
      \"hireDate\": \"2024-01-$((i % 28 + 1))\",
      \"departmentId\": $((i % 3 + 1))
    }" > /dev/null

  if [ $((i % 10)) -eq 0 ]; then
    echo "Created $i employees..."
  fi
done

echo "Performance test data created. Testing search performance..."

time curl -s "http://localhost:8080/api/v1/employees/search?term=Employee" > /dev/null
time curl -s "http://localhost:8080/api/v1/employees?activeOnly=true" > /dev/null
time curl -s "http://localhost:8080/api/v1/departments/with-employee-count" > /dev/null

echo "Performance tests completed!"
```

## 📊 Monitoring and Health Checks

### Health Endpoint
```bash
# Check application health
curl http://localhost:8080/actuator/health
```

**Response:**
```json
{
  "status": "UP",
  "components": {
    "db": {
      "status": "UP",
      "details": {
        "database": "PostgreSQL",
        "validationQuery": "isValid()"
      }
    }
  }
}
```

### Metrics Endpoint
```bash
# Get application metrics
curl http://localhost:8080/actuator/metrics
```

---

**Next Steps**: Use this API documentation alongside the [Testing Guide](TESTING_GUIDE.md) to create comprehensive test scenarios for your learning journey.