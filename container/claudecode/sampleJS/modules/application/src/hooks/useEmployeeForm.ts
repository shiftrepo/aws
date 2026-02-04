import { useState, useCallback } from 'react';
import { Employee, EmployeeProps } from '@samplejs/domain';
import { IEmployeeRepository } from '../ports/IEmployeeRepository';
import { GetEmployeeUseCase } from '../usecases/GetEmployeeUseCase';
import { CreateEmployeeUseCase } from '../usecases/CreateEmployeeUseCase';
import { UpdateEmployeeUseCase } from '../usecases/UpdateEmployeeUseCase';

export interface UseEmployeeFormResult {
  employee: Employee | null;
  loading: boolean;
  error: string | null;
  loadEmployee: (id: string) => Promise<void>;
  createEmployee: (props: Omit<EmployeeProps, 'id'>) => Promise<Employee>;
  updateEmployee: (id: string, props: Partial<EmployeeProps>) => Promise<Employee>;
}

export function useEmployeeForm(repository: IEmployeeRepository): UseEmployeeFormResult {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadEmployee = useCallback(
    async (id: string) => {
      try {
        setLoading(true);
        setError(null);
        const useCase = new GetEmployeeUseCase(repository);
        const result = await useCase.execute(id);
        setEmployee(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load employee');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [repository]
  );

  const createEmployee = useCallback(
    async (props: Omit<EmployeeProps, 'id'>) => {
      try {
        setLoading(true);
        setError(null);
        const useCase = new CreateEmployeeUseCase(repository);
        const result = await useCase.execute(props);
        setEmployee(result);
        return result;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create employee');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [repository]
  );

  const updateEmployee = useCallback(
    async (id: string, props: Partial<EmployeeProps>) => {
      try {
        setLoading(true);
        setError(null);
        const useCase = new UpdateEmployeeUseCase(repository);
        const result = await useCase.execute(id, props);
        setEmployee(result);
        return result;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update employee');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [repository]
  );

  return {
    employee,
    loading,
    error,
    loadEmployee,
    createEmployee,
    updateEmployee,
  };
}
