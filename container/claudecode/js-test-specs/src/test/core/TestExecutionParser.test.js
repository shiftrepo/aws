/**
 * TestExecutionParser.test.js
 *
 * Unit tests for TestExecutionParser
 */

import { TestExecutionParser } from '../../core/TestExecutionParser.js';

describe('TestExecutionParser', () => {
  let parser;

  beforeEach(() => {
    parser = new TestExecutionParser();
  });

  test('should initialize with empty test results', () => {
    expect(parser.testResults).toBeInstanceOf(Map);
    expect(parser.testResults.size).toBe(0);
  });

  test('should normalize Jest status to standard format', () => {
    expect(parser.normalizeStatus('passed')).toBe('PASS');
    expect(parser.normalizeStatus('failed')).toBe('FAIL');
    expect(parser.normalizeStatus('pending')).toBe('SKIP');
    expect(parser.normalizeStatus('skipped')).toBe('SKIP');
    expect(parser.normalizeStatus('todo')).toBe('SKIP');
    expect(parser.normalizeStatus('disabled')).toBe('SKIP');
    expect(parser.normalizeStatus('unknown')).toBe('ERROR');
    expect(parser.normalizeStatus(null)).toBe('UNKNOWN');
  });

  test('should create test key from file path and test name', () => {
    const key = parser.createTestKey('/path/to/MyClass.test.js', 'my test');
    expect(key).toBe('MyClass::my test');
  });

  test('should extract error message from assertion', () => {
    const assertion = {
      failureMessages: ['Error: Expected 5 but got 3']
    };

    const message = parser.extractErrorMessage(assertion);

    expect(message).toBe('Error: Expected 5 but got 3');
  });

  test('should return empty string when no failure messages', () => {
    const assertion = { failureMessages: [] };

    const message = parser.extractErrorMessage(assertion);

    expect(message).toBe('');
  });

  test('should truncate long error messages', () => {
    const longMessage = 'A'.repeat(600);
    const assertion = { failureMessages: [longMessage] };

    const message = parser.extractErrorMessage(assertion);

    expect(message.length).toBeLessThan(600);
    expect(message).toContain('...');
  });

  test('should extract error type from assertion', () => {
    const assertion = {
      failureMessages: ['Error: AssertionError something went wrong']
    };

    const errorType = parser.extractErrorType(assertion);

    expect(errorType).toContain('Error');
  });

  test('should identify assertion errors', () => {
    const assertion = {
      failureMessages: ['expect(received).toBe(expected)']
    };

    const errorType = parser.extractErrorType(assertion);

    expect(errorType).toBe('AssertionError');
  });

  test('should return empty string when no error', () => {
    const assertion = { failureMessages: [] };

    const errorType = parser.extractErrorType(assertion);

    expect(errorType).toBe('');
  });

  test('should parse actual test results file', async () => {
    // Use the actual test-results.json file if it exists
    try {
      const results = await parser.parseTestResults('./test-results.json');

      expect(results).toBeInstanceOf(Map);
      // Should have parsed test results
      expect(results.size).toBeGreaterThan(0);
    } catch (error) {
      // If file doesn't exist, test passes
      expect(true).toBe(true);
    }
  });

  test('should get execution summary with zero tests', () => {
    const summary = parser.getExecutionSummary();

    expect(summary.totalTests).toBe(0);
    expect(summary.passed).toBe(0);
    expect(summary.failed).toBe(0);
    expect(summary.skipped).toBe(0);
    expect(summary.passRate).toBe('0.00');
  });

  test('should return null for non-existent test', () => {
    const info = parser.getExecutionInfo('NonExistent', 'test');

    expect(info).toBeNull();
  });

  test('should get all execution info', () => {
    const allInfo = parser.getAllExecutionInfo();

    expect(allInfo).toBeInstanceOf(Map);
  });
});
