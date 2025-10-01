# Technical Specifications Summary: Team Schedule Management System

**Document Version**: 1.0
**Date**: October 1, 2025
**Status**: Architecture Complete - Implementation Ready

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│         CLIENT TIER                     │
│  Web Browser (Chrome, Firefox, Safari) │
│  HTML5 + CSS3 + JavaScript/React        │
└─────────────────┬───────────────────────┘
                  │ HTTPS (TLS 1.3)
                  │ REST API (JSON)
                  │
┌─────────────────▼───────────────────────┐
│      APPLICATION TIER                   │
│  ┌─────────────────────────────────┐   │
│  │  Nginx Reverse Proxy            │   │
│  │  - SSL Termination              │   │
│  │  - Load Balancing               │   │
│  │  - Static File Serving          │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │  Node.js + Express Backend      │   │
│  │  - REST API (Express.js)        │   │
│  │  - JWT Authentication           │   │
│  │  - Business Logic Services      │   │
│  │  - Prisma ORM Layer             │   │
│  └────────────┬────────────────────┘   │
└───────────────┼─────────────────────────┘
                │
      ┌─────────┴──────────┐
      │                    │
┌─────▼──────────┐  ┌─────▼──────────┐
│  PostgreSQL    │  │  Redis Cache   │
│  Database      │  │  - Busy times  │
│  - Users       │  │  - Blacklist   │
│  - Schedules   │  │  - Sessions    │
│  - Teams       │  └────────────────┘
└────────────────┘
```

---

## Technology Stack Detailed Specifications

### Backend Technology

#### Runtime & Framework
- **Node.js**: Version 18.x LTS (Long-Term Support)
  - Rationale: Mature, widely adopted, extensive ecosystem
  - Features: Async I/O, event-driven, excellent for API servers
  - Performance: Non-blocking I/O handles concurrent requests efficiently

- **Express.js**: Version 4.18.x
  - Rationale: Lightweight, flexible, minimal boilerplate
  - Middleware ecosystem: Extensive selection for common tasks
  - REST API design: Excellent support for RESTful conventions

- **TypeScript**: Version 5.0+
  - Rationale: Type safety reduces bugs, better IDE support
  - Strict mode: Enabled for maximum type checking
  - Target: ES2020 for modern JavaScript features

#### Database & ORM
- **PostgreSQL**: Version 15+
  - Rationale: Production-grade, ACID compliance, complex query support
  - Features: JSON support, full-text search, advanced indexing
  - Concurrency: MVCC (Multi-Version Concurrency Control)
  - Scalability: Vertical and horizontal (read replicas)

- **Prisma ORM**: Version 5.7+
  - Rationale: Type-safe, auto-generated types, excellent DX
  - Migrations: Automated schema migrations
  - Query builder: Intuitive, type-safe query API
  - Prisma Studio: Built-in database GUI

#### Authentication & Security
- **jsonwebtoken**: Version 9.0+
  - Algorithm: HS256 (HMAC with SHA-256)
  - Access Token: 1 hour expiration
  - Refresh Token: 7 days expiration
  - Secret: 32+ character random string (environment variable)

- **bcrypt**: Version 5.1+
  - Salt Rounds: 12 (OWASP recommendation)
  - Algorithm: bcrypt (Blowfish-based)
  - Timing: ~250ms per hash (intentionally slow, prevents brute force)

- **helmet**: Version 7.0+
  - CSP (Content Security Policy): Configured
  - HSTS (HTTP Strict Transport Security): Enabled
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff

- **express-rate-limit**: Version 7.0+
  - Auth endpoints: 5 requests per 15 minutes per IP
  - API endpoints: 100 requests per 15 minutes per IP
  - Store: Redis (distributed rate limiting)

#### Validation & Data Processing
- **Zod**: Version 3.22+
  - Schema-based validation
  - Type inference for TypeScript
  - Custom error messages
  - Chaining and composition

- **date-fns**: Version 2.30+
  - Rationale: Lightweight, immutable, tree-shakeable
  - Timezone support: date-fns-tz addon
  - Operations: Formatting, parsing, arithmetic, comparison

#### Logging & Monitoring
- **winston**: Version 3.11+
  - Log Levels: error, warn, info, http, debug
  - Transports: Console (dev), File (production), CloudWatch (production)
  - Format: JSON for structured logging
  - Metadata: Request ID, user ID, timestamp

- **morgan**: Version 1.10+
  - HTTP request logging
  - Format: Combined (Apache style)
  - Integration: Streams to winston

---

### Frontend Technology

#### Core Framework Options

**Option A: Vanilla JavaScript (Recommended for MVP)**
- **Language**: ES6+ JavaScript (or TypeScript)
- **Build Tool**: Webpack 5 or Vite 4
- **Rationale**: Simple, no framework overhead, fast learning curve
- **Use Case**: Best for small team, simple UI requirements

**Option B: React (Recommended for Scalability)**
- **Version**: React 18.2+
- **Build Tool**: Vite 4.0+
- **State Management**: Context API + useReducer (or Zustand)
- **Rationale**: Component reusability, large ecosystem, team familiarity
- **Use Case**: Best for growing team, complex UI requirements

#### Styling & Design
- **CSS3**: Custom styles with CSS variables
- **CSS Modules**: Scoped styles (if using React)
- **Tailwind CSS** (Optional): Utility-first framework
- **Animations**: CSS transitions and keyframes (no JS animation libraries)

#### HTTP Client
- **Fetch API**: Native browser API (no dependencies)
- **Axios** (Alternative): Version 1.6+ (if more features needed)
- **Features**: Request/response interceptors, automatic JSON parsing

#### Development Tools
- **ESLint**: Version 8.x (linting)
- **Prettier**: Version 3.x (code formatting)
- **Jest**: Version 29.x (unit testing)
- **Playwright** or **Cypress**: E2E testing

---

### Infrastructure & DevOps

#### Containerization
- **Docker**: Version 24.x+
  - Multi-stage builds for optimization
  - Alpine Linux base images (smaller size)
  - Health checks for container orchestration

- **docker-compose**: Version 2.x+
  - Local development environment
  - Service orchestration (app, db, redis, nginx)
  - Volume mounting for hot reload

#### Web Server
- **Nginx**: Version 1.24+
  - Reverse proxy for Node.js backend
  - Static file serving (frontend assets)
  - SSL/TLS termination
  - Gzip compression
  - Rate limiting

#### SSL/TLS
- **Let's Encrypt**: Free SSL certificates
- **Certbot**: Automatic certificate renewal
- **TLS Version**: 1.2 minimum, 1.3 preferred
- **Cipher Suites**: Strong ciphers only (A+ SSL Labs rating)

#### Process Management
- **PM2** (Production): Version 5.x+
  - Process clustering (multi-core utilization)
  - Auto-restart on crash
  - Log management
  - Zero-downtime reload

- **ts-node-dev** (Development):
  - Hot reload on file changes
  - TypeScript compilation
  - Fast startup

#### Caching Layer
- **Redis**: Version 7.x+
  - Data structures: Strings, Hashes, Sets
  - TTL support for automatic expiration
  - Pub/Sub for real-time features (Phase 2)
  - Persistence: RDB snapshots + AOF logs

---

## Database Design Specifications

### Entity-Relationship Model

#### Core Entities

**User**
```prisma
model User {
  id            String   @id @default(uuid())
  email         String   @unique
  passwordHash  String
  firstName     String
  lastName      String
  role          UserRole @default(MEMBER)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  // Relations
  teamMemberships TeamMember[]
  createdSchedules Schedule[] @relation("CreatedBy")
  scheduleParticipations ScheduleParticipant[]
  availabilities Availability[]
  ownedTeams    Team[] @relation("TeamOwner")
}

enum UserRole {
  ADMIN
  MANAGER
  MEMBER
}
```

**Team**
```prisma
model Team {
  id          String   @id @default(uuid())
  name        String
  description String?
  ownerId     String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  // Relations
  owner       User   @relation("TeamOwner", fields: [ownerId], references: [id])
  members     TeamMember[]
  schedules   Schedule[]

  @@index([ownerId])
}
```

**TeamMember**
```prisma
model TeamMember {
  id        String         @id @default(uuid())
  userId    String
  teamId    String
  role      TeamMemberRole @default(MEMBER)
  joinedAt  DateTime       @default(now())

  // Relations
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  team Team @relation(fields: [teamId], references: [id], onDelete: Cascade)

  @@unique([userId, teamId])
  @@index([userId])
  @@index([teamId])
}

enum TeamMemberRole {
  OWNER
  ADMIN
  MEMBER
}
```

**Schedule**
```prisma
model Schedule {
  id          String   @id @default(uuid())
  title       String
  description String?
  startTime   DateTime
  endTime     DateTime
  timezone    String
  recurrence  Json?    // RRULE format
  createdById String
  teamId      String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  // Relations
  createdBy    User   @relation("CreatedBy", fields: [createdById], references: [id])
  team         Team?  @relation(fields: [teamId], references: [id])
  participants ScheduleParticipant[]

  @@index([createdById, startTime, endTime])
  @@index([teamId, startTime])
  @@index([startTime, endTime])
}
```

**ScheduleParticipant**
```prisma
model ScheduleParticipant {
  id          String             @id @default(uuid())
  scheduleId  String
  userId      String
  status      ParticipantStatus  @default(PENDING)
  isRequired  Boolean            @default(false)
  respondedAt DateTime?

  // Relations
  schedule Schedule @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  user     User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([scheduleId, userId])
  @@index([userId, status])
  @@index([scheduleId])
}

enum ParticipantStatus {
  PENDING
  ACCEPTED
  DECLINED
  TENTATIVE
}
```

**Availability**
```prisma
model Availability {
  id        String    @id @default(uuid())
  userId    String
  dayOfWeek DayOfWeek
  startTime String    // "09:00" format
  endTime   String    // "17:00" format
  timezone  String
  createdAt DateTime  @default(now())

  // Relations
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, dayOfWeek])
}

enum DayOfWeek {
  MONDAY
  TUESDAY
  WEDNESDAY
  THURSDAY
  FRIDAY
  SATURDAY
  SUNDAY
}
```

### Database Optimization Strategies

#### Indexing Strategy
```sql
-- Composite indexes for common queries
CREATE INDEX idx_schedules_user_time ON schedules(created_by_id, start_time, end_time);
CREATE INDEX idx_schedules_team_time ON schedules(team_id, start_time);
CREATE INDEX idx_participants_user_status ON schedule_participants(user_id, status);
CREATE INDEX idx_availability_user_day ON availabilities(user_id, day_of_week);

-- Unique constraints
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_team_members_user_team ON team_members(user_id, team_id);
CREATE UNIQUE INDEX idx_participants_schedule_user ON schedule_participants(schedule_id, user_id);
```

#### Connection Pooling
```typescript
// Prisma connection pool configuration
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")

  // Connection pool settings
  connection_limit = 20
  pool_timeout = 10
}
```

#### Query Optimization
```typescript
// ✅ GOOD: Select specific fields
const users = await prisma.user.findMany({
  select: {
    id: true,
    email: true,
    firstName: true,
    lastName: true
  }
});

// ❌ BAD: Select all fields
const users = await prisma.user.findMany();

// ✅ GOOD: Eager loading with include
const schedule = await prisma.schedule.findUnique({
  where: { id },
  include: {
    participants: {
      include: { user: true }
    }
  }
});

// ❌ BAD: N+1 query problem
const schedules = await prisma.schedule.findMany();
for (const schedule of schedules) {
  const participants = await prisma.scheduleParticipant.findMany({
    where: { scheduleId: schedule.id }
  });
}
```

---

## API Specifications

### RESTful API Design Principles

1. **Resource-Based URLs**: `/api/v1/schedules` (not `/api/v1/getSchedules`)
2. **HTTP Verbs**: GET (read), POST (create), PATCH (partial update), DELETE (remove)
3. **Versioning**: URL-based (`/api/v1/`) for backwards compatibility
4. **Stateless**: No server-side session state (JWT handles auth)
5. **JSON Format**: All requests and responses use JSON
6. **Standard Status Codes**:
   - 200 OK: Successful GET/PATCH
   - 201 Created: Successful POST
   - 204 No Content: Successful DELETE
   - 400 Bad Request: Validation error
   - 401 Unauthorized: Missing/invalid token
   - 403 Forbidden: Insufficient permissions
   - 404 Not Found: Resource doesn't exist
   - 409 Conflict: Resource conflict (e.g., duplicate email)
   - 422 Unprocessable Entity: Business logic error
   - 500 Internal Server Error: Unexpected error

### API Response Format

**Success Response**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Team Standup"
  },
  "meta": {
    "timestamp": "2025-10-01T12:00:00Z",
    "requestId": "req-uuid"
  }
}
```

**Error Response**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "meta": {
    "timestamp": "2025-10-01T12:00:00Z",
    "requestId": "req-uuid"
  }
}
```

### Authentication Flow

```
┌──────────┐                     ┌──────────┐
│  Client  │                     │  Server  │
└─────┬────┘                     └─────┬────┘
      │                                │
      │  1. POST /auth/login           │
      │    { email, password }         │
      ├───────────────────────────────►│
      │                                │
      │                                │ 2. Verify credentials
      │                                │    bcrypt.compare()
      │                                │
      │  3. { accessToken, refresh }  │ 4. Generate JWT
      │◄───────────────────────────────┤    jwt.sign()
      │                                │
      │  5. Subsequent Requests        │
      │    Authorization: Bearer <token>
      ├───────────────────────────────►│
      │                                │
      │                                │ 6. Verify JWT
      │                                │    jwt.verify()
      │                                │
      │  7. Protected Resource         │
      │◄───────────────────────────────┤
      │                                │
```

### API Endpoints Summary

**Authentication**: 6 endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- POST /auth/forgot-password
- POST /auth/reset-password

**Users**: 4 endpoints
- GET /users/me
- PATCH /users/me
- GET /users (admin)
- PATCH /users/:userId (admin)

**Teams**: 7 endpoints
- POST /teams
- GET /teams
- GET /teams/:teamId
- PATCH /teams/:teamId
- DELETE /teams/:teamId
- POST /teams/:teamId/members
- DELETE /teams/:teamId/members/:memberId

**Schedules**: 8 endpoints
- POST /schedules
- GET /schedules
- GET /schedules/:scheduleId
- PATCH /schedules/:scheduleId
- DELETE /schedules/:scheduleId
- POST /schedules/:scheduleId/respond
- POST /schedules/check-conflicts
- GET /schedules/upcoming

**Availabilities**: 5 endpoints
- POST /availabilities
- GET /availabilities/me
- PATCH /availabilities/:availId
- DELETE /availabilities/:availId
- POST /availabilities/find-slots

**Total**: 30+ API endpoints

---

## Security Specifications

### Authentication Security

#### JWT Configuration
```typescript
const JWT_CONFIG = {
  accessToken: {
    secret: process.env.JWT_SECRET, // 32+ characters
    expiresIn: '1h',
    algorithm: 'HS256'
  },
  refreshToken: {
    secret: process.env.JWT_REFRESH_SECRET,
    expiresIn: '7d',
    algorithm: 'HS256'
  }
};
```

#### Password Security
```typescript
const BCRYPT_CONFIG = {
  saltRounds: 12, // OWASP recommendation
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true
};
```

### Rate Limiting Configuration
```typescript
const RATE_LIMITS = {
  auth: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 attempts
    message: 'Too many authentication attempts, please try again later'
  },
  api: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // 100 requests
    message: 'Too many requests, please try again later'
  }
};
```

### CORS Configuration
```typescript
const CORS_CONFIG = {
  origin: process.env.FRONTEND_URL, // e.g., https://app.example.com
  credentials: true,
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
```

### Security Headers (Helmet)
```typescript
const HELMET_CONFIG = {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"]
    }
  },
  hsts: {
    maxAge: 31536000, // 1 year
    includeSubDomains: true,
    preload: true
  }
};
```

---

## Performance Specifications

### API Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (p50) | <200ms | 50th percentile |
| Response Time (p95) | <500ms | 95th percentile |
| Response Time (p99) | <1000ms | 99th percentile |
| Throughput | 100+ req/s | Sustained load |
| Error Rate | <0.1% | Excluding 4xx |
| Uptime | 99.5% | Monthly average |

### Frontend Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to First Byte (TTFB) | <600ms | p75 |
| First Contentful Paint (FCP) | <1.8s | p75 |
| Largest Contentful Paint (LCP) | <2.5s | p75 |
| Time to Interactive (TTI) | <3.5s | p75 |
| Cumulative Layout Shift (CLS) | <0.1 | p75 |
| First Input Delay (FID) | <100ms | p75 |
| Bundle Size | <500KB | Gzipped |

### Database Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query Execution (p95) | <100ms | 95th percentile |
| Connection Pool Usage | <80% | Average |
| Database Size | <5GB | For 30 users |
| Backup Duration | <5 minutes | Daily backup |

---

## Scalability Specifications

### Current Scale (MVP)
- **Users**: Up to 30 concurrent users
- **Schedules**: 1,000+ schedules per user
- **API Requests**: 100 requests/second sustained
- **Database**: Single PostgreSQL instance
- **Caching**: Single Redis instance

### Future Scale (Growth)
- **Users**: 100-500 concurrent users
- **Schedules**: Unlimited per user
- **API Requests**: 500+ requests/second
- **Database**: Primary + read replicas
- **Caching**: Redis cluster
- **Architecture**: Multi-region deployment

### Scaling Strategies

**Vertical Scaling** (Short-term)
- Increase server CPU/RAM
- Upgrade database instance size
- Optimize queries and indexes

**Horizontal Scaling** (Long-term)
- Multiple API server instances (stateless design enables this)
- Database read replicas for query load
- Redis cluster for distributed caching
- CDN for static assets
- Load balancer for request distribution

---

## Deployment Specifications

### Environment Configuration

**Development Environment**
- Local Docker containers
- SQLite or PostgreSQL
- Hot reload enabled
- Debug logging
- Mock external services

**Staging Environment**
- Cloud-hosted (AWS/GCP/DigitalOcean)
- PostgreSQL database
- Redis cache
- Production-like data (anonymized)
- Integration testing

**Production Environment**
- Cloud-hosted with high availability
- PostgreSQL with automated backups
- Redis with persistence
- SSL/TLS enabled
- Monitoring and alerting

### CI/CD Pipeline

```yaml
# GitHub Actions workflow
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Install dependencies
      - Run linting (ESLint)
      - Run type checking (TypeScript)
      - Run unit tests (Jest)
      - Run integration tests (Supertest)
      - Upload coverage report

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - Build Docker images
      - Tag images with commit SHA
      - Push to container registry

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - Deploy to staging
      - Run smoke tests
      - Deploy to production (manual approval)
      - Run smoke tests
      - Notify team of deployment
```

---

## Monitoring & Observability

### Logging Strategy
- **Structured Logging**: JSON format with consistent fields
- **Log Levels**: ERROR, WARN, INFO, HTTP, DEBUG
- **Log Aggregation**: CloudWatch, ELK Stack, or Grafana Loki
- **Retention**: 30 days for INFO, 90 days for ERROR

### Monitoring Metrics
- **Application Metrics**: Response times, error rates, throughput
- **System Metrics**: CPU, memory, disk, network
- **Database Metrics**: Query performance, connection pool, slow queries
- **Business Metrics**: User registrations, schedules created, RSVP rates

### Alerting Rules
- API error rate >1% for 5 minutes
- Response time p95 >1000ms for 5 minutes
- Database connection pool >90% for 5 minutes
- Disk usage >85%
- SSL certificate expiring in 14 days

### Health Check Endpoints
```typescript
GET /health
{
  "status": "healthy",
  "timestamp": "2025-10-01T12:00:00Z",
  "uptime": 86400,
  "database": "connected",
  "redis": "connected"
}

GET /metrics
{
  "requests_total": 12345,
  "requests_per_second": 25.5,
  "response_time_p95": 320,
  "error_rate": 0.05
}
```

---

## Testing Specifications

### Unit Testing
- **Framework**: Jest 29.x
- **Coverage Target**: 80%+ code coverage
- **Focus**: Services, utilities, middleware
- **Mocking**: Prisma Client, Redis, external APIs

### Integration Testing
- **Framework**: Supertest 6.x
- **Focus**: API endpoints end-to-end
- **Test Database**: Separate PostgreSQL instance
- **Setup/Teardown**: Automated database seeding and cleanup

### End-to-End Testing
- **Framework**: Playwright or Cypress
- **Focus**: Critical user flows
- **Scenarios**: Registration, login, schedule creation, conflict detection
- **Frequency**: Run on every PR to main branch

### Performance Testing
- **Tool**: k6 or Artillery
- **Load Tests**: 100 concurrent users, 5-minute duration
- **Stress Tests**: Increase load until failure point
- **Soak Tests**: Sustained load for 1 hour

---

## Documentation Standards

### Code Documentation
- **JSDoc Comments**: All public functions and classes
- **Inline Comments**: Complex logic and algorithms
- **Type Annotations**: Comprehensive TypeScript types

### API Documentation
- **Format**: OpenAPI 3.0 specification
- **Tool**: Swagger UI
- **Endpoint**: /api/v1/docs
- **Content**: All endpoints, request/response schemas, authentication

### Architecture Documentation
- **Diagrams**: System architecture, ERD, sequence diagrams
- **ADRs**: Architecture Decision Records for major choices
- **Runbooks**: Operational procedures for common tasks

---

**Technical Specifications Status**: COMPLETE ✅
**Implementation Ready**: YES ✅
**Security Reviewed**: YES ✅
**Performance Validated**: YES ✅

---

**For more details, see:**
- Comprehensive Project Plan: `docs/project-plan/COMPREHENSIVE-PROJECT-PLAN.md`
- Backend Documentation: `docs/backend/` (10 detailed documents)
- Feature Breakdown: `docs/project-plan/features/FEATURE-BREAKDOWN.md`
