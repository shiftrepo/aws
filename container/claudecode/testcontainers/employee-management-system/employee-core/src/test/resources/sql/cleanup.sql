-- Cleanup script for test data
-- Used to clean up test data after test execution

-- Disable foreign key checks temporarily (PostgreSQL way)
SET session_replication_role = replica;

-- Delete test data in order to respect foreign key constraints
DELETE FROM employees WHERE email LIKE '%@test.com' OR email LIKE '%@company.com' OR email LIKE '%test%';
DELETE FROM departments WHERE code IN ('HR', 'IT', 'FIN', 'MKT', 'OPS', 'RND', 'CS', 'QA', 'LEG', 'FAC');

-- Alternative: Delete all data (use with caution)
-- TRUNCATE TABLE employees RESTART IDENTITY CASCADE;
-- TRUNCATE TABLE departments RESTART IDENTITY CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- Reset sequences to start from 1
ALTER SEQUENCE IF EXISTS employees_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS departments_id_seq RESTART WITH 1;

-- Optional: Reset all sequences in the database
DO $$
DECLARE
    seq_record RECORD;
BEGIN
    FOR seq_record IN
        SELECT schemaname, sequencename
        FROM pg_sequences
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ALTER SEQUENCE ' || seq_record.schemaname || '.' || seq_record.sequencename || ' RESTART WITH 1';
    END LOOP;
END $$;