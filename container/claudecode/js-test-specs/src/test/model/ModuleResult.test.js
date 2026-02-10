/**
 * ModuleResult.test.js
 *
 * Unit tests for ModuleResult model
 */

import { ModuleResult } from '../../model/ModuleResult.js';
import { ModuleInfo } from '../../model/ModuleInfo.js';

describe('ModuleResult', () => {
  let moduleInfo;
  let moduleResult;

  beforeEach(() => {
    moduleInfo = new ModuleInfo();
    moduleInfo.moduleName = 'test-module';
    moduleInfo.modulePath = '/path/to/module';

    moduleResult = new ModuleResult(moduleInfo);
  });

  test('should initialize with default values', () => {
    expect(moduleResult.moduleInfo).toBe(moduleInfo);
    expect(moduleResult.testCases).toEqual([]);
    expect(moduleResult.status).toBe('pending');
    expect(moduleResult.processingTime).toBe(0);
    expect(moduleResult.error).toBeNull();
    expect(moduleResult.warnings).toEqual([]);
  });

  test('should set test cases', () => {
    const testCases = [{ name: 'test1' }, { name: 'test2' }];
    moduleResult.setTestCases(testCases);

    expect(moduleResult.testCases).toBe(testCases);
    expect(moduleResult.testCases.length).toBe(2);
  });

  test('should handle null test cases', () => {
    moduleResult.setTestCases(null);
    expect(moduleResult.testCases).toEqual([]);
  });

  test('should set coverage summary', () => {
    const summary = {
      branchCoverage: 80,
      lineCoverage: 85
    };

    moduleResult.setCoverageSummary(summary);

    expect(moduleResult.coverageSummary.branchCoverage).toBe(80);
    expect(moduleResult.coverageSummary.lineCoverage).toBe(85);
  });

  test('should set execution summary', () => {
    const summary = {
      totalTests: 10,
      passed: 8,
      failed: 2
    };

    moduleResult.setExecutionSummary(summary);

    expect(moduleResult.executionSummary.totalTests).toBe(10);
    expect(moduleResult.executionSummary.passed).toBe(8);
    expect(moduleResult.executionSummary.failed).toBe(2);
  });

  test('should start processing', () => {
    moduleResult.startProcessing();

    expect(moduleResult.status).toBe('processing');
    expect(moduleResult.startTime).toBeDefined();
  });

  test('should complete processing successfully', () => {
    moduleResult.startProcessing();

    // Simulate some processing time
    const delay = 100;
    const start = Date.now();
    while (Date.now() - start < delay) {
      // busy wait
    }

    moduleResult.completeProcessing();

    expect(moduleResult.status).toBe('success');
    expect(moduleResult.processingTime).toBeGreaterThan(0);
  });

  test('should fail processing with error', () => {
    moduleResult.startProcessing();

    const error = new Error('Test error');
    moduleResult.failProcessing(error);

    expect(moduleResult.status).toBe('failed');
    expect(moduleResult.error).toBeDefined();
    expect(moduleResult.error.message).toBe('Test error');
    expect(moduleResult.error.stack).toBeDefined();
  });

  test('should add warnings', () => {
    moduleResult.addWarning('Warning 1');
    moduleResult.addWarning('Warning 2');

    expect(moduleResult.warnings).toEqual(['Warning 1', 'Warning 2']);
  });

  test('should check if successful', () => {
    expect(moduleResult.isSuccessful()).toBe(false);

    moduleResult.status = 'success';
    expect(moduleResult.isSuccessful()).toBe(true);

    moduleResult.status = 'failed';
    expect(moduleResult.isSuccessful()).toBe(false);
  });

  test('should get result summary', () => {
    moduleResult.startProcessing();
    moduleResult.setTestCases([{}, {}, {}]);
    moduleResult.setCoverageSummary({ branchCoverage: 85 });
    moduleResult.setExecutionSummary({ passRate: 90 });
    moduleResult.addWarning('Test warning');
    moduleResult.completeProcessing();

    const summary = moduleResult.getSummary();

    expect(summary.moduleName).toBe('test-module');
    expect(summary.status).toBe('success');
    expect(summary.testCaseCount).toBe(3);
    expect(summary.branchCoverage).toBe('85.00%');
    expect(summary.passRate).toBe('90.00%');
    expect(summary.warnings).toBe(1);
    expect(summary.hasError).toBe(false);
  });

  test('should convert to JSON', () => {
    moduleResult.setTestCases([{}]);
    moduleResult.setCoverageSummary({ branchCoverage: 80 });
    moduleResult.setExecutionSummary({ totalTests: 5 });
    moduleResult.status = 'success';

    const json = moduleResult.toJSON();

    expect(json.moduleInfo).toBeDefined();
    expect(json.testCaseCount).toBe(1);
    expect(json.coverageSummary.branchCoverage).toBe(80);
    expect(json.executionSummary.totalTests).toBe(5);
    expect(json.status).toBe('success');
  });

  test('should generate toString output', () => {
    moduleResult.setTestCases([{}, {}]);
    moduleResult.setCoverageSummary({ branchCoverage: 85 });
    moduleResult.status = 'success';

    const str = moduleResult.toString();
    expect(str).toContain('test-module');
    expect(str).toContain('success');
    expect(str).toContain('2');
    expect(str).toContain('85.00');
  });
});
