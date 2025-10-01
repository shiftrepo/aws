# API Specification - Team Meeting Scheduler

**Version:** 1.0
**Base URL:** `https://api.scheduler.example.com/api`
**Protocol:** HTTPS
**Format:** JSON

---

## Authentication

All endpoints except `/auth/login` and `/auth/register` require authentication.

**Authentication Method:** Bearer Token (JWT)

**Request Header:**
```
Authorization: Bearer <jwt_token>
```

**Token Expiry:** 24 hours (configurable)

---

## Standard Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | VALIDATION_ERROR | Invalid request parameters |
| 401 | UNAUTHORIZED | Missing or invalid token |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict (duplicate, etc.) |
| 500 | INTERNAL_ERROR | Server error |

---

## API Endpoints

### 1. Authentication

#### 1.1 Register User
```
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "role": "member"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-10-02T04:42:00Z"
  }
}
```

**Validation Rules:**
- Email: Valid email format, unique
- Password: Min 8 chars, 1 uppercase, 1 number, 1 special char
- Name: 2-100 characters

#### 1.2 Login
```
POST /auth/login
```

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
      "id": 1,
      "email": "user@example.com",
      "name": "John Doe",
      "role": "member"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-10-02T04:42:00Z"
  }
}
```

#### 1.3 Logout
```
POST /auth/logout
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### 1.4 Get Current User
```
GET /auth/me
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "member",
    "createdAt": "2025-09-01T10:00:00Z"
  }
}
```

---

### 2. User Management

#### 2.1 List Users
```
GET /users
Authorization: Bearer <token>
Permissions: admin
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search by name or email

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "role": "member",
        "createdAt": "2025-09-01T10:00:00Z"
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

#### 2.2 Get User Details
```
GET /users/:id
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "member",
    "createdAt": "2025-09-01T10:00:00Z",
    "updatedAt": "2025-09-15T14:30:00Z"
  }
}
```

#### 2.3 Update User Profile
```
PUT /users/:id
Authorization: Bearer <token>
Permissions: self or admin
```

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "newmail@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "newmail@example.com",
    "name": "John Smith",
    "role": "member",
    "updatedAt": "2025-10-01T04:42:00Z"
  }
}
```

#### 2.4 Delete User
```
DELETE /users/:id
Authorization: Bearer <token>
Permissions: admin
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

### 3. Availability Management

#### 3.1 Get User Availability
```
GET /availability/user/:userId
Authorization: Bearer <token>
```

**Query Parameters:**
- `includeExpired` (optional): Include past availability (default: false)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "availability": [
      {
        "id": 42,
        "dayOfWeek": 1,
        "startTime": "09:00",
        "endTime": "17:00",
        "isRecurring": true,
        "validFrom": null,
        "validUntil": null,
        "createdAt": "2025-09-01T10:00:00Z"
      }
    ]
  }
}
```

#### 3.2 Create Availability
```
POST /availability
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "dayOfWeek": 1,
  "startTime": "09:00",
  "endTime": "17:00",
  "isRecurring": true,
  "validFrom": null,
  "validUntil": null
}
```

**Validation Rules:**
- `dayOfWeek`: Integer 0-6 (0=Sunday, 6=Saturday)
- `startTime`: Format HH:MM, 24-hour
- `endTime`: Format HH:MM, must be after startTime
- `validFrom`/`validUntil`: ISO date format YYYY-MM-DD

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "userId": 1,
    "dayOfWeek": 1,
    "startTime": "09:00",
    "endTime": "17:00",
    "isRecurring": true,
    "createdAt": "2025-10-01T04:42:00Z"
  }
}
```

#### 3.3 Update Availability
```
PUT /availability/:id
Authorization: Bearer <token>
Permissions: owner or admin
```

**Request Body:**
```json
{
  "startTime": "10:00",
  "endTime": "16:00"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "userId": 1,
    "dayOfWeek": 1,
    "startTime": "10:00",
    "endTime": "16:00",
    "isRecurring": true,
    "updatedAt": "2025-10-01T04:42:00Z"
  }
}
```

#### 3.4 Delete Availability
```
DELETE /availability/:id
Authorization: Bearer <token>
Permissions: owner or admin
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Availability deleted successfully"
}
```

#### 3.5 Check Availability Conflicts
```
GET /availability/conflicts
Authorization: Bearer <token>
```

**Query Parameters:**
- `userId`: User ID to check
- `dayOfWeek`: Day of week (0-6)
- `startTime`: Start time (HH:MM)
- `endTime`: End time (HH:MM)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "hasConflicts": true,
    "conflicts": [
      {
        "id": 42,
        "dayOfWeek": 1,
        "startTime": "09:00",
        "endTime": "17:00"
      }
    ]
  }
}
```

---

### 4. Meeting Management

#### 4.1 List Meetings
```
GET /meetings
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)
- `startDate` (optional): Filter meetings after this date (YYYY-MM-DD)
- `endDate` (optional): Filter meetings before this date (YYYY-MM-DD)
- `status` (optional): Filter by participant status (pending/accepted/declined)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "meetings": [
      {
        "id": 1,
        "title": "Team Standup",
        "description": "Daily standup meeting",
        "startTime": "2025-10-05T10:00:00Z",
        "endTime": "2025-10-05T10:30:00Z",
        "location": "Conference Room A",
        "createdBy": {
          "id": 1,
          "name": "John Doe"
        },
        "participants": [
          {
            "id": 2,
            "name": "Jane Smith",
            "status": "accepted"
          }
        ],
        "createdAt": "2025-10-01T04:42:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 15,
      "totalPages": 1
    }
  }
}
```

#### 4.2 Get Meeting Details
```
GET /meetings/:id
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "startTime": "2025-10-05T10:00:00Z",
    "endTime": "2025-10-05T10:30:00Z",
    "location": "Conference Room A",
    "createdBy": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    "participants": [
      {
        "id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "status": "accepted",
        "responseAt": "2025-10-02T08:15:00Z"
      }
    ],
    "createdAt": "2025-10-01T04:42:00Z",
    "updatedAt": "2025-10-02T08:15:00Z"
  }
}
```

#### 4.3 Create Meeting
```
POST /meetings
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Team Standup",
  "description": "Daily standup meeting",
  "startTime": "2025-10-05T10:00:00Z",
  "endTime": "2025-10-05T10:30:00Z",
  "location": "Conference Room A",
  "participantIds": [2, 3, 4]
}
```

**Validation Rules:**
- `title`: 3-200 characters
- `startTime`: ISO 8601 datetime, future date
- `endTime`: ISO 8601 datetime, after startTime
- `participantIds`: Array of valid user IDs

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "startTime": "2025-10-05T10:00:00Z",
    "endTime": "2025-10-05T10:30:00Z",
    "location": "Conference Room A",
    "createdBy": {
      "id": 1,
      "name": "John Doe"
    },
    "participants": [
      {
        "id": 2,
        "name": "Jane Smith",
        "status": "pending"
      }
    ],
    "createdAt": "2025-10-01T04:42:00Z"
  }
}
```

#### 4.4 Update Meeting
```
PUT /meetings/:id
Authorization: Bearer <token>
Permissions: creator or admin
```

**Request Body:**
```json
{
  "title": "Updated Team Standup",
  "startTime": "2025-10-05T11:00:00Z",
  "endTime": "2025-10-05T11:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Updated Team Standup",
    "startTime": "2025-10-05T11:00:00Z",
    "endTime": "2025-10-05T11:30:00Z",
    "updatedAt": "2025-10-01T05:00:00Z"
  }
}
```

#### 4.5 Delete Meeting
```
DELETE /meetings/:id
Authorization: Bearer <token>
Permissions: creator or admin
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Meeting deleted successfully"
}
```

#### 4.6 Find Available Time Slots
```
GET /meetings/available
Authorization: Bearer <token>
```

**Query Parameters:**
- `participants`: Comma-separated user IDs (e.g., "1,2,3")
- `duration`: Duration in minutes (e.g., 30)
- `startDate`: Search start date (YYYY-MM-DD)
- `endDate`: Search end date (YYYY-MM-DD)
- `startHour` (optional): Earliest hour (0-23, default: 9)
- `endHour` (optional): Latest hour (0-23, default: 17)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "availableSlots": [
      {
        "startTime": "2025-10-05T10:00:00Z",
        "endTime": "2025-10-05T10:30:00Z",
        "participants": [1, 2, 3],
        "dayOfWeek": 1
      },
      {
        "startTime": "2025-10-05T14:00:00Z",
        "endTime": "2025-10-05T14:30:00Z",
        "participants": [1, 2, 3],
        "dayOfWeek": 1
      }
    ],
    "totalSlots": 2,
    "searchCriteria": {
      "participants": [1, 2, 3],
      "duration": 30,
      "dateRange": {
        "start": "2025-10-05",
        "end": "2025-10-12"
      }
    }
  }
}
```

#### 4.7 Add Meeting Participants
```
POST /meetings/:id/participants
Authorization: Bearer <token>
Permissions: creator or admin
```

**Request Body:**
```json
{
  "participantIds": [5, 6]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "meetingId": 1,
    "participants": [
      {
        "id": 5,
        "name": "Alice Johnson",
        "status": "pending"
      },
      {
        "id": 6,
        "name": "Bob Williams",
        "status": "pending"
      }
    ]
  }
}
```

#### 4.8 Update Participant Status
```
PUT /meetings/:id/participants/:userId
Authorization: Bearer <token>
Permissions: participant (self) or admin
```

**Request Body:**
```json
{
  "status": "accepted"
}
```

**Allowed statuses:** `pending`, `accepted`, `declined`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "meetingId": 1,
    "userId": 2,
    "status": "accepted",
    "responseAt": "2025-10-01T05:30:00Z"
  }
}
```

---

## Rate Limiting

**Limits:**
- Authentication endpoints: 5 requests per minute per IP
- General API endpoints: 100 requests per minute per user
- Available slots search: 20 requests per minute per user

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1633024800
```

**Rate Limit Exceeded (429):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retryAfter": 45
  }
}
```

---

## Webhooks (Future Enhancement)

**Webhook Events:**
- `meeting.created`
- `meeting.updated`
- `meeting.deleted`
- `meeting.participant_status_changed`

**Webhook Payload Example:**
```json
{
  "event": "meeting.created",
  "timestamp": "2025-10-01T04:42:00Z",
  "data": {
    "meeting": { ... }
  }
}
```

---

## API Versioning

**Current Version:** v1
**Version Header:** `Accept: application/vnd.scheduler.v1+json`
**URL Versioning:** Not used (header-based versioning preferred)

---

## CORS Configuration

**Allowed Origins:** Configurable via environment variable
**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS
**Allowed Headers:** Authorization, Content-Type
**Credentials:** Allowed (cookies, authorization headers)

---

## OpenAPI/Swagger Documentation

**Interactive Documentation:** Available at `/api/docs` (Swagger UI)
**OpenAPI Specification:** Available at `/api/openapi.json`

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-01 | Initial API specification |

---

**Next Review Date:** 2025-11-01
