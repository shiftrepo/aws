-- Large enterprise scenario for pattern data switching
-- 実装戦略: パターンデータの切替 - SQLファイル分離

-- Large enterprise setup (500+ employees, 10+ departments)
DELETE FROM employees;
DELETE FROM departments;

-- Large enterprise departments
INSERT INTO departments (id, name, code, budget, description, active, created_at, modified_at, version) VALUES
    (1, 'Executive Management', 'EXEC', 10000000.00, 'Executive Management', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (2, 'Engineering', 'ENG', 25000000.00, 'Software Engineering', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (3, 'Product Management', 'PM', 8000000.00, 'Product Management', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (4, 'Sales', 'SALES', 15000000.00, 'Sales Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (5, 'Marketing', 'MKT', 12000000.00, 'Marketing Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (6, 'Human Resources', 'HR', 6000000.00, 'Human Resources', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (7, 'Finance', 'FIN', 8000000.00, 'Finance Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (8, 'Legal', 'LEG', 5000000.00, 'Legal Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (9, 'Operations', 'OPS', 18000000.00, 'Operations', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (10, 'Customer Support', 'CS', 7000000.00, 'Customer Support', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (11, 'Research & Development', 'RND', 20000000.00, 'R&D Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (12, 'Quality Assurance', 'QA', 9000000.00, 'Quality Assurance', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0);

-- Generate large number of employees using SQL
-- Executive Management (10 employees)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version)
SELECT
    'Executive' || generate_series,
    'Leader' || generate_series,
    'exec' || generate_series || '@enterprise.com',
    '2015-01-01'::date + (generate_series * 30),
    true,
    1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    0
FROM generate_series(1, 10);

-- Engineering (200 employees)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version)
SELECT
    'Engineer' || generate_series,
    'Code' || generate_series,
    'eng' || generate_series || '@enterprise.com',
    '2018-01-01'::date + (generate_series * 10),
    true,
    2,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    0
FROM generate_series(1, 200);

-- Product Management (50 employees)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version)
SELECT
    'Product' || generate_series,
    'Manager' || generate_series,
    'pm' || generate_series || '@enterprise.com',
    '2017-01-01'::date + (generate_series * 20),
    true,
    3,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    0
FROM generate_series(1, 50);

-- Sales (120 employees)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version)
SELECT
    'Sales' || generate_series,
    'Rep' || generate_series,
    'sales' || generate_series || '@enterprise.com',
    '2019-01-01'::date + (generate_series * 15),
    true,
    4,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    0
FROM generate_series(1, 120);

-- Marketing (80 employees)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version)
SELECT
    'Marketing' || generate_series,
    'Specialist' || generate_series,
    'mkt' || generate_series || '@enterprise.com',
    '2020-01-01'::date + (generate_series * 12),
    true,
    5,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    0
FROM generate_series(1, 80);

-- Continue for other departments with appropriate sizes...
-- HR (30 employees)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version)
SELECT
    'HR' || generate_series,
    'Professional' || generate_series,
    'hr' || generate_series || '@enterprise.com',
    '2018-06-01'::date + (generate_series * 25),
    true,
    6,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP,
    0
FROM generate_series(1, 30);

-- Reset sequences
SELECT setval('departments_id_seq', 12, true);
SELECT setval('employees_id_seq', (SELECT MAX(id) FROM employees), true);