-- Small company scenario for pattern data switching
-- 実装戦略: パターンデータの切替 - SQLファイル分離

-- Small company setup (10-50 employees, 3-7 departments)
DELETE FROM employees;
DELETE FROM departments;

-- Small company departments
INSERT INTO departments (id, name, code, budget, description, active, created_at, modified_at, version) VALUES
    (1, 'General Management', 'GM', 800000.00, 'General Management', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (2, 'Development', 'DEV', 1200000.00, 'Software Development', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    (3, 'Sales & Marketing', 'SM', 600000.00, 'Sales and Marketing', true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0);

-- Small company employees (15 total)
INSERT INTO employees (first_name, last_name, email, hire_date, active, department_id, created_at, modified_at, version) VALUES
    -- Management (2 employees)
    ('John', 'CEO', 'john.ceo@smallco.com', '2020-01-01', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Jane', 'COO', 'jane.coo@smallco.com', '2020-02-01', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),

    -- Development (8 employees)
    ('Alice', 'Developer1', 'alice.dev1@smallco.com', '2021-03-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Bob', 'Developer2', 'bob.dev2@smallco.com', '2021-04-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Carol', 'Developer3', 'carol.dev3@smallco.com', '2021-05-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Dave', 'Developer4', 'dave.dev4@smallco.com', '2022-01-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Eva', 'Developer5', 'eva.dev5@smallco.com', '2022-02-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Frank', 'Developer6', 'frank.dev6@smallco.com', '2022-03-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Grace', 'Developer7', 'grace.dev7@smallco.com', '2023-01-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Henry', 'Developer8', 'henry.dev8@smallco.com', '2023-02-01', true, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),

    -- Sales & Marketing (5 employees)
    ('Ivy', 'Sales1', 'ivy.sales1@smallco.com', '2021-06-01', true, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Jack', 'Sales2', 'jack.sales2@smallco.com', '2021-07-01', true, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Kate', 'Marketing1', 'kate.mkt1@smallco.com', '2022-04-01', true, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Leo', 'Marketing2', 'leo.mkt2@smallco.com', '2022-05-01', true, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Maya', 'Sales3', 'maya.sales3@smallco.com', '2023-03-01', true, 3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0);

-- Reset sequences
SELECT setval('departments_id_seq', 3, true);
SELECT setval('employees_id_seq', (SELECT MAX(id) FROM employees), true);