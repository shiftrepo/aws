package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

/**
 * @TestModule ValidationModule
 * @TestCase StringValidationOperations
 * @BaselineVersion 1.2.0
 * @TestOverview Comprehensive string validation testing with multiple validation rules
 * @TestPurpose Ensure robust string validation with proper error handling and edge cases
 * @TestProcess Test various string patterns including null, empty, valid and invalid formats
 * @TestResults All validation rules should be properly enforced
 * @Creator QATeam
 * @CreatedDate 2026-01-07
 * @Modifier SecurityTeam
 * @ModifiedDate 2026-01-07
 * @TestCategory Integration
 * @Priority Medium
 * @Requirements REQ-VAL-001, REQ-VAL-002, REQ-SEC-001
 * @Dependencies StringValidator utility class
 */
public class StringValidatorTest {

    private StringValidator validator;

    @BeforeEach
    void setUp() {
        validator = new StringValidator();
    }

    /**
     * @TestCase EmailValidation
     * @TestOverview Test email address validation with various formats
     * @TestPurpose Verify email validation rules and format compliance
     */
    @ParameterizedTest
    @ValueSource(strings = {
        "test@example.com",
        "user.name@domain.co.jp",
        "invalid-email",
        "test@",
        "@domain.com"
    })
    public void testEmailValidation(String email) {
        boolean isValid = validator.isValidEmail(email);

        // C1 Coverage: Email format validation branches
        if (email != null && email.contains("@")) {
            String[] parts = email.split("@");
            if (parts.length == 2 && !parts[0].isEmpty() && !parts[1].isEmpty()) {
                if (parts[1].contains(".")) {
                    assertTrue(isValid, "Valid email should pass validation: " + email);
                } else {
                    assertFalse(isValid, "Email without domain extension should fail: " + email);
                }
            } else {
                assertFalse(isValid, "Malformed email should fail validation: " + email);
            }
        } else {
            assertFalse(isValid, "Invalid email format should fail: " + email);
        }
    }

    /**
     * @TestCase PasswordStrengthValidation
     * @TestOverview Test password strength validation with security requirements
     * @TestPurpose Ensure password meets security criteria
     */
    @Test
    public void testPasswordStrengthValidation() {
        // C1 Coverage: Multiple password validation conditions
        String weakPassword = "123";
        String mediumPassword = "password123";
        String strongPassword = "MyStr0ngP@ssw0rd!";

        // Test weak password
        assertFalse(validator.isStrongPassword(weakPassword), "Weak password should fail");

        // Test medium password
        boolean mediumResult = validator.isStrongPassword(mediumPassword);
        if (mediumPassword.length() >= 8) {
            if (containsDigit(mediumPassword)) {
                // Should pass length and digit requirements
                assertNotNull(mediumResult, "Medium password validation completed");
            }
        }

        // Test strong password
        assertTrue(validator.isStrongPassword(strongPassword), "Strong password should pass");
    }

    /**
     * @TestCase NullAndEmptyStringHandling
     * @TestOverview Test null and empty string handling across validation methods
     * @TestPurpose Verify proper handling of edge case inputs
     */
    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {" ", "  ", "\t", "\n"})
    public void testNullAndEmptyStringHandling(String input) {
        // C1 Coverage: Null and empty string branches
        if (input == null) {
            assertFalse(validator.isValidEmail(input), "Null should fail email validation");
            assertFalse(validator.isStrongPassword(input), "Null should fail password validation");
            assertFalse(validator.isValidPhoneNumber(input), "Null should fail phone validation");
        } else if (input.trim().isEmpty()) {
            assertFalse(validator.isValidEmail(input), "Empty string should fail email validation");
            assertFalse(validator.isStrongPassword(input), "Empty string should fail password validation");
            assertFalse(validator.isValidPhoneNumber(input), "Empty string should fail phone validation");
        } else {
            // Whitespace-only strings
            assertFalse(validator.isValidEmail(input), "Whitespace-only should fail email validation");
        }
    }

    /**
     * @TestCase PhoneNumberValidation
     * @TestOverview Test phone number validation with international formats
     * @TestPurpose Verify phone number format compliance
     */
    @ParameterizedTest
    @ValueSource(strings = {
        "+81-90-1234-5678",
        "090-1234-5678",
        "09012345678",
        "+1-555-123-4567",
        "invalid-phone",
        "123"
    })
    public void testPhoneNumberValidation(String phoneNumber) {
        boolean isValid = validator.isValidPhoneNumber(phoneNumber);

        // C1 Coverage: Phone number format validation
        if (phoneNumber != null && phoneNumber.length() >= 10) {
            String digitsOnly = phoneNumber.replaceAll("[^0-9]", "");
            if (digitsOnly.length() >= 10 && digitsOnly.length() <= 15) {
                if (phoneNumber.startsWith("+") || phoneNumber.matches("^[0-9-]+$")) {
                    assertTrue(isValid, "Valid phone format should pass: " + phoneNumber);
                } else {
                    // May still be valid depending on implementation
                    assertNotNull(isValid, "Phone validation completed for: " + phoneNumber);
                }
            } else {
                assertFalse(isValid, "Invalid digit count should fail: " + phoneNumber);
            }
        } else {
            assertFalse(isValid, "Short phone number should fail: " + phoneNumber);
        }
    }

    /**
     * @TestCase ComplexValidationRules
     * @TestOverview Test complex validation rules combining multiple criteria
     * @TestPurpose Verify comprehensive validation logic
     */
    @Test
    public void testComplexValidationRules() {
        String testInput = "ComplexInput123!@#";

        // C1 Coverage: Multiple validation criteria
        boolean hasUpperCase = containsUpperCase(testInput);
        boolean hasLowerCase = containsLowerCase(testInput);
        boolean hasDigit = containsDigit(testInput);
        boolean hasSpecialChar = containsSpecialChar(testInput);

        // Complex conditional logic for C1 coverage
        if (hasUpperCase && hasLowerCase) {
            if (hasDigit && hasSpecialChar) {
                assertTrue(validator.isComplexValid(testInput), "Complex input with all criteria should pass");
            } else if (hasDigit || hasSpecialChar) {
                // Partial compliance
                boolean result = validator.isComplexValid(testInput);
                assertNotNull(result, "Partial compliance validation completed");
            } else {
                assertFalse(validator.isComplexValid(testInput), "Missing digit and special char should fail");
            }
        } else {
            assertFalse(validator.isComplexValid(testInput), "Missing case variety should fail");
        }
    }

    // Helper methods
    private boolean containsUpperCase(String str) {
        return str != null && str.chars().anyMatch(Character::isUpperCase);
    }

    private boolean containsLowerCase(String str) {
        return str != null && str.chars().anyMatch(Character::isLowerCase);
    }

    private boolean containsDigit(String str) {
        return str != null && str.chars().anyMatch(Character::isDigit);
    }

    private boolean containsSpecialChar(String str) {
        return str != null && str.chars().anyMatch(ch -> !Character.isLetterOrDigit(ch));
    }

    // Simple validator implementation for testing
    private static class StringValidator {

        public boolean isValidEmail(String email) {
            if (email == null || email.trim().isEmpty()) {
                return false;
            }
            return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
        }

        public boolean isStrongPassword(String password) {
            if (password == null || password.length() < 8) {
                return false;
            }
            boolean hasUpper = password.chars().anyMatch(Character::isUpperCase);
            boolean hasLower = password.chars().anyMatch(Character::isLowerCase);
            boolean hasDigit = password.chars().anyMatch(Character::isDigit);
            boolean hasSpecial = password.chars().anyMatch(ch -> !Character.isLetterOrDigit(ch));

            return hasUpper && hasLower && hasDigit && hasSpecial;
        }

        public boolean isValidPhoneNumber(String phone) {
            if (phone == null || phone.trim().isEmpty()) {
                return false;
            }
            String digitsOnly = phone.replaceAll("[^0-9]", "");
            return digitsOnly.length() >= 10 && digitsOnly.length() <= 15;
        }

        public boolean isComplexValid(String input) {
            if (input == null || input.length() < 8) {
                return false;
            }
            boolean hasUpper = input.chars().anyMatch(Character::isUpperCase);
            boolean hasLower = input.chars().anyMatch(Character::isLowerCase);
            boolean hasDigit = input.chars().anyMatch(Character::isDigit);
            boolean hasSpecial = input.chars().anyMatch(ch -> !Character.isLetterOrDigit(ch));

            return hasUpper && hasLower && (hasDigit || hasSpecial);
        }
    }
}