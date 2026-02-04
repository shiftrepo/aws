import { Employee, EmployeeProps } from '@samplejs/domain';
import { IEmployeeRepository } from '../ports/IEmployeeRepository';

export class UpdateEmployeeUseCase {
  constructor(private readonly repository: IEmployeeRepository) {}

  async execute(id: string, props: Partial<EmployeeProps>): Promise<Employee> {
    const existing = await this.repository.findById(id);
    if (!existing) {
      throw new Error(`Employee with id ${id} not found`);
    }
    return await this.repository.update(id, props);
  }
}
