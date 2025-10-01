# Technical Constraints & Assumptions Analysis
## Team Meeting Scheduler System

### Document Information
- **Date**: 2025-10-01
- **Version**: 1.0
- **Status**: Initial Analysis

---

## 1. TECHNOLOGY STACK CONSTRAINTS

### Requirement 8: "平易なプログラム言語 + docker-compose"

#### Interpretation: "Easy/Simple Programming Language"

**Recommended Technology Stacks (3 Options)**

---

### 🏆 **OPTION 1: Python + Flask (RECOMMENDED)**

#### Rationale
- ✅ Python is considered "easy to read and write"
- ✅ Flask is minimalist (microframework)
- ✅ Large ecosystem for web development
- ✅ Excellent SQLite support (built-in)
- ✅ Strong typing available (type hints)
- ✅ Great for rapid development

#### Technology Components
```yaml
Backend:
  Language: Python 3.11+
  Web Framework: Flask 3.0+
  ORM: SQLAlchemy 2.0+ (optional) or raw SQL
  Authentication: Flask-HTTPAuth (Basic Auth)
  Database: SQLite3 (built-in)

Frontend:
  Framework: Vanilla JavaScript + Tailwind CSS
  OR: Vue.js 3 (progressive framework)
  Animations: CSS transitions + anime.js
  Date/Time: date-fns or Day.js

Infrastructure:
  Containerization: Docker + docker-compose
  Web Server: Gunicorn (production) or Flask dev server
  Reverse Proxy: Nginx (optional, for static files)
```

#### File Structure
```
project/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── routes.py          # API endpoints
│   ├── auth.py            # Basic authentication
│   ├── scheduler.py       # Business logic
│   └── static/
│       ├── css/
│       ├── js/
│       └── index.html
├── tests/
│   ├── test_models.py
│   ├── test_routes.py
│   └── test_scheduler.py
└── data/
    └── scheduler.db       # SQLite database (volume mount)
```

#### Sample docker-compose.yml
```yaml
version: '3.8'

services:
  scheduler:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
      - DATABASE_PATH=/app/data/scheduler.db
      - SECRET_KEY=${SECRET_KEY:-default-secret-key}
    restart: unless-stopped
```

#### Complexity Assessment
- **Learning Curve**: Low (1-2 weeks for new developer)
- **Maintenance**: Easy (clear code structure)
- **Debugging**: Excellent (Python tracebacks, Flask debug mode)
- **Community**: Large (Stack Overflow, documentation)

---

### **OPTION 2: JavaScript + Node.js + Express**

#### Rationale
- ✅ JavaScript is ubiquitous (same language frontend/backend)
- ✅ Express is minimalist and flexible
- ✅ npm ecosystem is massive
- ✅ Async/await for clean async code
- ✅ JSON-native (easy API development)

#### Technology Components
```yaml
Backend:
  Runtime: Node.js 20 LTS
  Web Framework: Express.js 4.18+
  ORM: Sequelize 6.0+ or Knex.js
  Authentication: express-basic-auth
  Database: SQLite3 (better-sqlite3 package)

Frontend:
  Framework: React 18+ or Vue.js 3
  UI Library: Tailwind CSS + shadcn/ui
  State Management: Zustand or Pinia (Vue)
  Animations: Framer Motion or anime.js

Infrastructure:
  Containerization: Docker + docker-compose
  Process Manager: PM2 (production)
```

#### File Structure
```
project/
├── docker-compose.yml
├── Dockerfile
├── package.json
├── server/
│   ├── index.js           # App entry point
│   ├── models/            # Database models
│   ├── routes/            # API routes
│   ├── middleware/        # Auth, error handling
│   └── services/          # Business logic
├── client/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── public/
└── data/
    └── scheduler.db
```

#### Complexity Assessment
- **Learning Curve**: Low-Medium (JavaScript basics required)
- **Maintenance**: Medium (callback hell risk if not careful)
- **Debugging**: Good (Chrome DevTools, VS Code debugging)
- **Community**: Very large

---

### **OPTION 3: Ruby + Sinatra**

#### Rationale
- ✅ Ruby syntax is very readable ("reads like English")
- ✅ Sinatra is extremely minimal (DSL-style routing)
- ✅ Convention over configuration
- ✅ ActiveRecord ORM is elegant

#### Technology Components
```yaml
Backend:
  Language: Ruby 3.2+
  Web Framework: Sinatra 3.0+
  ORM: ActiveRecord (standalone)
  Authentication: Rack::Auth::Basic
  Database: SQLite3 (sqlite3 gem)

Frontend:
  (Same as Python option)

Infrastructure:
  Containerization: Docker + docker-compose
  Web Server: Puma (production)
```

#### File Structure
```
project/
├── docker-compose.yml
├── Dockerfile
├── Gemfile
├── app.rb                 # Main application
├── models/
├── routes/
├── public/
│   └── (static files)
└── data/
    └── scheduler.db
```

#### Complexity Assessment
- **Learning Curve**: Low (Ruby is beginner-friendly)
- **Maintenance**: Easy (clean syntax)
- **Debugging**: Good (pry debugger)
- **Community**: Medium (smaller than Python/JS)

---

## 2. DATABASE CONSTRAINTS

### Requirement 10: "ユーザ数30名以下 + SQLite"

#### SQLite Analysis

**Strengths for This Use Case**:
- ✅ Zero configuration (no server process)
- ✅ Single file database (easy backup)
- ✅ ACID compliant (reliable)
- ✅ Sufficient for 30 users
- ✅ Excellent read performance
- ✅ Small footprint (< 1MB library)

**Limitations (Acceptable for This Project)**:
- ⚠️ Limited concurrent writes (1 writer at a time)
  - **Impact**: Low (30 users, write operations infrequent)
  - **Mitigation**: Use WAL mode (Write-Ahead Logging)
- ⚠️ No network access (file-based)
  - **Impact**: None (single-server deployment)
- ⚠️ No user management/permissions
  - **Impact**: None (application-level auth)

#### SQLite Configuration
```sql
-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Faster synchronization (acceptable for internal use)
PRAGMA synchronous=NORMAL;

-- Foreign key constraints
PRAGMA foreign_keys=ON;

-- Optimize for reads
PRAGMA cache_size=10000;

-- Timeout for write locks (milliseconds)
PRAGMA busy_timeout=5000;
```

#### Schema Design

```sql
-- Users table
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    default_start_time TIME NOT NULL DEFAULT '09:00',
    default_end_time TIME NOT NULL DEFAULT '18:00',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Availability slots table
CREATE TABLE availability (
    availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (start_time < end_time)
);

-- Indexes for performance
CREATE INDEX idx_availability_user_day ON availability(user_id, day_of_week);
CREATE INDEX idx_availability_day_time ON availability(day_of_week, start_time, end_time);

-- Optional: User status tracking
CREATE TABLE user_status (
    user_id TEXT PRIMARY KEY,
    status TEXT CHECK(status IN ('available', 'busy', 'offline')) DEFAULT 'offline',
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### Database Size Estimation
```
Users table:
  30 users × 200 bytes/user = 6 KB

Availability table:
  30 users × 50 slots/week × 100 bytes/slot = 150 KB

Total with indexes and overhead: < 1 MB
Annual growth (assuming updates): < 10 MB

Conclusion: SQLite is MORE than sufficient
```

---

## 3. DEPLOYMENT CONSTRAINTS

### Requirement 8: "docker-compose"

#### Docker Architecture

```yaml
# Minimal docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: team-scheduler
    ports:
      - "${PORT:-8080}:8080"
    volumes:
      - ./data:/app/data          # Database persistence
      - ./logs:/app/logs          # Log persistence (optional)
    environment:
      - NODE_ENV=production
      - DATABASE_PATH=/app/data/scheduler.db
      - SESSION_SECRET=${SESSION_SECRET:-change-me}
      - LOG_LEVEL=${LOG_LEVEL:-info}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 60s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  data:
    driver: local
```

#### Dockerfile (Python Example)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY static/ ./static/

# Create data directory
RUN mkdir -p /app/data /app/logs

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:create_app()"]
```

#### Deployment Commands

```bash
# Development
docker-compose up

# Production
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Backup database
docker-compose exec app cp /app/data/scheduler.db /app/data/backup_$(date +%Y%m%d).db
```

---

## 4. UI/UX CONSTRAINTS

### Requirement 9: "ポップで親しみやすい画面 + 淡い色基調 + アニメーション"

#### Design System Specifications

**Color Palette (Pastel Theme)**:
```css
:root {
  /* Primary Colors */
  --color-primary: #A8D5E2;      /* Soft blue */
  --color-primary-dark: #7FB3C5;
  --color-primary-light: #C9E4ED;

  /* Secondary Colors */
  --color-secondary: #C9E4CA;    /* Mint green */
  --color-secondary-dark: #A8C9A9;
  --color-secondary-light: #E0F2E0;

  /* Accent Colors */
  --color-accent: #FFB5A7;       /* Coral pink */
  --color-accent-dark: #FF9580;
  --color-accent-light: #FFD4CC;

  /* Neutral Colors */
  --color-bg: #FDFCF9;           /* Off-white */
  --color-surface: #FFFFFF;
  --color-text: #3A3A3A;         /* Dark gray */
  --color-text-light: #6B6B6B;

  /* Status Colors */
  --color-success: #B8E6B8;      /* Pastel green */
  --color-warning: #FFE5B4;      /* Pastel yellow */
  --color-error: #FFB8B8;        /* Pastel red */
  --color-info: #B8D8FF;         /* Pastel blue */
}
```

**Typography**:
```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

:root {
  --font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 2rem;      /* 32px */

  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-normal: 1.6;
  --line-height-relaxed: 1.8;
}
```

**Animation Specifications**:
```css
:root {
  /* Timing Functions */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0.0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);

  /* Durations */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* Transitions */
  --transition-all: all var(--duration-normal) var(--ease-in-out);
  --transition-color: color var(--duration-fast) var(--ease-in-out);
  --transition-transform: transform var(--duration-normal) var(--ease-out);
}

/* Example Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Utility Classes */
.fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-in-out);
}

.slide-in-up {
  animation: slideInUp var(--duration-slow) var(--ease-out);
}

.hover-lift {
  transition: var(--transition-transform);
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

**Component Styling Guidelines**:
```css
/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: var(--font-weight-medium);
  transition: var(--transition-all);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(168, 213, 226, 0.4);
}

/* Cards */
.card {
  background: var(--color-surface);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: var(--transition-all);
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* Time Slot Selection */
.time-slot {
  padding: 0.5rem;
  border: 2px solid transparent;
  border-radius: 0.25rem;
  transition: var(--transition-all);
  cursor: pointer;
}

.time-slot:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.time-slot.selected {
  background: var(--color-primary);
  color: white;
  animation: pulse var(--duration-fast);
}
```

---

## 5. SECURITY CONSTRAINTS

### Requirement 11: "内部簡易利用、セキュリティ最小限"

#### Security Baseline (Minimal but Responsible)

**What MUST Be Implemented**:
1. ✅ Password hashing (bcrypt, cost 10)
2. ✅ Parameterized SQL queries (prevent SQL injection)
3. ✅ Output encoding (prevent XSS)
4. ✅ CSRF token (for state-changing operations)
5. ✅ Input validation (server-side)
6. ✅ HTTPS option (strongly recommended, easy to add)

**What Can Be Skipped** (Acknowledged Risks):
1. ❌ Multi-factor authentication
2. ❌ Password complexity requirements
3. ❌ Account lockout after failed attempts
4. ❌ Session management sophistication
5. ❌ Audit logging
6. ❌ Rate limiting
7. ❌ HTTPS enforcement (deployment choice)

#### Security Implementation Example (Python/Flask)

```python
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
auth = HTTPBasicAuth()

# Password hashing
def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)

# Basic Auth verification
@auth.verify_password
def verify_credentials(username, password):
    conn = sqlite3.connect('scheduler.db')
    cursor = conn.cursor()

    # Parameterized query (SQL injection prevention)
    cursor.execute('SELECT password_hash FROM users WHERE user_id = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result and verify_password(password, result[0]):
        return username
    return None

# Protected endpoint example
@app.route('/api/availability', methods=['GET'])
@auth.login_required
def get_availability():
    user_id = auth.current_user()
    # ... implementation
    return jsonify({'user_id': user_id, 'availability': []})

# Input validation example
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validation
    if not data.get('user_id') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = data['user_id']

    # Sanitize user_id (only alphanumeric)
    if not user_id.isalnum() or len(user_id) < 3 or len(user_id) > 20:
        return jsonify({'error': 'Invalid user_id format'}), 400

    # Hash password
    password_hash = hash_password(data['password'])

    # ... store in database
    return jsonify({'message': 'User registered'}), 201
```

---

## 6. SCALE & PERFORMANCE CONSTRAINTS

### Requirement 10: "ユーザ数30名以下"

#### Performance Targets

**Load Profile**:
```
Maximum users: 30
Concurrent users (peak): 15
Requests per second: < 10
Database operations: < 100/minute

Expected Performance:
- Page load: < 2 seconds
- API response: < 500ms
- Database query: < 100ms
- Availability calculation (30 users): < 3 seconds
```

#### Optimization Strategies

**Database Optimization**:
```sql
-- Indexes for common queries
CREATE INDEX idx_availability_lookup
ON availability(user_id, day_of_week, start_time, end_time);

-- Avoid N+1 queries with JOIN
SELECT u.user_id, u.default_start_time, a.day_of_week, a.start_time, a.end_time
FROM users u
LEFT JOIN availability a ON u.user_id = a.user_id
WHERE a.day_of_week = ?;
```

**Caching Strategy**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache user list for 5 minutes
@lru_cache(maxsize=1)
def get_all_users_cached(cache_key):
    # cache_key = current_minute // 5 (invalidates every 5 min)
    return get_all_users_from_db()

# Usage
cache_key = datetime.now().minute // 5
users = get_all_users_cached(cache_key)
```

**Frontend Optimization**:
```javascript
// Debounce availability updates
const saveAvailability = debounce((data) => {
  fetch('/api/availability', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}, 500); // Wait 500ms after last change

// Lazy load historical data
const loadHistory = () => {
  if (isScrolledToBottom()) {
    fetchOlderData();
  }
};
```

---

## 7. BROWSER & DEVICE CONSTRAINTS

### Requirement 7: "マウスなどで簡易に入力"

#### Target Devices & Browsers

**Primary Targets**:
- Desktop: Windows 10+, macOS 11+ (1920×1080, 1366×768)
- Laptop: 1440×900, 1280×800
- Tablet: iPad (768×1024), Android tablets

**Browser Support**:
- Chrome 90+ (primary)
- Firefox 88+ (primary)
- Safari 14+ (secondary)
- Edge 90+ (secondary)
- ❌ IE11 (not supported)

#### Input Methods

**Mouse/Trackpad**:
```javascript
// Drag to select time slots
let isDragging = false;
let startSlot = null;

timeSlot.addEventListener('mousedown', (e) => {
  isDragging = true;
  startSlot = e.target;
  startSlot.classList.add('selected');
});

document.addEventListener('mousemove', (e) => {
  if (isDragging) {
    const currentSlot = document.elementFromPoint(e.clientX, e.clientY);
    if (currentSlot && currentSlot.classList.contains('time-slot')) {
      currentSlot.classList.add('selected');
    }
  }
});

document.addEventListener('mouseup', () => {
  if (isDragging) {
    isDragging = false;
    saveSelection();
  }
});
```

**Touch Support** (Tablets):
```javascript
// Touch events for mobile/tablet
timeSlot.addEventListener('touchstart', handleTouchStart);
timeSlot.addEventListener('touchmove', handleTouchMove);
timeSlot.addEventListener('touchend', handleTouchEnd);

function handleTouchStart(e) {
  e.preventDefault();
  const touch = e.touches[0];
  // ... similar to mousedown
}
```

**Keyboard Navigation** (Accessibility):
```javascript
// Arrow keys to navigate, Space to toggle
timeSlot.addEventListener('keydown', (e) => {
  switch(e.key) {
    case 'ArrowRight':
      focusNextSlot();
      break;
    case 'ArrowLeft':
      focusPrevSlot();
      break;
    case ' ':
      toggleSlot(e.target);
      break;
  }
});
```

---

## 8. ASSUMPTIONS DOCUMENTATION

### Explicit Assumptions

1. **Network Environment**:
   - Assumption: Deployed on internal LAN
   - Impact: No need for CDN, can use server-side rendering
   - Risk: Low (stated in requirements)

2. **User Expertise**:
   - Assumption: Users have basic computer literacy
   - Impact: Minimal onboarding needed
   - Risk: Low (internal team)

3. **Timezone**:
   - Assumption: All users in same timezone
   - Impact: No timezone conversion logic needed
   - Risk: Medium (if remote team expands)
   - Mitigation: Document limitation, add later if needed

4. **Meeting Creation**:
   - Assumption: Actual meeting scheduling happens outside this system
   - Impact: System only manages availability, not bookings
   - Risk: Low (clarify with stakeholders)

5. **Data Retention**:
   - Assumption: No automatic data purging needed
   - Impact: Historical data accumulates
   - Risk: Low (30 users, minimal data)

6. **Availability Patterns**:
   - Assumption: Weekly patterns are sufficient (no special dates)
   - Impact: No holiday/vacation management
   - Risk: Medium (may need future enhancement)

7. **Concurrent Editing**:
   - Assumption: Users rarely edit same data simultaneously
   - Impact: No conflict resolution needed
   - Risk: Very low (30 users, personal schedules)

8. **Backup**:
   - Assumption: Manual backup is acceptable
   - Impact: No automated backup system
   - Risk: Medium (could lose data)
   - Mitigation: Document backup procedure, cron job option

---

## 9. TECHNICAL DEBT & TRADEOFFS

### Accepted Technical Debt

| Decision | Tradeoff | Justification |
|----------|----------|---------------|
| Basic Auth | Weak security | Internal use only, fast implementation |
| No HTTPS enforcement | Credentials in clear | Optional at deployment, easy to add |
| SQLite | Limited concurrency | 30 users is well within limits |
| No audit logs | Can't track changes | Not required for internal tool |
| Manual backup | Risk of data loss | Acceptable for non-critical system |
| No mobile app | Desktop-only | Web responsive is sufficient |

### Future Enhancement Opportunities

1. **Phase 2 Features**:
   - Holiday/vacation management
   - Recurring event templates
   - Email reminders
   - Calendar export (iCal)

2. **Scalability Path** (if needed):
   - Migrate to PostgreSQL (>100 users)
   - Add Redis for caching (>50 users)
   - Implement OAuth/SSO (enterprise use)

3. **Security Hardening** (if needed):
   - Enforce HTTPS
   - Add rate limiting
   - Implement audit logging
   - MFA option

---

## 10. RISK ASSESSMENT

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| SQLite write lock contention | Low | Medium | Use WAL mode, acceptable delays |
| Basic Auth credentials stolen | Medium | Medium | Internal network only, HTTPS option |
| Browser compatibility issues | Low | Low | Test on target browsers |
| Docker deployment complexity | Low | Medium | Provide detailed documentation |
| Disk space exhaustion | Very Low | High | Monitor disk, alert at 80% |

### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Data loss (no backup) | Medium | High | Document backup, create cron job |
| Server downtime | Low | Medium | Docker auto-restart, health checks |
| User adoption issues | Low | Low | Intuitive UI, training session |
| Performance degradation | Very Low | Low | 30 users is well within capacity |

---

## SUMMARY

### Key Constraints
1. ✅ **Language**: Python/Flask (recommended) or Node.js/Express
2. ✅ **Database**: SQLite with WAL mode
3. ✅ **Deployment**: docker-compose single-command setup
4. ✅ **Scale**: 30 users maximum
5. ✅ **Security**: Minimal (Basic Auth + password hashing)
6. ✅ **UI**: Pastel colors, smooth animations, intuitive interactions

### Technical Stack Recommendation
**Winner: Python + Flask + Vue.js + Tailwind CSS**

**Rationale**:
- Python is widely considered "easy" (平易)
- Flask is minimal yet powerful
- Vue.js is progressive (can start simple)
- Tailwind CSS perfect for pastel color system
- Excellent community support
- Fast development cycle

### Implementation Complexity
- **Backend**: Low (Flask + SQLite)
- **Frontend**: Medium (Vue.js + animations)
- **Deployment**: Low (docker-compose)
- **Maintenance**: Low (clear code structure)

**Total Effort Estimate**: 2-3 weeks for MVP with 1 developer

---

**Document Prepared By**: Requirements Analysis Specialist
**Review Status**: Pending Stakeholder Approval
**Last Updated**: 2025-10-01
