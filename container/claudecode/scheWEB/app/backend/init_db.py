#!/usr/bin/env python3
"""
Database initialization script for Team Schedule Manager
Creates SQLite database with required tables
"""

import sqlite3
import os
import bcrypt

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/scheduler.db')

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_database():
    """Initialize the database with required tables"""

    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            start_time TEXT NOT NULL,  -- Default work start time (e.g., "09:00")
            end_time TEXT NOT NULL,    -- Default work end time (e.g., "18:00")
            created_at TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create availability table for user's available time slots
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,  -- "monday", "tuesday", etc.
            start_time TEXT NOT NULL,   -- Time in HH:MM format
            end_time TEXT NOT NULL,     -- Time in HH:MM format
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Create meetings table for scheduled meetings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            day_of_week TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    # Create meeting_participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meeting_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'invited',  -- 'invited', 'accepted', 'declined'
            created_at TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(meeting_id, user_id)
        )
    ''')

    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_availability_user_day ON availability (user_id, day_of_week)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_availability_time ON availability (day_of_week, start_time, end_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meetings_day ON meetings (day_of_week)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meeting_participants ON meeting_participants (meeting_id, user_id)')

    # Insert sample data for development/testing - using bcrypt hashed passwords
    sample_users = [
        ("admin", "admin123", "09:00", "18:00"),
        ("user1", "admin123", "09:30", "17:30"),
        ("user2", "admin123", "08:30", "17:00"),
    ]

    for username, password, start_time, end_time in sample_users:
        # Hash the password using bcrypt
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, start_time, end_time, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (username, password_hash, start_time, end_time))

    # Sample availability data - 重複なし、30分刻みで明確に分離
    sample_availability = [
        # admin user (id: 1) - 各曜日に明確に分離された時間帯
        (1, "monday", "09:00", "10:30"),    # 時間帯1
        (1, "monday", "11:00", "12:30"),    # 時間帯2
        (1, "monday", "14:00", "15:30"),    # 時間帯3
        (1, "monday", "16:00", "17:00"),    # 時間帯4
        (1, "tuesday", "09:00", "10:00"),
        (1, "tuesday", "14:00", "15:30"),
        (1, "wednesday", "13:00", "14:30"),
        (1, "wednesday", "15:00", "16:30"),
        (1, "thursday", "10:00", "11:30"),
        (1, "thursday", "14:30", "16:00"),
        (1, "friday", "09:30", "11:00"),
        (1, "friday", "15:00", "17:00"),

        # user1 (id: 2) - 重複なし
        (2, "monday", "08:30", "09:30"),
        (2, "monday", "13:00", "14:00"),
        (2, "monday", "15:30", "17:00"),
        (2, "tuesday", "10:30", "12:00"),
        (2, "tuesday", "13:30", "15:00"),
        (2, "wednesday", "09:00", "10:30"),
        (2, "wednesday", "14:00", "16:00"),
        (2, "thursday", "11:30", "13:00"),
        (2, "friday", "08:30", "10:00"),
        (2, "friday", "13:30", "15:00"),

        # user2 (id: 3) - 重複なし
        (3, "monday", "10:30", "12:00"),
        (3, "monday", "13:30", "14:30"),
        (3, "tuesday", "08:30", "09:30"),
        (3, "tuesday", "11:30", "13:00"),
        (3, "wednesday", "10:00", "11:30"),
        (3, "wednesday", "16:30", "17:30"),
        (3, "thursday", "09:00", "10:00"),
        (3, "thursday", "14:00", "15:30"),
        (3, "friday", "11:00", "12:30"),
        (3, "friday", "16:30", "17:30"),
    ]

    for user_id, day, start_time, end_time in sample_availability:
        cursor.execute('''
            INSERT OR IGNORE INTO availability (user_id, day_of_week, start_time, end_time, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (user_id, day, start_time, end_time))

    conn.commit()
    conn.close()

    print(f"Database initialized successfully at {DATABASE_PATH}")
    print("Sample users created:")
    print("  - admin / admin123 (working hours: 09:00-18:00)")
    print("  - user1 / admin123 (working hours: 09:30-17:30)")
    print("  - user2 / admin123 (working hours: 08:30-17:00)")

if __name__ == "__main__":
    init_database()