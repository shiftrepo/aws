# Non-Functional Requirements Analysis
## Team Meeting Scheduler System

### Document Information
- **Date**: 2025-10-01
- **Version**: 1.0
- **Status**: Initial Analysis

---

## 1. PERFORMANCE REQUIREMENTS

### NFR-PERF-001: Response Time
**Priority**: High

- **Page Load Time**: < 2 seconds (initial page load)
- **API Response Time**: < 500ms (90th percentile)
- **Availability Calculation**: < 3 seconds (for 30 users)
- **Database Queries**: < 100ms (average)
- **UI Interactions**: < 100ms (perceived as instant)
- **Animation Frame Rate**: 60 FPS (smooth transitions)

**Measurement**:
- Use browser dev tools (Network tab)
- Server-side logging for API endpoints
- Performance.now() for client-side operations

---

### NFR-PERF-002: Scalability
**Priority**: Medium

- **Maximum Users**: 30 concurrent users
- **Maximum Availability Slots**: 500 per user per week
- **Database Size**: < 100MB (1 year operation)
- **Concurrent Requests**: 10 simultaneous requests
- **Browser Memory**: < 150MB per tab

**Load Profile**:
- Peak usage: Monday mornings (9:00-10:00)
- Average usage: 5-10 concurrent users
- Data growth: ~10KB per user per month

---

### NFR-PERF-003: Resource Utilization
**Priority**: Medium

- **CPU Usage**: < 50% during normal operations
- **Memory Usage**: < 512MB total (container)
- **Disk I/O**: < 10 operations/second
- **Network Bandwidth**: < 1Mbps per user

**Optimization Targets**:
- SQLite WAL mode for better concurrency
- Index on user_id, day_of_week for queries
- Client-side caching of user list
- Lazy loading of historical data

---

## 2. USABILITY REQUIREMENTS

### NFR-USE-001: User Interface
**Priority**: High

**Visual Design**:
- **Color Scheme**: Pastel colors (淡い色基調)
  - Primary: Soft blue (#A8D5E2)
  - Secondary: Mint green (#C9E4CA)
  - Accent: Coral pink (#FFB5A7)
  - Background: Off-white (#FDFCF9)
  - Text: Dark gray (#3A3A3A)
- **Typography**:
  - Sans-serif fonts (Noto Sans JP, Inter, Roboto)
  - Font sizes: 14-18px body, 24-32px headings
  - Line height: 1.6 for readability
- **Layout**:
  - Responsive grid system
  - Maximum content width: 1440px
  - Generous white space
  - Card-based components

**Animation Requirements**:
- **Micro-interactions**: 200-300ms duration
- **Page transitions**: 400ms fade/slide
- **Loading states**: Skeleton screens or spinners
- **Hover effects**: Subtle scale/shadow changes
- **Types**:
  - Button click: ripple effect
  - Form validation: shake on error
  - Success messages: slide in from top
  - Time slot selection: smooth highlight

---

### NFR-USE-002: Ease of Use
**Priority**: High

- **Learning Curve**: New user productive in < 5 minutes
- **Task Completion**:
  - Register account: < 30 seconds
  - Set weekly availability: < 2 minutes
  - Find common time: < 10 seconds
- **Error Prevention**:
  - Inline validation with helpful messages
  - Confirmation dialogs for destructive actions
  - Visual feedback for all interactions
- **Accessibility**:
  - WCAG 2.1 Level A minimum (AA target)
  - Keyboard navigation support
  - Screen reader friendly (aria-labels)
  - Sufficient color contrast (4.5:1 ratio)

---

### NFR-USE-003: User Experience
**Priority**: High

**Interaction Patterns**:
- Drag-and-drop for time slot selection
- Click to toggle individual slots
- Touch-friendly targets (≥44×44px)
- Immediate visual feedback
- Undo/redo functionality
- Auto-save with confirmation

**Responsive Design**:
- Desktop: 1920×1080 to 1280×720
- Tablet: 768×1024 (landscape/portrait)
- Mobile: 375×667 minimum (optional)

**Browser Support**:
- Chrome 90+ (primary)
- Firefox 88+ (primary)
- Safari 14+ (secondary)
- Edge 90+ (secondary)

---

## 3. SECURITY REQUIREMENTS

### NFR-SEC-001: Authentication & Authorization
**Priority**: Medium (内部簡易利用)

**Authentication**:
- HTTP Basic Authentication (RFC 7617)
- Credentials transmitted over HTTPS (recommended)
- Session timeout: 8 hours
- No "remember me" functionality
- Password storage: bcrypt hash (cost factor 10)

**Authorization**:
- All authenticated users have equal access
- No role-based access control (RBAC)
- Users can only edit own availability
- All users can view all availabilities

**Limitations (Acknowledged)**:
- No multi-factor authentication (MFA)
- No password complexity requirements
- No account lockout mechanism
- No audit logging
- No HTTPS enforcement (deployment choice)

---

### NFR-SEC-002: Data Protection
**Priority**: Low (internal use)

**Data at Rest**:
- SQLite database file permissions: 600 (owner read/write only)
- Passwords: bcrypt hashed (never plaintext)
- No encryption of availability data (not sensitive)

**Data in Transit**:
- HTTPS recommended but not enforced
- Basic Auth credentials base64 encoded (standard)

**Data Privacy**:
- No personal data beyond user ID
- No email/phone number collection
- No data sharing with external services
- No analytics tracking

**Backup & Recovery**:
- Database backup: manual copy of SQLite file
- Recovery: restore from backup file
- No automated backup (out of scope)

---

### NFR-SEC-003: Input Validation
**Priority**: High

**Server-Side Validation**:
- SQL injection prevention: parameterized queries
- XSS prevention: output encoding
- CSRF protection: same-origin policy
- Input sanitization: reject special characters in user_id
- Time format validation: HH:MM (00:00-23:59)

**Client-Side Validation**:
- Pre-submit validation for UX
- Cannot substitute server-side validation
- Immediate feedback on invalid input

---

## 4. RELIABILITY REQUIREMENTS

### NFR-REL-001: Availability
**Priority**: Medium

- **Uptime Target**: 95% during business hours (9:00-18:00)
- **Planned Downtime**: Weekends/holidays acceptable
- **Unplanned Downtime**: < 4 hours per month
- **Recovery Time Objective (RTO)**: < 1 hour
- **Recovery Point Objective (RPO)**: < 24 hours (daily backup)

**Failure Scenarios**:
- Database corruption: Restore from backup
- Container crash: Auto-restart via docker-compose
- Disk full: Alert at 80% capacity

---

### NFR-REL-002: Data Integrity
**Priority**: High

- **Database Transactions**: ACID compliance (SQLite default)
- **Referential Integrity**: Foreign key constraints enabled
- **Data Validation**: All inputs validated before persistence
- **Concurrent Access**: SQLite WAL mode for write concurrency
- **Error Handling**: Graceful degradation, no data loss

**Data Consistency Rules**:
- No orphaned availability records
- Time slots cannot overlap for same user/day
- Start time < end time enforced
- Day of week: 0-6 (Monday-Sunday)

---

### NFR-REL-003: Error Handling
**Priority**: Medium

**Client-Side**:
- User-friendly error messages (Japanese)
- No technical jargon in UI
- Actionable guidance ("Please enter a valid time")
- Graceful degradation (offline mode future consideration)

**Server-Side**:
- Structured logging (timestamp, level, message, context)
- Error codes for API responses
- 4xx for client errors, 5xx for server errors
- No sensitive data in error responses

**Error Scenarios**:
- Network timeout: Retry with exponential backoff
- Database locked: Retry up to 3 times
- Invalid input: Return 400 with validation details
- Server error: Return 500 with generic message

---

## 5. MAINTAINABILITY REQUIREMENTS

### NFR-MAIN-001: Code Quality
**Priority**: High (平易なプログラム言語)

**Code Standards**:
- **Readability**: Self-documenting code with clear naming
- **Simplicity**: Avoid over-engineering, keep it simple
- **Comments**: Japanese comments for complex logic
- **Structure**: Modular design, separation of concerns
- **File Size**: < 500 lines per file

**Language-Specific Guidelines**:
- **If Python**: PEP 8 style guide, type hints
- **If JavaScript**: ESLint standard config, JSDoc
- **If Ruby**: RuboCop, Ruby Style Guide

**Documentation**:
- README with setup instructions
- API documentation (inline or separate)
- Database schema diagram
- Deployment guide

---

### NFR-MAIN-002: Testability
**Priority**: Medium

**Test Coverage**:
- Unit tests: 60% coverage minimum
- Integration tests: Critical paths covered
- End-to-end tests: Happy path scenarios

**Test Types**:
- Unit: Business logic, data validation
- Integration: Database operations, API endpoints
- UI: Critical user flows (registration, availability input)
- Manual: Visual design, animations

**Test Environment**:
- Separate test database (SQLite in-memory)
- Mock data fixtures
- Automated test runner

---

### NFR-MAIN-003: Deployability
**Priority**: High

**Containerization**:
- Docker image < 500MB
- docker-compose.yml for single-command deployment
- Environment variables for configuration
- Volume mounts for database persistence

**Deployment Steps**:
1. `docker-compose up -d` (starts all services)
2. Navigate to http://localhost:PORT
3. Register first user
4. System ready

**Configuration**:
- Port: configurable via env var (default 8080)
- Database path: configurable (default ./data/scheduler.db)
- Log level: configurable (default INFO)

---

### NFR-MAIN-004: Monitoring
**Priority**: Low

**Logging**:
- Application logs: stdout (captured by Docker)
- Log rotation: handled by Docker or external tool
- Log levels: DEBUG, INFO, WARN, ERROR
- Structured format: timestamp, level, message

**Health Checks**:
- Endpoint: `/health` (returns 200 OK)
- Checks: Database connection, disk space
- Frequency: Every 60 seconds

**Metrics (Optional)**:
- Request count by endpoint
- Response time percentiles
- Active user sessions
- Database size

---

## 6. PORTABILITY REQUIREMENTS

### NFR-PORT-001: Platform Independence
**Priority**: High

**Operating System**:
- Linux (primary): Ubuntu 20.04+, CentOS 8+
- macOS (development): 11+
- Windows (development): 10+ with WSL2

**Docker Support**:
- Docker Engine: 20.10+
- docker-compose: 1.29+
- No Kubernetes required

**Browser Compatibility**:
- Cross-platform: Chrome, Firefox, Safari, Edge
- No IE11 support (deprecated)

---

### NFR-PORT-002: Data Portability
**Priority**: Low

**Export Formats**:
- Database: SQLite file (standard format)
- Availability: CSV export (optional)
- User list: JSON export (optional)

**Import Capabilities**:
- Bulk user import from CSV (optional)
- Database migration from backup

---

## 7. LOCALIZATION REQUIREMENTS

### NFR-LOC-001: Language Support
**Priority**: High

**Primary Language**: Japanese (日本語)
- UI labels and messages in Japanese
- Error messages in Japanese
- Documentation in Japanese

**Secondary Language**: English (optional)
- Code comments can be English or Japanese
- Technical documentation in English acceptable
- No UI translation required (single-language system)

**Date/Time Format**:
- Time: 24-hour format (HH:MM)
- Date: YYYY-MM-DD or YYYY年MM月DD日
- Day of week: 月火水木金土日

---

## 8. COMPLIANCE REQUIREMENTS

### NFR-COMP-001: Standards Compliance
**Priority**: Medium

**Web Standards**:
- HTML5 semantic markup
- CSS3 for styling
- ECMAScript 2020+ for JavaScript
- RESTful API design principles

**Data Standards**:
- ISO 8601 for date/time storage
- UTF-8 encoding for all text
- JSON for API responses

**Accessibility**:
- WCAG 2.1 Level A (minimum)
- Keyboard navigation
- Screen reader support (basic)

---

### NFR-COMP-002: Legal & Regulatory
**Priority**: Low (internal use)

**Privacy**:
- No personal data collection beyond user_id
- No cookies except session management
- No third-party tracking

**License**:
- Open-source components: permissive licenses (MIT, Apache)
- No GPL dependencies (optional requirement)

---

## 9. OPERATIONAL REQUIREMENTS

### NFR-OPS-001: Installation
**Priority**: High

**Setup Time**: < 10 minutes from zero to running system
**Prerequisites**:
- Docker and docker-compose installed
- 1GB free disk space
- Port 8080 (or configurable) available

**Installation Steps**:
```bash
git clone <repository>
cd team-scheduler
docker-compose up -d
# System ready at http://localhost:8080
```

---

### NFR-OPS-002: Backup & Recovery
**Priority**: Medium

**Backup Strategy**:
- Frequency: Daily (manual or cron job)
- Method: Copy SQLite file
- Retention: 7 days minimum
- Location: External to container

**Recovery Process**:
1. Stop application: `docker-compose down`
2. Replace database file
3. Start application: `docker-compose up -d`
4. Verify data integrity

---

### NFR-OPS-003: Upgrade Path
**Priority**: Low

**Version Updates**:
- Docker image versioning: semantic versioning
- Database migrations: included in application startup
- Backward compatibility: 1 major version

**Upgrade Process**:
1. Backup database
2. Pull new image: `docker-compose pull`
3. Restart services: `docker-compose up -d`
4. Run migrations (automatic)

---

## 10. NON-FUNCTIONAL REQUIREMENTS SUMMARY

### Critical (Must Have)
1. ✅ Performance: < 2s page load, < 500ms API response
2. ✅ Usability: Pastel colors, smooth animations, intuitive UI
3. ✅ Security: Basic Auth, password hashing, input validation
4. ✅ Maintainability: Simple code, well-documented
5. ✅ Deployability: docker-compose single-command deploy

### Important (Should Have)
6. ✅ Reliability: 95% uptime, data integrity
7. ✅ Accessibility: WCAG 2.1 Level A, keyboard nav
8. ✅ Browser Support: Modern browsers (last 2 versions)
9. ✅ Responsive: Desktop + tablet support

### Nice-to-Have (Could Have)
10. ⭕ Monitoring: Health checks, metrics
11. ⭕ Localization: English UI option
12. ⭕ Export: CSV/JSON data export

---

## 11. QUALITY ATTRIBUTES PRIORITY

| Quality Attribute | Priority | Rationale |
|------------------|----------|-----------|
| **Usability** | ⭐⭐⭐⭐⭐ | Explicitly required: pop/friendly UI, animations |
| **Performance** | ⭐⭐⭐⭐ | Small scale (30 users) but must feel responsive |
| **Maintainability** | ⭐⭐⭐⭐ | "Easy language" requirement, long-term use |
| **Deployability** | ⭐⭐⭐⭐ | docker-compose requirement, simple setup |
| **Security** | ⭐⭐ | "Minimal security" for internal use |
| **Scalability** | ⭐⭐ | Fixed max 30 users, no growth expected |
| **Availability** | ⭐⭐⭐ | Internal tool, some downtime acceptable |

---

## 12. CONSTRAINTS ANALYSIS

### Technical Constraints
| Constraint | Impact | Mitigation |
|-----------|--------|------------|
| SQLite (single file) | Limited concurrency | Use WAL mode, accept limitations |
| Basic Auth | Weak security | Deploy on internal network only |
| No SSL enforcement | Credentials in clear | HTTPS recommended but optional |
| Max 30 users | Scalability limit | Clear in documentation, no issue for use case |
| Single server | No high availability | Acceptable for internal tool |

### Organizational Constraints
| Constraint | Impact | Solution |
|-----------|--------|----------|
| Internal use only | No internet exposure needed | LAN deployment |
| Small team | Limited support requirements | Simple, self-service design |
| Minimal security | Reduced development effort | Focus on usability over hardening |

---

## ACCEPTANCE CRITERIA (NON-FUNCTIONAL)

### Performance Acceptance
- [ ] Dashboard loads in < 2 seconds with 30 users
- [ ] Availability calculation completes in < 3 seconds
- [ ] All animations run at 60 FPS
- [ ] Database operations < 100ms average

### Usability Acceptance
- [ ] New user completes registration in < 30 seconds (user test)
- [ ] User can set weekly availability in < 2 minutes (user test)
- [ ] 8/10 users rate UI as "pop/friendly" (survey)
- [ ] Color scheme uses pastel colors (visual inspection)
- [ ] All interactions have smooth animations (visual inspection)

### Security Acceptance
- [ ] Basic Auth protects all endpoints
- [ ] Passwords stored as bcrypt hashes
- [ ] No SQL injection vulnerabilities (security scan)
- [ ] No XSS vulnerabilities (security scan)

### Reliability Acceptance
- [ ] System runs continuously for 7 days without restart
- [ ] Database maintains integrity after 1000 operations
- [ ] Graceful error messages for all failure scenarios

### Deployment Acceptance
- [ ] Full deployment with `docker-compose up -d` in < 2 minutes
- [ ] System accessible immediately after deployment
- [ ] Database persists after container restart
- [ ] Configuration via environment variables works

---

**Document Prepared By**: Requirements Analysis Specialist
**Review Status**: Pending Stakeholder Approval
**Last Updated**: 2025-10-01
