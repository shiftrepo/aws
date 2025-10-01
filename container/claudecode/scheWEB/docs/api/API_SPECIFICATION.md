# API Specification - Team Schedule Management System

## API Overview

RESTful API built with Express.js for team schedule management operations.

**Base URL:** `http://localhost:3001/api`
**Content-Type:** `application/json`
**Authentication:** JWT tokens in HTTP-only cookies

## Global Response Format

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2025-10-01T12:00:00.000Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional error context */ }
  },
  "timestamp": "2025-10-01T12:00:00.000Z"
}
```

### Pagination Format
```json
{
  "success": true,
  "data": [ /* array of items */ ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "totalPages": 3,
    "hasNext": true,
    "hasPrev": false
  }
}
```

## Authentication Endpoints

### POST /api/auth/register

Register a new user account (Admin only).

**Permissions:** Requires `users:write` permission

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890",
  "roleId": 3
}
```

**Validation Rules:**
- `email`: Valid email format, unique
- `password`: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special
- `firstName`, `lastName`: 2-50 characters
- `phone`: Optional, valid phone format
- `roleId`: 1 (Admin), 2 (Manager), 3 (Employee)

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "roleId": 3,
    "isActive": true,
    "createdAt": "2025-10-01T12:00:00.000Z"
  }
}
```

### POST /api/auth/login

Authenticate user and create session.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "john.doe@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": {
        "id": 3,
        "name": "Employee",
        "permissions": ["schedule:read", "shifts:swap", "profile:write"]
      }
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Side Effects:**
- Sets HTTP-only cookie: `authToken`
- Updates `last_login_at` timestamp
- Creates audit log entry

### POST /api/auth/logout

Terminate user session.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Side Effects:**
- Clears `authToken` cookie
- Invalidates JWT token (added to blacklist)

### GET /api/auth/me

Get current authenticated user information.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "avatarUrl": null,
    "preferences": {
      "theme": "light",
      "notifications": true
    },
    "role": {
      "id": 3,
      "name": "Employee",
      "permissions": ["schedule:read", "shifts:swap"]
    },
    "lastLoginAt": "2025-10-01T11:00:00.000Z"
  }
}
```

### POST /api/auth/refresh

Refresh JWT token.

**Authentication:** Required (valid or expired token)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

## User Management Endpoints

### GET /api/users

List all users with optional filtering.

**Authentication:** Required
**Permissions:** `users:read`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)
- `role`: Filter by role ID
- `isActive`: Filter by active status (true/false)
- `search`: Search by name or email
- `sortBy`: Sort field (firstName, lastName, email, createdAt)
- `sortOrder`: asc or desc (default: asc)

**Example:** `GET /api/users?page=1&limit=20&role=3&isActive=true&search=john`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "email": "john.doe@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "phone": "+1234567890",
      "avatarUrl": null,
      "role": {
        "id": 3,
        "name": "Employee"
      },
      "isActive": true,
      "lastLoginAt": "2025-10-01T11:00:00.000Z",
      "createdAt": "2025-09-01T10:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 25,
    "totalPages": 2
  }
}
```

### GET /api/users/:id

Get specific user details.

**Authentication:** Required
**Permissions:** `users:read` or own profile

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+1234567890",
    "avatarUrl": null,
    "preferences": {
      "theme": "light",
      "emailNotifications": true
    },
    "role": {
      "id": 3,
      "name": "Employee",
      "permissions": ["schedule:read", "shifts:swap"]
    },
    "isActive": true,
    "lastLoginAt": "2025-10-01T11:00:00.000Z",
    "createdAt": "2025-09-01T10:00:00.000Z",
    "stats": {
      "totalShifts": 45,
      "completedShifts": 42,
      "upcomingShifts": 3,
      "totalHoursThisMonth": 120
    }
  }
}
```

### PATCH /api/users/:id

Update user information.

**Authentication:** Required
**Permissions:** `users:write` or own profile (limited fields)

**Request Body (Admin/Manager):**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "new.email@example.com",
  "phone": "+1234567890",
  "roleId": 2,
  "isActive": true
}
```

**Request Body (Self - limited fields):**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "phone": "+1234567890",
  "preferences": {
    "theme": "dark",
    "emailNotifications": false
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "new.email@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "updatedAt": "2025-10-01T12:00:00.000Z"
  }
}
```

### DELETE /api/users/:id

Soft delete user (sets is_active = 0).

**Authentication:** Required
**Permissions:** `users:write`, cannot delete self

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

## Shift Management Endpoints

### GET /api/shifts

List shifts with filtering and pagination.

**Authentication:** Required
**Permissions:** `schedule:read`

**Query Parameters:**
- `startDate`: Filter shifts from date (YYYY-MM-DD)
- `endDate`: Filter shifts to date (YYYY-MM-DD)
- `userId`: Filter by user ID (multiple allowed: userId=1&userId=2)
- `status`: Filter by status (scheduled, completed, cancelled)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)
- `sortBy`: Sort field (shiftDate, startTime, createdAt)
- `sortOrder`: asc or desc (default: asc)

**Example:** `GET /api/shifts?startDate=2025-10-01&endDate=2025-10-07&userId=1`

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "shiftDate": "2025-10-01",
      "startTime": "09:00",
      "endTime": "17:00",
      "status": "scheduled",
      "notes": "Front desk coverage",
      "user": {
        "id": 1,
        "firstName": "John",
        "lastName": "Doe",
        "avatarUrl": null
      },
      "template": {
        "id": 2,
        "name": "Day Shift",
        "color": "#3B82F6"
      },
      "createdBy": {
        "id": 2,
        "firstName": "Jane",
        "lastName": "Manager"
      },
      "createdAt": "2025-09-25T10:00:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 15
  }
}
```

### POST /api/shifts

Create new shift assignment.

**Authentication:** Required
**Permissions:** `shifts:assign`

**Request Body:**
```json
{
  "userId": 1,
  "templateId": 2,
  "shiftDate": "2025-10-01",
  "startTime": "09:00",
  "endTime": "17:00",
  "notes": "Front desk coverage"
}
```

**Validation Rules:**
- `userId`: Must be active user
- `shiftDate`: Cannot be in the past
- `startTime`, `endTime`: Valid time format (HH:MM)
- No overlapping shifts for user
- User not on approved time-off
- Respects max hours per week setting

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 1,
    "templateId": 2,
    "shiftDate": "2025-10-01",
    "startTime": "09:00",
    "endTime": "17:00",
    "status": "scheduled",
    "notes": "Front desk coverage",
    "createdAt": "2025-09-25T10:00:00.000Z"
  }
}
```

**Side Effects:**
- Creates notification for assigned user
- Creates audit log entry

### PATCH /api/shifts/:id

Update existing shift.

**Authentication:** Required
**Permissions:** `shifts:assign`

**Request Body:**
```json
{
  "userId": 2,
  "shiftDate": "2025-10-02",
  "startTime": "10:00",
  "endTime": "18:00",
  "status": "scheduled",
  "notes": "Updated coverage notes"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 2,
    "shiftDate": "2025-10-02",
    "startTime": "10:00",
    "endTime": "18:00",
    "status": "scheduled",
    "updatedAt": "2025-09-25T14:00:00.000Z"
  }
}
```

**Side Effects:**
- Creates notification if user or time changed
- Creates audit log entry with old/new values

### DELETE /api/shifts/:id

Delete shift assignment.

**Authentication:** Required
**Permissions:** `shifts:assign`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Shift deleted successfully"
}
```

**Side Effects:**
- Creates notification for affected user
- Creates audit log entry

### POST /api/shifts/bulk

Create multiple shifts at once (batch operation).

**Authentication:** Required
**Permissions:** `shifts:assign`

**Request Body:**
```json
{
  "shifts": [
    {
      "userId": 1,
      "templateId": 2,
      "shiftDate": "2025-10-01",
      "startTime": "09:00",
      "endTime": "17:00"
    },
    {
      "userId": 2,
      "templateId": 3,
      "shiftDate": "2025-10-01",
      "startTime": "14:00",
      "endTime": "22:00"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "created": 2,
    "failed": 0,
    "errors": [],
    "shifts": [
      { "id": 1, "userId": 1, "shiftDate": "2025-10-01" },
      { "id": 2, "userId": 2, "shiftDate": "2025-10-01" }
    ]
  }
}
```

## Schedule Endpoints

### GET /api/schedule

Get schedule view for date range.

**Authentication:** Required
**Permissions:** `schedule:read`

**Query Parameters:**
- `startDate`: Start date (YYYY-MM-DD) - required
- `endDate`: End date (YYYY-MM-DD) - required
- `userIds`: Filter by user IDs (comma-separated)
- `view`: View type (week, month, custom) - default: week

**Example:** `GET /api/schedule?startDate=2025-10-01&endDate=2025-10-07&view=week`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "startDate": "2025-10-01",
    "endDate": "2025-10-07",
    "view": "week",
    "shifts": [
      {
        "id": 1,
        "date": "2025-10-01",
        "startTime": "09:00",
        "endTime": "17:00",
        "user": {
          "id": 1,
          "name": "John Doe",
          "avatarUrl": null
        },
        "template": {
          "name": "Day Shift",
          "color": "#3B82F6"
        },
        "status": "scheduled"
      }
    ],
    "stats": {
      "totalShifts": 35,
      "totalHours": 280,
      "employeesScheduled": 8,
      "openShifts": 0
    },
    "conflicts": []
  }
}
```

### POST /api/schedule/generate

Auto-generate schedule based on templates and availability.

**Authentication:** Required
**Permissions:** `schedule:write`

**Request Body:**
```json
{
  "startDate": "2025-10-01",
  "endDate": "2025-10-07",
  "userIds": [1, 2, 3, 4, 5],
  "templateIds": [1, 2, 3],
  "rules": {
    "maxHoursPerWeek": 40,
    "minHoursBetweenShifts": 8,
    "respectTimeOff": true,
    "balanceLoad": true
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "generatedShifts": 35,
    "assignments": [
      {
        "userId": 1,
        "shifts": 7,
        "totalHours": 56
      }
    ],
    "conflicts": [],
    "unassignedSlots": []
  }
}
```

### GET /api/schedule/conflicts

Check for scheduling conflicts.

**Authentication:** Required
**Permissions:** `schedule:read`

**Query Parameters:**
- `startDate`: Start date (YYYY-MM-DD)
- `endDate`: End date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "conflicts": [
      {
        "type": "overlap",
        "severity": "error",
        "userId": 1,
        "userName": "John Doe",
        "date": "2025-10-01",
        "shifts": [
          { "id": 1, "time": "09:00-17:00" },
          { "id": 2, "time": "14:00-22:00" }
        ],
        "message": "Overlapping shifts detected"
      },
      {
        "type": "excessive_hours",
        "severity": "warning",
        "userId": 2,
        "userName": "Jane Smith",
        "weekStart": "2025-10-01",
        "totalHours": 45,
        "maxHours": 40,
        "message": "Exceeds maximum weekly hours"
      }
    ]
  }
}
```

## Shift Swap Endpoints

### GET /api/shifts/swaps

List shift swap requests.

**Authentication:** Required
**Permissions:** `schedule:read` or own swaps

**Query Parameters:**
- `status`: Filter by status (pending, approved, rejected)
- `userId`: Filter by requester or target
- `page`: Page number
- `limit`: Items per page

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "shift": {
        "id": 5,
        "date": "2025-10-05",
        "startTime": "09:00",
        "endTime": "17:00"
      },
      "requester": {
        "id": 1,
        "name": "John Doe"
      },
      "target": {
        "id": 2,
        "name": "Jane Smith"
      },
      "status": "pending",
      "reason": "Family emergency",
      "createdAt": "2025-10-01T10:00:00.000Z"
    }
  ]
}
```

### POST /api/shifts/swaps

Request shift swap.

**Authentication:** Required
**Permissions:** `shifts:swap`

**Request Body:**
```json
{
  "shiftId": 5,
  "targetId": 2,
  "reason": "Family emergency"
}
```

**Validation Rules:**
- Must own the shift being swapped
- Target user must be active
- Target user cannot have conflicting shift
- Cannot swap past shifts

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "shiftId": 5,
    "requesterId": 1,
    "targetId": 2,
    "status": "pending",
    "reason": "Family emergency",
    "createdAt": "2025-10-01T10:00:00.000Z"
  }
}
```

**Side Effects:**
- Creates notification for target user
- Creates notification for manager (if approval required)

### PATCH /api/shifts/swaps/:id

Respond to swap request (approve/reject).

**Authentication:** Required
**Permissions:** Target user or `shifts:assign` (manager)

**Request Body:**
```json
{
  "status": "approved",
  "notes": "Approved by manager"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "approved",
    "approvedBy": 3,
    "resolvedAt": "2025-10-01T12:00:00.000Z"
  }
}
```

**Side Effects (if approved):**
- Updates shift assignment to target user
- Creates notifications for both users
- Creates audit log entry

## Time-Off Endpoints

### GET /api/timeoff

List time-off requests.

**Authentication:** Required
**Permissions:** `schedule:read` or own requests

**Query Parameters:**
- `userId`: Filter by user
- `status`: Filter by status
- `startDate`, `endDate`: Date range filter

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "name": "John Doe"
      },
      "startDate": "2025-10-10",
      "endDate": "2025-10-12",
      "type": "vacation",
      "status": "approved",
      "reason": "Family trip",
      "approvedBy": {
        "id": 2,
        "name": "Jane Manager"
      },
      "createdAt": "2025-09-20T10:00:00.000Z"
    }
  ]
}
```

### POST /api/timeoff

Request time off.

**Authentication:** Required
**Permissions:** `timeoff:request`

**Request Body:**
```json
{
  "startDate": "2025-10-10",
  "endDate": "2025-10-12",
  "type": "vacation",
  "reason": "Family trip"
}
```

**Validation Rules:**
- Start date cannot be in the past
- End date must be >= start date
- Maximum 30 consecutive days
- Cannot overlap with existing approved time-off

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 1,
    "startDate": "2025-10-10",
    "endDate": "2025-10-12",
    "type": "vacation",
    "status": "pending",
    "reason": "Family trip",
    "createdAt": "2025-09-20T10:00:00.000Z"
  }
}
```

**Side Effects:**
- Creates notification for managers
- Flags affected shifts

### PATCH /api/timeoff/:id

Approve/reject time-off request.

**Authentication:** Required
**Permissions:** `schedule:write`

**Request Body:**
```json
{
  "status": "approved",
  "approvalNotes": "Approved for vacation"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "approved",
    "approvedBy": 2,
    "approvalNotes": "Approved for vacation",
    "updatedAt": "2025-09-21T10:00:00.000Z"
  }
}
```

**Side Effects:**
- Creates notification for requester
- Auto-cancels conflicting shifts (if approved)

## Notification Endpoints

### GET /api/notifications

List user notifications.

**Authentication:** Required

**Query Parameters:**
- `isRead`: Filter by read status (true/false)
- `type`: Filter by notification type
- `page`: Page number
- `limit`: Items per page (default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "type": "shift_assigned",
      "title": "New Shift Assigned",
      "message": "You have been assigned a shift on 2025-10-01 from 09:00 to 17:00",
      "isRead": false,
      "priority": "normal",
      "relatedId": 5,
      "relatedType": "shift",
      "actionUrl": "/schedule",
      "createdAt": "2025-09-30T10:00:00.000Z"
    }
  ],
  "unreadCount": 3
}
```

### PATCH /api/notifications/:id/read

Mark notification as read.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "isRead": true,
    "readAt": "2025-10-01T12:00:00.000Z"
  }
}
```

### POST /api/notifications/read-all

Mark all notifications as read.

**Authentication:** Required

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "updated": 5
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_001 | 401 | Invalid credentials |
| AUTH_002 | 401 | Token expired |
| AUTH_003 | 403 | Insufficient permissions |
| AUTH_004 | 409 | Email already exists |
| SHIFT_001 | 409 | Overlapping shift detected |
| SHIFT_002 | 400 | Invalid time range |
| SHIFT_003 | 409 | User on approved time-off |
| SHIFT_004 | 400 | Exceeds maximum weekly hours |
| SWAP_001 | 400 | Cannot swap past shift |
| SWAP_002 | 409 | Target user has conflict |
| TIME_001 | 400 | Invalid date range |
| TIME_002 | 409 | Overlapping time-off request |
| VAL_001 | 400 | Validation error |
| SYS_001 | 500 | Internal server error |
| SYS_002 | 503 | Service unavailable |

## Rate Limiting

- **Authentication endpoints:** 5 requests/minute per IP
- **Write operations:** 30 requests/minute per user
- **Read operations:** 100 requests/minute per user
- **Bulk operations:** 10 requests/minute per user

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1696161600
```

## Webhook Events (Future)

Future support for webhooks to notify external systems:

- `shift.assigned` - New shift created
- `shift.updated` - Shift modified
- `shift.deleted` - Shift removed
- `swap.requested` - Swap request created
- `swap.approved` - Swap approved
- `timeoff.requested` - Time-off requested
- `timeoff.approved` - Time-off approved

## API Versioning

Current version: `v1`

Version can be specified via header:
```
API-Version: 1
```

Or URL prefix (future):
```
/api/v1/users
/api/v2/users
```
