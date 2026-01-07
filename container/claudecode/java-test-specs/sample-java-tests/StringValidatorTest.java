package com.example.validator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.params.provider.NullSource;
import org.junit.jupiter.params.provider.EmptySource;
import static org.junit.jupiter.api.Assertions.*;

/**
 * @TestModule StringValidationModule
 * @TestCase StringValidationOperations
 * @BaselineVersion 1.0.0
 * @TestOverview Validate string inputs with comprehensive conditional logic for C1 coverage
 * @TestPurpose Ensure proper handling of various string types including null, empty, and valid strings
 * @TestProcess Execute validation tests with different string parameters to achieve full condition coverage
 * @TestResults All string validation conditions should be properly tested and validated
 * @Creator DeveloperName
 * @CreatedDate 2026-01-07
 * @Modifier ReviewerName
 * @ModifiedDate 2026-01-07
 */
public class StringValidatorTest {

    private StringValidator validator;

    @BeforeEach
    void setUp() {
        validator = new StringValidator();
    }

    /**
     * @TestModule StringValidationModule
     * @TestCase EmailValidationTest
     * @BaselineVersion 1.0.0
     * @TestOverview Test email validation with multiple conditional branches
     * @TestPurpose Demonstrate C1 coverage through different email format validations
     * @TestProcess Test valid emails, invalid formats, null, and empty strings
     * @TestResults Each validation condition should execute properly and return correct boolean result
     * @Creator DeveloperName
     * @CreatedDate 2026-01-07
     * @Modifier ReviewerName
     * @ModifiedDate 2026-01-07
     */
    @ParameterizedTest
    @ValueSource(strings = {"test@example.com", "user@domain.co.jp", "invalid-email", "@domain.com",
                           "user@", "user.domain.com", "a@b.c", ""})
    @NullSource
    @EmptySource
    @DisplayName("Test email validation with various input formats")
    public void testEmailValidation(String email) {
        boolean result = validator.isValidEmail(email);

        // C1 Coverage: Multiple conditional branches for email validation
        if (email == null) {
            // Null input branch
            assertFalse(result, "Null email should be invalid");
        } else if (email.isEmpty()) {
            // Empty string branch
            assertFalse(result, "Empty email should be invalid");
        } else if (email.length() < 5) {
            // Too short email branch
            assertFalse(result, "Email shorter than 5 characters should be invalid");
        } else if (!email.contains("@")) {
            // Missing @ symbol branch
            assertFalse(result, "Email without @ symbol should be invalid");
        } else if (email.startsWith("@") || email.endsWith("@")) {
            // Invalid @ position branch
            assertFalse(result, "Email starting or ending with @ should be invalid");
        } else if (!email.contains(".")) {
            // Missing dot in domain branch
            assertFalse(result, "Email without domain dot should be invalid");
        } else {
            // Valid email format branch
            String[] parts = email.split("@");
            if (parts.length == 2 && !parts[0].isEmpty() && !parts[1].isEmpty()) {
                if (parts[1].contains(".") && !parts[1].startsWith(".") && !parts[1].endsWith(".")) {
                    assertTrue(result, "Valid email format should be accepted");
                } else {
                    assertFalse(result, "Invalid domain format should be rejected");
                }
            } else {
                assertFalse(result, "Multiple @ symbols should make email invalid");
            }
        }
    }

    /**
     * @TestModule StringValidationModule
     * @TestCase PasswordStrengthTest
     * @BaselineVersion 1.0.0
     * @TestOverview Test password strength validation with complex conditional logic
     * @TestPurpose Achieve comprehensive C1 coverage through password criteria checking
     * @TestProcess Test passwords of various lengths and complexity levels
     * @TestResults Password strength levels should be correctly categorized based on criteria
     * @Creator DeveloperName
     * @CreatedDate 2026-01-07
     * @Modifier ReviewerName
     * @ModifiedDate 2026-01-07
     */
    @Test
    @DisplayName("Test password strength validation with complex branching")
    public void testPasswordStrengthValidation() {
        String[] passwords = {
            null, "", "123", "password", "Password1", "P@ssw0rd", "VeryStr0ng!P@ssw0rd"
        };

        for (String password : passwords) {
            PasswordStrength strength = validator.evaluatePasswordStrength(password);

            // Complex branching for C1 coverage
            if (password == null) {
                // Null password branch
                assertEquals(PasswordStrength.INVALID, strength, "Null password should be invalid");
            } else if (password.length() == 0) {
                // Empty password branch
                assertEquals(PasswordStrength.INVALID, strength, "Empty password should be invalid");
            } else if (password.length() < 6) {
                // Too short password branch
                assertEquals(PasswordStrength.WEAK, strength, "Short password should be weak");
            } else if (password.length() >= 6 && password.length() < 12) {
                // Medium length password - check complexity
                if (hasUpperCase(password) && hasLowerCase(password) && hasDigit(password)) {
                    if (hasSpecialChar(password)) {
                        assertEquals(PasswordStrength.STRONG, strength,
                                   "Medium length with all criteria should be strong");
                    } else {
                        assertEquals(PasswordStrength.MEDIUM, strength,
                                   "Medium length with most criteria should be medium");
                    }
                } else {
                    assertEquals(PasswordStrength.WEAK, strength,
                               "Medium length without complexity should be weak");
                }
            } else {
                // Long password (>= 12 characters) - enhanced validation
                if (hasUpperCase(password) && hasLowerCase(password) &&
                    hasDigit(password) && hasSpecialChar(password)) {
                    assertEquals(PasswordStrength.VERY_STRONG, strength,
                               "Long password with all criteria should be very strong");
                } else if ((hasUpperCase(password) || hasLowerCase(password)) && hasDigit(password)) {
                    assertEquals(PasswordStrength.STRONG, strength,
                               "Long password with basic criteria should be strong");
                } else {
                    assertEquals(PasswordStrength.MEDIUM, strength,
                               "Long password without complexity should be medium");
                }
            }
        }
    }

    /**
     * @TestModule StringValidationModule
     * @TestCase UsernameValidation
     * @BaselineVersion 1.0.0
     * @TestOverview Test username validation with character and length restrictions
     * @TestPurpose Demonstrate multiple decision points for username acceptance criteria
     * @TestProcess Test usernames with various characters, lengths, and formats
     * @TestResults Username validation should properly handle all edge cases and valid formats
     * @Creator DeveloperName
     * @CreatedDate 2026-01-07
     * @Modifier ReviewerName
     * @ModifiedDate 2026-01-07
     */
    @ParameterizedTest
    @ValueSource(strings = {"user", "User123", "user_name", "user-name", "123user", "user@domain",
                           "a", "verylongusernamethatexceedslimits", "user name", "validUser123"})
    @NullSource
    @EmptySource
    @DisplayName("Test username validation with various formats")
    public void testUsernameValidation(String username) {
        boolean result = validator.isValidUsername(username);

        // Multiple conditions for C1 coverage
        if (username == null || username.isEmpty()) {
            // Null or empty branch
            assertFalse(result, "Null or empty username should be invalid");
        } else if (username.length() < 3) {
            // Too short username branch
            assertFalse(result, "Username shorter than 3 characters should be invalid");
        } else if (username.length() > 20) {
            // Too long username branch
            assertFalse(result, "Username longer than 20 characters should be invalid");
        } else if (username.contains(" ")) {
            // Contains spaces branch
            assertFalse(result, "Username with spaces should be invalid");
        } else if (username.contains("@") || username.contains("#") || username.contains("$")) {
            // Contains special characters branch
            assertFalse(result, "Username with special characters (@, #, $) should be invalid");
        } else if (Character.isDigit(username.charAt(0))) {
            // Starts with digit branch
            assertFalse(result, "Username starting with digit should be invalid");
        } else {
            // Valid username format branch
            boolean hasValidChars = username.matches("^[a-zA-Z][a-zA-Z0-9_-]*$");
            if (hasValidChars) {
                assertTrue(result, "Valid username format should be accepted");
            } else {
                assertFalse(result, "Invalid characters should make username invalid");
            }
        }
    }

    // Helper methods for password validation
    private boolean hasUpperCase(String password) {
        return password.chars().anyMatch(Character::isUpperCase);
    }

    private boolean hasLowerCase(String password) {
        return password.chars().anyMatch(Character::isLowerCase);
    }

    private boolean hasDigit(String password) {
        return password.chars().anyMatch(Character::isDigit);
    }

    private boolean hasSpecialChar(String password) {
        return password.chars().anyMatch(ch -> "!@#$%^&*()_+-=[]{}|;':\",./<>?".indexOf(ch) >= 0);
    }
}

/**
 * String Validator class for testing purposes
 */
class StringValidator {

    public boolean isValidEmail(String email) {
        if (email == null || email.isEmpty() || email.length() < 5) {
            return false;
        }
        if (!email.contains("@") || email.startsWith("@") || email.endsWith("@")) {
            return false;
        }
        String[] parts = email.split("@");
        if (parts.length != 2 || parts[0].isEmpty() || parts[1].isEmpty()) {
            return false;
        }
        return parts[1].contains(".") && !parts[1].startsWith(".") && !parts[1].endsWith(".");
    }

    public boolean isValidUsername(String username) {
        if (username == null || username.isEmpty()) {
            return false;
        }
        if (username.length() < 3 || username.length() > 20) {
            return false;
        }
        if (username.contains(" ") || username.contains("@") ||
            username.contains("#") || username.contains("$")) {
            return false;
        }
        if (Character.isDigit(username.charAt(0))) {
            return false;
        }
        return username.matches("^[a-zA-Z][a-zA-Z0-9_-]*$");
    }

    public PasswordStrength evaluatePasswordStrength(String password) {
        if (password == null || password.isEmpty()) {
            return PasswordStrength.INVALID;
        }
        if (password.length() < 6) {
            return PasswordStrength.WEAK;
        }

        boolean hasUpper = password.chars().anyMatch(Character::isUpperCase);
        boolean hasLower = password.chars().anyMatch(Character::isLowerCase);
        boolean hasDigit = password.chars().anyMatch(Character::isDigit);
        boolean hasSpecial = password.chars().anyMatch(ch -> "!@#$%^&*()_+-=[]{}|;':\",./<>?".indexOf(ch) >= 0);

        if (password.length() >= 12) {
            if (hasUpper && hasLower && hasDigit && hasSpecial) {
                return PasswordStrength.VERY_STRONG;
            } else if ((hasUpper || hasLower) && hasDigit) {
                return PasswordStrength.STRONG;
            } else {
                return PasswordStrength.MEDIUM;
            }
        } else {
            if (hasUpper && hasLower && hasDigit) {
                return hasSpecial ? PasswordStrength.STRONG : PasswordStrength.MEDIUM;
            } else {
                return PasswordStrength.WEAK;
            }
        }
    }
}

/**
 * Password strength enumeration
 */
enum PasswordStrength {
    INVALID, WEAK, MEDIUM, STRONG, VERY_STRONG
}