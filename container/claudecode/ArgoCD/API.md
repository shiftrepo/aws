# API Documentation

Complete REST API reference for the Organization Management System.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Common Response Codes](#common-response-codes)
- [Error Handling](#error-handling)
- [Pagination](#pagination)
- [Organization Endpoints](#organization-endpoints)
- [Department Endpoints](#department-endpoints)
- [User Endpoints](#user-endpoints)
- [Health Check Endpoints](#health-check-endpoints)

## Overview

The Organization Management API is a RESTful API that allows you to manage organizations, departments, and users. All requests and responses use JSON format.

### API Version

Current Version: **v1**

### Content Type

All requests should use the following headers:

```
Content-Type: application/json
Accept: application/json
```

## Base URL

### Local Development
```
http://localhost:8080
```

### Production
```
https://api.example.com
```

## Authentication

Currently, the API does not require authentication. In production, implement one of the following:

### JWT Authentication (Recommended)

```http
Authorization: Bearer <jwt-token>
```

### API Key Authentication

```http
X-API-Key: <api-key>
```

### OAuth 2.0

```http
Authorization: Bearer <oauth-token>
```

## Common Response Codes

| Status Code | Description |
|-------------|-------------|
| **200 OK** | Request succeeded |
| **201 Created** | Resource created successfully |
| **204 No Content** | Request succeeded, no content to return |
| **400 Bad Request** | Invalid request parameters |
| **404 Not Found** | Resource not found |
| **409 Conflict** | Resource already exists |
| **422 Unprocessable Entity** | Validation error |
| **500 Internal Server Error** | Server error |

## Error Handling

### Error Response Format

```json
{
  "timestamp": "2024-02-05T10:30:00.000+00:00",
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed",
  "path": "/api/organizations",
  "errors": [
    {
      "field": "name",
      "message": "must not be blank"
    },
    {
      "field": "code",
      "message": "must match pattern [A-Z0-9]+"
    }
  ]
}
```

### Common Error Messages

| Message | Meaning |
|---------|---------|
| `Resource not found` | The requested resource doesn't exist |
| `Duplicate resource` | A resource with the same unique field already exists |
| `Validation failed` | One or more fields failed validation |
| `Database error` | Internal database error occurred |

## Pagination

List endpoints support pagination using query parameters.

### Pagination Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 0 | Page number (0-indexed) |
| `size` | integer | 20 | Number of items per page |
| `sort` | string | - | Sort field and direction (e.g., `name,asc`) |

### Example

```http
GET /api/organizations?page=0&size=10&sort=name,asc
```

### Paginated Response Format

```json
{
  "content": [...],
  "pageable": {
    "pageNumber": 0,
    "pageSize": 10,
    "sort": {
      "sorted": true,
      "unsorted": false,
      "empty": false
    }
  },
  "totalPages": 5,
  "totalElements": 50,
  "last": false,
  "first": true,
  "numberOfElements": 10,
  "size": 10,
  "number": 0,
  "sort": {
    "sorted": true,
    "unsorted": false,
    "empty": false
  },
  "empty": false
}
```

## Organization Endpoints

### Create Organization

Create a new organization.

**Endpoint:** `POST /api/organizations`

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "code": "ACME001",
  "description": "Leading technology company",
  "active": true
}
```

**Field Validation:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `name` | string | Yes | 1-100 characters |
| `code` | string | Yes | 1-20 characters, alphanumeric, unique |
| `description` | string | No | Max 500 characters |
| `active` | boolean | No | Default: true |

**Success Response (201 Created):**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "code": "ACME001",
  "description": "Leading technology company",
  "active": true,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T10:30:00.000+00:00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "timestamp": "2024-02-05T10:30:00.000+00:00",
  "status": 400,
  "error": "Bad Request",
  "message": "Validation failed",
  "errors": [
    {
      "field": "name",
      "message": "must not be blank"
    }
  ]
}
```

**Error Response (409 Conflict):**
```json
{
  "timestamp": "2024-02-05T10:30:00.000+00:00",
  "status": 409,
  "error": "Conflict",
  "message": "Organization with code 'ACME001' already exists"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8080/api/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "code": "ACME001",
    "description": "Leading technology company",
    "active": true
  }'
```

### Get All Organizations

Retrieve a paginated list of all organizations.

**Endpoint:** `GET /api/organizations`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number (default: 0) |
| `size` | integer | No | Page size (default: 20) |
| `sort` | string | No | Sort field and direction |

**Success Response (200 OK):**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "code": "ACME001",
      "description": "Leading technology company",
      "active": true,
      "createdAt": "2024-02-05T10:30:00.000+00:00",
      "updatedAt": "2024-02-05T10:30:00.000+00:00"
    },
    {
      "id": 2,
      "name": "Tech Innovations",
      "code": "TECH002",
      "description": "Innovation focused company",
      "active": true,
      "createdAt": "2024-02-05T11:00:00.000+00:00",
      "updatedAt": "2024-02-05T11:00:00.000+00:00"
    }
  ],
  "pageable": {
    "pageNumber": 0,
    "pageSize": 20
  },
  "totalPages": 1,
  "totalElements": 2,
  "last": true,
  "first": true
}
```

**cURL Example:**
```bash
curl http://localhost:8080/api/organizations?page=0&size=10&sort=name,asc
```

### Get Organization by ID

Retrieve a specific organization by its ID.

**Endpoint:** `GET /api/organizations/{id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Organization ID |

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "code": "ACME001",
  "description": "Leading technology company",
  "active": true,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T10:30:00.000+00:00"
}
```

**Error Response (404 Not Found):**
```json
{
  "timestamp": "2024-02-05T10:30:00.000+00:00",
  "status": 404,
  "error": "Not Found",
  "message": "Organization with id '999' not found"
}
```

**cURL Example:**
```bash
curl http://localhost:8080/api/organizations/1
```

### Get Organization by Code

Retrieve a specific organization by its unique code.

**Endpoint:** `GET /api/organizations/code/{code}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | string | Organization code |

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "code": "ACME001",
  "description": "Leading technology company",
  "active": true,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T10:30:00.000+00:00"
}
```

**cURL Example:**
```bash
curl http://localhost:8080/api/organizations/code/ACME001
```

### Get Active Organizations

Retrieve all active organizations.

**Endpoint:** `GET /api/organizations/active`

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Acme Corporation",
    "code": "ACME001",
    "description": "Leading technology company",
    "active": true,
    "createdAt": "2024-02-05T10:30:00.000+00:00",
    "updatedAt": "2024-02-05T10:30:00.000+00:00"
  }
]
```

**cURL Example:**
```bash
curl http://localhost:8080/api/organizations/active
```

### Search Organizations

Search organizations by name, code, or description.

**Endpoint:** `GET /api/organizations/search`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `page` | integer | No | Page number |
| `size` | integer | No | Page size |

**Success Response (200 OK):**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "code": "ACME001",
      "description": "Leading technology company",
      "active": true,
      "createdAt": "2024-02-05T10:30:00.000+00:00",
      "updatedAt": "2024-02-05T10:30:00.000+00:00"
    }
  ],
  "pageable": {...},
  "totalElements": 1
}
```

**cURL Example:**
```bash
curl "http://localhost:8080/api/organizations/search?q=Acme"
```

### Update Organization

Update an existing organization.

**Endpoint:** `PUT /api/organizations/{id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Organization ID |

**Request Body:**
```json
{
  "name": "Acme Corporation Updated",
  "code": "ACME001",
  "description": "Updated description",
  "active": true
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corporation Updated",
  "code": "ACME001",
  "description": "Updated description",
  "active": true,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T12:00:00.000+00:00"
}
```

**cURL Example:**
```bash
curl -X PUT http://localhost:8080/api/organizations/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation Updated",
    "code": "ACME001",
    "description": "Updated description",
    "active": true
  }'
```

### Deactivate Organization

Deactivate an organization (soft delete).

**Endpoint:** `PATCH /api/organizations/{id}/deactivate`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Organization ID |

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "code": "ACME001",
  "description": "Leading technology company",
  "active": false,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T13:00:00.000+00:00"
}
```

**cURL Example:**
```bash
curl -X PATCH http://localhost:8080/api/organizations/1/deactivate
```

### Delete Organization

Permanently delete an organization.

**Endpoint:** `DELETE /api/organizations/{id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Organization ID |

**Success Response (204 No Content)**

No response body.

**cURL Example:**
```bash
curl -X DELETE http://localhost:8080/api/organizations/1
```

## Department Endpoints

### Create Department

Create a new department within an organization.

**Endpoint:** `POST /api/departments`

**Request Body:**
```json
{
  "organizationId": 1,
  "name": "Engineering",
  "code": "ENG001",
  "description": "Engineering department",
  "active": true
}
```

**Field Validation:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `organizationId` | integer | Yes | Must exist |
| `name` | string | Yes | 1-100 characters |
| `code` | string | Yes | 1-20 characters, unique |
| `description` | string | No | Max 500 characters |
| `active` | boolean | No | Default: true |

**Success Response (201 Created):**
```json
{
  "id": 1,
  "organizationId": 1,
  "organizationName": "Acme Corporation",
  "name": "Engineering",
  "code": "ENG001",
  "description": "Engineering department",
  "active": true,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T10:30:00.000+00:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8080/api/departments \
  -H "Content-Type: application/json" \
  -d '{
    "organizationId": 1,
    "name": "Engineering",
    "code": "ENG001",
    "description": "Engineering department",
    "active": true
  }'
```

### Get All Departments

Retrieve a paginated list of all departments.

**Endpoint:** `GET /api/departments`

**Query Parameters:** Same as organizations

**Success Response (200 OK):**
```json
{
  "content": [
    {
      "id": 1,
      "organizationId": 1,
      "organizationName": "Acme Corporation",
      "name": "Engineering",
      "code": "ENG001",
      "description": "Engineering department",
      "active": true,
      "createdAt": "2024-02-05T10:30:00.000+00:00",
      "updatedAt": "2024-02-05T10:30:00.000+00:00"
    }
  ],
  "pageable": {...},
  "totalElements": 1
}
```

**cURL Example:**
```bash
curl http://localhost:8080/api/departments
```

### Get Department by ID

**Endpoint:** `GET /api/departments/{id}`

**cURL Example:**
```bash
curl http://localhost:8080/api/departments/1
```

### Get Departments by Organization

Retrieve all departments for a specific organization.

**Endpoint:** `GET /api/departments/organization/{organizationId}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `organizationId` | integer | Organization ID |

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "organizationId": 1,
    "organizationName": "Acme Corporation",
    "name": "Engineering",
    "code": "ENG001",
    "description": "Engineering department",
    "active": true,
    "createdAt": "2024-02-05T10:30:00.000+00:00",
    "updatedAt": "2024-02-05T10:30:00.000+00:00"
  }
]
```

**cURL Example:**
```bash
curl http://localhost:8080/api/departments/organization/1
```

### Update Department

**Endpoint:** `PUT /api/departments/{id}`

**cURL Example:**
```bash
curl -X PUT http://localhost:8080/api/departments/1 \
  -H "Content-Type: application/json" \
  -d '{
    "organizationId": 1,
    "name": "Engineering Updated",
    "code": "ENG001",
    "description": "Updated description",
    "active": true
  }'
```

### Delete Department

**Endpoint:** `DELETE /api/departments/{id}`

**Success Response:** 204 No Content

**cURL Example:**
```bash
curl -X DELETE http://localhost:8080/api/departments/1
```

## User Endpoints

### Create User

Create a new user within a department.

**Endpoint:** `POST /api/users`

**Request Body:**
```json
{
  "departmentId": 1,
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "active": true
}
```

**Field Validation:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `departmentId` | integer | Yes | Must exist |
| `firstName` | string | Yes | 1-50 characters |
| `lastName` | string | Yes | 1-50 characters |
| `email` | string | Yes | Valid email, unique |
| `phone` | string | No | Valid phone format |
| `active` | boolean | No | Default: true |

**Success Response (201 Created):**
```json
{
  "id": 1,
  "departmentId": 1,
  "departmentName": "Engineering",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "active": true,
  "createdAt": "2024-02-05T10:30:00.000+00:00",
  "updatedAt": "2024-02-05T10:30:00.000+00:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "departmentId": 1,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "active": true
  }'
```

### Get All Users

**Endpoint:** `GET /api/users`

**cURL Example:**
```bash
curl http://localhost:8080/api/users
```

### Get User by ID

**Endpoint:** `GET /api/users/{id}`

**cURL Example:**
```bash
curl http://localhost:8080/api/users/1
```

### Get Users by Department

**Endpoint:** `GET /api/users/department/{departmentId}`

**cURL Example:**
```bash
curl http://localhost:8080/api/users/department/1
```

### Update User

**Endpoint:** `PUT /api/users/{id}`

**cURL Example:**
```bash
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "departmentId": 1,
    "firstName": "John",
    "lastName": "Smith",
    "email": "john.smith@example.com",
    "phone": "+1-555-0123",
    "active": true
  }'
```

### Delete User

**Endpoint:** `DELETE /api/users/{id}`

**Success Response:** 204 No Content

**cURL Example:**
```bash
curl -X DELETE http://localhost:8080/api/users/1
```

## Health Check Endpoints

### Application Health

Check if the application is running and healthy.

**Endpoint:** `GET /actuator/health`

**Success Response (200 OK):**
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
    },
    "diskSpace": {
      "status": "UP",
      "details": {
        "total": 53687091200,
        "free": 23456789000,
        "threshold": 10485760
      }
    },
    "ping": {
      "status": "UP"
    }
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8080/actuator/health
```

### Application Info

**Endpoint:** `GET /actuator/info`

**Success Response (200 OK):**
```json
{
  "app": {
    "name": "Organization Management Backend",
    "version": "1.0.0-SNAPSHOT",
    "description": "Spring Boot backend for organization management system"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8080/actuator/info
```

## Rate Limiting

**Not currently implemented.** In production, consider implementing rate limiting:

- 100 requests per minute per IP
- 1000 requests per hour per IP
- Custom limits for authenticated users

## Best Practices

### Request Guidelines

1. **Always validate input** before sending requests
2. **Handle errors gracefully** on the client side
3. **Use pagination** for list endpoints
4. **Implement retry logic** for failed requests
5. **Cache responses** when appropriate

### Performance Tips

1. Use pagination for large datasets
2. Request only needed fields (when projection is available)
3. Implement client-side caching
4. Use ETags for conditional requests
5. Batch operations when possible

### Error Handling

1. Always check response status code
2. Parse error messages for user display
3. Log errors for debugging
4. Implement retry logic for 5xx errors
5. Handle validation errors appropriately

## Support

For API support:
- Documentation: See [README.md](README.md)
- Issues: GitHub Issues
- Email: support@example.com

---

API Version: 1.0.0 | Last Updated: 2024-02-05
