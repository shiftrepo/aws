export interface EmailValidationResult {
  isValid: boolean;
  errors: string[];
}

export class EmailValidator {
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  private static readonly MAX_LENGTH = 254;
  private static readonly MIN_LENGTH = 3;

  static validate(email: string): EmailValidationResult {
    const errors: string[] = [];

    if (!email || email.trim().length === 0) {
      errors.push('Email is required');
      return { isValid: false, errors };
    }

    const trimmedEmail = email.trim();

    if (trimmedEmail.length < this.MIN_LENGTH) {
      errors.push('Email is too short');
    }

    if (trimmedEmail.length > this.MAX_LENGTH) {
      errors.push('Email exceeds maximum length of 254 characters');
    }

    if (!this.EMAIL_REGEX.test(trimmedEmail)) {
      errors.push('Email format is invalid');
    }

    const [localPart, domain] = trimmedEmail.split('@');

    if (localPart && localPart.length > 64) {
      errors.push('Local part exceeds maximum length of 64 characters');
    }

    if (domain) {
      if (domain.length > 255) {
        errors.push('Domain exceeds maximum length of 255 characters');
      }

      if (domain.startsWith('.') || domain.endsWith('.')) {
        errors.push('Domain cannot start or end with a dot');
      }

      if (domain.includes('..')) {
        errors.push('Domain cannot contain consecutive dots');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  static isValid(email: string): boolean {
    return this.validate(email).isValid;
  }

  static normalize(email: string): string {
    return email.trim().toLowerCase();
  }

  static getDomain(email: string): string | null {
    const parts = email.split('@');
    return parts.length === 2 ? parts[1] : null;
  }

  static getLocalPart(email: string): string | null {
    const parts = email.split('@');
    return parts.length === 2 ? parts[0] : null;
  }
}
