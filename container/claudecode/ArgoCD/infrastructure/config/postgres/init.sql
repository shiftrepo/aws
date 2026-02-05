-- PostgreSQL Initialization Script
-- This script runs automatically when the database is first created

-- Create the organization management database
CREATE DATABASE orgmgmt;

-- Grant all privileges to the application user
GRANT ALL PRIVILEGES ON DATABASE orgmgmt TO orgmgmt_user;

-- Connect to the orgmgmt database
\c orgmgmt;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO orgmgmt_user;

-- Create initial audit table (optional)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(50) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant table permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO orgmgmt_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO orgmgmt_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO orgmgmt_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO orgmgmt_user;

-- Log initialization
INSERT INTO audit_log (table_name, operation, new_data, changed_by)
VALUES ('database', 'INITIALIZE', '{"message": "Database initialized successfully"}', 'system');

-- Display confirmation message
DO $$
BEGIN
    RAISE NOTICE 'Database orgmgmt initialized successfully';
    RAISE NOTICE 'User orgmgmt_user has been granted all privileges';
END $$;
