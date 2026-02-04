import { describe, it, expect } from 'vitest';
import { EmailValidator } from '../../src/validators/emailValidator';

describe('EmailValidator', () => {
  describe('validate', () => {
    it('should validate correct email addresses', () => {
      const validEmails = [
        'user@example.com',
        'john.doe@company.co.uk',
        'test+tag@domain.org',
        'user123@test-domain.com',
      ];

      validEmails.forEach((email) => {
        const result = EmailValidator.validate(email);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('should reject empty email', () => {
      const result = EmailValidator.validate('');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Email is required');
    });

    it('should reject email without @', () => {
      const result = EmailValidator.validate('invalidemail.com');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Email format is invalid');
    });

    it('should reject email without domain', () => {
      const result = EmailValidator.validate('user@');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Email format is invalid');
    });

    it('should reject email without local part', () => {
      const result = EmailValidator.validate('@example.com');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Email format is invalid');
    });

    it('should reject email exceeding maximum length', () => {
      const longEmail = 'a'.repeat(250) + '@example.com';
      const result = EmailValidator.validate(longEmail);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Email exceeds maximum length of 254 characters');
    });

    it('should reject email with too short value', () => {
      const result = EmailValidator.validate('a@');
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should reject domain starting with dot', () => {
      const result = EmailValidator.validate('user@.example.com');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Domain cannot start or end with a dot');
    });

    it('should reject domain ending with dot', () => {
      const result = EmailValidator.validate('user@example.com.');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Domain cannot start or end with a dot');
    });

    it('should reject domain with consecutive dots', () => {
      const result = EmailValidator.validate('user@example..com');
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Domain cannot contain consecutive dots');
    });

    it('should reject local part exceeding 64 characters', () => {
      const longLocal = 'a'.repeat(65);
      const result = EmailValidator.validate(`${longLocal}@example.com`);
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Local part exceeds maximum length of 64 characters');
    });
  });

  describe('isValid', () => {
    it('should return true for valid email', () => {
      expect(EmailValidator.isValid('user@example.com')).toBe(true);
    });

    it('should return false for invalid email', () => {
      expect(EmailValidator.isValid('invalid')).toBe(false);
    });
  });

  describe('normalize', () => {
    it('should trim and lowercase email', () => {
      expect(EmailValidator.normalize('  User@Example.COM  ')).toBe('user@example.com');
    });

    it('should handle already normalized email', () => {
      expect(EmailValidator.normalize('user@example.com')).toBe('user@example.com');
    });
  });

  describe('getDomain', () => {
    it('should extract domain from email', () => {
      expect(EmailValidator.getDomain('user@example.com')).toBe('example.com');
    });

    it('should return null for invalid email', () => {
      expect(EmailValidator.getDomain('invalid')).toBeNull();
    });
  });

  describe('getLocalPart', () => {
    it('should extract local part from email', () => {
      expect(EmailValidator.getLocalPart('user@example.com')).toBe('user');
    });

    it('should return null for invalid email', () => {
      expect(EmailValidator.getLocalPart('invalid')).toBeNull();
    });
  });
});
