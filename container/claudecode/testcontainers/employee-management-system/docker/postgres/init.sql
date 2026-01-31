-- Initialize employee management database
-- This script runs when PostgreSQL container starts for the first time

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS employee_schema;

-- Set default search path
ALTER DATABASE employee_db SET search_path TO public, employee_schema;

-- Create extension for UUID generation (useful for primary keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create extension for full-text search (useful for employee search)
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE employee_db TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA employee_schema TO postgres;

-- Create sequences for auto-increment IDs (Spring will use these)
CREATE SEQUENCE IF NOT EXISTS employee_id_seq START 1000;
CREATE SEQUENCE IF NOT EXISTS department_id_seq START 100;

-- Create audit trigger function for tracking changes
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'Employee Management Database initialization completed successfully';
END $$;