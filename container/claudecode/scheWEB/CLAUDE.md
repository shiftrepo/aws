# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: CONCURRENT EXECUTION & FILE MANAGEMENT

**ABSOLUTE RULES**:
1. ALL operations MUST be concurrent/parallel in a single message
2. **NEVER save working files, text/mds and tests to the root folder**
3. ALWAYS organize files in appropriate subdirectories
4. **USE CLAUDE CODE'S TASK TOOL** for spawning agents concurrently, not just MCP

### ⚡ GOLDEN RULE: "1 MESSAGE = ALL RELATED OPERATIONS"

**MANDATORY PATTERNS:**
- **TodoWrite**: ALWAYS batch ALL todos in ONE call (5-10+ todos minimum)
- **Task tool (Claude Code)**: ALWAYS spawn ALL agents in ONE message with full instructions
- **File operations**: ALWAYS batch ALL reads/writes/edits in ONE message
- **Bash commands**: ALWAYS batch ALL terminal operations in ONE message
- **Memory operations**: ALWAYS batch ALL memory store/retrieve in ONE message

## Project Overview - Team Schedule Manager (チームスケジューラー)

A Japanese team scheduling web application that helps teams find common meeting times through AI-powered analysis. Built with Flask backend, vanilla JavaScript frontend, and AWS Bedrock integration for LLM-powered schedule optimization.

### Architecture Overview

- **Backend**: Flask 3.0 + SQLite + JWT authentication + AWS Bedrock integration
- **Frontend**: Single-page HTML application with vanilla JavaScript
- **Infrastructure**: Docker containers with nginx reverse proxy
- **AI Features**: AWS Bedrock Claude 3 Sonnet for meeting candidate analysis

### Key Components

1. **Schedule Grid System**: 7:00-19:00 time slots in 30-minute increments
2. **User Management**: JWT-based authentication with work hours
3. **Availability Tracking**: Overlapping time slot detection algorithm
4. **LLM Analysis**: AI-powered optimal meeting time recommendations
5. **Version Control**: Embedded version numbers (currently v2.1.5) in UI and APIs

## Essential Commands

### Docker Development
```bash
# Start the application
docker compose up --build -d

# View logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend

# Restart services
docker compose restart backend
docker compose restart frontend

# Stop and clean
docker compose down
docker compose down -v  # Also remove volumes/database

# Force rebuild with no cache
docker compose build --no-cache
docker compose up --build --force-recreate
```

### Database Management
```bash
# Reset database (removes all data)
docker compose down -v
docker compose up --build

# Backup database
docker cp $(docker compose ps -q backend):/app/data/scheduler.db ./backup_$(date +%Y%m%d).db

# Access database directly
docker compose exec backend sqlite3 /app/data/scheduler.db
```

### Testing & Debugging
```bash
# Test database connectivity
curl -s http://localhost:8080/api/test/database | jq

# Test LLM analysis (no auth required)
curl -s http://localhost:8080/api/test/llm-analysis | jq

# Get JWT token for testing
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8080/api/login | jq -r '.access_token')

# Test authenticated endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/availability/all | jq
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/llm-analysis | jq
```

### Version Management
```bash
# Check current version displayed
curl -s http://localhost:8080/ | grep "v2\."

# Version is embedded in multiple places:
# - Frontend console.log message
# - Frontend HTML title
# - Backend API responses (version field)
```

## Architecture Deep Dive

### Backend Structure (`app/backend/`)

#### Core Files
- **`app.py`**: Main Flask application with all API endpoints
  - Authentication routes (`/api/login`, `/api/register`)
  - Schedule routes (`/api/availability`, `/api/grid-schedule`)
  - LLM analysis route (`/api/llm-analysis`)
  - Test routes (`/api/test/database`, `/api/test/llm-analysis`)

- **`meeting_candidates.py`**: LLM analysis engine
  - `MeetingCandidateAnalyzer` class with AWS Bedrock integration
  - Time slot generation and overlap detection algorithms
  - Claude 3 Sonnet integration for meeting optimization

- **`grid_logic.py`**: Schedule grid utilities
  - Time slot generation (7:00-19:00, 30-min intervals)
  - User availability checking functions
  - Grid index mapping

- **`init_db.py`**: Database initialization
  - Creates SQLite tables (users, availability, meetings, meeting_participants)
  - Inserts sample data for development
  - Proper indexing for performance

#### Database Schema
```sql
-- Users with work hours
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    start_time TEXT NOT NULL,  -- Work start (e.g., "09:00")
    end_time TEXT NOT NULL,    -- Work end (e.g., "18:00")
    created_at TEXT NOT NULL
);

-- User availability by day/time
CREATE TABLE availability (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,  -- "monday", "tuesday", etc.
    start_time TEXT NOT NULL,   -- "10:00"
    end_time TEXT NOT NULL,     -- "12:00"
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### Frontend Structure (`app/frontend/`)

#### Single-Page Application
- **`schedule-grid-improved.html`**: Complete SPA with embedded CSS/JavaScript
  - Authentication system (`AuthManager` class)
  - Schedule management (`ScheduleManager` class)
  - Grid rendering and time slot interaction
  - LLM analysis modal with scrollable results
  - Version display and identification

#### Key Frontend Classes
```javascript
// Authentication and page routing
class AuthManager {
    checkAuthStatus()     // JWT token validation
    showLogin()          // Login form
    showDashboard()      // Main application
    logout()             // Clear tokens
}

// Schedule grid and LLM features
class ScheduleManager {
    generateTimeSlots()   // Create 7:00-19:00 grid
    loadData()           // Fetch user availability
    renderGrid()         // Draw schedule visualization
    runLLMAnalysis()     // Call AI analysis API
    displayAnalysisResults() // Show TOP 4 candidates
}
```

### Infrastructure (`docker-compose.yml`)

#### Service Architecture
```yaml
# Backend API server
backend:
  - Flask application on port 5000
  - SQLite volume mount for persistence
  - AWS environment variables for Bedrock
  - Development mode with debug enabled

# Frontend web server
frontend:
  - nginx serving static HTML
  - Proxy to backend API on /api/ routes
  - Port 8080 exposed to host
```

### AWS Bedrock Integration

#### Environment Variables Required
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### LLM Analysis Flow
1. Collect all user availability from database
2. Generate meeting candidates (2+ participants)
3. Send top 10 candidates to Claude 3 Sonnet
4. Receive AI-optimized TOP 4 recommendations
5. Display with reasoning and participant details

## Development Patterns

### Version Management
- **ALWAYS update version numbers** when making UI/API changes
- Version format: `v2.1.X` (currently v2.1.5)
- Update locations:
  - Frontend console.log message
  - Frontend HTML title display
  - Backend API test endpoints

### Error Handling
- Use `/api/test/` endpoints for debugging without authentication
- Check database connectivity before LLM operations
- Graceful fallback when AWS Bedrock unavailable

### UI/UX Guidelines
- Modal windows must be scrollable (`max-height: 90vh`)
- Sticky headers/footers for long content
- Compact result display for better usability
- Japanese text with emoji for visual appeal

## File Organization Rules

**NEVER save to root folder. Use these directories:**
- `/docs` - Documentation and analysis files
- `/app/backend` - Python Flask application
- `/app/frontend` - HTML/CSS/JavaScript files
- `/test` - Test files and verification scripts
- `/memory` - Session and agent coordination

## Common Tasks

### Adding New API Endpoints
1. Add route to `app/backend/app.py`
2. Use `@jwt_required()` decorator for authentication
3. Follow existing error handling patterns
4. Update version number in responses

### Modifying Frontend
1. Edit `app/frontend/schedule-grid-improved.html`
2. Update version in console.log and HTML title
3. Restart frontend container: `docker compose restart frontend`
4. Clear browser cache to see changes

### Database Changes
1. Modify `app/backend/init_db.py` for schema
2. Use `docker compose down -v` to reset database
3. Rebuild: `docker compose up --build`

### AWS Integration Issues
1. Verify environment variables are set
2. Check `/api/test/llm-analysis` endpoint first
3. LLM failures fallback to traditional algorithm
4. No AWS credentials = LLM analysis disabled (graceful degradation)

## Important Technical Details

### Time Slot System
- Fixed grid: 7:00 AM to 7:00 PM (12 hours)
- 30-minute intervals = 24 total slots per day
- Grid indices 0-23 map to time ranges
- Monday-Friday schedule (no weekends)

### Authentication Flow
- JWT tokens stored in localStorage
- Bearer token authentication for API calls
- Automatic redirect to login when token expires
- Demo accounts: admin/admin123, ken/admin123

### LLM Analysis Algorithm
1. **Data Collection**: Get all user availability
2. **Candidate Generation**: Find 2+ person overlaps
3. **Prioritization**: Sort by participant count, duration
4. **LLM Enhancement**: Send to Claude 3 Sonnet for optimization
5. **Result Display**: TOP 4 with AI reasoning

Remember: This is a production scheduling application with real user data and AWS integration. Always test changes in development environment first.