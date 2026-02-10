/**
 * TestExecutionInfo.test.js
 *
 * Unit tests for TestExecutionInfo model
 */

import { TestExecutionInfo } from '../../model/TestExecutionInfo.js';

describe('TestExecutionInfo', () => {
  let executionInfo;

  beforeEach(() => {
    executionInfo = new TestExecutionInfo();
  });

  test('should initialize with default values', () => {
    expect(executionInfo.testSuiteName).toBe('');
    expect(executionInfo.testsTotal).toBe(0);
    expect(executionInfo.testsPassed).toBe(0);
    expect(executionInfo.testsFailed).toBe(0);
    expect(executionInfo.testsSkipped).toBe(0);
    expect(executionInfo.executionTime).toBe(0);
  });

  test('should calculate success rate correctly', () => {
    executionInfo.testsTotal = 10;
    executionInfo.testsPassed = 8;

    expect(executionInfo.getSuccessRate()).toBe(80);
  });

  test('should return 0 success rate when no tests', () => {
    executionInfo.testsTotal = 0;
    executionInfo.testsPassed = 0;

    expect(executionInfo.getSuccessRate()).toBe(0);
  });

  test('should return 100% success rate when all tests pass', () => {
    executionInfo.testsTotal = 10;
    executionInfo.testsPassed = 10;

    expect(executionInfo.getSuccessRate()).toBe(100);
  });

  test('should return N/A execution status when no tests', () => {
    executionInfo.testsTotal = 0;

    expect(executionInfo.getExecutionStatus()).toBe('N/A');
  });

  test('should return 成功 status when all tests pass', () => {
    executionInfo.testsTotal = 10;
    executionInfo.testsPassed = 10;
    executionInfo.testsFailed = 0;
    executionInfo.testsSkipped = 0;

    expect(executionInfo.getExecutionStatus()).toBe('成功');
  });

  test('should return 失敗 status when some tests fail', () => {
    executionInfo.testsTotal = 10;
    executionInfo.testsPassed = 7;
    executionInfo.testsFailed = 3;
    executionInfo.testsSkipped = 0;

    expect(executionInfo.getExecutionStatus()).toBe('失敗');
  });

  test('should return 一部スキップ status when no failures but some skipped', () => {
    executionInfo.testsTotal = 10;
    executionInfo.testsPassed = 7;
    executionInfo.testsFailed = 0;
    executionInfo.testsSkipped = 3;

    expect(executionInfo.getExecutionStatus()).toBe('一部スキップ');
  });

  test('should generate toString output', () => {
    executionInfo.testSuiteName = 'MyTestSuite';
    executionInfo.testsTotal = 15;
    executionInfo.testsPassed = 12;
    executionInfo.testsFailed = 2;
    executionInfo.testsSkipped = 1;

    const str = executionInfo.toString();

    expect(str).toContain('MyTestSuite');
    expect(str).toContain('total=15');
    expect(str).toContain('passed=12');
    expect(str).toContain('failed=2');
    expect(str).toContain('skipped=1');
    expect(str).toContain('80.00%');
  });

  test('should handle execution time', () => {
    executionInfo.executionTime = 1234;

    expect(executionInfo.executionTime).toBe(1234);
  });
});
