-- Engineering team employees for @Sql tests
-- 実装戦略: テストケース毎のデータ投入 - @Sql

-- Insert engineering department employees
INSERT INTO employees (first_name, last_name, email, hire_date, phone_number, address, active, department_id, created_at, modified_at, version) VALUES
    ('Alice', 'Johnson', 'alice.johnson@company.com', '2023-01-15', '+1-555-0201', '123 Tech St, San Francisco, CA', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Bob', 'Smith', 'bob.smith@company.com', '2023-02-20', '+1-555-0202', '456 Code Ave, San Francisco, CA', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Carol', 'Williams', 'carol.williams@company.com', '2023-03-10', '+1-555-0203', '789 Dev Rd, San Francisco, CA', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('David', 'Brown', 'david.brown@company.com', '2023-04-05', '+1-555-0204', '321 Program Pl, San Francisco, CA', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0),
    ('Eva', 'Davis', 'eva.davis@company.com', '2023-05-12', '+1-555-0205', '654 Software Blvd, San Francisco, CA', true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0);