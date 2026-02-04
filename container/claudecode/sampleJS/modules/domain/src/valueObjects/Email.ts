export class Email {
  private readonly _value: string;

  private constructor(value: string) {
    this._value = value;
  }

  static create(value: string): Email {
    const normalized = value.trim().toLowerCase();
    if (!this.isValid(normalized)) {
      throw new Error(`Invalid email address: ${value}`);
    }
    return new Email(normalized);
  }

  static isValid(value: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) && value.length <= 254;
  }

  get value(): string {
    return this._value;
  }

  equals(other: Email): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }

  get domain(): string {
    return this._value.split('@')[1];
  }

  get localPart(): string {
    return this._value.split('@')[0];
  }
}
