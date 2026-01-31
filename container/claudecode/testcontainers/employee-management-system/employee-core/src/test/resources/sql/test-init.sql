-- Test database initialization script
-- This script is executed when the test container starts

-- Enable necessary PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone for consistent testing
SET TIME ZONE 'UTC';

-- Create test-specific database objects if needed
-- (Most will be created by Hibernate/JPA)

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Test database initialization completed';
END $$;