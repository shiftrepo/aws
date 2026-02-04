import { IEmployeeRepository } from '../ports/IEmployeeRepository';

export class DeleteEmployeeUseCase {
  constructor(private readonly repository: IEmployeeRepository) {}

  async execute(id: string): Promise<void> {
    const existing = await this.repository.findById(id);
    if (!existing) {
      throw new Error(`Employee with id ${id} not found`);
    }
    await this.repository.delete(id);
  }
}
