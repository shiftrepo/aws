import { useState, useEffect, useCallback } from 'react';
import { Employee } from '@samplejs/domain';
import { IEmployeeRepository } from '../ports/IEmployeeRepository';
import { GetEmployeesUseCase } from '../usecases/GetEmployeesUseCase';
import { DeleteEmployeeUseCase } from '../usecases/DeleteEmployeeUseCase';

export interface UseEmployeesResult {
  employees: Employee[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  deleteEmployee: (id: string) => Promise<void>;
}

export function useEmployees(repository: IEmployeeRepository): UseEmployeesResult {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadEmployees = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const useCase = new GetEmployeesUseCase(repository);
      const result = await useCase.execute();
      setEmployees(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load employees');
    } finally {
      setLoading(false);
    }
  }, [repository]);

  useEffect(() => {
    loadEmployees();
  }, [loadEmployees]);

  const deleteEmployee = useCallback(
    async (id: string) => {
      try {
        setError(null);
        const useCase = new DeleteEmployeeUseCase(repository);
        await useCase.execute(id);
        await loadEmployees();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete employee');
        throw err;
      }
    },
    [repository, loadEmployees]
  );

  return {
    employees,
    loading,
    error,
    refresh: loadEmployees,
    deleteEmployee,
  };
}
