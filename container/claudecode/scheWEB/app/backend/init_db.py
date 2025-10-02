#!/usr/bin/env python3
"""
Database initialization script for Team Schedule Manager
Creates SQLite database with required tables
"""

import sqlite3
import os

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/scheduler.db')

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

    # Insert sample data for development/testing
    sample_users = [
        ("admin", "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkY4u2QNuP1YtlW", "09:00", "18:00"),  # password: admin123
        ("user1", "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkY4u2QNuP1YtlW", "09:30", "17:30"),  # password: admin123
        ("user2", "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkY4u2QNuP1YtlW", "08:30", "17:00"),  # password: admin123
    ]

    for username, password_hash, start_time, end_time in sample_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, start_time, end_time, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        ''', (username, password_hash, start_time, end_time))

    # Sample availability data
    sample_availability = [
        # admin user (id: 1)
        (1, "monday", "10:00", "12:00"),
        (1, "monday", "14:00", "16:00"),
        (1, "tuesday", "09:00", "11:00"),
        (1, "wednesday", "13:00", "15:00"),
        (1, "thursday", "10:00", "12:00"),
        (1, "friday", "14:00", "17:00"),

        # user1 (id: 2)
        (2, "monday", "10:00", "12:00"),
        (2, "monday", "15:00", "17:00"),
        (2, "tuesday", "09:30", "11:30"),
        (2, "wednesday", "14:00", "16:00"),
        (2, "thursday", "10:30", "12:30"),
        (2, "friday", "13:00", "15:00"),

        # user2 (id: 3)
        (3, "monday", "11:00", "12:00"),
        (3, "tuesday", "10:00", "11:00"),
        (3, "wednesday", "14:30", "16:30"),
        (3, "thursday", "11:00", "12:00"),
        (3, "friday", "14:00", "16:00"),
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