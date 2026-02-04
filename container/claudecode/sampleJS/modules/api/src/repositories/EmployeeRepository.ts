import { Employee, EmployeeProps } from '@samplejs/domain';
import { IEmployeeRepository } from '@samplejs/application';
import { ApiClient, defaultApiClient } from '../client/apiClient';

interface EmployeeDTO {
  id: string;
  name: string;
  email: string;
  department: string;
  position: string;
  hireDate: string;
}

export class EmployeeRepository implements IEmployeeRepository {
  private readonly apiClient: ApiClient;
  private readonly basePath = '/employees';

  constructor(apiClient: ApiClient = defaultApiClient) {
    this.apiClient = apiClient;
  }

  async findAll(): Promise<Employee[]> {
    const dtos = await this.apiClient.get<EmployeeDTO[]>(this.basePath);
    return dtos.map((dto) => this.dtoToEmployee(dto));
  }

  async findById(id: string): Promise<Employee | null> {
    try {
      const dto = await this.apiClient.get<EmployeeDTO>(`${this.basePath}/${id}`);
      return this.dtoToEmployee(dto);
    } catch (error) {
      if (error instanceof Error && error.message.includes('404')) {
        return null;
      }
      throw error;
    }
  }

  async create(props: Omit<EmployeeProps, 'id'>): Promise<Employee> {
    const dto = await this.apiClient.post<EmployeeDTO>(this.basePath, {
      name: props.name,
      email: props.email,
      department: props.department,
      position: props.position,
      hireDate: props.hireDate.toISOString(),
    });
    return this.dtoToEmployee(dto);
  }

  async update(id: string, props: Partial<EmployeeProps>): Promise<Employee> {
    const updateData: any = { ...props };
    if (props.hireDate) {
      updateData.hireDate = props.hireDate.toISOString();
    }

    const dto = await this.apiClient.put<EmployeeDTO>(`${this.basePath}/${id}`, updateData);
    return this.dtoToEmployee(dto);
  }

  async delete(id: string): Promise<void> {
    await this.apiClient.delete(`${this.basePath}/${id}`);
  }

  private dtoToEmployee(dto: EmployeeDTO): Employee {
    return Employee.create({
      id: dto.id,
      name: dto.name,
      email: dto.email,
      department: dto.department,
      position: dto.position,
      hireDate: new Date(dto.hireDate),
    });
  }
}
