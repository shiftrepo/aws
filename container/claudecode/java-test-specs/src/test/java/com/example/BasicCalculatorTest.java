package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

/**
 * @TestModule CalculatorModule
 * @TestCase BasicArithmeticOperations
 * @BaselineVersion 1.0.0
 * @TestOverview Verify basic calculator operations with conditional logic for C1 coverage
 * @TestPurpose Ensure proper handling of different input types and edge cases
 * @TestProcess Execute tests with various parameters to achieve C1 coverage
 * @TestResults All conditions should pass validation checks
 * @Creator DeveloperTeam
 * @CreatedDate 2026-01-07
 * @Modifier ReviewerTeam
 * @ModifiedDate 2026-01-07
 * @TestCategory Unit
 * @Priority High
 * @Requirements REQ-CALC-001, REQ-CALC-002
 * @Dependencies BasicCalculator class
 */
public class BasicCalculatorTest {

    private BasicCalculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new BasicCalculator();
    }

    /**
     * @TestCase PositiveNumberAddition
     * @TestOverview Test addition with positive numbers
     * @TestPurpose Verify positive number calculations
     */
    @Test
    public void testPositiveAddition() {
        // C1 Coverage: Testing positive path
        int result = calculator.add(5, 3);
        if (result > 0) {
            assertTrue(result == 8, "Positive addition should work correctly");
        } else {
            fail("Positive addition failed");
        }
    }

    /**
     * @TestCase ConditionalCalculation
     * @TestOverview Test conditional calculation logic for different input ranges
     * @TestPurpose Achieve C1 coverage with multiple condition branches
     */
    @ParameterizedTest
    @ValueSource(ints = {-5, 0, 5, 10})
    public void testConditionalCalculation(int value) {
        int result = calculator.multiply(value, 2);

        // C1 Coverage: Multiple conditional branches
        if (value > 0) {
            // Positive path
            assertTrue(result > 0, "Positive multiplication should yield positive result");
            if (value > 5) {
                assertTrue(result > 10, "Large positive values should yield large results");
            }
        } else if (value < 0) {
            // Negative path
            assertTrue(result < 0, "Negative multiplication should yield negative result");
        } else {
            // Zero path
            assertEquals(0, result, "Zero multiplication should yield zero");
        }
    }

    /**
     * @TestCase DivisionEdgeCases
     * @TestOverview Test division with edge cases including zero division
     * @TestPurpose Verify proper error handling and edge case management
     */
    @Test
    public void testDivisionEdgeCases() {
        // C1 Coverage: Exception handling paths
        try {
            double result = calculator.divide(10, 2);
            assertEquals(5.0, result, 0.001, "Normal division should work");

            // Test zero division
            assertThrows(ArithmeticException.class, () -> {
                calculator.divide(10, 0);
            }, "Division by zero should throw exception");

        } catch (Exception e) {
            fail("Unexpected exception in division test: " + e.getMessage());
        }
    }

    /**
     * @TestCase SubtractionBoundaries
     * @TestOverview Test subtraction with boundary values
     * @TestPurpose Verify correct handling of boundary conditions
     */
    @Test
    public void testSubtractionBoundaries() {
        // C1 Coverage: Boundary condition testing
        int maxValue = Integer.MAX_VALUE;
        int minValue = Integer.MIN_VALUE;

        // Test normal subtraction
        int normalResult = calculator.subtract(10, 3);
        assertEquals(7, normalResult, "Normal subtraction should work");

        // Test with boundary values
        if (maxValue > 0) {
            // Boundary test for large values
            assertTrue(calculator.subtract(maxValue, 1) < maxValue, "Max value subtraction");
        }

        if (minValue < 0) {
            // Boundary test for minimum values
            assertTrue(calculator.subtract(0, 1) > minValue, "Min value handling");
        }
    }

    // Simple calculator implementation for testing
    private static class BasicCalculator {

        public int add(int a, int b) {
            return a + b;
        }

        public int subtract(int a, int b) {
            return a - b;
        }

        public int multiply(int a, int b) {
            return a * b;
        }

        public double divide(int a, int b) {
            if (b == 0) {
                throw new ArithmeticException("Division by zero");
            }
            return (double) a / b;
        }
    }
}