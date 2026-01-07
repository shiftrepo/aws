package com.example.calculator;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

/**
 * @TestModule CalculatorModule
 * @TestCase BasicArithmeticOperations
 * @BaselineVersion 1.0.0
 * @TestOverview Verify basic calculator operations with conditional logic for C1 coverage
 * @TestPurpose Ensure proper handling of different numeric input types and edge cases
 * @TestProcess Execute tests with various parameters to achieve condition/decision coverage
 * @TestResults All conditions should pass validation checks with proper branching
 * @Creator DeveloperName
 * @CreatedDate 2026-01-07
 * @Modifier ReviewerName
 * @ModifiedDate 2026-01-07
 */
public class BasicCalculatorTest {

    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
    }

    /**
     * @TestModule CalculatorModule
     * @TestCase ConditionalAdditionTest
     * @BaselineVersion 1.0.0
     * @TestOverview Test addition with conditional branching based on input values
     * @TestPurpose Demonstrate C1 coverage through parameter-based conditional logic
     * @TestProcess Test positive, negative, and zero values to cover all branches
     * @TestResults Each condition branch should execute and pass assertions
     * @Creator DeveloperName
     * @CreatedDate 2026-01-07
     * @Modifier ReviewerName
     * @ModifiedDate 2026-01-07
     */
    @ParameterizedTest
    @ValueSource(ints = {-5, -1, 0, 1, 5, 10, 100})
    @DisplayName("Test conditional calculation with various input values")
    public void testConditionalCalculation(int value) {
        int result = calculator.add(value, 1);

        // C1 Coverage: Condition/Decision coverage with multiple branches
        if (value > 0) {
            // Positive branch - should increase the value
            assertTrue(result > value, "Result should be greater than positive input");
            assertEquals(value + 1, result, "Addition should work correctly for positive numbers");
        } else if (value < 0) {
            // Negative branch - result should be closer to zero
            assertTrue(result > value, "Result should be greater than negative input");
            assertEquals(value + 1, result, "Addition should work correctly for negative numbers");
        } else {
            // Zero branch - special case handling
            assertEquals(1, result, "Adding 1 to zero should equal 1");
            assertTrue(result > 0, "Result should be positive when adding to zero");
        }
    }

    /**
     * @TestModule CalculatorModule
     * @TestCase MultiplicationBranching
     * @BaselineVersion 1.0.0
     * @TestOverview Test multiplication with complex conditional logic
     * @TestPurpose Achieve comprehensive C1 coverage with nested conditions
     * @TestProcess Test various numeric ranges with multiple decision points
     * @TestResults All conditional paths should be exercised and validated
     * @Creator DeveloperName
     * @CreatedDate 2026-01-07
     * @Modifier ReviewerName
     * @ModifiedDate 2026-01-07
     */
    @Test
    @DisplayName("Test multiplication with complex branching logic")
    public void testMultiplicationBranching() {
        int[] testValues = {-10, -1, 0, 1, 2, 5, 10};

        for (int value : testValues) {
            int result = calculator.multiply(value, 2);

            // Complex branching for C1 coverage
            if (value == 0) {
                // Zero multiplication branch
                assertEquals(0, result, "Multiplication by zero should return zero");
            } else if (value > 0 && value < 10) {
                // Small positive numbers branch
                assertEquals(value * 2, result, "Small positive multiplication should work correctly");
                assertTrue(result > 0, "Result should be positive for positive inputs");
            } else if (value >= 10) {
                // Large positive numbers branch
                assertEquals(value * 2, result, "Large positive multiplication should work correctly");
                assertTrue(result >= 20, "Large number results should be at least 20");
            } else {
                // Negative numbers branch (value < 0)
                assertEquals(value * 2, result, "Negative multiplication should work correctly");
                assertTrue(result < 0, "Result should be negative for negative inputs");

                // Additional nested condition for negative values
                if (value <= -5) {
                    assertTrue(result <= -10, "Large negative results should be very negative");
                }
            }
        }
    }

    /**
     * @TestModule CalculatorModule
     * @TestCase DivisionWithValidation
     * @BaselineVersion 1.0.0
     * @TestOverview Test division operations with error handling and validation
     * @TestPurpose Demonstrate exception handling and boundary condition testing
     * @TestProcess Test normal division and division by zero scenarios
     * @TestResults Proper results for valid operations, exceptions for invalid ones
     * @Creator DeveloperName
     * @CreatedDate 2026-01-07
     * @Modifier ReviewerName
     * @ModifiedDate 2026-01-07
     */
    @Test
    @DisplayName("Test division with validation and error handling")
    public void testDivisionWithValidation() {
        // Test various division scenarios for C1 coverage
        int dividend = 10;

        // Test normal division cases
        for (int divisor = -5; divisor <= 5; divisor++) {
            if (divisor == 0) {
                // Division by zero - should throw exception
                assertThrows(ArithmeticException.class, () -> {
                    calculator.divide(dividend, divisor);
                }, "Division by zero should throw ArithmeticException");
            } else {
                // Valid division cases
                double result = calculator.divide(dividend, divisor);
                double expected = (double) dividend / divisor;

                if (divisor > 0) {
                    // Positive divisor branch
                    assertTrue(result == expected, "Positive division should be accurate");
                    if (divisor == 1) {
                        assertEquals(dividend, result, "Division by 1 should return original number");
                    }
                } else {
                    // Negative divisor branch (divisor < 0, already checked != 0)
                    assertTrue(result == expected, "Negative division should be accurate");
                    assertTrue(result < 0, "Division by negative should give negative result");
                }
            }
        }
    }
}

/**
 * Simple Calculator class for testing purposes
 */
class Calculator {

    public int add(int a, int b) {
        return a + b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public double divide(int dividend, int divisor) {
        if (divisor == 0) {
            throw new ArithmeticException("Division by zero is not allowed");
        }
        return (double) dividend / divisor;
    }
}