export interface Organization {
  code: string;
  name: string;
  description?: string;
  active: boolean;
}

export interface Department {
  code: string;
  name: string;
  description?: string;
  parentId?: number;
  organizationId?: number;
  active: boolean;
}

export interface User {
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  departmentId?: number;
  active: boolean;
}

export const sampleOrganizations: Organization[] = [
  {
    code: 'ORG001',
    name: 'Test Organization Alpha',
    description: 'Primary test organization for E2E testing',
    active: true,
  },
  {
    code: 'ORG002',
    name: 'Test Organization Beta',
    description: 'Secondary test organization',
    active: true,
  },
  {
    code: 'ORG003',
    name: 'Test Organization Gamma',
    description: 'Inactive organization for testing',
    active: false,
  },
];

export const sampleDepartments: Department[] = [
  {
    code: 'DEPT001',
    name: 'Engineering Department',
    description: 'Main engineering department',
    active: true,
  },
  {
    code: 'DEPT002',
    name: 'Human Resources',
    description: 'HR department',
    active: true,
  },
  {
    code: 'DEPT003',
    name: 'Frontend Team',
    description: 'Sub-department under Engineering',
    active: true,
  },
  {
    code: 'DEPT004',
    name: 'Backend Team',
    description: 'Sub-department under Engineering',
    active: true,
  },
];

export const sampleUsers: User[] = [
  {
    username: 'john.doe',
    email: 'john.doe@example.com',
    firstName: 'John',
    lastName: 'Doe',
    active: true,
  },
  {
    username: 'jane.smith',
    email: 'jane.smith@example.com',
    firstName: 'Jane',
    lastName: 'Smith',
    active: true,
  },
  {
    username: 'bob.wilson',
    email: 'bob.wilson@example.com',
    firstName: 'Bob',
    lastName: 'Wilson',
    active: false,
  },
];

export const invalidData = {
  organizations: [
    { code: '', name: 'Invalid Org', description: 'Empty code', active: true },
    { code: 'ORG', name: '', description: 'Empty name', active: true },
  ],
  departments: [
    { code: '', name: 'Invalid Dept', description: 'Empty code', active: true },
    { code: 'DEPT', name: '', description: 'Empty name', active: true },
  ],
  users: [
    { username: '', email: 'test@example.com', firstName: 'Test', lastName: 'User', active: true },
    { username: 'testuser', email: '', firstName: 'Test', lastName: 'User', active: true },
    { username: 'testuser', email: 'invalid-email', firstName: 'Test', lastName: 'User', active: true },
  ],
};

export function generateRandomOrg(): Organization {
  const timestamp = Date.now();
  return {
    code: `ORG${timestamp}`,
    name: `Test Organization ${timestamp}`,
    description: `Auto-generated test organization at ${new Date().toISOString()}`,
    active: true,
  };
}

export function generateRandomDept(): Department {
  const timestamp = Date.now();
  return {
    code: `DEPT${timestamp}`,
    name: `Test Department ${timestamp}`,
    description: `Auto-generated test department at ${new Date().toISOString()}`,
    active: true,
  };
}

export function generateRandomUser(): User {
  const timestamp = Date.now();
  return {
    username: `user${timestamp}`,
    email: `user${timestamp}@example.com`,
    firstName: `FirstName${timestamp}`,
    lastName: `LastName${timestamp}`,
    active: true,
  };
}
