import { EmployeeId } from '../valueObjects/EmployeeId';
import { Email } from '../valueObjects/Email';

export interface EmployeeProps {
  id?: string;
  name: string;
  email: string;
  department: string;
  position: string;
  hireDate: Date;
}

export class Employee {
  private readonly _id: EmployeeId;
  private _name: string;
  private _email: Email;
  private _department: string;
  private _position: string;
  private _hireDate: Date;

  private constructor(props: EmployeeProps) {
    this._id = EmployeeId.create(props.id);
    this._name = props.name;
    this._email = Email.create(props.email);
    this._department = props.department;
    this._position = props.position;
    this._hireDate = props.hireDate;

    this.validate();
  }

  static create(props: EmployeeProps): Employee {
    return new Employee(props);
  }

  private validate(): void {
    if (!this._name || this._name.trim().length === 0) {
      throw new Error('Employee name is required');
    }
    if (this._name.length > 100) {
      throw new Error('Employee name must not exceed 100 characters');
    }
    if (!this._department || this._department.trim().length === 0) {
      throw new Error('Department is required');
    }
    if (!this._position || this._position.trim().length === 0) {
      throw new Error('Position is required');
    }
    if (!(this._hireDate instanceof Date) || isNaN(this._hireDate.getTime())) {
      throw new Error('Invalid hire date');
    }
    if (this._hireDate > new Date()) {
      throw new Error('Hire date cannot be in the future');
    }
  }

  get id(): string {
    return this._id.value;
  }

  get name(): string {
    return this._name;
  }

  get email(): string {
    return this._email.value;
  }

  get department(): string {
    return this._department;
  }

  get position(): string {
    return this._position;
  }

  get hireDate(): Date {
    return this._hireDate;
  }

  updateName(name: string): void {
    this._name = name;
    this.validate();
  }

  updateEmail(email: string): void {
    this._email = Email.create(email);
  }

  updateDepartment(department: string): void {
    this._department = department;
    this.validate();
  }

  updatePosition(position: string): void {
    this._position = position;
    this.validate();
  }

  toJSON() {
    return {
      id: this._id.value,
      name: this._name,
      email: this._email.value,
      department: this._department,
      position: this._position,
      hireDate: this._hireDate.toISOString(),
    };
  }

  static fromJSON(json: any): Employee {
    return new Employee({
      id: json.id,
      name: json.name,
      email: json.email,
      department: json.department,
      position: json.position,
      hireDate: new Date(json.hireDate),
    });
  }
}
