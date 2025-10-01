# Team Schedule Management System - Architecture Summary

## Executive Summary

This document provides a comprehensive overview of the system architecture for the Team Schedule Management System, designed for small teams (<30 users) with a focus on simplicity, maintainability, and modern user experience.

## Technology Stack

### Backend
- **Runtime:** Node.js 20 LTS
- **Framework:** Express.js 4.x
- **Database:** SQLite 3.x with better-sqlite3 driver
- **Authentication:** JWT with HTTP-only cookies
- **Password Security:** bcrypt (cost factor 12)
- **Validation:** express-validator 7.x

### Frontend
- **Framework:** React 18.x
- **Build Tool:** Vite 5.x
- **Styling:** TailwindCSS 3.x (Light, poppy color scheme)
- **Animation:** Framer Motion 11.x
- **State Management:** React Context API
- **Routing:** React Router 6.x

### Infrastructure
- **Containerization:** Docker 24.x
- **Orchestration:** Docker Compose 2.x
- **Web Server:** Nginx 1.25 (Reverse proxy, SSL termination)
- **Deployment:** Single-server architecture

## Architecture Decisions (ADRs)

### ADR-001: Node.js/Express Backend
**Decision:** Use Node.js with Express framework for backend API
**Rationale:**
- Simple, widely-adopted stack suitable for small teams
- Excellent package ecosystem for rapid development
- Strong TypeScript support for type safety
- Easy Docker containerization
- Good performance for 30 concurrent users

### ADR-002: SQLite Database
**Decision:** SQLite with better-sqlite3 driver
**Rationale:**
- Zero configuration, file-based database perfect for <30 users
- ACID compliance for data integrity
- No separate database server needed
- Easy backup (single file)
- Sufficient performance for use case

**Constraints:** Max 30 users, primarily read operations, low concurrent writes

### ADR-003: JWT with HTTP-only Cookies
**Decision:** JWT-based authentication with HTTP-only cookies
**Rationale:**
- Stateless authentication scales well
- HTTP-only cookies prevent XSS attacks
- Simple to implement and maintain
- Suitable for session management in small teams

### ADR-004: React with Vite
**Decision:** React SPA with Vite bundler
**Rationale:**
- Component-based architecture for maintainability
- Vite provides fast development experience
- Large ecosystem for UI components and animations
- Easy to create responsive, animated interfaces

### ADR-005: Docker Compose Deployment
**Decision:** Multi-container Docker Compose setup
**Rationale:**
- Separate containers for frontend, backend, and reverse proxy
- Easy deployment and scaling
- Consistent development and production environments
- Simple orchestration for small-scale deployment

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                         │
│               React SPA (Port 3000)                     │
└─────────────────────────────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────┐
│               REVERSE PROXY LAYER                       │
│               Nginx (Port 80/443)                       │
│         - SSL Termination                               │
│         - Static Asset Serving                          │
│         - API Request Routing                           │
└─────────────────────────────────────────────────────────┘
                        │ HTTP
                        ▼
┌─────────────────────────────────────────────────────────┐
│              APPLICATION LAYER                          │
│          Node.js/Express API (Port 3001)                │
│         - Authentication Middleware                     │
│         - API Routes                                    │
│         - Business Logic Layer                          │
│         - Data Access Layer                             │
└─────────────────────────────────────────────────────────┘
                        │ SQL
                        ▼
┌─────────────────────────────────────────────────────────┐
│                    DATA LAYER                           │
│              SQLite Database                            │
│         File: /data/schedule.db                         │
└─────────────────────────────────────────────────────────┘
```

## Database Schema Overview

### Core Tables

1. **users** - User accounts and authentication
   - Bcrypt password hashing
   - Role-based permissions
   - Soft delete support
   - Last login tracking

2. **roles** - User roles and permissions
   - Predefined roles: Admin, Manager, Employee
   - JSON permissions array
   - Flexible permission system

3. **shift_templates** - Pre-defined shift types
   - Morning, Day, Evening, Night shifts
   - Color-coded for UI display
   - Duration calculation

4. **shifts** - Individual shift assignments
   - User assignment
   - Date and time range
   - Status tracking (scheduled, completed, cancelled)
   - Conflict prevention via constraints

5. **shift_swaps** - Shift swap requests
   - Requester and target users
   - Approval workflow
   - Status tracking

6. **time_off** - Employee time-off requests
   - Date ranges
   - Types (vacation, sick, personal)
   - Approval workflow

7. **notifications** - System notifications
   - Real-time alerts
   - Read/unread status
   - Priority levels

8. **audit_logs** - Comprehensive audit trail
   - All user actions
   - Old/new value tracking
   - IP address and user agent logging

9. **settings** - System configuration
   - Key-value pairs
   - Type validation
   - Update tracking

### Key Features
- Foreign key constraints enabled
- Automatic timestamp updates via triggers
- Conflict detection via unique constraints
- Indexed columns for performance
- Automated notification generation

## API Architecture

### Endpoint Categories

1. **Authentication** (`/api/auth`)
   - POST /register - Create new user (Admin only)
   - POST /login - User authentication
   - POST /logout - Session termination
   - GET /me - Current user info
   - POST /refresh - Token refresh

2. **User Management** (`/api/users`)
   - GET / - List users (paginated, filterable)
   - GET /:id - User details
   - PATCH /:id - Update user
   - DELETE /:id - Soft delete user

3. **Shift Management** (`/api/shifts`)
   - GET / - List shifts (date range, filters)
   - POST / - Create shift
   - PATCH /:id - Update shift
   - DELETE /:id - Delete shift
   - POST /bulk - Batch create shifts

4. **Schedule** (`/api/schedule`)
   - GET / - Get schedule view
   - POST /generate - Auto-generate schedule
   - GET /conflicts - Check conflicts

5. **Shift Swaps** (`/api/shifts/swaps`)
   - GET / - List swap requests
   - POST / - Create swap request
   - PATCH /:id - Approve/reject swap

6. **Time-Off** (`/api/timeoff`)
   - GET / - List time-off requests
   - POST / - Create request
   - PATCH /:id - Approve/reject request

7. **Notifications** (`/api/notifications`)
   - GET / - List notifications
   - PATCH /:id/read - Mark as read
   - POST /read-all - Mark all as read

### API Features
- RESTful design
- Consistent JSON response format
- Pagination support (default 50 items)
- Comprehensive error codes
- Rate limiting
- Request validation
- CORS configuration

## Frontend Architecture

### Component Hierarchy

```
App
├── Providers (Context)
│   ├── AuthProvider
│   ├── ScheduleProvider
│   ├── NotificationProvider
│   └── ThemeProvider
│
├── Layout
│   ├── AppShell
│   │   ├── Header (Navigation, UserMenu, NotificationBell)
│   │   ├── Sidebar (Optional)
│   │   └── MainContent
│   └── AuthLayout (Login/Register)
│
├── Pages
│   ├── LoginPage
│   ├── DashboardPage
│   ├── SchedulePage
│   ├── TeamMembersPage
│   ├── ShiftManagementPage
│   ├── TimeOffPage
│   └── ProfilePage
│
├── Features (Domain-specific)
│   ├── Schedule (Calendar, ShiftCard, DragDrop)
│   ├── Team (MemberList, MemberCard)
│   ├── Shifts (Templates, Swaps)
│   └── TimeOff (Calendar, RequestForm)
│
└── Shared Components (UI Kit)
    ├── Button, Input, Select, DatePicker
    ├── Card, Badge, Avatar, Modal
    └── LoadingSpinner, ErrorBoundary, Toast
```

### State Management

**React Context API** for global state:
- **AuthContext:** User session, permissions, login/logout
- **ScheduleContext:** Shifts, filters, CRUD operations
- **NotificationContext:** Alerts, unread count, real-time updates
- **ThemeContext:** UI preferences, color scheme

### Design System

**Color Scheme (Light, Poppy):**
- Primary: Blue (#3B82F6) - Trust, Professional
- Secondary: Purple (#A855F7) - Creative, Modern
- Accents: Orange, Pink, Green, Yellow, Teal
- Shift Colors:
  - Morning: Yellow (#FBBF24)
  - Day: Blue (#3B82F6)
  - Evening: Purple (#A855F7)
  - Night: Dark Gray (#374151)
  - Split: Green (#10B981)

**Typography:**
- Font: Inter (sans-serif), JetBrains Mono (monospace)
- Sizes: xs (12px) → 5xl (48px)
- Weights: Light (300) → Bold (700)

**Spacing:** 4px base unit (0.25rem → 5rem)

**Animations (Framer Motion):**
- Page transitions: Fade + slide (300ms)
- Card hover: Scale + shadow (200ms)
- List stagger: 100ms delay per item
- Modal: Slide down from top

### Responsive Design

**Mobile-First Approach:**
- Mobile: < 640px (single column, day view)
- Tablet: 640px - 1024px (week view)
- Desktop: > 1024px (month view, full features)

## Authentication Flow

### Login Process

1. User submits credentials (email, password)
2. Backend validates email existence
3. Bcrypt verifies password hash
4. JWT token generated (24h expiration)
5. Token stored in HTTP-only cookie
6. User data returned (excluding password)
7. Frontend stores user in AuthContext
8. Redirect to dashboard

### Security Features

- **Password:** Bcrypt hash (cost 12), 8+ chars, complexity requirements
- **JWT:** HTTP-only, Secure, SameSite=strict cookies
- **Session:** 24h expiration, refresh mechanism
- **API:** Rate limiting, input validation, CORS
- **Audit:** All auth events logged with IP/user-agent

## Docker Configuration

### Container Architecture

```
┌─────────────────────────────────────────┐
│   nginx (Port 80/443)                   │
│   - SSL Termination                     │
│   - Static Files                        │
│   - Reverse Proxy                       │
└─────────────────────────────────────────┘
            │            │
    ┌───────┘            └───────┐
    ▼                            ▼
┌──────────────┐        ┌──────────────┐
│  frontend    │        │   backend    │
│  (React)     │        │  (Express)   │
│  Port: 3000  │        │  Port: 3001  │
└──────────────┘        └──────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │  Volume:     │
                        │  db-data     │
                        │  (SQLite)    │
                        └──────────────┘
```

### Services

1. **nginx** - Reverse proxy and static file server
2. **backend** - Express API server
3. **frontend-dev** - Vite dev server (development only)

### Volumes

- **db-data:** SQLite database persistence
- **backend-logs:** Application logs
- **nginx-logs:** Access and error logs

### Networks

- **app-network:** Bridge network for inter-container communication

## Security Architecture

### Defense Layers

1. **Network:** HTTPS, rate limiting, CORS
2. **Authentication:** Bcrypt, JWT, HTTP-only cookies
3. **Authorization:** Role-based access control (RBAC)
4. **Application:** Input validation, SQL injection prevention, XSS protection
5. **Data:** File permissions, encrypted backups, audit logging

### Permission System

**Roles:**
- **Admin:** Full access (`*` permission)
- **Manager:** Schedule management, reporting
- **Employee:** View schedule, request changes

**Permissions:**
- `schedule:read` / `schedule:write`
- `shifts:assign` / `shifts:swap`
- `users:read` / `users:write`
- `reports:read`
- `timeoff:request`

## Performance Optimization

### Database
- Indexed foreign keys and filter columns
- Prepared statements for caching
- Connection pooling (max 10)
- Regular VACUUM operations

### API
- Response compression (gzip)
- Pagination (max 50 items)
- ETags for conditional requests
- Request coalescing

### Frontend
- Code splitting by route
- Lazy loading components
- Memoization (React.memo, useMemo)
- Virtual scrolling for long lists
- Asset optimization

### Caching
- Browser cache: 1 year for static assets
- API cache: 5-60 minutes by volatility
- Memory cache: Frequently accessed data

## Deployment Workflow

### Development

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production

```bash
docker-compose build --no-cache
docker-compose up -d
docker-compose exec backend npm run migrate
```

### Backup Strategy

- **Automated:** Daily backups at 2 AM
- **Retention:** 7 daily, 4 weekly, 12 monthly
- **Method:** SQLite .backup command
- **Verification:** PRAGMA integrity_check

## Monitoring

### Health Checks

- `/health` endpoint for all services
- Database connectivity verification
- Memory usage tracking
- Disk space monitoring

### Logging

- **Application:** Winston logger (DEBUG, INFO, WARN, ERROR)
- **Access:** Nginx combined format
- **Audit:** All auth and CRUD operations

### Metrics

- API response times (p50, p95, p99)
- Error rates by endpoint
- Database query performance
- Active user sessions

## Scalability Path

### Current: Single Server (Phase 0)
- 30 users
- SQLite database
- Single container instance

### Future Scaling Options

**Phase 1: Vertical Scaling**
- Increase server resources
- Add Redis for caching
- Optimize queries

**Phase 2: Database Migration**
- Migrate to PostgreSQL
- Read replicas
- Connection pooling

**Phase 3: Horizontal Scaling**
- Multiple API instances
- Load balancer
- Session store (Redis)
- CDN for static assets

## File Locations

### Architecture Documentation
- **System Overview:** `/root/aws.git/container/claudecode/scheWEB/docs/architecture/SYSTEM_ARCHITECTURE.md`
- **Database Schema:** `/root/aws.git/container/claudecode/scheWEB/docs/database/DATABASE_SCHEMA.md`
- **API Specification:** `/root/aws.git/container/claudecode/scheWEB/docs/api/API_SPECIFICATION.md`
- **Frontend Architecture:** `/root/aws.git/container/claudecode/scheWEB/docs/architecture/FRONTEND_ARCHITECTURE.md`
- **Docker Configuration:** `/root/aws.git/container/claudecode/scheWEB/docs/architecture/DOCKER_CONFIGURATION.md`
- **UI/UX Design:** `/root/aws.git/container/claudecode/scheWEB/docs/architecture/UI_UX_DESIGN.md`
- **Authentication Flow:** `/root/aws.git/container/claudecode/scheWEB/docs/architecture/AUTHENTICATION_FLOW.md`

### Memory Keys (Swarm Coordination)
- `architecture/system-overview`
- `architecture/database-schema`
- `architecture/api-endpoints`
- `architecture/frontend-components`
- `architecture/docker-deployment`
- `architecture/ui-design`
- `architecture/authentication`

## Next Steps

1. **Review & Approval:** Stakeholder review of architectural decisions
2. **Environment Setup:** Initialize project structure, install dependencies
3. **Database Implementation:** Create migration scripts, seed data
4. **Backend Development:** Implement API endpoints, authentication
5. **Frontend Development:** Build UI components, integrate API
6. **Testing:** Unit tests, integration tests, E2E tests
7. **Docker Setup:** Create Dockerfiles, compose configuration
8. **Deployment:** Set up production environment, CI/CD pipeline

## Quick Reference

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run migrations
docker-compose exec backend npm run migrate

# Run tests
docker-compose exec backend npm test
docker-compose exec frontend npm test

# View logs
docker-compose logs -f backend

# Database backup
docker-compose exec backend npm run backup
```

### Production Commands

```bash
# Deploy
docker-compose up -d

# Health check
curl http://localhost/health

# Database backup
docker-compose exec backend sqlite3 /data/schedule.db ".backup /data/backup.db"

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend
```

## Contact & Support

For questions about this architecture:
- Review detailed documentation in `/docs` directory
- Check swarm memory keys for coordination data
- Consult with other agents via hooks protocol

---

**Architecture Version:** 1.0.0
**Last Updated:** October 1, 2025
**Status:** Design Complete, Ready for Implementation
