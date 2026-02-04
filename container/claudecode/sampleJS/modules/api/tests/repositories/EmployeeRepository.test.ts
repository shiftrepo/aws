import { describe, it, expect, beforeAll, afterEach, afterAll } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { EmployeeRepository } from '../../src/repositories/EmployeeRepository';
import { ApiClient } from '../../src/client/apiClient';

const mockEmployees = [
  {
    id: 'EMP-1',
    name: 'John Doe',
    email: 'john.doe@example.com',
    department: 'Engineering',
    position: 'Senior Developer',
    hireDate: '2023-01-01T00:00:00.000Z',
  },
  {
    id: 'EMP-2',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    department: 'Marketing',
    position: 'Marketing Manager',
    hireDate: '2023-02-01T00:00:00.000Z',
  },
];

const handlers = [
  http.get('/api/employees', () => {
    return HttpResponse.json(mockEmployees);
  }),

  http.get('/api/employees/:id', ({ params }) => {
    const employee = mockEmployees.find((e) => e.id === params.id);
    if (!employee) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json(employee);
  }),

  http.post('/api/employees', async ({ request }) => {
    const body = await request.json() as any;
    const newEmployee = {
      id: 'EMP-NEW',
      ...body,
    };
    return HttpResponse.json(newEmployee, { status: 201 });
  }),

  http.put('/api/employees/:id', async ({ params, request }) => {
    const body = await request.json() as any;
    const employee = mockEmployees.find((e) => e.id === params.id);
    if (!employee) {
      return new HttpResponse(null, { status: 404 });
    }
    const updated = { ...employee, ...body };
    return HttpResponse.json(updated);
  }),

  http.delete('/api/employees/:id', ({ params }) => {
    const employee = mockEmployees.find((e) => e.id === params.id);
    if (!employee) {
      return new HttpResponse(null, { status: 404 });
    }
    return new HttpResponse(null, { status: 204 });
  }),
];

const server = setupServer(...handlers);

describe('EmployeeRepository', () => {
  let repository: EmployeeRepository;

  beforeAll(() => {
    server.listen({ onUnhandledRequest: 'error' });
    const apiClient = new ApiClient({ baseURL: '/api' });
    repository = new EmployeeRepository(apiClient);
  });

  afterEach(() => {
    server.resetHandlers();
  });

  afterAll(() => {
    server.close();
  });

  describe('findAll', () => {
    it('should return all employees', async () => {
      const employees = await repository.findAll();

      expect(employees).toHaveLength(2);
      expect(employees[0].name).toBe('John Doe');
      expect(employees[1].name).toBe('Jane Smith');
    });
  });

  describe('findById', () => {
    it('should return employee by id', async () => {
      const employee = await repository.findById('EMP-1');

      expect(employee).not.toBeNull();
      expect(employee?.name).toBe('John Doe');
      expect(employee?.email).toBe('john.doe@example.com');
    });

    it('should return null for non-existent employee', async () => {
      const employee = await repository.findById('EMP-999');

      expect(employee).toBeNull();
    });
  });

  describe('create', () => {
    it('should create a new employee', async () => {
      const props = {
        name: 'New Employee',
        email: 'new@example.com',
        department: 'Sales',
        position: 'Sales Rep',
        hireDate: new Date('2023-03-01'),
      };

      const employee = await repository.create(props);

      expect(employee.id).toBe('EMP-NEW');
      expect(employee.name).toBe('New Employee');
      expect(employee.email).toBe('new@example.com');
    });
  });

  describe('update', () => {
    it('should update an existing employee', async () => {
      const props = {
        name: 'Updated Name',
        position: 'Lead Developer',
      };

      const employee = await repository.update('EMP-1', props);

      expect(employee.name).toBe('Updated Name');
      expect(employee.position).toBe('Lead Developer');
    });
  });

  describe('delete', () => {
    it('should delete an employee', async () => {
      await expect(repository.delete('EMP-1')).resolves.toBeUndefined();
    });
  });
});
