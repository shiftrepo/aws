# Architecture Summary - Team Meeting Scheduler

**Project:** Web-Based Team Meeting Scheduler
**Architecture Version:** 1.0
**Date:** 2025-10-01
**Architect:** System Architecture Designer

---

## Quick Reference

### Documentation Files

| Document | Description | Path |
|----------|-------------|------|
| **System Architecture** | Complete system design, diagrams, and technical decisions | `/docs/architecture/SYSTEM_ARCHITECTURE.md` |
| **API Specification** | REST API endpoints, request/response formats, authentication | `/docs/architecture/API_SPECIFICATION.md` |
| **Deployment Guide** | Step-by-step deployment, backup, monitoring procedures | `/docs/architecture/DEPLOYMENT_GUIDE.md` |

---

## Technology Stack (Recommended)

### Backend
- **Language:** Python 3.11+
- **Framework:** Flask 3.0 or FastAPI
- **Database:** SQLite 3.40+
- **ORM:** SQLAlchemy 2.0
- **Authentication:** PyJWT + bcrypt
- **Server:** Gunicorn or Uvicorn

### Frontend
- **Base:** HTML5 + CSS3 + Vanilla JavaScript (ES6)
- **HTTP Client:** Fetch API
- **Calendar UI:** FullCalendar.js (optional)
- **No Build Tools:** Direct browser execution

### Infrastructure
- **Containerization:** Docker 24+
- **Orchestration:** Docker Compose 2.20+
- **Reverse Proxy:** Nginx (with SSL/TLS)
- **SSL Certificates:** Let's Encrypt (Certbot)

### Alternative Stacks
- **Option B:** Go + Gin/Echo + database/sql
- **Option C:** Node.js + Express/Fastify + TypeScript

**Rationale:** Python selected for balance of simplicity, development speed, extensive libraries, and maintainability.

---

## System Architecture Overview

### 3-Tier Architecture

```
┌─────────────────────────┐
│   Presentation Tier     │  ← Web Browser (HTML/CSS/JS)
│   (Frontend)            │
└───────────┬─────────────┘
            │ HTTPS/REST
┌───────────▼─────────────┐
│   Application Tier      │  ← Python Flask/FastAPI
│   (Business Logic)      │    - Authentication
└───────────┬─────────────┘    - Availability logic
            │ SQLAlchemy       - Meeting scheduler
┌───────────▼─────────────┐
│   Data Tier             │  ← SQLite Database
│   (Persistence)         │    - users, availability
└─────────────────────────┘    - meetings, sessions
```

### Container Architecture

```
┌──────────────────────────────────────┐
│        Docker Compose Stack          │
│                                      │
│  ┌────────────┐    ┌─────────────┐ │
│  │   Nginx    │────│     App     │ │
│  │  (Port 80) │    │  (Port 8000)│ │
│  │  (Port 443)│    │   Python    │ │
│  └────────────┘    └──────┬──────┘ │
│                           │         │
│                    ┌──────▼──────┐  │
│                    │   Volume    │  │
│                    │  /app/data  │  │
│                    │ (SQLite DB) │  │
│                    └─────────────┘  │
└──────────────────────────────────────┘
```

---

## Database Schema

### Core Tables (5)

1. **users** - User accounts and authentication
2. **availability** - User availability patterns (day-of-week + time ranges)
3. **meetings** - Scheduled meetings
4. **meeting_participants** - Many-to-many relationship for meeting attendees
5. **sessions** - Authentication tokens and session management

### Key Relationships

```
users (1) ──< (M) availability
users (1) ──< (M) meetings (creator)
users (M) ──< (M) meeting_participants >── (M) meetings
users (1) ──< (M) sessions
```

### Design Decisions

- **Day-of-Week Pattern:** Recurring availability stored as day (0-6) + time range
- **Time Format:** HH:MM (24-hour) for daily patterns, DATETIME for actual meetings
- **Cascading Deletes:** Automatic cleanup of related records
- **Indexes:** Strategic indexing on foreign keys and query-heavy columns

---

## API Design Highlights

### Endpoint Categories

| Category | Endpoints | Key Features |
|----------|-----------|--------------|
| **Authentication** | 5 endpoints | JWT tokens, bcrypt hashing, 24hr expiry |
| **Users** | 4 endpoints | Profile management, admin controls |
| **Availability** | 5 endpoints | CRUD operations, conflict detection |
| **Meetings** | 8 endpoints | CRUD, participant management, slot discovery |

### Critical Endpoint: Available Time Slots

```
GET /api/meetings/available
  ?participants=1,2,3
  &duration=30
  &startDate=2025-10-05
  &endDate=2025-10-12
```

**Algorithm:**
1. Retrieve all participants' availability
2. Find overlapping time windows
3. Generate slots matching duration requirement
4. Check against existing meetings
5. Return available slots sorted by date/time

---

## Security Architecture

### Authentication Flow

```
1. User Login (POST /api/auth/login)
   ↓
2. Validate credentials (bcrypt compare)
   ↓
3. Generate JWT token (24hr expiry)
   ↓
4. Return token to client
   ↓
5. Client stores token (LocalStorage)
   ↓
6. Subsequent requests include token in Authorization header
   ↓
7. Middleware validates token on each request
```

### Security Measures

| Threat | Mitigation |
|--------|------------|
| SQL Injection | Parameterized queries via SQLAlchemy ORM |
| XSS | Input sanitization, CSP headers |
| CSRF | SameSite cookies, CSRF tokens |
| Password Attacks | Bcrypt (cost 12), rate limiting |
| Token Theft | HTTPS only, short expiry (24h) |
| Unauthorized Access | RBAC (admin/member roles), middleware auth |

### Role-Based Access Control (RBAC)

**Admin Role:**
- Full system access
- User management (CRUD)
- View all availability and meetings
- Delete any meeting

**Member Role:**
- Manage own profile
- Manage own availability
- Create meetings
- View others' availability (for scheduling)
- Delete own meetings only

---

## Deployment Architecture

### Production Topology

```
Internet (HTTPS)
    ↓
DNS / Load Balancer
    ↓
Docker Host (VM/VPS)
    ├─ Nginx Container (SSL termination, reverse proxy)
    └─ App Container (Python application)
        └─ Persistent Volume (SQLite database)
```

### Deployment Steps (Summary)

1. **Server Prep:** Install Docker, create app user, clone repo
2. **Configuration:** Create .env file with secure secrets
3. **SSL Setup:** Obtain Let's Encrypt certificate via Certbot
4. **Nginx Config:** Configure reverse proxy with SSL and rate limiting
5. **Start Services:** `docker-compose up -d --build`
6. **Initialize DB:** Run migrations and create admin user
7. **Systemd Service:** Enable auto-start on boot
8. **Backup Setup:** Configure daily automated backups

### Backup Strategy

- **Method:** SQLite hot backup via `.backup` command
- **Frequency:** Daily at 2 AM (cron job)
- **Retention:** 30 days local, optional S3 upload
- **Restore Time:** < 15 minutes

---

## Non-Functional Requirements

### Performance Targets

- **API Response Time:** < 200ms (95th percentile)
- **Concurrent Users:** 50 simultaneous users
- **Database Size:** Optimized for < 1GB
- **Page Load Time:** < 2 seconds on 3G

### Reliability Targets

- **Uptime:** 99% availability
- **Data Integrity:** ACID compliance (SQLite transactions)
- **Backup Frequency:** Daily automated backups
- **Disaster Recovery:** < 15 minute restore time

### Scalability Path

**Phase 1 (Current):** SQLite + Single Docker Host (5-50 users)

**Phase 2 (Growth):** PostgreSQL + Load Balancer + Multiple App Containers (50-200 users)

**Phase 3 (Enterprise):** Kubernetes + Microservices + Redis Cache + Message Queue (200+ users)

---

## Architecture Decision Records (ADRs)

### ADR-001: SQLite vs PostgreSQL/MySQL
**Decision:** Use SQLite for initial deployment
**Rationale:** Zero configuration, embedded, sufficient for target user count (5-50)
**Trade-off:** Limited concurrent writes (acceptable for scheduler use case)

### ADR-002: JWT Token-Based Authentication
**Decision:** Use JWT with bcrypt password hashing
**Rationale:** Stateless, scalable, industry standard
**Trade-off:** Cannot revoke tokens before expiry (mitigated with short 24hr expiry)

### ADR-003: Vanilla JavaScript Frontend
**Decision:** No React/Vue/Angular framework
**Rationale:** No build pipeline, smaller bundle, easier maintenance
**Trade-off:** More manual DOM manipulation

### ADR-004: Python Flask/FastAPI Backend
**Decision:** Python 3.11+ with Flask or FastAPI
**Rationale:** Rapid development, excellent libraries, easy maintenance
**Trade-off:** Slower than compiled languages (not critical for I/O-bound app)

### ADR-005: Docker Compose Orchestration
**Decision:** Use Docker Compose (not Kubernetes)
**Rationale:** Simple configuration, suitable for single-server deployment
**Trade-off:** Limited auto-scaling (acceptable for initial scale)

---

## Frontend-Backend Interaction

### Communication Pattern

**Single Page Application (SPA) with REST API**

- **Protocol:** HTTPS
- **Format:** JSON
- **Authentication:** Bearer token in Authorization header
- **State Management:**
  - Client: LocalStorage (token), session state (user data)
  - Server: Database (persistent), optional session table

### Example Request Flow

```javascript
// Frontend (JavaScript)
const response = await fetch('/api/meetings/available', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
```

---

## Key Features

### 1. Availability Management
- Users define weekly availability patterns
- Support for recurring schedules (e.g., "Monday 9 AM - 5 PM")
- Optional date ranges for temporary availability
- Conflict detection when creating/updating availability

### 2. Meeting Slot Discovery
- Intelligent algorithm to find common availability
- Filter by participants, duration, date range
- Considers existing meetings to avoid double-booking
- Returns sorted list of available time slots

### 3. Meeting Management
- Create meetings with multiple participants
- Participant status tracking (pending/accepted/declined)
- Meeting CRUD operations with ownership controls
- Real-time conflict detection

### 4. Authentication & Authorization
- Secure user registration and login
- JWT token-based session management
- Role-based access control (admin/member)
- Password strength requirements

---

## Monitoring & Maintenance

### Health Checks

```bash
# Application health endpoint
curl https://scheduler.example.com/health

# Container status
docker-compose ps

# Database size
ls -lh /opt/meeting-scheduler/data/scheduler.db
```

### Log Management

- **Application Logs:** `/app/logs/app.log` (inside container)
- **Nginx Logs:** `/var/log/nginx/` (access and error logs)
- **Log Rotation:** Configured via logrotate (30-day retention)

### Performance Monitoring

- Container resource usage: `docker stats`
- API response times: Application logging
- Database statistics: SQLite queries for record counts
- Optional: Prometheus + Grafana for advanced metrics

---

## Future Enhancements

### Short-Term (Phase 1)
1. Email notifications for meeting invites
2. Calendar export (ICS format)
3. Time zone support
4. Meeting reminders

### Medium-Term (Phase 2)
1. Google Calendar integration
2. Outlook calendar sync
3. Recurring meetings support
4. Advanced analytics and reporting

### Long-Term (Phase 3)
1. Mobile apps (iOS/Android)
2. Real-time updates via WebSocket
3. AI-powered scheduling suggestions
4. Video conferencing integration

---

## Development Workflow

### Local Setup (Quick Start)

```bash
# Clone and setup
git clone https://github.com/yourorg/meeting-scheduler.git
cd meeting-scheduler

# Create environment
cat > .env << EOF
JWT_SECRET_KEY=$(openssl rand -hex 32)
EOF

# Start development environment
docker-compose up -d --build

# Initialize database
docker-compose exec app python -m src.migrations.init_db

# Create admin user
docker-compose exec app python -m src.scripts.create_admin \
  --email admin@localhost --password AdminPass123! --name "Admin"

# Access application
open http://localhost:8000
```

---

## Testing Strategy

### Unit Tests
- Models and database operations
- Authentication and authorization logic
- Availability conflict detection
- Meeting slot discovery algorithm

### Integration Tests
- API endpoint testing
- Database transaction testing
- Authentication flow testing

### End-to-End Tests
- User registration and login
- Availability management workflow
- Meeting creation and scheduling
- Multi-user interaction scenarios

**Target Coverage:** 80%

---

## Support & Documentation

### Documentation Structure

```
/docs
  /architecture
    - SYSTEM_ARCHITECTURE.md (this file)
    - API_SPECIFICATION.md
    - DEPLOYMENT_GUIDE.md
    - ARCHITECTURE_SUMMARY.md
  /api
    - OpenAPI specification (auto-generated)
  /developer
    - Contributing guidelines
    - Code style guide
```

### API Documentation

- **Interactive Docs:** https://scheduler.example.com/api/docs (Swagger UI)
- **OpenAPI Spec:** https://scheduler.example.com/api/openapi.json

---

## Team Coordination

### Memory Store Keys (for Swarm Coordination)

All architecture decisions stored in memory namespace `coordination`:

- `architecture-stack` - Technology stack and alternatives
- `architecture-database` - Database schema design
- `architecture-api` - REST API endpoints and patterns
- `architecture-docker` - Containerization strategy
- `architecture-security` - Authentication and security measures
- `architecture-patterns` - Frontend-backend interaction patterns
- `architecture-deployment` - Production deployment topology

### Handoff to Development Team

**Next Steps:**
1. **Backend Developer:** Implement REST API based on API_SPECIFICATION.md
2. **Frontend Developer:** Build UI components and API integration
3. **Database Developer:** Implement schema from SYSTEM_ARCHITECTURE.md
4. **DevOps Engineer:** Setup deployment pipeline per DEPLOYMENT_GUIDE.md
5. **QA Engineer:** Create test suite based on requirements and API spec

---

## Quick Command Reference

### Development
```bash
docker-compose up -d --build        # Start dev environment
docker-compose logs -f              # View logs
docker-compose exec app /bin/bash  # Interactive shell
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d  # Start production
/usr/local/bin/scheduler-backup.sh               # Manual backup
sudo systemctl status scheduler                  # Check service status
```

### Database
```bash
# Initialize
docker-compose exec app python -m src.migrations.init_db

# Backup
docker-compose exec app sqlite3 /app/data/scheduler.db ".backup /tmp/backup.db"

# Vacuum (optimize)
docker-compose exec app sqlite3 /app/data/scheduler.db "VACUUM;"
```

---

## Success Criteria

- ✅ **Simplicity:** Easy to understand and maintain
- ✅ **Security:** Industry-standard authentication and authorization
- ✅ **Scalability:** Clear path from 5 to 200+ users
- ✅ **Reliability:** 99% uptime with automated backups
- ✅ **Performance:** Sub-200ms API response times
- ✅ **Portability:** Docker-based deployment anywhere
- ✅ **Documentation:** Comprehensive guides for all stakeholders

---

## Architecture Review Checklist

- [x] Technology stack selected and justified
- [x] Database schema designed and normalized
- [x] API endpoints specified with examples
- [x] Authentication and security measures defined
- [x] Containerization strategy documented
- [x] Deployment procedures detailed
- [x] Backup and disaster recovery planned
- [x] Monitoring and maintenance procedures outlined
- [x] Scalability path defined
- [x] Non-functional requirements addressed
- [x] Architecture Decision Records created
- [x] Team coordination mechanisms established

---

## Approval Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| System Architect | System Architecture Designer | ✓ | 2025-10-01 |
| Technical Lead | _Pending_ | | |
| Security Reviewer | _Pending_ | | |
| DevOps Lead | _Pending_ | | |
| Product Owner | _Pending_ | | |

---

**Architecture Version:** 1.0
**Status:** Complete - Ready for Development
**Next Review:** 2025-11-01

---

**Questions or clarifications?** Contact the architecture team or refer to detailed documentation in `/docs/architecture/`.
