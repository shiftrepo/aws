import { Employee } from '@samplejs/domain';
import { IEmployeeRepository } from '../ports/IEmployeeRepository';

export class GetEmployeeUseCase {
  constructor(private readonly repository: IEmployeeRepository) {}

  async execute(id: string): Promise<Employee> {
    const employee = await this.repository.findById(id);
    if (!employee) {
      throw new Error(`Employee with id ${id} not found`);
    }
    return employee;
  }
}
