# System Architecture - Team Schedule Management System

## Architecture Decision Records (ADR)

### ADR-001: Technology Stack Selection
**Decision:** Node.js/Express backend with React frontend
**Rationale:**
- Simple, widely-adopted stack suitable for small teams
- Excellent package ecosystem for rapid development
- Strong TypeScript support for type safety
- Easy Docker containerization
- Good performance for 30 concurrent users

**Alternatives Considered:**
- Python/Flask: Good but slower development for real-time features
- Go: Overkill for small team size and complexity

### ADR-002: Database Choice
**Decision:** SQLite with better-sqlite3 driver
**Rationale:**
- Zero configuration, file-based database perfect for <30 users
- ACID compliance for data integrity
- No separate database server needed
- Easy backup (single file)
- Sufficient performance for use case

**Constraints:**
- Max 30 users, primarily read operations
- Low concurrent write operations

### ADR-003: Authentication Strategy
**Decision:** JWT-based authentication with HTTP-only cookies
**Rationale:**
- Stateless authentication scales well
- HTTP-only cookies prevent XSS attacks
- Simple to implement and maintain
- Suitable for session management in small teams

### ADR-004: Frontend Framework
**Decision:** React with Vite bundler
**Rationale:**
- Component-based architecture for maintainability
- Vite provides fast development experience
- Large ecosystem for UI components and animations
- Easy to create responsive, animated interfaces

### ADR-005: Containerization Strategy
**Decision:** Multi-container Docker Compose setup
**Rationale:**
- Separate containers for frontend, backend, and reverse proxy
- Easy deployment and scaling
- Consistent development and production environments
- Simple orchestration for small-scale deployment

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │         React SPA (Port 3000)                      │     │
│  │  - Schedule Calendar View                          │     │
│  │  - Team Member Management                          │     │
│  │  - Shift Assignment Interface                      │     │
│  │  - Notifications & Real-time Updates               │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    REVERSE PROXY LAYER                       │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Nginx (Port 80/443)                        │     │
│  │  - SSL Termination                                 │     │
│  │  - Static Asset Serving                            │     │
│  │  - API Request Routing                             │     │
│  │  - Load Balancing (future)                         │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │      Node.js/Express API (Port 3001)               │     │
│  │                                                     │     │
│  │  ┌─────────────────────────────────────────┐      │     │
│  │  │      Authentication Middleware          │      │     │
│  │  │  - JWT Validation                       │      │     │
│  │  │  - Role-based Access Control            │      │     │
│  │  └─────────────────────────────────────────┘      │     │
│  │                                                     │     │
│  │  ┌─────────────────────────────────────────┐      │     │
│  │  │         API Routes                      │      │     │
│  │  │  /api/auth  - Authentication            │      │     │
│  │  │  /api/users - User Management           │      │     │
│  │  │  /api/shifts - Shift Operations         │      │     │
│  │  │  /api/schedule - Schedule Views         │      │     │
│  │  │  /api/notifications - Alerts            │      │     │
│  │  └─────────────────────────────────────────┘      │     │
│  │                                                     │     │
│  │  ┌─────────────────────────────────────────┐      │     │
│  │  │      Business Logic Layer               │      │     │
│  │  │  - Schedule Generator                   │      │     │
│  │  │  - Conflict Detector                    │      │     │
│  │  │  - Notification Service                 │      │     │
│  │  │  - Report Generator                     │      │     │
│  │  └─────────────────────────────────────────┘      │     │
│  │                                                     │     │
│  │  ┌─────────────────────────────────────────┐      │     │
│  │  │      Data Access Layer                  │      │     │
│  │  │  - Repository Pattern                   │      │     │
│  │  │  - Query Builders                       │      │     │
│  │  │  - Transaction Management               │      │     │
│  │  └─────────────────────────────────────────┘      │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQL
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │         SQLite Database                            │     │
│  │  - File: /data/schedule.db                         │     │
│  │  - Tables: users, shifts, schedule, notifications  │     │
│  │  - Indexes for performance                         │     │
│  │  - Foreign key constraints enabled                 │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Backend Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Express Application                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Middleware Stack                        │   │
│  │  1. CORS Handler                                     │   │
│  │  2. Body Parser (JSON)                               │   │
│  │  3. Cookie Parser                                    │   │
│  │  4. Request Logger                                   │   │
│  │  5. Error Handler                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Controller Layer                        │   │
│  │  - AuthController: Login, Logout, Register           │   │
│  │  - UserController: CRUD operations                   │   │
│  │  - ShiftController: Shift management                 │   │
│  │  - ScheduleController: Schedule generation           │   │
│  │  - NotificationController: Alerts                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Service Layer                           │   │
│  │  - AuthService: JWT operations                       │   │
│  │  - UserService: Business logic                       │   │
│  │  - ShiftService: Conflict detection                  │   │
│  │  - ScheduleService: Auto-generation                  │   │
│  │  - NotificationService: Event handling               │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Repository Layer                        │   │
│  │  - UserRepository: DB access                         │   │
│  │  - ShiftRepository: Query building                   │   │
│  │  - ScheduleRepository: Optimized queries             │   │
│  │  - NotificationRepository: Event storage             │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Database Layer                          │   │
│  │  - Connection Pool Management                        │   │
│  │  - Transaction Handling                              │   │
│  │  - Migration System                                  │   │
│  │  - Seed Data Management                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Frontend Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Application                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              App Shell (Layout)                      │   │
│  │  - Header with Navigation                            │   │
│  │  - Sidebar Menu                                      │   │
│  │  - Main Content Area                                 │   │
│  │  - Footer                                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Page Components                         │   │
│  │  - LoginPage                                         │   │
│  │  - DashboardPage                                     │   │
│  │  - SchedulePage                                      │   │
│  │  - TeamMembersPage                                   │   │
│  │  - ShiftManagementPage                               │   │
│  │  - ProfilePage                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Feature Components                         │   │
│  │  - CalendarView: Weekly/Monthly calendar            │   │
│  │  - ShiftCard: Individual shift display              │   │
│  │  - TeamMemberList: User directory                   │   │
│  │  - ShiftAssignmentModal: Drag-drop interface        │   │
│  │  - NotificationBell: Alert center                   │   │
│  │  - FilterBar: Schedule filtering                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Shared Components                       │   │
│  │  - Button, Input, Select (Form controls)            │   │
│  │  - Modal, Toast, Tooltip (Overlays)                 │   │
│  │  - Card, Badge, Avatar (Display)                    │   │
│  │  - LoadingSpinner, ErrorBoundary (States)           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              State Management                        │   │
│  │  - React Context API                                │   │
│  │  - AuthContext: User session                        │   │
│  │  - ScheduleContext: Schedule state                  │   │
│  │  - NotificationContext: Alert state                 │   │
│  │  - ThemeContext: UI preferences                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Services/Hooks                          │   │
│  │  - useAuth: Authentication hook                     │   │
│  │  - useSchedule: Schedule operations                 │   │
│  │  - useNotifications: Alert management               │   │
│  │  - apiClient: HTTP request handling                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### Authentication Flow
```
User Input → LoginForm → AuthService → API (/api/auth/login)
                                              ↓
                                    Validate Credentials
                                              ↓
                                      Generate JWT Token
                                              ↓
                                Set HTTP-only Cookie ← Response
                                              ↓
                                    Redirect to Dashboard
```

### Schedule Update Flow
```
User Action → ShiftAssignment → ScheduleContext → API (/api/shifts/assign)
                                                          ↓
                                                  Validate Shift
                                                          ↓
                                                  Check Conflicts
                                                          ↓
                                                  Update Database
                                                          ↓
                                        Trigger Notifications
                                                          ↓
                                        Return Updated Schedule ← Response
                                                          ↓
                                                Update Local State
                                                          ↓
                                                Re-render Calendar
```

## Security Architecture

### Security Layers

1. **Network Layer**
   - HTTPS enforcement via Nginx
   - Rate limiting on API endpoints
   - CORS configuration for trusted origins

2. **Authentication Layer**
   - Bcrypt password hashing (cost factor: 12)
   - JWT tokens with 24-hour expiration
   - HTTP-only, Secure, SameSite cookies
   - Refresh token rotation

3. **Authorization Layer**
   - Role-based access control (Admin, Manager, Employee)
   - Resource-level permissions
   - Middleware-based route protection

4. **Application Layer**
   - Input validation with express-validator
   - SQL injection prevention via parameterized queries
   - XSS prevention via content sanitization
   - CSRF protection via token validation

5. **Data Layer**
   - Database file permissions (600)
   - Encrypted backups
   - Audit logging for sensitive operations

## Deployment Architecture

### Development Environment
```
localhost:3000 (React Dev Server)
       ↓
localhost:3001 (Express API)
       ↓
./data/schedule-dev.db (SQLite)
```

### Production Environment
```
External Port 80/443 (Nginx)
       ↓
Internal Port 3000 (React Static Files)
       ↓
Internal Port 3001 (Express API)
       ↓
/data/schedule.db (Persistent Volume)
```

## Performance Considerations

### Optimization Strategies

1. **Database Optimization**
   - Indexed columns: user_id, shift_date, status
   - Query result caching for read-heavy operations
   - Connection pooling (max 10 connections)
   - Regular VACUUM operations for file size

2. **API Optimization**
   - Response compression (gzip)
   - Pagination for list endpoints (max 50 items)
   - ETags for conditional requests
   - Request coalescing for duplicate queries

3. **Frontend Optimization**
   - Code splitting by route
   - Lazy loading for non-critical components
   - Memoization for expensive computations
   - Virtual scrolling for long lists
   - Asset optimization (minification, compression)

4. **Caching Strategy**
   - Browser cache for static assets (1 year)
   - API response caching (5-60 minutes based on volatility)
   - Memory cache for frequently accessed data

## Scalability Path

### Current Capacity
- 30 concurrent users
- Single server deployment
- SQLite database

### Future Scaling Options (if needed)

1. **Phase 1: Vertical Scaling**
   - Increase server resources
   - Add Redis for caching
   - Optimize database queries

2. **Phase 2: Database Migration**
   - Migrate to PostgreSQL
   - Add read replicas
   - Implement connection pooling

3. **Phase 3: Horizontal Scaling**
   - Multiple API server instances
   - Load balancer (Nginx/HAProxy)
   - Session store (Redis)
   - CDN for static assets

## Monitoring and Observability

### Logging Strategy
- Application logs: Winston logger
- Access logs: Nginx format
- Error tracking: Console + file rotation
- Log levels: DEBUG, INFO, WARN, ERROR

### Metrics to Track
- API response times (p50, p95, p99)
- Error rates by endpoint
- Database query performance
- Active user sessions
- Shift assignment success rate

### Health Checks
- `/health` endpoint for container orchestration
- Database connectivity check
- Disk space monitoring
- Memory usage tracking

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend Framework | React | 18.x | UI components |
| Build Tool | Vite | 5.x | Fast development |
| UI Library | TailwindCSS | 3.x | Styling system |
| Animation | Framer Motion | 11.x | Smooth transitions |
| Backend Framework | Express | 4.x | API server |
| Runtime | Node.js | 20.x LTS | Server execution |
| Database | SQLite | 3.x | Data persistence |
| Database Driver | better-sqlite3 | 9.x | Node.js integration |
| Authentication | jsonwebtoken | 9.x | JWT handling |
| Password Hashing | bcrypt | 5.x | Secure passwords |
| Validation | express-validator | 7.x | Input validation |
| Web Server | Nginx | 1.25 | Reverse proxy |
| Containerization | Docker | 24.x | Deployment |
| Orchestration | Docker Compose | 2.x | Multi-container |

## Next Steps

1. Review and approve architectural decisions
2. Proceed with database schema design
3. Define API endpoint specifications
4. Create UI/UX wireframes
5. Implement Docker configuration
6. Begin development sprints
