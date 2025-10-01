# Functional Requirements Analysis
## Team Meeting Scheduler System

### Document Information
- **Date**: 2025-10-01
- **Version**: 1.0
- **Status**: Initial Analysis

---

## 1. FUNCTIONAL REQUIREMENTS BREAKDOWN

### FR-001: User Management System
**Priority**: High | **Complexity**: Medium

#### FR-001.1 User Registration
- **Description**: Allow new users to register with credentials and availability preferences
- **Inputs**:
  - User ID (unique identifier)
  - Password (encrypted storage)
  - Default work start time (基本始業時間)
  - Default work end time (基本終業時間)
- **Validation Rules**:
  - User ID: Unique, alphanumeric, 3-20 characters
  - Password: Minimum 8 characters
  - Start time < End time
  - Time format: HH:MM (24-hour)
- **Output**: User account created, redirect to login

#### FR-001.2 Basic Authentication
- **Description**: Simple HTTP Basic Auth for access control
- **Type**: Basic Authentication (RFC 7617)
- **Scope**: All protected endpoints
- **Session Management**: Browser-based credential caching
- **Security Level**: Minimal (internal use only)

---

### FR-002: Dashboard/Top Screen
**Priority**: High | **Complexity**: High

#### FR-002.1 All Users Status Display
- **Description**: Show current availability status of all registered users
- **Display Elements**:
  - User list (up to 30 users)
  - Current availability indicator (Available/Busy/Offline)
  - Today's schedule summary
  - Visual status indicators (color-coded)
- **Refresh**: Real-time or periodic auto-refresh
- **Sorting**: By name, availability status, department (optional)

#### FR-002.2 Common Available Time Slots Display
- **Description**: Calculate and display time slots when multiple users are available
- **Algorithm Requirements**:
  - Intersection of all user availabilities
  - Filter by selected participants (optional)
  - Group by day of week
  - Minimum meeting duration threshold (e.g., 30 min)
- **Display Format**:
  - Weekly calendar view
  - Time slot grid (rows = days, columns = hours)
  - Color intensity = number of available users
  - Click to see participant list

---

### FR-003: Schedule Input/Editing
**Priority**: High | **Complexity**: High

#### FR-003.1 Weekly Availability Input
- **Description**: Allow users to input their available time slots by day of week
- **Input Method**:
  - Mouse-based drag-and-drop interface
  - Click to toggle time slots
  - Drag to select multiple slots
  - Touch-friendly for tablets
- **Data Structure**:
  - Day of week: Monday - Sunday (月-日)
  - Time slots: 15-minute or 30-minute granularity
  - Multiple non-contiguous slots per day supported
- **Features**:
  - Copy/paste between days
  - "Repeat" function (apply to multiple weeks)
  - Template saving (common patterns)
  - Quick actions: "Mark all available", "Clear day"

#### FR-003.2 Availability Management
- **Description**: CRUD operations for user availability
- **Operations**:
  - Create: Add new availability slots
  - Read: View current schedule
  - Update: Modify existing slots
  - Delete: Remove availability
- **Constraints**:
  - Cannot overlap with default non-working hours
  - Must respect user's registered start/end times
  - Visual conflict indicators

---

### FR-004: Meeting Coordination Features
**Priority**: Medium | **Complexity**: Medium

#### FR-004.1 Optimal Time Finder
- **Description**: Suggest best meeting times based on participant availability
- **Algorithm**:
  - Find intersecting available slots
  - Rank by number of participants
  - Consider time preferences (morning/afternoon)
  - Avoid lunch hours (12:00-13:00)
- **Output**: Ranked list of suggested times

#### FR-004.2 Conflict Detection
- **Description**: Warn users of scheduling conflicts
- **Types**:
  - User double-booking
  - Outside working hours
  - Minimum rest time violations
- **Display**: Visual warnings with amber/red indicators

---

## 2. USER STORIES

### Epic 1: User Onboarding
```
US-001: As a new team member,
I want to register my account with my work hours,
So that I can participate in meeting scheduling.

Acceptance Criteria:
✓ Registration form with 4 fields
✓ Password is hidden during input
✓ Default times pre-filled (9:00-18:00)
✓ Validation errors shown inline
✓ Success message on completion
```

### Epic 2: Availability Management
```
US-002: As a team member,
I want to visually mark my available time slots by dragging on a calendar,
So that I can quickly update my schedule.

Acceptance Criteria:
✓ Weekly grid interface (7 days × 24 hours)
✓ Drag to select continuous time blocks
✓ Click to toggle individual slots
✓ Immediate visual feedback
✓ Auto-save on changes
✓ Undo/redo functionality
```

```
US-003: As a team member,
I want to set multiple available time slots per day,
So that I can accommodate my complex schedule.

Acceptance Criteria:
✓ Support 5+ non-contiguous slots per day
✓ Visual differentiation of slots
✓ Ability to add/remove individual slots
✓ No limit on number of slots
```

### Epic 3: Meeting Coordination
```
US-004: As a team leader,
I want to see when all team members are available,
So that I can find the best meeting time.

Acceptance Criteria:
✓ Dashboard shows all users
✓ Availability status color-coded
✓ Common time slots highlighted
✓ Filter by specific participants
✓ Export to calendar format
```

```
US-005: As a busy team member,
I want the system to suggest optimal meeting times,
So that I don't have to manually compare schedules.

Acceptance Criteria:
✓ Algorithm finds overlapping slots
✓ Results ranked by convenience
✓ Shows number of available participants
✓ One-click meeting proposal
```

### Epic 4: User Experience
```
US-006: As a user,
I want a colorful and friendly interface with smooth animations,
So that scheduling feels less tedious.

Acceptance Criteria:
✓ Pastel color scheme (淡い色)
✓ Smooth transitions (200-300ms)
✓ Loading animations
✓ Hover effects
✓ Micro-interactions on clicks
✓ Responsive design
```

---

## 3. USE CASES

### UC-001: Register New User Account
**Actors**: New Team Member
**Preconditions**: None
**Postconditions**: User account created, can log in

**Main Flow**:
1. User navigates to registration page
2. System displays registration form
3. User enters: ID, password, start time, end time
4. User submits form
5. System validates inputs
6. System creates user account
7. System displays success message
8. System redirects to login page

**Alternative Flows**:
- 5a. Validation fails → Display errors, return to step 3
- 5b. User ID already exists → Display error, suggest alternatives

---

### UC-002: Update Weekly Availability
**Actors**: Team Member
**Preconditions**: User is authenticated
**Postconditions**: User availability updated in database

**Main Flow**:
1. User navigates to schedule input page
2. System displays weekly calendar grid with current availability
3. User selects start time slot
4. User drags to end time slot
5. System highlights selected range
6. User releases mouse
7. System marks time slots as available
8. System auto-saves changes
9. System displays confirmation animation

**Alternative Flows**:
- 3a. User clicks single slot → Toggle availability
- 7a. Overlaps with non-working hours → Display warning, prevent save
- 8a. Network error → Queue for retry, show offline indicator

---

### UC-003: Find Common Meeting Time
**Actors**: Team Leader, System
**Preconditions**: Multiple users have set availability
**Postconditions**: Common time slots displayed

**Main Flow**:
1. User navigates to dashboard/top screen
2. System loads all user availabilities
3. System calculates intersection of availabilities
4. System displays common time slots in calendar view
5. User hovers over time slot
6. System shows tooltip with participant names
7. User clicks time slot
8. System shows detailed participant list and suggests meeting creation

**Alternative Flows**:
- 3a. No common slots found → Display message, suggest alternatives
- 5a. User filters by specific participants → Recalculate and update display

---

### UC-004: View Team Availability Status
**Actors**: Any Team Member
**Preconditions**: User is authenticated
**Postconditions**: None

**Main Flow**:
1. User logs in and lands on top screen
2. System displays list of all users (≤30)
3. System shows each user's current status
4. System updates status indicators every 60 seconds
5. User views availability
6. User identifies available colleagues

**Alternative Flows**:
- 4a. User's status changes → Real-time update without refresh
- 6a. User clicks on colleague → Show detailed schedule

---

## 4. FUNCTIONAL REQUIREMENTS SUMMARY

### Critical Features (Must Have - MVP)
1. ✅ User registration with work hours
2. ✅ Basic authentication
3. ✅ Weekly availability input (mouse-based)
4. ✅ Dashboard showing all users
5. ✅ Common time slot calculation
6. ✅ Multiple slots per day support

### Important Features (Should Have - V1.1)
7. ✅ Drag-and-drop schedule editing
8. ✅ Real-time status updates
9. ✅ Conflict detection
10. ✅ Responsive UI with animations

### Nice-to-Have Features (Could Have - V2.0)
11. ⭕ Meeting proposal system
12. ⭕ Calendar export (iCal format)
13. ⭕ Email notifications
14. ⭕ Schedule templates
15. ⭕ Recurring availability patterns

### Out of Scope (Won't Have)
- ❌ Integration with external calendar systems
- ❌ Mobile native apps
- ❌ Video conferencing integration
- ❌ Advanced reporting/analytics
- ❌ Multi-language support
- ❌ LDAP/SSO integration

---

## 5. DATA REQUIREMENTS

### Entities

#### User
- user_id (PK, VARCHAR(20), UNIQUE)
- password_hash (VARCHAR(255))
- default_start_time (TIME)
- default_end_time (TIME)
- created_at (TIMESTAMP)
- last_login (TIMESTAMP)

#### Availability
- availability_id (PK, INTEGER, AUTOINCREMENT)
- user_id (FK → User.user_id)
- day_of_week (INTEGER, 0-6, 0=Monday)
- start_time (TIME)
- end_time (TIME)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### UserStatus (Optional)
- user_id (FK → User.user_id)
- status (ENUM: 'available', 'busy', 'offline')
- last_updated (TIMESTAMP)

### Relationships
- User 1:N Availability (one user has many availability slots)

---

## 6. BUSINESS RULES

### BR-001: Working Hours
- Default working hours: 9:00 - 18:00 (customizable per user)
- Availability slots must be within user's working hours
- Lunch break: 12:00 - 13:00 (recommended to exclude)

### BR-002: User Limits
- Maximum users: 30
- Minimum meeting duration: 15 minutes
- Maximum daily availability slots: unlimited (practical limit ~20)

### BR-003: Time Slot Granularity
- Minimum slot duration: 15 minutes
- Slot boundaries: aligned to :00, :15, :30, :45

### BR-004: Availability Rules
- Slots cannot overlap for same user
- Slots must have start_time < end_time
- Past time slots auto-expire (optional)

### BR-005: Authentication
- Session timeout: 8 hours
- Password requirements: minimum 8 characters
- No password complexity requirements (internal use)

---

## 7. ACCEPTANCE CRITERIA

### System-Level Acceptance
1. ✅ System supports up to 30 concurrent users
2. ✅ Response time < 2 seconds for all operations
3. ✅ Data persists across server restarts
4. ✅ Works on modern browsers (Chrome, Firefox, Safari, Edge)
5. ✅ Mobile responsive (tablets 768px+, phones 375px+)
6. ✅ Basic authentication works on all endpoints
7. ✅ SQLite database < 100MB for 30 users over 1 year

### Feature-Level Acceptance
8. ✅ User can register in < 30 seconds
9. ✅ Availability input feels natural and intuitive
10. ✅ Dashboard loads in < 1 second
11. ✅ Common time slot calculation < 3 seconds
12. ✅ Animations smooth (60fps)
13. ✅ Color scheme is pastel and welcoming

---

## 8. CONSTRAINTS & ASSUMPTIONS

### Technical Constraints
- **Language**: "平易なプログラム言語" (easy/simple programming language)
  - Suggested: Python, JavaScript/Node.js, Ruby, PHP
  - Avoid: Complex frameworks requiring steep learning curve
- **Database**: SQLite (file-based, no server required)
- **Deployment**: docker-compose (containerized)
- **Scale**: ≤ 30 users (small team)
- **Security**: Minimal ("セキュリティ最小限") - internal use only

### Assumptions
1. All users are in the same timezone
2. Network is internal/LAN (no internet access required)
3. Users have basic computer literacy
4. Browser support: last 2 versions of major browsers
5. Data backup is handled externally (not in scope)
6. No concurrent editing conflicts expected (small team)
7. Meeting creation happens outside this system (this is availability only)

### Risks & Dependencies
- **Risk**: SQLite performance with concurrent writes (low risk with ≤30 users)
- **Risk**: Basic Auth security (mitigated by internal-only deployment)
- **Dependency**: Docker runtime environment
- **Dependency**: Modern web browser with JavaScript enabled

---

## NEXT STEPS

1. ✅ Review and approve requirements with stakeholders
2. → Create non-functional requirements specification
3. → Design system architecture
4. → Create UI/UX mockups
5. → Define technical implementation plan
6. → Setup development environment

---

**Document Prepared By**: Requirements Analysis Specialist
**Review Status**: Pending Stakeholder Approval
**Last Updated**: 2025-10-01
