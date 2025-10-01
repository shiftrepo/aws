# Database Schema Design - Team Schedule Management System

## Schema Overview

This document defines the complete SQLite database schema for the team schedule management system, optimized for up to 30 concurrent users.

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                     │
│  │    users     │         │    roles     │                     │
│  ├──────────────┤         ├──────────────┤                     │
│  │ id (PK)      │◄────────│ id (PK)      │                     │
│  │ email        │         │ name         │                     │
│  │ password_hash│         │ permissions  │                     │
│  │ role_id (FK) │         └──────────────┘                     │
│  │ first_name   │                                              │
│  │ last_name    │                                              │
│  │ phone        │                                              │
│  │ is_active    │                                              │
│  │ created_at   │                                              │
│  │ updated_at   │                                              │
│  └──────────────┘                                              │
│         │                                                       │
│         │ 1:N                                                   │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────┐         ┌──────────────────┐                │
│  │   shifts     │◄────────│  shift_templates │                │
│  ├──────────────┤    N:1  ├──────────────────┤                │
│  │ id (PK)      │         │ id (PK)          │                │
│  │ user_id (FK) │         │ name             │                │
│  │ template_id  │         │ start_time       │                │
│  │ shift_date   │         │ end_time         │                │
│  │ start_time   │         │ color            │                │
│  │ end_time     │         │ description      │                │
│  │ status       │         │ is_active        │                │
│  │ notes        │         └──────────────────┘                │
│  │ created_by   │                                              │
│  │ created_at   │                                              │
│  │ updated_at   │                                              │
│  └──────────────┘                                              │
│         │                                                       │
│         │ 1:N                                                   │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────┐                                          │
│  │ shift_swaps      │                                          │
│  ├──────────────────┤                                          │
│  │ id (PK)          │                                          │
│  │ shift_id (FK)    │                                          │
│  │ requester_id (FK)│                                          │
│  │ target_id (FK)   │                                          │
│  │ status           │                                          │
│  │ reason           │                                          │
│  │ created_at       │                                          │
│  │ resolved_at      │                                          │
│  └──────────────────┘                                          │
│                                                                 │
│  ┌──────────────────┐         ┌─────────────────┐             │
│  │ notifications    │         │ time_off        │             │
│  ├──────────────────┤         ├─────────────────┤             │
│  │ id (PK)          │         │ id (PK)         │             │
│  │ user_id (FK)     │         │ user_id (FK)    │             │
│  │ type             │         │ start_date      │             │
│  │ title            │         │ end_date        │             │
│  │ message          │         │ type            │             │
│  │ is_read          │         │ status          │             │
│  │ related_id       │         │ reason          │             │
│  │ created_at       │         │ approved_by     │             │
│  └──────────────────┘         │ created_at      │             │
│                                │ updated_at      │             │
│                                └─────────────────┘             │
│                                                                 │
│  ┌──────────────────┐         ┌─────────────────┐             │
│  │ audit_logs       │         │ settings        │             │
│  ├──────────────────┤         ├─────────────────┤             │
│  │ id (PK)          │         │ id (PK)         │             │
│  │ user_id (FK)     │         │ key             │             │
│  │ action           │         │ value           │             │
│  │ table_name       │         │ type            │             │
│  │ record_id        │         │ description     │             │
│  │ old_values       │         │ updated_at      │             │
│  │ new_values       │         └─────────────────┘             │
│  │ ip_address       │                                          │
│  │ timestamp        │                                          │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Table Definitions

### 1. users

Stores user account information and authentication credentials.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL DEFAULT 3,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    avatar_url TEXT,
    preferences TEXT DEFAULT '{}', -- JSON for user preferences
    is_active INTEGER DEFAULT 1,
    last_login_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_last_name ON users(last_name);
```

**Columns:**
- `id`: Primary key, auto-incrementing
- `email`: Unique email address for login
- `password_hash`: Bcrypt hashed password (never store plaintext)
- `role_id`: Foreign key to roles table (1=Admin, 2=Manager, 3=Employee)
- `first_name`, `last_name`: User's full name
- `phone`: Optional contact number
- `avatar_url`: Optional profile picture URL
- `preferences`: JSON field for user-specific settings (theme, notifications, etc.)
- `is_active`: Soft delete flag (1=active, 0=inactive)
- `last_login_at`: Track last successful login
- `created_at`, `updated_at`: Audit timestamps

### 2. roles

Defines user roles and their permissions.

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    permissions TEXT NOT NULL, -- JSON array of permission strings
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed default roles
INSERT INTO roles (id, name, permissions, description) VALUES
(1, 'Admin', '["*"]', 'Full system access'),
(2, 'Manager', '["schedule:read", "schedule:write", "shifts:assign", "users:read", "reports:read"]', 'Schedule management and reporting'),
(3, 'Employee', '["schedule:read", "shifts:swap", "profile:write", "timeoff:request"]', 'View schedule and request changes');

CREATE INDEX idx_roles_name ON roles(name);
```

**Permissions Schema:**
- `schedule:read` - View schedules
- `schedule:write` - Create/edit schedules
- `shifts:assign` - Assign shifts to users
- `shifts:swap` - Request shift swaps
- `users:read` - View user list
- `users:write` - Create/edit users
- `reports:read` - Generate reports
- `timeoff:request` - Request time off
- `*` - All permissions (admin only)

### 3. shift_templates

Pre-defined shift types for quick scheduling.

```sql
CREATE TABLE shift_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_time TEXT NOT NULL, -- Format: HH:MM
    end_time TEXT NOT NULL,   -- Format: HH:MM
    duration_minutes INTEGER GENERATED ALWAYS AS (
        (strftime('%s', end_time) - strftime('%s', start_time)) / 60
    ) STORED,
    color TEXT DEFAULT '#3B82F6', -- Hex color for UI display
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed common shift types
INSERT INTO shift_templates (name, start_time, end_time, color, description) VALUES
('Morning Shift', '06:00', '14:00', '#F59E0B', '8-hour morning shift'),
('Day Shift', '09:00', '17:00', '#3B82F6', '8-hour day shift'),
('Evening Shift', '14:00', '22:00', '#8B5CF6', '8-hour evening shift'),
('Night Shift', '22:00', '06:00', '#1F2937', '8-hour night shift'),
('Split Shift', '09:00', '13:00', '#10B981', '4-hour split shift');

CREATE INDEX idx_shift_templates_active ON shift_templates(is_active);
```

### 4. shifts

Individual shift assignments for users.

```sql
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_id INTEGER,
    shift_date DATE NOT NULL,
    start_time TEXT NOT NULL, -- Format: HH:MM
    end_time TEXT NOT NULL,   -- Format: HH:MM
    status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    notes TEXT,
    created_by INTEGER NOT NULL, -- User ID who created the shift
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES shift_templates(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    -- Constraint: No overlapping shifts for same user
    CONSTRAINT no_overlap UNIQUE (user_id, shift_date, start_time)
);

-- Indexes for performance
CREATE INDEX idx_shifts_user ON shifts(user_id);
CREATE INDEX idx_shifts_date ON shifts(shift_date);
CREATE INDEX idx_shifts_status ON shifts(status);
CREATE INDEX idx_shifts_date_range ON shifts(shift_date, start_time);
CREATE INDEX idx_shifts_user_date ON shifts(user_id, shift_date);

-- Trigger to prevent overlapping shifts
CREATE TRIGGER prevent_overlap_shifts
BEFORE INSERT ON shifts
BEGIN
    SELECT RAISE(ABORT, 'Overlapping shift detected')
    WHERE EXISTS (
        SELECT 1 FROM shifts
        WHERE user_id = NEW.user_id
        AND shift_date = NEW.shift_date
        AND id != NEW.id
        AND (
            (NEW.start_time >= start_time AND NEW.start_time < end_time)
            OR (NEW.end_time > start_time AND NEW.end_time <= end_time)
            OR (NEW.start_time <= start_time AND NEW.end_time >= end_time)
        )
    );
END;
```

### 5. shift_swaps

Manage shift swap requests between employees.

```sql
CREATE TABLE shift_swaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_id INTEGER NOT NULL,
    requester_id INTEGER NOT NULL, -- User requesting the swap
    target_id INTEGER,              -- User being asked to swap (optional)
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')),
    reason TEXT,
    approved_by INTEGER,            -- Manager who approved (if applicable)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (shift_id) REFERENCES shifts(id) ON DELETE CASCADE,
    FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_shift_swaps_status ON shift_swaps(status);
CREATE INDEX idx_shift_swaps_requester ON shift_swaps(requester_id);
CREATE INDEX idx_shift_swaps_target ON shift_swaps(target_id);
```

### 6. time_off

Employee time-off requests and approvals.

```sql
CREATE TABLE time_off (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    type TEXT DEFAULT 'vacation' CHECK(type IN ('vacation', 'sick', 'personal', 'other')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')),
    reason TEXT,
    approved_by INTEGER,
    approval_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    CHECK (end_date >= start_date)
);

CREATE INDEX idx_time_off_user ON time_off(user_id);
CREATE INDEX idx_time_off_dates ON time_off(start_date, end_date);
CREATE INDEX idx_time_off_status ON time_off(status);
```

### 7. notifications

System notifications and alerts for users.

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('shift_assigned', 'shift_changed', 'shift_swap', 'time_off', 'reminder', 'system')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    related_id INTEGER,        -- ID of related entity (shift, swap, etc.)
    related_type TEXT,         -- Type of related entity
    priority TEXT DEFAULT 'normal' CHECK(priority IN ('low', 'normal', 'high', 'urgent')),
    action_url TEXT,           -- Optional URL for action button
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at DESC);
```

### 8. audit_logs

Comprehensive audit trail for security and compliance.

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,         -- e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN'
    table_name TEXT,              -- Table affected
    record_id INTEGER,            -- ID of affected record
    old_values TEXT,              -- JSON of old values
    new_values TEXT,              -- JSON of new values
    ip_address TEXT,
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_table ON audit_logs(table_name);
```

### 9. settings

System-wide configuration settings.

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    type TEXT DEFAULT 'string' CHECK(type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed default settings
INSERT INTO settings (key, value, type, description) VALUES
('schedule_start_day', '0', 'number', 'Week start day (0=Sunday, 1=Monday)'),
('max_hours_per_week', '40', 'number', 'Maximum hours per employee per week'),
('min_hours_between_shifts', '8', 'number', 'Minimum hours between shifts'),
('allow_shift_swaps', 'true', 'boolean', 'Enable shift swap requests'),
('require_swap_approval', 'true', 'boolean', 'Manager approval required for swaps'),
('notification_email_enabled', 'true', 'boolean', 'Send email notifications'),
('schedule_publish_days', '7', 'number', 'Days in advance to publish schedule');

CREATE INDEX idx_settings_key ON settings(key);
```

## Database Triggers

### Update Timestamp Trigger

Automatically update `updated_at` timestamps on modifications.

```sql
-- Users table
CREATE TRIGGER update_users_timestamp
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Shifts table
CREATE TRIGGER update_shifts_timestamp
AFTER UPDATE ON shifts
FOR EACH ROW
BEGIN
    UPDATE shifts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Time off table
CREATE TRIGGER update_time_off_timestamp
AFTER UPDATE ON time_off
FOR EACH ROW
BEGIN
    UPDATE time_off SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Shift templates table
CREATE TRIGGER update_shift_templates_timestamp
AFTER UPDATE ON shift_templates
FOR EACH ROW
BEGIN
    UPDATE shift_templates SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### Notification Trigger

Automatically create notifications for important events.

```sql
-- Notify user when shift is assigned
CREATE TRIGGER notify_shift_assigned
AFTER INSERT ON shifts
FOR EACH ROW
BEGIN
    INSERT INTO notifications (user_id, type, title, message, related_id, related_type)
    VALUES (
        NEW.user_id,
        'shift_assigned',
        'New Shift Assigned',
        'You have been assigned a shift on ' || NEW.shift_date || ' from ' || NEW.start_time || ' to ' || NEW.end_time,
        NEW.id,
        'shift'
    );
END;

-- Notify when shift is changed
CREATE TRIGGER notify_shift_changed
AFTER UPDATE ON shifts
FOR EACH ROW
WHEN OLD.start_time != NEW.start_time OR OLD.end_time != NEW.end_time OR OLD.shift_date != NEW.shift_date
BEGIN
    INSERT INTO notifications (user_id, type, title, message, related_id, related_type)
    VALUES (
        NEW.user_id,
        'shift_changed',
        'Shift Updated',
        'Your shift on ' || NEW.shift_date || ' has been updated',
        NEW.id,
        'shift'
    );
END;

-- Notify on shift swap request
CREATE TRIGGER notify_shift_swap_request
AFTER INSERT ON shift_swaps
FOR EACH ROW
WHEN NEW.target_id IS NOT NULL
BEGIN
    INSERT INTO notifications (user_id, type, title, message, related_id, related_type, priority)
    VALUES (
        NEW.target_id,
        'shift_swap',
        'Shift Swap Request',
        'You have a new shift swap request',
        NEW.id,
        'shift_swap',
        'high'
    );
END;
```

## Database Views

### Current Week Schedule View

```sql
CREATE VIEW view_current_week_schedule AS
SELECT
    s.id,
    s.shift_date,
    s.start_time,
    s.end_time,
    s.status,
    s.notes,
    u.id as user_id,
    u.first_name,
    u.last_name,
    u.email,
    st.name as shift_template_name,
    st.color as shift_color
FROM shifts s
JOIN users u ON s.user_id = u.id
LEFT JOIN shift_templates st ON s.template_id = st.id
WHERE s.shift_date BETWEEN date('now', 'weekday 0', '-7 days') AND date('now', 'weekday 0')
ORDER BY s.shift_date, s.start_time;
```

### User Schedule Summary View

```sql
CREATE VIEW view_user_schedule_summary AS
SELECT
    u.id as user_id,
    u.first_name,
    u.last_name,
    COUNT(s.id) as total_shifts,
    SUM(CASE WHEN s.status = 'completed' THEN 1 ELSE 0 END) as completed_shifts,
    SUM(CASE WHEN s.status = 'scheduled' THEN 1 ELSE 0 END) as upcoming_shifts,
    SUM(CASE WHEN s.status = 'no_show' THEN 1 ELSE 0 END) as missed_shifts
FROM users u
LEFT JOIN shifts s ON u.id = s.user_id
    AND s.shift_date >= date('now', '-30 days')
WHERE u.is_active = 1
GROUP BY u.id;
```

## Migration Scripts

### Initial Migration (001_initial_schema.sql)

```sql
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Create all tables in dependency order
-- (Include all CREATE TABLE statements from above)

-- Create all indexes
-- (Include all CREATE INDEX statements from above)

-- Create all triggers
-- (Include all CREATE TRIGGER statements from above)

-- Create all views
-- (Include all CREATE VIEW statements from above)

-- Insert seed data
-- (Include all INSERT statements from above)
```

## Database Backup Strategy

### Backup Commands

```bash
# Full backup
sqlite3 /data/schedule.db ".backup '/backups/schedule-$(date +%Y%m%d-%H%M%S).db'"

# Export as SQL
sqlite3 /data/schedule.db .dump > /backups/schedule-$(date +%Y%m%d).sql

# Verify backup integrity
sqlite3 /backups/schedule-backup.db "PRAGMA integrity_check;"
```

### Backup Schedule
- Automated daily backups at 2 AM
- Keep last 7 daily backups
- Weekly backups retained for 4 weeks
- Monthly backups retained for 1 year

## Performance Optimization

### Query Optimization Tips

1. **Use Indexes Effectively**
   - All foreign keys are indexed
   - Common filter columns (date, status) are indexed
   - Composite indexes for multi-column queries

2. **Prepared Statements**
   - Use parameterized queries to prevent SQL injection
   - Better query plan caching

3. **Analyze and Optimize**
   ```sql
   ANALYZE; -- Gather statistics
   VACUUM;  -- Reclaim space and defragment
   ```

4. **Connection Pool Settings**
   ```javascript
   const db = new Database('schedule.db', {
     readonly: false,
     fileMustExist: false,
     timeout: 5000,
     verbose: console.log
   });

   // Enable WAL mode for better concurrency
   db.pragma('journal_mode = WAL');
   db.pragma('synchronous = NORMAL');
   db.pragma('cache_size = 10000');
   db.pragma('temp_store = MEMORY');
   ```

## Data Validation Rules

### Business Rules

1. **Shift Assignment**
   - No overlapping shifts for same user
   - Maximum 40 hours per week per user
   - Minimum 8 hours between shifts
   - Cannot assign shifts during approved time-off

2. **Time-Off Requests**
   - Cannot request past dates
   - Maximum 30 consecutive days
   - Must provide reason for sick leave

3. **Shift Swaps**
   - Both users must be active
   - Target user must not have conflicting shift
   - Requires manager approval if enabled in settings

4. **User Management**
   - Email must be unique
   - Password minimum 8 characters
   - Cannot deactivate last admin user

## Database Maintenance

### Regular Maintenance Tasks

```sql
-- Weekly optimization (run during off-hours)
PRAGMA optimize;
ANALYZE;

-- Monthly maintenance
VACUUM;
PRAGMA integrity_check;

-- Check foreign key consistency
PRAGMA foreign_key_check;
```

### Monitoring Queries

```sql
-- Check database size
SELECT page_count * page_size as size_bytes
FROM pragma_page_count(), pragma_page_size();

-- Find slow queries (enable query log first)
SELECT * FROM pragma_stats;

-- Check index usage
SELECT name, tbl_name FROM sqlite_master
WHERE type = 'index'
ORDER BY tbl_name;
```

## Schema Version Control

Track schema changes using migrations table:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_migrations (version, description) VALUES
('001', 'Initial schema creation'),
('002', 'Add shift swap functionality'),
('003', 'Add time-off management');
```
