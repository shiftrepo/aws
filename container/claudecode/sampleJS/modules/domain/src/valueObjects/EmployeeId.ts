export class EmployeeId {
  private readonly _value: string;

  private constructor(value: string) {
    this._value = value;
  }

  static create(value?: string): EmployeeId {
    const id = value || this.generateId();
    if (!this.isValid(id)) {
      throw new Error(`Invalid employee ID: ${id}`);
    }
    return new EmployeeId(id);
  }

  static isValid(value: string): boolean {
    return /^[a-zA-Z0-9-]{1,50}$/.test(value);
  }

  private static generateId(): string {
    return `EMP-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  get value(): string {
    return this._value;
  }

  equals(other: EmployeeId): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }
}
