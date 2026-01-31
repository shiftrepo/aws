-- Test data for employee management system
-- This script inserts sample data for development and testing

-- Note: The actual tables will be created by Spring Boot JPA/Hibernate
-- This script will be executed after the application creates the schema

-- Insert sample departments (will be inserted by application after tables are created)
-- Keeping this file for reference and future manual data insertion

-- Sample departments:
-- INSERT INTO departments (id, name, code, budget, created_at, modified_at) VALUES
-- (1, 'Human Resources', 'HR', 1000000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
-- (2, 'Information Technology', 'IT', 2000000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
-- (3, 'Finance', 'FIN', 1500000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
-- (4, 'Marketing', 'MKT', 800000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Sample employees:
-- INSERT INTO employees (id, first_name, last_name, email, hire_date, department_id, created_at, modified_at) VALUES
-- (1, 'John', 'Doe', 'john.doe@company.com', '2023-01-15', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
-- (2, 'Jane', 'Smith', 'jane.smith@company.com', '2023-02-20', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
-- (3, 'Bob', 'Johnson', 'bob.johnson@company.com', '2023-03-10', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
-- (4, 'Alice', 'Brown', 'alice.brown@company.com', '2023-04-05', 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Test data script loaded (tables will be created by Spring Boot)';
END $$;