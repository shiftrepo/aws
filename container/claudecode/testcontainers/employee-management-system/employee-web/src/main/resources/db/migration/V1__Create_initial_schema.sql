-- Initial schema creation for Employee Management System
-- This script creates the database structure for employees and departments

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    budget DECIMAL(12,2) NOT NULL CHECK (budget > 0),
    description VARCHAR(500),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0
);

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    hire_date DATE NOT NULL,
    phone_number VARCHAR(15),
    address VARCHAR(200),
    active BOOLEAN NOT NULL DEFAULT true,
    department_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version BIGINT NOT NULL DEFAULT 0,

    CONSTRAINT fk_employee_department FOREIGN KEY (department_id)
        REFERENCES departments(id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_departments_code ON departments(code);
CREATE INDEX IF NOT EXISTS idx_departments_active ON departments(active);
CREATE INDEX IF NOT EXISTS idx_departments_name ON departments(name);
CREATE INDEX IF NOT EXISTS idx_departments_budget ON departments(budget);

CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_active ON employees(active);
CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date ON employees(hire_date);
CREATE INDEX IF NOT EXISTS idx_employees_name ON employees(last_name, first_name);

-- Create full-text search indexes (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_employees_fulltext ON employees
    USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || COALESCE(email, '')));

-- Create trigger function to automatically update modified_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_departments_modified_at ON departments;
CREATE TRIGGER update_departments_modified_at
    BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS update_employees_modified_at ON employees;
CREATE TRIGGER update_employees_modified_at
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Insert initial sample data for development and testing
INSERT INTO departments (id, name, code, budget, description, active) VALUES
(1, 'Human Resources', 'HR', 1000000.00, 'Manages employee relations and company policies', true),
(2, 'Information Technology', 'IT', 2000000.00, 'Handles technology infrastructure and software development', true),
(3, 'Finance', 'FIN', 1500000.00, 'Manages company finances and accounting', true),
(4, 'Marketing', 'MKT', 800000.00, 'Handles marketing campaigns and brand management', true),
(5, 'Operations', 'OPS', 1200000.00, 'Manages day-to-day business operations', true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO employees (id, first_name, last_name, email, hire_date, phone_number, address, active, department_id) VALUES
(1, 'John', 'Doe', 'john.doe@company.com', '2023-01-15', '+1-555-0101', '123 Main St, City, State', true, 1),
(2, 'Jane', 'Smith', 'jane.smith@company.com', '2023-02-20', '+1-555-0102', '456 Oak Ave, City, State', true, 2),
(3, 'Bob', 'Johnson', 'bob.johnson@company.com', '2023-03-10', '+1-555-0103', '789 Pine Rd, City, State', true, 2),
(4, 'Alice', 'Brown', 'alice.brown@company.com', '2023-04-05', '+1-555-0104', '321 Elm St, City, State', true, 3),
(5, 'Charlie', 'Davis', 'charlie.davis@company.com', '2023-05-12', '+1-555-0105', '654 Maple Dr, City, State', true, 4),
(6, 'Diana', 'Wilson', 'diana.wilson@company.com', '2022-08-20', '+1-555-0106', '987 Cedar Ln, City, State', true, 5),
(7, 'Frank', 'Miller', 'frank.miller@company.com', '2022-11-30', '+1-555-0107', '147 Birch Ct, City, State', true, 2),
(8, 'Grace', 'Taylor', 'grace.taylor@company.com', '2024-01-08', '+1-555-0108', '258 Willow Way, City, State', true, 1),
(9, 'Henry', 'Anderson', 'henry.anderson@company.com', '2021-07-15', '+1-555-0109', '369 Spruce St, City, State', true, 3),
(10, 'Ivy', 'Thomas', 'ivy.thomas@company.com', '2024-03-22', '+1-555-0110', '741 Aspen Ave, City, State', true, NULL)
ON CONFLICT (id) DO NOTHING;

-- Reset sequences to continue from the inserted data
SELECT setval('departments_id_seq', COALESCE((SELECT MAX(id) FROM departments), 1), true);
SELECT setval('employees_id_seq', COALESCE((SELECT MAX(id) FROM employees), 1), true);

-- Add constraints and checks
ALTER TABLE departments ADD CONSTRAINT chk_departments_name_not_empty
    CHECK (LENGTH(TRIM(name)) > 0);

ALTER TABLE departments ADD CONSTRAINT chk_departments_code_not_empty
    CHECK (LENGTH(TRIM(code)) > 0);

ALTER TABLE employees ADD CONSTRAINT chk_employees_first_name_not_empty
    CHECK (LENGTH(TRIM(first_name)) > 0);

ALTER TABLE employees ADD CONSTRAINT chk_employees_last_name_not_empty
    CHECK (LENGTH(TRIM(last_name)) > 0);

ALTER TABLE employees ADD CONSTRAINT chk_employees_email_not_empty
    CHECK (LENGTH(TRIM(email)) > 0);

ALTER TABLE employees ADD CONSTRAINT chk_employees_hire_date_not_future
    CHECK (hire_date <= CURRENT_DATE);

-- Create views for common queries
CREATE OR REPLACE VIEW active_departments AS
    SELECT d.*,
           COUNT(e.id) as employee_count,
           COALESCE(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date))), 0) as avg_years_service
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id AND e.active = true
    WHERE d.active = true
    GROUP BY d.id, d.name, d.code, d.budget, d.description, d.active, d.created_at, d.modified_at, d.version;

CREATE OR REPLACE VIEW active_employees_with_department AS
    SELECT e.*,
           d.name as department_name,
           d.code as department_code,
           d.budget as department_budget,
           EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date)) as years_service
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE e.active = true;

-- Create function for employee statistics
CREATE OR REPLACE FUNCTION get_employee_stats(dept_id BIGINT DEFAULT NULL)
RETURNS TABLE (
    total_employees BIGINT,
    active_employees BIGINT,
    avg_years_service NUMERIC,
    newest_hire_date DATE,
    oldest_hire_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_employees,
        COUNT(CASE WHEN e.active THEN 1 END)::BIGINT as active_employees,
        AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, e.hire_date))) as avg_years_service,
        MAX(e.hire_date) as newest_hire_date,
        MIN(e.hire_date) as oldest_hire_date
    FROM employees e
    WHERE (dept_id IS NULL OR e.department_id = dept_id);
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE departments IS 'Organizational departments within the company';
COMMENT ON TABLE employees IS 'Company employees with their personal and professional information';
COMMENT ON FUNCTION get_employee_stats IS 'Returns statistical information about employees, optionally filtered by department';
COMMENT ON VIEW active_departments IS 'Active departments with employee count and average years of service';
COMMENT ON VIEW active_employees_with_department IS 'Active employees with their department information and years of service';