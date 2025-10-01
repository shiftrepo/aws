# Technical Recommendations - Team Schedule Management System

## Technology Stack Selection

### Backend: Node.js + Express.js ⭐ RECOMMENDED

**Pros:**
- Simple, minimal learning curve
- Vast ecosystem (npm packages)
- Excellent for small-scale applications
- Strong session management libraries
- Easy Docker deployment
- Asynchronous I/O perfect for web app

**Cons:**
- Callback hell (mitigated by async/await)
- Single-threaded (not an issue for 30 users)

**Package Recommendations:**
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "express-session": "^1.17.3",
    "passport": "^0.6.0",
    "passport-local": "^1.0.0",
    "bcrypt": "^5.1.1",
    "better-sqlite3": "^9.2.2",
    "express-validator": "^7.0.1",
    "helmet": "^7.1.0",
    "csurf": "^1.11.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.2",
    "eslint": "^8.55.0",
    "jest": "^29.7.0"
  }
}
```

### Alternative: Python + Flask

**Pros:**
- Very simple syntax
- Good for rapid prototyping
- Strong data processing libraries

**Cons:**
- Less mature session management
- Heavier Docker image
- Async support more complex

**Verdict:** Node.js preferred for better frontend-backend synergy

---

## Frontend Architecture

### Vanilla JavaScript + CSS3 ⭐ RECOMMENDED

**Structure:**
```
/public
  /css
    main.css          # Global styles
    animations.css    # Transition effects
    components.css    # Reusable components
  /js
    app.js            # Main application logic
    auth.js           # Login/registration
    schedule.js       # Schedule management
    dashboard.js      # Availability display
    utils.js          # Helper functions
  /assets
    /icons            # SVG icons
    /images           # Illustrations
  index.html          # Login page
  dashboard.html      # Main app (post-login)
  schedule.html       # Schedule input page
```

**CSS Framework:** None (custom CSS)
- Use CSS Grid for layout
- CSS Flexbox for components
- CSS Variables for theming

**Animations:**
```css
/* Example animation style */
.button {
  transition: all 0.3s ease;
}

.button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.time-slot {
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.time-slot:hover {
  transform: translateY(-2px);
}

.toast {
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### Alternative: React

**Pros:**
- Component reusability
- Strong ecosystem
- State management

**Cons:**
- Complexity overkill for this project
- Build step required
- Larger bundle size

**Verdict:** Vanilla JS sufficient, avoid framework overhead

---

## Database Design

### SQLite3 with WAL Mode ⭐ RECOMMENDED

**Configuration:**
```javascript
// better-sqlite3 setup
const Database = require('better-sqlite3');
const db = new Database('schedule.db');

// Enable WAL mode for better concurrency
db.pragma('journal_mode = WAL');

// Enable foreign keys
db.pragma('foreign_keys = ON');

// Set cache size (10MB)
db.pragma('cache_size = -10000');
```

**Schema (Final):**
```sql
-- Users table
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  work_hours_start TEXT NOT NULL,
  work_hours_end TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

-- Availability table
CREATE TABLE availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  day_of_week INTEGER NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_availability_user ON availability(user_id);
CREATE INDEX idx_availability_day ON availability(day_of_week);

-- Sessions table
CREATE TABLE sessions (
  sid TEXT PRIMARY KEY,
  sess TEXT NOT NULL,
  expired DATETIME NOT NULL
);

CREATE INDEX idx_sessions_expired ON sessions(expired);
```

**Migration Strategy:**
```javascript
// Simple migration system
const migrations = [
  {
    version: 1,
    up: `CREATE TABLE users (...);`,
    down: `DROP TABLE users;`
  },
  // Add more migrations as needed
];

function migrate(db) {
  // Check current version, apply pending migrations
}
```

---

## Authentication Strategy

### Passport.js Local Strategy ⭐ RECOMMENDED

**Implementation:**
```javascript
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcrypt');

// Configure Passport
passport.use(new LocalStrategy(
  function(username, password, done) {
    const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);

    if (!user) {
      return done(null, false, { message: 'Incorrect username.' });
    }

    if (!bcrypt.compareSync(password, user.password_hash)) {
      return done(null, false, { message: 'Incorrect password.' });
    }

    return done(null, user);
  }
));

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser((id, done) => {
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(id);
  done(null, user);
});
```

**Session Configuration:**
```javascript
const session = require('express-session');
const SQLiteStore = require('connect-sqlite3')(session);

app.use(session({
  store: new SQLiteStore({
    db: 'schedule.db',
    table: 'sessions'
  }),
  secret: process.env.SESSION_SECRET || 'change-this-secret',
  resave: false,
  saveUninitialized: false,
  cookie: {
    maxAge: 30 * 60 * 1000, // 30 minutes
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production'
  }
}));
```

---

## API Design

### RESTful Endpoints

**Authentication:**
```
POST   /api/register          # User registration
POST   /api/login             # User login
POST   /api/logout            # User logout
GET    /api/me                # Get current user info
```

**Schedule Management:**
```
GET    /api/schedule          # Get current user's schedule
POST   /api/schedule          # Update schedule (upsert)
DELETE /api/schedule/:id      # Delete specific availability slot
```

**Availability Dashboard:**
```
GET    /api/availability      # Get all users' availability
GET    /api/availability/common?day=2&min_users=3  # Find common slots
```

**Request/Response Examples:**

**POST /api/schedule**
```json
{
  "availability": [
    {
      "day_of_week": 1,
      "start_time": "09:00",
      "end_time": "12:00"
    },
    {
      "day_of_week": 1,
      "start_time": "14:00",
      "end_time": "17:00"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Schedule updated successfully",
  "slots_added": 2
}
```

**GET /api/availability**
```json
{
  "users": [
    {
      "id": 1,
      "username": "akiko",
      "availability": [
        {
          "day_of_week": 1,
          "start_time": "09:00",
          "end_time": "12:00"
        }
      ]
    }
  ]
}
```

---

## UI/UX Implementation Details

### Color Palette

```css
:root {
  /* Primary Colors */
  --primary-blue: #6BAED6;
  --primary-blue-light: #A0D0EC;
  --primary-blue-dark: #3D8AB8;

  /* Secondary Colors */
  --mint-green: #A8E6CF;
  --mint-green-light: #D4F4E4;
  --mint-green-dark: #7DD1A8;

  /* Accent */
  --pastel-yellow: #FFD3B6;
  --pastel-yellow-light: #FFE7D4;

  /* Neutrals */
  --background: #F9FAFB;
  --surface: #FFFFFF;
  --text-primary: #333333;
  --text-secondary: #666666;
  --border: #E5E7EB;

  /* Status */
  --success: #10B981;
  --error: #EF4444;
  --warning: #F59E0B;
}
```

### Component Library

**Button:**
```css
.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-blue-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(107, 174, 214, 0.4);
}
```

**Time Slot Card:**
```css
.time-slot {
  padding: 12px;
  border-radius: 8px;
  border: 2px solid var(--border);
  background: var(--surface);
  cursor: pointer;
  transition: all 0.2s ease;
}

.time-slot:hover {
  border-color: var(--primary-blue);
  transform: translateY(-2px);
}

.time-slot.selected {
  background: var(--mint-green-light);
  border-color: var(--mint-green-dark);
}

.time-slot.selected:hover {
  background: var(--mint-green);
}
```

**Toast Notification:**
```css
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 8px;
  background: var(--surface);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slide-in 0.3s ease-out;
  z-index: 1000;
}

.toast.success {
  border-left: 4px solid var(--success);
}

.toast.error {
  border-left: 4px solid var(--error);
}
```

### Dashboard Layout

**Grid-Based Availability Matrix:**
```html
<div class="availability-grid">
  <div class="grid-header">
    <div class="grid-cell">User</div>
    <div class="grid-cell">Mon</div>
    <div class="grid-cell">Tue</div>
    <!-- ... -->
  </div>
  <div class="grid-row">
    <div class="grid-cell user-cell">Akiko</div>
    <div class="grid-cell time-cell" data-day="1">
      <!-- Time slots here -->
    </div>
    <!-- ... -->
  </div>
</div>
```

```css
.availability-grid {
  display: grid;
  grid-template-columns: 150px repeat(7, 1fr);
  gap: 2px;
  background: var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.grid-cell {
  background: var(--surface);
  padding: 12px;
  min-height: 60px;
}

.time-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.time-badge {
  padding: 4px 8px;
  background: var(--primary-blue-light);
  border-radius: 4px;
  font-size: 12px;
}
```

---

## Docker Configuration

### Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

EXPOSE 3000

CMD ["node", "server.js"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data          # SQLite database persistence
      - ./logs:/app/logs          # Application logs
    environment:
      - NODE_ENV=production
      - SESSION_SECRET=${SESSION_SECRET:-change-this-secret}
      - DATABASE_PATH=/app/data/schedule.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### .env.example

```bash
# Server Configuration
NODE_ENV=production
PORT=3000

# Security
SESSION_SECRET=your-super-secret-session-key-change-this

# Database
DATABASE_PATH=/app/data/schedule.db

# Limits
MAX_USERS=30
SESSION_TIMEOUT=1800000  # 30 minutes in milliseconds
```

---

## Testing Strategy

### Unit Tests (Jest)

```javascript
// Example: tests/auth.test.js
const { registerUser, loginUser } = require('../src/auth');

describe('User Authentication', () => {
  test('should register new user with valid credentials', async () => {
    const user = await registerUser('testuser', 'password123', '09:00', '17:00');
    expect(user).toHaveProperty('id');
    expect(user.username).toBe('testuser');
  });

  test('should reject duplicate username', async () => {
    await expect(
      registerUser('testuser', 'password123', '09:00', '17:00')
    ).rejects.toThrow('Username already exists');
  });

  test('should hash password before storing', async () => {
    const user = await registerUser('testuser2', 'password123', '09:00', '17:00');
    expect(user.password_hash).not.toBe('password123');
    expect(user.password_hash.length).toBeGreaterThan(20);
  });
});
```

### Integration Tests

```javascript
// Example: tests/api.test.js
const request = require('supertest');
const app = require('../src/app');

describe('API Endpoints', () => {
  let agent;

  beforeAll(() => {
    agent = request.agent(app);
  });

  test('POST /api/login should authenticate user', async () => {
    const res = await agent
      .post('/api/login')
      .send({ username: 'testuser', password: 'password123' });

    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('success', true);
  });

  test('GET /api/schedule should require authentication', async () => {
    const res = await request(app).get('/api/schedule');
    expect(res.statusCode).toBe(401);
  });
});
```

### End-to-End Tests (Optional: Playwright)

```javascript
// Example: e2e/registration.spec.js
test('user registration flow', async ({ page }) => {
  await page.goto('http://localhost:3000/register');

  await page.fill('input[name="username"]', 'newuser');
  await page.fill('input[name="password"]', 'securepass123');
  await page.fill('input[name="workHoursStart"]', '09:00');
  await page.fill('input[name="workHoursEnd"]', '17:00');

  await page.click('button[type="submit"]');

  await expect(page).toHaveURL('http://localhost:3000/login');
  await expect(page.locator('.success-message')).toContainText('Registration successful');
});
```

---

## Performance Optimization

### Backend Optimizations

**1. Database Query Optimization:**
```javascript
// Use prepared statements (better-sqlite3 does this by default)
const getUserSchedule = db.prepare(`
  SELECT * FROM availability WHERE user_id = ? ORDER BY day_of_week, start_time
`);

// Batch operations
const insertSlot = db.prepare(`
  INSERT INTO availability (user_id, day_of_week, start_time, end_time)
  VALUES (?, ?, ?, ?)
`);

const insertMany = db.transaction((slots) => {
  for (const slot of slots) {
    insertSlot.run(slot.user_id, slot.day_of_week, slot.start_time, slot.end_time);
  }
});
```

**2. Response Compression:**
```javascript
const compression = require('compression');
app.use(compression());
```

**3. Static Asset Caching:**
```javascript
app.use(express.static('public', {
  maxAge: '1d',
  etag: true
}));
```

### Frontend Optimizations

**1. Debounce User Input:**
```javascript
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Usage
const saveSchedule = debounce(async (scheduleData) => {
  await fetch('/api/schedule', {
    method: 'POST',
    body: JSON.stringify(scheduleData)
  });
}, 500);
```

**2. Lazy Load Dashboard Data:**
```javascript
// Only load visible week, not all weeks
async function loadWeekData(weekOffset = 0) {
  const response = await fetch(`/api/availability?week=${weekOffset}`);
  // Render only visible data
}
```

**3. CSS Optimization:**
```css
/* Use will-change for animated elements */
.time-slot {
  will-change: transform;
}

/* Use transform instead of position changes */
.slide-in {
  transform: translateY(0);
  /* NOT: top: 0; */
}
```

---

## Security Checklist

- [x] **Password Security:** bcrypt with cost factor 12
- [x] **Session Security:** HTTP-only cookies, secure in production
- [x] **CSRF Protection:** csurf middleware
- [x] **Input Validation:** express-validator on all inputs
- [x] **SQL Injection:** Prepared statements (better-sqlite3 default)
- [x] **XSS Prevention:** Sanitize user input, use CSP headers
- [x] **Rate Limiting:** express-rate-limit on login/register
- [x] **Helmet:** Security headers (helmet middleware)
- [x] **Environment Variables:** Never commit secrets to Git

**Security Headers:**
```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:"]
    }
  }
}));
```

---

## Deployment Checklist

- [ ] Build Docker image
- [ ] Configure environment variables (.env)
- [ ] Set strong SESSION_SECRET
- [ ] Run `docker-compose up -d`
- [ ] Verify health check endpoint
- [ ] Test registration flow
- [ ] Test login flow
- [ ] Test schedule input
- [ ] Test dashboard display
- [ ] Configure backups (SQLite volume)
- [ ] Set up logging (Winston or similar)
- [ ] Monitor disk usage (SQLite grows over time)

---

## Maintenance Recommendations

**Weekly:**
- Check application logs for errors
- Monitor disk usage

**Monthly:**
- Backup SQLite database
- Review session table size (cleanup expired sessions)
- Check for npm security vulnerabilities (`npm audit`)

**Quarterly:**
- Update dependencies
- Review performance metrics
- User feedback survey

---

## Future Enhancements (Phase 2)

**Priority 1:**
- [ ] Email notifications for schedule changes
- [ ] Export common slots to calendar (iCal)
- [ ] Admin panel for user management

**Priority 2:**
- [ ] Timezone support
- [ ] Recurring schedule patterns (templates)
- [ ] Mobile-responsive design

**Priority 3:**
- [ ] Mobile app (React Native)
- [ ] Slack integration
- [ ] Advanced analytics (most common meeting times)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-01
**Author:** Research Agent (Claude Flow)
