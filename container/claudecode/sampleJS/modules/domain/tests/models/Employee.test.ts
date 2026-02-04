import { describe, it, expect } from 'vitest';
import { Employee } from '../../src/models/Employee';

describe('Employee', () => {
  const validProps = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    department: 'Engineering',
    position: 'Senior Developer',
    hireDate: new Date('2023-01-01'),
  };

  describe('create', () => {
    it('should create a valid employee', () => {
      const employee = Employee.create(validProps);

      expect(employee.name).toBe('John Doe');
      expect(employee.email).toBe('john.doe@example.com');
      expect(employee.department).toBe('Engineering');
      expect(employee.position).toBe('Senior Developer');
      expect(employee.hireDate).toEqual(new Date('2023-01-01'));
      expect(employee.id).toBeDefined();
    });

    it('should create employee with provided id', () => {
      const employee = Employee.create({ ...validProps, id: 'EMP-123' });

      expect(employee.id).toBe('EMP-123');
    });

    it('should throw error for empty name', () => {
      expect(() => Employee.create({ ...validProps, name: '' })).toThrow('Employee name is required');
    });

    it('should throw error for name exceeding 100 characters', () => {
      const longName = 'a'.repeat(101);
      expect(() => Employee.create({ ...validProps, name: longName })).toThrow('must not exceed 100 characters');
    });

    it('should throw error for empty department', () => {
      expect(() => Employee.create({ ...validProps, department: '' })).toThrow('Department is required');
    });

    it('should throw error for empty position', () => {
      expect(() => Employee.create({ ...validProps, position: '' })).toThrow('Position is required');
    });

    it('should throw error for invalid email', () => {
      expect(() => Employee.create({ ...validProps, email: 'invalid-email' })).toThrow('Invalid email address');
    });

    it('should throw error for future hire date', () => {
      const futureDate = new Date();
      futureDate.setFullYear(futureDate.getFullYear() + 1);

      expect(() => Employee.create({ ...validProps, hireDate: futureDate })).toThrow('Hire date cannot be in the future');
    });
  });

  describe('update methods', () => {
    it('should update name', () => {
      const employee = Employee.create(validProps);
      employee.updateName('Jane Doe');

      expect(employee.name).toBe('Jane Doe');
    });

    it('should update email', () => {
      const employee = Employee.create(validProps);
      employee.updateEmail('jane.doe@example.com');

      expect(employee.email).toBe('jane.doe@example.com');
    });

    it('should update department', () => {
      const employee = Employee.create(validProps);
      employee.updateDepartment('Marketing');

      expect(employee.department).toBe('Marketing');
    });

    it('should update position', () => {
      const employee = Employee.create(validProps);
      employee.updatePosition('Lead Developer');

      expect(employee.position).toBe('Lead Developer');
    });

    it('should throw error when updating with invalid name', () => {
      const employee = Employee.create(validProps);

      expect(() => employee.updateName('')).toThrow('Employee name is required');
    });
  });

  describe('toJSON and fromJSON', () => {
    it('should serialize to JSON', () => {
      const employee = Employee.create(validProps);
      const json = employee.toJSON();

      expect(json.id).toBeDefined();
      expect(json.name).toBe('John Doe');
      expect(json.email).toBe('john.doe@example.com');
      expect(json.department).toBe('Engineering');
      expect(json.position).toBe('Senior Developer');
      expect(json.hireDate).toBe('2023-01-01T00:00:00.000Z');
    });

    it('should deserialize from JSON', () => {
      const json = {
        id: 'EMP-123',
        name: 'John Doe',
        email: 'john.doe@example.com',
        department: 'Engineering',
        position: 'Senior Developer',
        hireDate: '2023-01-01T00:00:00.000Z',
      };

      const employee = Employee.fromJSON(json);

      expect(employee.id).toBe('EMP-123');
      expect(employee.name).toBe('John Doe');
      expect(employee.email).toBe('john.doe@example.com');
    });

    it('should maintain data integrity through serialization cycle', () => {
      const original = Employee.create(validProps);
      const json = original.toJSON();
      const restored = Employee.fromJSON(json);

      expect(restored.name).toBe(original.name);
      expect(restored.email).toBe(original.email);
      expect(restored.department).toBe(original.department);
      expect(restored.position).toBe(original.position);
    });
  });
});
