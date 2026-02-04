import { Employee, EmployeeProps } from '@samplejs/domain';

export interface IEmployeeRepository {
  findAll(): Promise<Employee[]>;
  findById(id: string): Promise<Employee | null>;
  create(props: Omit<EmployeeProps, 'id'>): Promise<Employee>;
  update(id: string, props: Partial<EmployeeProps>): Promise<Employee>;
  delete(id: string): Promise<void>;
}
