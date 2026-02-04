import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Employee } from '@samplejs/domain';
import { CreateEmployeeUseCase } from '../../src/usecases/CreateEmployeeUseCase';
import { IEmployeeRepository } from '../../src/ports/IEmployeeRepository';

describe('CreateEmployeeUseCase', () => {
  let mockRepository: IEmployeeRepository;
  let useCase: CreateEmployeeUseCase;

  beforeEach(() => {
    mockRepository = {
      findAll: vi.fn(),
      findById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    };
    useCase = new CreateEmployeeUseCase(mockRepository);
  });

  it('should create a new employee', async () => {
    const employeeProps = {
      name: 'John Doe',
      email: 'john.doe@example.com',
      department: 'Engineering',
      position: 'Senior Developer',
      hireDate: new Date('2023-01-01'),
    };

    const mockEmployee = Employee.create({ ...employeeProps, id: 'EMP-123' });
    vi.mocked(mockRepository.create).mockResolvedValue(mockEmployee);

    const result = await useCase.execute(employeeProps);

    expect(mockRepository.create).toHaveBeenCalledWith(employeeProps);
    expect(result).toBe(mockEmployee);
  });

  it('should propagate repository errors', async () => {
    const employeeProps = {
      name: 'John Doe',
      email: 'john.doe@example.com',
      department: 'Engineering',
      position: 'Senior Developer',
      hireDate: new Date('2023-01-01'),
    };

    vi.mocked(mockRepository.create).mockRejectedValue(new Error('Database error'));

    await expect(useCase.execute(employeeProps)).rejects.toThrow('Database error');
  });
});
