# Team Meeting Scheduler - System Architecture

**Version:** 1.0
**Date:** 2025-10-01
**Architect:** System Architecture Designer
**Status:** Initial Design

---

## 1. Executive Summary

This document defines the system architecture for a web-based team meeting scheduler. The architecture emphasizes:
- **Simplicity**: Easy to understand, deploy, and maintain
- **Containerization**: Docker-based deployment for consistency
- **Minimal dependencies**: SQLite database, single-language backend
- **Security**: Basic authentication with token-based sessions
- **Scalability**: Designed for small to medium teams (5-50 users)

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                          │
├─────────────────────────────────────────────────────────────┤
│  Web Browser (Chrome, Firefox, Safari, Edge)                │
│  - HTML5 + CSS3 + Vanilla JavaScript                        │
│  - Responsive UI with calendar visualization                │
│  - Local state management                                   │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS/HTTP
                 │ REST API (JSON)
┌────────────────▼────────────────────────────────────────────┐
│                      APPLICATION TIER                        │
├─────────────────────────────────────────────────────────────┤
│  Web Application (Python Flask/FastAPI or Go Gin or Node.js)│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ API Layer                                                ││
│  │  - Authentication middleware                             ││
│  │  - Request validation                                    ││
│  │  - Response formatting                                   ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Business Logic Layer                                     ││
│  │  - Availability management                               ││
│  │  - Meeting slot calculation                              ││
│  │  - Conflict detection                                    ││
│  │  - Notification generation                               ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Data Access Layer                                        ││
│  │  - SQLite ORM/Query builder                              ││
│  │  - Transaction management                                ││
│  │  - Data validation                                       ││
│  └─────────────────────────────────────────────────────────┘│
└────────────────┬────────────────────────────────────────────┘
                 │ File-based connection
┌────────────────▼────────────────────────────────────────────┐
│                        DATA TIER                             │
├─────────────────────────────────────────────────────────────┤
│  SQLite Database (scheduler.db)                              │
│  - Users table                                               │
│  - Availability table                                        │
│  - Meetings table                                            │
│  - Session tokens table                                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

```
User Login Flow:
Browser → POST /api/auth/login → Auth Handler → User DB Lookup
  → Token Generation → Session Store → Return Token → Browser Stores Token

Availability Update Flow:
Browser → PUT /api/availability/{id} (+ Token) → Auth Middleware
  → Validate Token → Availability Handler → Conflict Check
  → Update DB → Notify Affected Users → Return Success

Meeting Slot Discovery Flow:
Browser → GET /api/meetings/available?participants=1,2,3&duration=30
  → Auth Middleware → Meeting Calculator → Query All Availability
  → Find Overlapping Slots → Apply Constraints → Return Slots
```

---

## 3. Technology Stack Selection

### 3.1 Recommended Technology Stack (Option A: Python)

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Backend Language** | Python 3.11+ | Simple syntax, extensive libraries, fast development |
| **Web Framework** | Flask 3.0 or FastAPI | Lightweight, well-documented, minimal boilerplate |
| **Database** | SQLite 3.40+ | Zero configuration, file-based, sufficient for requirements |
| **ORM/Query Builder** | SQLAlchemy 2.0 | Mature, flexible, supports migrations |
| **Authentication** | PyJWT + bcrypt | Industry standard JWT tokens, secure password hashing |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | No build step, universal browser support, simple deployment |
| **Containerization** | Docker 24+ | Standard containerization platform |
| **Orchestration** | Docker Compose | Simple multi-container management |
| **HTTP Server** | Gunicorn or Uvicorn | Production-grade WSGI/ASGI server |
| **Reverse Proxy** | Nginx (optional) | SSL termination, static file serving |

### 3.2 Alternative Stack Options

**Option B: Go**
- Language: Go 1.21+
- Framework: Gin or Echo
- Database: database/sql + mattn/go-sqlite3
- Pros: Single binary, excellent performance, strong typing
- Cons: More verbose, smaller ecosystem

**Option C: Node.js**
- Language: Node.js 20 LTS + TypeScript
- Framework: Express or Fastify
- Database: better-sqlite3 or Sequelize
- Pros: JavaScript full-stack, large ecosystem
- Cons: Callback complexity, runtime overhead

**Recommendation**: **Python (Option A)** for optimal balance of simplicity, development speed, and maintainability.

---

## 4. Database Design

### 4.1 Entity-Relationship Diagram

```
┌──────────────┐         ┌────────────────────┐         ┌──────────────┐
│    users     │         │   availability     │         │   meetings   │
├──────────────┤         ├────────────────────┤         ├──────────────┤
│ id (PK)      │────┐    │ id (PK)            │    ┌────│ id (PK)      │
│ email        │    │    │ user_id (FK)       │    │    │ title        │
│ password_hash│    └───▶│ day_of_week        │    │    │ description  │
│ name         │         │ start_time         │    │    │ start_time   │
│ role         │         │ end_time           │    │    │ end_time     │
│ created_at   │         │ is_recurring       │    │    │ location     │
│ updated_at   │         │ valid_from         │    │    │ created_by   │
└──────────────┘         │ valid_until        │    │    │ created_at   │
                         │ created_at         │    │    └──────────────┘
┌──────────────┐         │ updated_at         │    │           │
│   sessions   │         └────────────────────┘    │           │
├──────────────┤                                   │           │
│ id (PK)      │         ┌────────────────────┐    │    ┌──────▼──────────┐
│ user_id (FK) │◀────────│   users            │    │    │meeting_participants│
│ token        │         └────────────────────┘    │    ├─────────────────┤
│ expires_at   │                                   │    │ meeting_id (FK)  │
│ created_at   │                                   └────│ user_id (FK)     │
└──────────────┘                                        │ status           │
                                                        │ response_at      │
                                                        └──────────────────┘
```

### 4.2 Database Schema (SQLite DDL)

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'member' CHECK(role IN ('admin', 'member')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Availability table
CREATE TABLE availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6), -- 0=Sunday, 6=Saturday
    start_time TEXT NOT NULL, -- Format: HH:MM (e.g., "09:00")
    end_time TEXT NOT NULL,   -- Format: HH:MM (e.g., "17:00")
    is_recurring BOOLEAN DEFAULT 1,
    valid_from DATE,          -- Optional: specific date range
    valid_until DATE,         -- Optional: specific date range
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_availability_user ON availability(user_id);
CREATE INDEX idx_availability_day ON availability(day_of_week);

-- Meetings table
CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    location TEXT,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_meetings_start ON meetings(start_time);
CREATE INDEX idx_meetings_creator ON meetings(created_by);

-- Meeting participants (many-to-many relationship)
CREATE TABLE meeting_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'declined')),
    response_at DATETIME,
    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(meeting_id, user_id)
);

CREATE INDEX idx_participants_meeting ON meeting_participants(meeting_id);
CREATE INDEX idx_participants_user ON meeting_participants(user_id);

-- Sessions table (for authentication tokens)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Triggers for updated_at timestamps
CREATE TRIGGER update_users_timestamp
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_availability_timestamp
AFTER UPDATE ON availability
BEGIN
    UPDATE availability SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_meetings_timestamp
AFTER UPDATE ON meetings
BEGIN
    UPDATE meetings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 4.3 Database Design Rationale

**Key Decisions:**

1. **Availability Model**: Day-of-week pattern with optional date ranges for recurring schedules
2. **Time Storage**: TEXT format (HH:MM) for daily patterns, DATETIME for actual meetings
3. **Normalization**: Normalized to 3NF to reduce redundancy
4. **Cascading Deletes**: ON DELETE CASCADE ensures referential integrity
5. **Indexes**: Strategic indexes on foreign keys and query-heavy columns
6. **Session Management**: Explicit session table for token-based auth (alternative to JWT-only)

---

## 5. API Design

### 5.1 REST API Endpoints

#### Authentication Endpoints

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
POST   /api/auth/refresh
```

#### User Management Endpoints

```
GET    /api/users              - List all users (admin only)
GET    /api/users/:id          - Get user details
PUT    /api/users/:id          - Update user profile
DELETE /api/users/:id          - Delete user (admin only)
```

#### Availability Endpoints

```
GET    /api/availability                    - Get all availability (admin/filter by user)
GET    /api/availability/user/:userId       - Get user's availability
POST   /api/availability                    - Create availability slot
PUT    /api/availability/:id                - Update availability slot
DELETE /api/availability/:id                - Delete availability slot
GET    /api/availability/conflicts          - Check for conflicts
```

#### Meeting Endpoints

```
GET    /api/meetings                        - List all meetings
GET    /api/meetings/:id                    - Get meeting details
POST   /api/meetings                        - Create meeting
PUT    /api/meetings/:id                    - Update meeting
DELETE /api/meetings/:id                    - Delete meeting
GET    /api/meetings/available              - Find available time slots
POST   /api/meetings/:id/participants       - Add participants
PUT    /api/meetings/:id/participants/:userId - Update participant status
```

### 5.2 API Request/Response Examples

#### POST /api/auth/login

**Request:**
```json
{
  "email": "alice@example.com",
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
      "email": "alice@example.com",
      "name": "Alice Smith",
      "role": "member"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2025-10-02T04:42:00Z"
  }
}
```

#### POST /api/availability

**Request:**
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

#### GET /api/meetings/available

**Request:**
```
GET /api/meetings/available?participants=1,2,3&duration=30&startDate=2025-10-05&endDate=2025-10-12
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "availableSlots": [
      {
        "startTime": "2025-10-05T10:00:00Z",
        "endTime": "2025-10-05T10:30:00Z",
        "participants": [1, 2, 3]
      },
      {
        "startTime": "2025-10-05T14:00:00Z",
        "endTime": "2025-10-05T14:30:00Z",
        "participants": [1, 2, 3]
      }
    ],
    "totalSlots": 2
  }
}
```

### 5.3 API Design Principles

- **RESTful conventions**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **JSON format**: All requests/responses use JSON
- **Consistent structure**: All responses follow `{success, data, error}` pattern
- **Proper status codes**: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)
- **Authentication**: Bearer token in Authorization header
- **Validation**: Input validation on all endpoints
- **Error handling**: Descriptive error messages with error codes

---

## 6. Authentication & Security

### 6.1 Authentication Strategy

**Token-Based Authentication (JWT)**

1. **User Registration**: Password hashed with bcrypt (cost factor 12)
2. **Login**: Validate credentials → Generate JWT → Store session (optional)
3. **Token Structure**:
   ```json
   {
     "sub": "user_id",
     "email": "user@example.com",
     "role": "member",
     "iat": 1633024800,
     "exp": 1633111200
   }
   ```
4. **Token Expiry**: 24 hours (configurable)
5. **Token Refresh**: Optional refresh token endpoint

### 6.2 Security Measures

| Threat | Mitigation |
|--------|------------|
| **SQL Injection** | Parameterized queries via ORM |
| **XSS** | Input sanitization, Content-Security-Policy headers |
| **CSRF** | SameSite cookies, CSRF tokens for state-changing operations |
| **Password Attacks** | Bcrypt hashing, rate limiting on login endpoint |
| **Token Theft** | HTTPS only, secure token storage, short expiry |
| **Unauthorized Access** | Role-based access control (RBAC), middleware authentication |
| **Data Exposure** | Minimal data in tokens, no sensitive data in logs |

### 6.3 RBAC (Role-Based Access Control)

**Roles:**
- **Admin**: Full access (user management, all meetings, all availability)
- **Member**: Own data only (own availability, participated meetings)

**Access Matrix:**

| Resource | Admin | Member |
|----------|-------|--------|
| View all users | ✓ | ✗ |
| Create user | ✓ | ✗ |
| Delete user | ✓ | ✗ |
| View own availability | ✓ | ✓ |
| Update own availability | ✓ | ✓ |
| View others' availability | ✓ | ✓ (limited to finding slots) |
| Create meeting | ✓ | ✓ |
| Delete any meeting | ✓ | ✗ (own meetings only) |

---

## 7. Containerization Strategy

### 7.1 Docker Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Docker Compose Stack                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────────┐         ┌──────────────────┐    │
│  │  nginx (optional)  │         │  app container   │    │
│  │  ┌──────────────┐  │         │  ┌────────────┐  │    │
│  │  │ Reverse Proxy│◀─┼─────────┼─▶│ Python App │  │    │
│  │  │ SSL Termination│  │       │  │ Gunicorn   │  │    │
│  │  └──────────────┘  │         │  └────────────┘  │    │
│  │  Port: 80, 443     │         │  Port: 8000      │    │
│  └────────────────────┘         └────────┬─────────┘    │
│                                           │              │
│                                           ▼              │
│                                  ┌────────────────┐      │
│                                  │ Volume Mount   │      │
│                                  │ /app/data      │      │
│                                  │ (SQLite DB)    │      │
│                                  └────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Dockerfile (Python Application)

```dockerfile
# Multi-stage build for minimal image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY config/ ./config/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/app/data/scheduler.db \
    JWT_SECRET_KEY=change-me-in-production

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "src.app:app"]
```

### 7.3 Docker Compose Configuration

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: scheduler-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_PATH=/app/data/scheduler.db
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_EXPIRY_HOURS=${JWT_EXPIRY_HOURS:-24}
      - BCRYPT_ROUNDS=${BCRYPT_ROUNDS:-12}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./data:/app/data  # Persistent SQLite database
      - ./logs:/app/logs  # Application logs
    networks:
      - scheduler-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: scheduler-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro  # SSL certificates
      - ./static:/usr/share/nginx/html:ro  # Static frontend files
    depends_on:
      - app
    networks:
      - scheduler-net

networks:
  scheduler-net:
    driver: bridge

volumes:
  data:
    driver: local
  logs:
    driver: local
```

### 7.4 Container Orchestration Benefits

1. **Isolation**: Each service in separate container
2. **Portability**: Run anywhere Docker is available
3. **Reproducibility**: Same environment dev/staging/prod
4. **Easy deployment**: Single `docker-compose up -d` command
5. **Health monitoring**: Built-in health checks
6. **Logging**: Centralized log management
7. **Scalability**: Easy horizontal scaling with Docker Swarm/K8s

---

## 8. Frontend-Backend Interaction

### 8.1 Communication Pattern

**Single Page Application (SPA) with REST API**

```
┌──────────────────────────────────────────────────────────┐
│                     Browser (Client)                      │
├──────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐    │
│  │   HTML     │  │    CSS     │  │   JavaScript    │    │
│  │            │  │            │  │  ┌───────────┐  │    │
│  │ - Login    │  │ - Styles   │  │  │API Client │  │    │
│  │ - Calendar │  │ - Responsive│  │  └─────┬─────┘  │    │
│  │ - Forms    │  │ - Themes   │  │        │        │    │
│  └────────────┘  └────────────┘  └────────┼────────┘    │
└──────────────────────────────────────────┼──────────────┘
                                            │
                                    fetch() / XMLHttpRequest
                                            │
┌───────────────────────────────────────────▼──────────────┐
│                   Backend API (Server)                    │
├──────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────┐  │
│  │              Flask/FastAPI Routes                  │  │
│  │  - JSON request/response                           │  │
│  │  - CORS enabled                                    │  │
│  │  - Authentication middleware                       │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 8.2 State Management

**Client-Side State:**
- LocalStorage: JWT token, user preferences
- Session state: Current user data, calendar view state
- Form state: Temporary form data

**Server-Side State:**
- Database: Persistent data (users, availability, meetings)
- Session table: Active sessions (optional)
- Cache: Frequently accessed data (if needed)

### 8.3 Frontend Technology Choices

**Minimal Vanilla JavaScript Approach:**
- No build tools required (Webpack, Babel, etc.)
- ES6 modules for code organization
- Fetch API for HTTP requests
- Template literals for HTML generation
- CSS Grid/Flexbox for layouts

**Calendar Visualization Options:**
- FullCalendar.js (feature-rich, MIT license)
- Custom HTML table-based calendar (lightweight)

---

## 9. Deployment Architecture

### 9.1 Production Deployment Topology

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS (443)
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Load Balancer (optional)                  │
│                    or DNS A/CNAME Record                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                 Docker Host (VM/VPS/Cloud)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Docker Compose Environment                   │  │
│  │                                                       │  │
│  │  ┌──────────────┐       ┌────────────────────────┐  │  │
│  │  │ Nginx        │       │ Application            │  │  │
│  │  │ - SSL Cert   │───────│ - Gunicorn/Uvicorn     │  │  │
│  │  │ - Static     │       │ - Python App           │  │  │
│  │  │   Files      │       │ - SQLite (/app/data)   │  │  │
│  │  └──────────────┘       └────────────────────────┘  │  │
│  │        │                           │                 │  │
│  │        │                           │                 │  │
│  │  ┌─────▼────────────────────────────▼────────────┐  │  │
│  │  │         Docker Volumes                        │  │  │
│  │  │  - /data (SQLite database - persistent)      │  │  │
│  │  │  - /logs (Application logs)                  │  │  │
│  │  │  - /ssl (SSL certificates)                   │  │  │
│  │  └──────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Host System Resources                       │  │
│  │  - Backup cron jobs (SQLite → S3/local)              │  │
│  │  - Log rotation (logrotate)                          │  │
│  │  - Monitoring (optional: Prometheus/Grafana)         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 Deployment Steps

```bash
# 1. Clone repository on server
git clone https://github.com/yourorg/meeting-scheduler.git
cd meeting-scheduler

# 2. Create environment file
cat > .env << EOF
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_EXPIRY_HOURS=24
BCRYPT_ROUNDS=12
LOG_LEVEL=INFO
EOF

# 3. Create directories
mkdir -p data logs nginx/ssl

# 4. Generate SSL certificate (Let's Encrypt)
certbot certonly --standalone -d your-domain.com

# 5. Build and start containers
docker-compose up -d --build

# 6. Initialize database (run migrations)
docker-compose exec app python -m src.migrations.init_db

# 7. Create admin user
docker-compose exec app python -m src.scripts.create_admin \
  --email admin@example.com \
  --password SecureAdminPass123! \
  --name "Admin User"

# 8. Check health
curl http://localhost:8000/health

# 9. View logs
docker-compose logs -f
```

### 9.3 Backup Strategy

**SQLite Database Backup:**
```bash
# Daily backup script (crontab)
#!/bin/bash
BACKUP_DIR="/backup/scheduler"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# SQLite backup (hot backup)
docker-compose exec -T app sqlite3 /app/data/scheduler.db ".backup /app/data/backup_$TIMESTAMP.db"
docker cp scheduler-app:/app/data/backup_$TIMESTAMP.db $BACKUP_DIR/

# Keep last 30 days
find $BACKUP_DIR -name "backup_*.db" -mtime +30 -delete

# Optional: Upload to S3/cloud storage
aws s3 cp $BACKUP_DIR/backup_$TIMESTAMP.db s3://your-bucket/backups/
```

### 9.4 Monitoring & Observability

**Essential Metrics:**
- Application health: `/health` endpoint
- Container status: `docker-compose ps`
- Database size: `ls -lh data/scheduler.db`
- Error logs: `docker-compose logs app | grep ERROR`
- Response times: Application logging

**Optional Advanced Monitoring:**
- Prometheus + Grafana for metrics
- ELK stack for log aggregation
- Uptime monitoring (UptimeRobot, Pingdom)

---

## 10. Architecture Decision Records (ADRs)

### ADR-001: Use SQLite Instead of PostgreSQL/MySQL

**Status:** Accepted
**Context:** Need simple, file-based database for small team scheduler
**Decision:** Use SQLite 3.40+
**Consequences:**
- ✓ Zero configuration, no separate database server
- ✓ Embedded in application container
- ✓ Sufficient for 5-50 users with low-medium load
- ✗ Limited concurrent writes (not issue for scheduler use case)
- ✗ Migration path to PostgreSQL if scaling needed

### ADR-002: Token-Based Authentication (JWT)

**Status:** Accepted
**Context:** Need secure, stateless authentication
**Decision:** Use JWT with bcrypt password hashing
**Consequences:**
- ✓ Stateless authentication (no session storage required)
- ✓ Easy to scale horizontally
- ✓ Standard industry approach
- ✗ Tokens cannot be revoked before expiry (mitigated with short expiry)
- ✗ Token size larger than session ID

### ADR-003: Vanilla JavaScript Frontend (No Framework)

**Status:** Accepted
**Context:** Need simple, fast-loading frontend
**Decision:** Use vanilla ES6 JavaScript, no React/Vue/Angular
**Consequences:**
- ✓ No build pipeline required
- ✓ Smaller bundle size, faster page loads
- ✓ Easier to understand and maintain
- ✗ More manual DOM manipulation
- ✗ No component reusability frameworks

### ADR-004: Python Flask/FastAPI for Backend

**Status:** Accepted
**Context:** Need simple, maintainable backend language
**Decision:** Python 3.11+ with Flask or FastAPI
**Consequences:**
- ✓ Rapid development, excellent libraries
- ✓ Easy to read and maintain
- ✓ Strong ORM support (SQLAlchemy)
- ✗ Slower than compiled languages (Go, Rust)
- ✗ GIL may limit concurrency (not issue for I/O-bound app)

### ADR-005: Docker Compose for Orchestration

**Status:** Accepted
**Context:** Need simple multi-container deployment
**Decision:** Use Docker Compose (not Kubernetes)
**Consequences:**
- ✓ Simple YAML configuration
- ✓ Easy local development environment
- ✓ Suitable for single-server deployment
- ✗ Not suitable for multi-node clusters
- ✗ Limited auto-scaling capabilities

---

## 11. Non-Functional Requirements

### 11.1 Performance

- **Response Time**: API responses < 200ms (95th percentile)
- **Concurrent Users**: Support 50 simultaneous users
- **Database Size**: Optimize for < 1GB database size
- **Page Load**: Frontend loads < 2 seconds on 3G

### 11.2 Scalability

- **Vertical Scaling**: Increase container resources (CPU/memory)
- **Horizontal Scaling**: Run multiple app containers behind load balancer
- **Database Migration**: Path to PostgreSQL if exceeding SQLite limits

### 11.3 Reliability

- **Uptime**: 99% availability target
- **Data Integrity**: ACID compliance via SQLite transactions
- **Backup**: Daily automated backups with 30-day retention
- **Disaster Recovery**: Database restore < 15 minutes

### 11.4 Security

- **Authentication**: JWT tokens with 24-hour expiry
- **Password Security**: Bcrypt hashing (cost factor 12)
- **Transport Security**: HTTPS/TLS 1.3
- **Input Validation**: All user inputs sanitized
- **SQL Injection**: Protected via ORM parameterized queries

### 11.5 Maintainability

- **Code Quality**: Linting (pylint/flake8), type hints
- **Testing**: Unit tests (80% coverage target)
- **Documentation**: API documentation (OpenAPI/Swagger)
- **Logging**: Structured logging (JSON format)
- **Monitoring**: Health checks, error tracking

---

## 12. Future Considerations

### 12.1 Potential Enhancements

1. **Email Notifications**: Send meeting invites via SMTP
2. **Calendar Integration**: Google Calendar / Outlook sync
3. **Recurring Meetings**: Support weekly/monthly recurring meetings
4. **Time Zone Support**: Handle multi-timezone teams
5. **Mobile App**: Native iOS/Android apps
6. **Real-time Updates**: WebSocket for live calendar updates
7. **Advanced Analytics**: Meeting statistics and reports

### 12.2 Scaling Path

**Phase 1 (Current):** SQLite + Single Docker Host
**Phase 2 (50-200 users):** PostgreSQL + Load Balancer + Multiple App Containers
**Phase 3 (200+ users):** Kubernetes + Microservices + Redis Cache + Message Queue

---

## 13. Conclusion

This architecture provides a solid foundation for a team meeting scheduler with:

- ✅ Simple technology stack (Python + SQLite + Docker)
- ✅ Clear separation of concerns (3-tier architecture)
- ✅ Security best practices (JWT, bcrypt, HTTPS)
- ✅ Easy deployment (Docker Compose)
- ✅ Maintainable codebase (well-documented, standard patterns)
- ✅ Scalability path (vertical then horizontal scaling)

The architecture balances simplicity with professional practices, making it suitable for small to medium teams while providing a clear path for future growth.

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-01 | System Architect | Initial architecture design |

**Approvals:**

- [ ] Technical Lead Review
- [ ] Security Review
- [ ] DevOps Review
- [ ] Product Owner Approval
