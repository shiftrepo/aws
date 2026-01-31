-- Basic departments setup for @Sql tests
-- 実装戦略: テストケース毎のデータ投入 - @Sql

-- Clean existing data
DELETE FROM employees;
DELETE FROM departments;

-- Insert basic departments
INSERT INTO departments (id, name, code, budget, description, active, created_at, modified_at, version) VALUES
    (1, 'Engineering', 'ENG', 5000000.00, 'Software Engineering Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (2, 'Sales', 'SALES', 3000000.00, 'Sales Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (3, 'Marketing', 'MKT', 2000000.00, 'Marketing Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (4, 'Human Resources', 'HR', 1500000.00, 'Human Resources Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (5, 'Finance', 'FIN', 2500000.00, 'Finance Department', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0);

-- Reset sequences
SELECT setval('departments_id_seq', 5, true);
SELECT setval('employees_id_seq', 1, false);