/**
 * TestCaseInfo.test.js
 *
 * Unit tests for TestCaseInfo model
 */

import { TestCaseInfo } from '../../model/TestCaseInfo.js';

describe('TestCaseInfo', () => {
  let testCase;

  beforeEach(() => {
    testCase = new TestCaseInfo();
  });

  test('should initialize with default values', () => {
    expect(testCase.filePath).toBe('');
    expect(testCase.className).toBe('');
    expect(testCase.methodName).toBe('');
    expect(testCase.softwareService).toBe('N/A');
    expect(testCase.coveragePercent).toBe(0.0);
    expect(testCase.testExecutionStatus).toBe('N/A');
  });

  test('should set coverage info correctly', () => {
    testCase.setCoverageInfo(80, 100);

    expect(testCase.branchesCovered).toBe(80);
    expect(testCase.branchesTotal).toBe(100);
    expect(testCase.coveragePercent).toBe(80);
  });

  test('should update coverage status to 優秀 for >= 90%', () => {
    testCase.setCoverageInfo(95, 100);
    expect(testCase.coverageStatus).toBe('優秀');
  });

  test('should update coverage status to 良好 for 70-89%', () => {
    testCase.setCoverageInfo(75, 100);
    expect(testCase.coverageStatus).toBe('良好');
  });

  test('should update coverage status to 普通 for 50-69%', () => {
    testCase.setCoverageInfo(55, 100);
    expect(testCase.coverageStatus).toBe('普通');
  });

  test('should update coverage status to 要改善 for < 50%', () => {
    testCase.setCoverageInfo(30, 100);
    expect(testCase.coverageStatus).toBe('要改善');
  });

  test('should handle zero total branches', () => {
    testCase.setCoverageInfo(0, 0);
    expect(testCase.coveragePercent).toBe(0);
    expect(testCase.coverageStatus).toBe('カバレッジなし');
  });

  test('should set test execution info', () => {
    testCase.setTestExecutionInfo(10, 8);

    expect(testCase.testsTotal).toBe(10);
    expect(testCase.testsPassed).toBe(8);
    expect(testCase.testSuccessRate).toBe(80);
    expect(testCase.testExecutionStatus).toBe('一部失敗');
  });

  test('should set test execution status to 成功 when all pass', () => {
    testCase.setTestExecutionInfo(10, 10);
    expect(testCase.testExecutionStatus).toBe('成功');
  });

  test('should set detailed execution info for PASS', () => {
    const executionInfo = {
      status: 'PASS',
      duration: 123,
      errorMessage: '',
      errorType: ''
    };

    testCase.setDetailedExecutionInfo(executionInfo);

    expect(testCase.testExecutionStatus).toBe('PASS');
    expect(testCase.executionDuration).toBe(123);
    expect(testCase.testsTotal).toBe(1);
    expect(testCase.testsPassed).toBe(1);
    expect(testCase.testSuccessRate).toBe(100);
  });

  test('should set detailed execution info for FAIL', () => {
    const executionInfo = {
      status: 'FAIL',
      duration: 50,
      errorMessage: 'Expected true but got false',
      errorType: 'AssertionError'
    };

    testCase.setDetailedExecutionInfo(executionInfo);

    expect(testCase.testExecutionStatus).toBe('FAIL');
    expect(testCase.executionDuration).toBe(50);
    expect(testCase.errorMessage).toBe('Expected true but got false');
    expect(testCase.errorType).toBe('AssertionError');
    expect(testCase.testSuccessRate).toBe(0);
  });

  test('should set detailed execution info for SKIP', () => {
    const executionInfo = {
      status: 'SKIP',
      duration: 0
    };

    testCase.setDetailedExecutionInfo(executionInfo);

    expect(testCase.testExecutionStatus).toBe('SKIP');
    expect(testCase.testSuccessRate).toBe(0);
  });

  test('should handle null execution info', () => {
    testCase.setDetailedExecutionInfo(null);
    expect(testCase.testExecutionStatus).toBe('N/A');
  });

  test('should get coverage display', () => {
    testCase.setCoverageInfo(85, 100);
    expect(testCase.getCoverageDisplay()).toBe('85.00% (85/100)');
  });

  test('should get test success display', () => {
    testCase.setTestExecutionInfo(20, 18);
    expect(testCase.getTestSuccessDisplay()).toBe('90.00% (18/20)');
  });

  test('should get execution status display with icons', () => {
    testCase.testExecutionStatus = 'PASS';
    expect(testCase.getExecutionStatusDisplay()).toBe('✓ PASS');

    testCase.testExecutionStatus = 'FAIL';
    expect(testCase.getExecutionStatusDisplay()).toBe('✗ FAIL');

    testCase.testExecutionStatus = 'SKIP';
    expect(testCase.getExecutionStatusDisplay()).toBe('○ SKIP');

    testCase.testExecutionStatus = 'ERROR';
    expect(testCase.getExecutionStatusDisplay()).toBe('⚠ ERROR');

    testCase.testExecutionStatus = 'UNKNOWN';
    expect(testCase.getExecutionStatusDisplay()).toBe('N/A');
  });

  test('should generate toString output', () => {
    testCase.filePath = '/path/to/test.js';
    testCase.className = 'MyClass';
    testCase.methodName = 'myMethod';
    testCase.testItemName = 'My Test';
    testCase.setCoverageInfo(80, 100);
    testCase.setTestExecutionInfo(5, 5);

    const str = testCase.toString();
    expect(str).toContain('MyClass');
    expect(str).toContain('myMethod');
    expect(str).toContain('My Test');
    expect(str).toContain('80.00');
    expect(str).toContain('100.00');
  });
});
