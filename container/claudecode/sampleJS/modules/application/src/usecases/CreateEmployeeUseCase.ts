import { Employee, EmployeeProps } from '@samplejs/domain';
import { IEmployeeRepository } from '../ports/IEmployeeRepository';

export class CreateEmployeeUseCase {
  constructor(private readonly repository: IEmployeeRepository) {}

  async execute(props: Omit<EmployeeProps, 'id'>): Promise<Employee> {
    return await this.repository.create(props);
  }
}
