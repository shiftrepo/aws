# API Endpoint Design and Specifications

## API Design Principles

1. **RESTful Conventions**: Use standard HTTP methods and status codes
2. **Versioning**: API version in URL path (/api/v1/)
3. **Consistent Naming**: Plural nouns for resources
4. **Filtering & Pagination**: Query parameters for list endpoints
5. **Error Responses**: Standardized error format
6. **Documentation**: OpenAPI/Swagger specification

## Base URL
```
http://localhost:3000/api/v1
```

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "firstName": "John",
  "lastName": "Doe",
  "timezone": "America/New_York"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "MEMBER",
      "timezone": "America/New_York"
    },
    "token": "jwt.token.here"
  }
}
```

### POST /auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "MEMBER"
    },
    "token": "jwt.token.here",
    "expiresIn": 86400
  }
}
```

### POST /auth/refresh
Refresh JWT token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token": "new.jwt.token.here",
    "expiresIn": 86400
  }
}
```

### POST /auth/logout
Logout user (blacklist token if using Redis).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

## User Endpoints

### GET /users/me
Get current user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "MEMBER",
    "timezone": "America/New_York",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

### PATCH /users/me
Update current user profile.

**Request Body:**
```json
{
  "firstName": "Jane",
  "timezone": "America/Los_Angeles"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "timezone": "America/Los_Angeles"
  }
}
```

### GET /users
Get list of users (Admin/Manager only).

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)
- `search` (search by name/email)
- `role` (filter by role)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "uuid",
        "email": "user@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "role": "MEMBER"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "totalPages": 3
    }
  }
}
```

## Team Endpoints

### POST /teams
Create a new team.

**Request Body:**
```json
{
  "name": "Engineering Team",
  "description": "Software development team"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Engineering Team",
    "description": "Software development team",
    "createdBy": "user-uuid",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

### GET /teams
Get list of teams user is member of.

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "teams": [
      {
        "id": "uuid",
        "name": "Engineering Team",
        "description": "Software development team",
        "memberCount": 5,
        "role": "MEMBER"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 3,
      "totalPages": 1
    }
  }
}
```

### GET /teams/:teamId
Get team details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Engineering Team",
    "description": "Software development team",
    "createdBy": "user-uuid",
    "members": [
      {
        "id": "member-uuid",
        "userId": "user-uuid",
        "role": "OWNER",
        "user": {
          "firstName": "John",
          "lastName": "Doe",
          "email": "john@example.com"
        }
      }
    ]
  }
}
```

### POST /teams/:teamId/members
Add member to team (Owner/Admin only).

**Request Body:**
```json
{
  "userId": "user-uuid",
  "role": "MEMBER"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "member-uuid",
    "teamId": "team-uuid",
    "userId": "user-uuid",
    "role": "MEMBER"
  }
}
```

### DELETE /teams/:teamId/members/:memberId
Remove member from team (Owner/Admin only).

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Member removed successfully"
}
```

## Schedule Endpoints

### POST /schedules
Create a new schedule/event.

**Request Body:**
```json
{
  "title": "Team Standup",
  "description": "Daily standup meeting",
  "startTime": "2024-01-15T09:00:00Z",
  "endTime": "2024-01-15T09:30:00Z",
  "location": "Conference Room A",
  "teamId": "team-uuid",
  "type": "MEETING",
  "participants": [
    {
      "userId": "user-uuid-1",
      "isRequired": true
    },
    {
      "userId": "user-uuid-2",
      "isRequired": false
    }
  ],
  "isRecurring": true,
  "recurrenceRule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "schedule-uuid",
    "title": "Team Standup",
    "startTime": "2024-01-15T09:00:00Z",
    "endTime": "2024-01-15T09:30:00Z",
    "type": "MEETING",
    "status": "SCHEDULED",
    "participants": [
      {
        "userId": "user-uuid-1",
        "status": "PENDING",
        "isRequired": true
      }
    ]
  }
}
```

### GET /schedules
Get list of schedules with filtering.

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)
- `startDate` (ISO date)
- `endDate` (ISO date)
- `teamId` (filter by team)
- `type` (filter by type)
- `status` (filter by status)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "schedules": [
      {
        "id": "uuid",
        "title": "Team Standup",
        "startTime": "2024-01-15T09:00:00Z",
        "endTime": "2024-01-15T09:30:00Z",
        "type": "MEETING",
        "status": "SCHEDULED",
        "participantCount": 5
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "totalPages": 3
    }
  }
}
```

### GET /schedules/:scheduleId
Get schedule details.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "startTime": "2024-01-15T09:00:00Z",
    "endTime": "2024-01-15T09:30:00Z",
    "location": "Conference Room A",
    "type": "MEETING",
    "status": "SCHEDULED",
    "participants": [
      {
        "id": "participant-uuid",
        "userId": "user-uuid",
        "status": "ACCEPTED",
        "isRequired": true,
        "user": {
          "firstName": "John",
          "lastName": "Doe",
          "email": "john@example.com"
        }
      }
    ],
    "createdBy": "user-uuid",
    "teamId": "team-uuid"
  }
}
```

### PATCH /schedules/:scheduleId
Update schedule details.

**Request Body:**
```json
{
  "title": "Updated Meeting",
  "startTime": "2024-01-15T10:00:00Z",
  "endTime": "2024-01-15T10:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Updated Meeting",
    "startTime": "2024-01-15T10:00:00Z",
    "endTime": "2024-01-15T10:30:00Z"
  }
}
```

### DELETE /schedules/:scheduleId
Delete/cancel schedule.

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Schedule cancelled successfully"
}
```

### POST /schedules/:scheduleId/respond
Respond to schedule invitation.

**Request Body:**
```json
{
  "status": "ACCEPTED"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "participantId": "uuid",
    "status": "ACCEPTED"
  }
}
```

## Availability Endpoints

### POST /availabilities
Set user availability.

**Request Body:**
```json
{
  "dayOfWeek": 1,
  "startTime": "09:00",
  "endTime": "17:00",
  "isAvailable": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "dayOfWeek": 1,
    "startTime": "09:00",
    "endTime": "17:00",
    "isAvailable": true
  }
}
```

### GET /availabilities/me
Get current user's availability.

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "dayOfWeek": 1,
      "startTime": "09:00",
      "endTime": "17:00",
      "isAvailable": true
    }
  ]
}
```

### POST /availabilities/find-slots
Find common available time slots for multiple users.

**Request Body:**
```json
{
  "userIds": ["user-uuid-1", "user-uuid-2"],
  "startDate": "2024-01-15",
  "endDate": "2024-01-19",
  "duration": 60,
  "timezone": "America/New_York"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "slots": [
      {
        "startTime": "2024-01-15T14:00:00Z",
        "endTime": "2024-01-15T15:00:00Z",
        "availableUsers": ["user-uuid-1", "user-uuid-2"]
      }
    ]
  }
}
```

## Conflict Detection Endpoint

### POST /schedules/check-conflicts
Check for scheduling conflicts.

**Request Body:**
```json
{
  "userIds": ["user-uuid-1", "user-uuid-2"],
  "startTime": "2024-01-15T09:00:00Z",
  "endTime": "2024-01-15T10:00:00Z",
  "excludeScheduleId": "optional-schedule-uuid"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "hasConflicts": true,
    "conflicts": [
      {
        "userId": "user-uuid-1",
        "schedule": {
          "id": "conflict-schedule-uuid",
          "title": "Another Meeting",
          "startTime": "2024-01-15T09:30:00Z",
          "endTime": "2024-01-15T10:30:00Z"
        }
      }
    ]
  }
}
```

## Standard Error Response

**Format:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "Additional error details"
    }
  }
}
```

## HTTP Status Codes

- `200 OK`: Successful GET, PATCH, DELETE
- `201 Created`: Successful POST
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (duplicate)
- `422 Unprocessable Entity`: Business logic error
- `500 Internal Server Error`: Server error
