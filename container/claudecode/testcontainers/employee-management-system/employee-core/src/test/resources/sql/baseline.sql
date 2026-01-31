-- Baseline test data for consistent test execution
-- This data is loaded for tests that require a consistent starting point

-- Insert baseline departments
INSERT INTO departments (id, name, code, budget, description, active, created_at, modified_at, version) VALUES
(1, 'Human Resources', 'HR', 1000000.00, 'Human Resources Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
(2, 'Information Technology', 'IT', 2000000.00, 'Information Technology Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
(3, 'Finance', 'FIN', 1500000.00, 'Finance Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    budget = EXCLUDED.budget,
    description = EXCLUDED.description,
    active = EXCLUDED.active,
    modified_at = CURRENT_TIMESTAMP,
    version = departments.version + 1;

-- Insert baseline employees
INSERT INTO employees (id, first_name, last_name, email, hire_date, phone_number, address, active, department_id, created_at, modified_at, version) VALUES
(1, 'John', 'Doe', 'john.doe@baseline.com', '2023-01-15', '+1-555-0001', '1 Baseline St, Test City, TC', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
(2, 'Jane', 'Smith', 'jane.smith@baseline.com', '2023-02-20', '+1-555-0002', '2 Baseline Ave, Test City, TC', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
(3, 'Bob', 'Johnson', 'bob.johnson@baseline.com', '2023-03-10', '+1-555-0003', '3 Baseline Rd, Test City, TC', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
ON CONFLICT (id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    hire_date = EXCLUDED.hire_date,
    phone_number = EXCLUDED.phone_number,
    address = EXCLUDED.address,
    active = EXCLUDED.active,
    department_id = EXCLUDED.department_id,
    modified_at = CURRENT_TIMESTAMP,
    version = employees.version + 1;

-- Reset sequences to continue from inserted data
SELECT setval('departments_id_seq', GREATEST(3, (SELECT COALESCE(MAX(id), 0) FROM departments)));
SELECT setval('employees_id_seq', GREATEST(3, (SELECT COALESCE(MAX(id), 0) FROM employees)));