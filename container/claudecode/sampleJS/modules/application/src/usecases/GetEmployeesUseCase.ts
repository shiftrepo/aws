import { Employee } from '@samplejs/domain';
import { IEmployeeRepository } from '../ports/IEmployeeRepository';

export class GetEmployeesUseCase {
  constructor(private readonly repository: IEmployeeRepository) {}

  async execute(): Promise<Employee[]> {
    return await this.repository.findAll();
  }
}
