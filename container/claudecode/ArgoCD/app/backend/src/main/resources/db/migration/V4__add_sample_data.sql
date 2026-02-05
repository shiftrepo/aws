-- Insert sample organizations
INSERT INTO organizations (code, name, description, established_date, active) VALUES
('ORG001', 'Acme Corporation', 'Leading technology company', '2010-01-15', TRUE),
('ORG002', 'TechStart Inc', 'Innovative startup', '2018-06-01', TRUE),
('ORG003', 'Global Services Ltd', 'International service provider', '2005-03-20', TRUE);

-- Insert sample departments for Acme Corporation
INSERT INTO departments (organization_id, parent_department_id, code, name, description, active) VALUES
((SELECT id FROM organizations WHERE code = 'ORG001'), NULL, 'ENG', 'Engineering', 'Product engineering division', TRUE),
((SELECT id FROM organizations WHERE code = 'ORG001'), NULL, 'HR', 'Human Resources', 'People operations', TRUE),
((SELECT id FROM organizations WHERE code = 'ORG001'), NULL, 'SALES', 'Sales', 'Sales and marketing', TRUE);

-- Insert sub-departments
INSERT INTO departments (organization_id, parent_department_id, code, name, description, active) VALUES
((SELECT id FROM organizations WHERE code = 'ORG001'),
 (SELECT id FROM departments WHERE code = 'ENG' AND organization_id = (SELECT id FROM organizations WHERE code = 'ORG001')),
 'ENG-BE', 'Backend Engineering', 'Backend development team', TRUE),
((SELECT id FROM organizations WHERE code = 'ORG001'),
 (SELECT id FROM departments WHERE code = 'ENG' AND organization_id = (SELECT id FROM organizations WHERE code = 'ORG001')),
 'ENG-FE', 'Frontend Engineering', 'Frontend development team', TRUE);

-- Insert sample users
INSERT INTO users (department_id, employee_number, username, email, first_name, last_name, active) VALUES
((SELECT id FROM departments WHERE code = 'ENG-BE' LIMIT 1), 'EMP001', 'john.doe', 'john.doe@acme.com', 'John', 'Doe', TRUE),
((SELECT id FROM departments WHERE code = 'ENG-FE' LIMIT 1), 'EMP002', 'jane.smith', 'jane.smith@acme.com', 'Jane', 'Smith', TRUE),
((SELECT id FROM departments WHERE code = 'HR' LIMIT 1), 'EMP003', 'bob.wilson', 'bob.wilson@acme.com', 'Bob', 'Wilson', TRUE);
