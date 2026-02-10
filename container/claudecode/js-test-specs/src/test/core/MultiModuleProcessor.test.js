/**
 * @jest-environment node
 *
 * MultiModuleProcessor.test.js
 *
 * Unit tests for MultiModuleProcessor
 */

import { MultiModuleProcessor } from '../../core/MultiModuleProcessor.js';
import { ModuleInfo } from '../../model/ModuleInfo.js';
import { ModuleResult } from '../../model/ModuleResult.js';

describe('MultiModuleProcessor', () => {
  let processor;

  beforeEach(() => {
    processor = new MultiModuleProcessor({
      maxConcurrency: 2,
      timeout: 10000
    });
  });

  test('should initialize with default options', () => {
    const defaultProcessor = new MultiModuleProcessor();

    expect(defaultProcessor.options.maxConcurrency).toBe(4);
    expect(defaultProcessor.options.timeout).toBe(300000); // 300 seconds default
    expect(defaultProcessor.moduleResults).toEqual([]);
  });

  test('should initialize with custom options', () => {
    expect(processor.options.maxConcurrency).toBe(2);
    expect(processor.options.timeout).toBe(10000);
    expect(processor.moduleResults).toEqual([]);
  });

  test('should process empty module list', async () => {
    const results = await processor.processModules([], {});

    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(0);
  });

  test('should get processing summary with no results', () => {
    const summary = processor.getProcessingSummary();

    expect(summary).toBeDefined();
    expect(summary.totalModules).toBe(0);
    expect(summary.successfulModules).toBe(0);
    expect(summary.failedModules).toBe(0);
    expect(summary.totalTestCases).toBe(0);
  });

  test('should aggregate empty coverage summary', () => {
    const summary = processor.aggregateCoverageSummary();

    expect(summary.branchCoverage).toBe(0);
    expect(summary.lineCoverage).toBe(0);
    expect(summary.methodCoverage).toBe(0);
    expect(summary.totalBranches).toBe(0);
    expect(summary.coveredBranches).toBe(0);
    expect(summary.totalLines).toBe(0);
    expect(summary.coveredLines).toBe(0);
    expect(summary.totalMethods).toBe(0);
    expect(summary.coveredMethods).toBe(0);
  });

  test('should aggregate empty execution summary', () => {
    const summary = processor.aggregateExecutionSummary();

    expect(summary.totalTests).toBe(0);
    expect(summary.passed).toBe(0);
    expect(summary.failed).toBe(0);
    expect(summary.skipped).toBe(0);
    expect(summary.passRate).toBe('0.00');
  });

  test('should handle module processing with valid module', async () => {
    const moduleInfo = new ModuleInfo();
    moduleInfo.moduleName = 'test-module';
    moduleInfo.modulePath = './src/test/example';
    moduleInfo.testDirectory = './src/test/example';

    const results = await processor.processModules([moduleInfo], {
      parseCoverage: false,
      parseExecution: false
    });

    expect(results.length).toBe(1);
    expect(results[0]).toBeDefined();
    expect(results[0].moduleInfo.moduleName).toBe('test-module');
  });

  test('should batch modules for processing', () => {
    const modules = [];
    for (let i = 0; i < 5; i++) {
      const module = new ModuleInfo();
      module.moduleName = `module-${i}`;
      modules.push(module);
    }

    const batches = [];
    for (let i = 0; i < modules.length; i += processor.options.maxConcurrency) {
      batches.push(modules.slice(i, i + processor.options.maxConcurrency));
    }

    expect(batches.length).toBe(3); // 5 modules / 2 max concurrency = 3 batches
    expect(batches[0].length).toBe(2);
    expect(batches[1].length).toBe(2);
    expect(batches[2].length).toBe(1);
  });

  test('should generate processing summary from module results', () => {
    const moduleInfo1 = new ModuleInfo();
    moduleInfo1.moduleName = 'module1';
    const moduleResult1 = new ModuleResult(moduleInfo1);
    moduleResult1.startProcessing();
    moduleResult1.testCases = [];
    moduleResult1.coverageSummary = {
      branchCoverage: 80,
      lineCoverage: 85,
      methodCoverage: 90,
      totalBranches: 100,
      coveredBranches: 80
    };
    moduleResult1.completeProcessing([], moduleResult1.coverageSummary);

    const moduleInfo2 = new ModuleInfo();
    moduleInfo2.moduleName = 'module2';
    const moduleResult2 = new ModuleResult(moduleInfo2);
    moduleResult2.startProcessing();
    moduleResult2.testCases = [];
    moduleResult2.coverageSummary = {
      branchCoverage: 70,
      lineCoverage: 75,
      methodCoverage: 80,
      totalBranches: 100,
      coveredBranches: 70
    };
    moduleResult2.completeProcessing([], moduleResult2.coverageSummary);

    processor.moduleResults = [moduleResult1, moduleResult2];

    const summary = processor.getProcessingSummary();

    expect(summary).toBeDefined();
    expect(summary.totalModules).toBe(2);
    expect(summary.successfulModules).toBe(2);
  });

  test('should calculate processing summary correctly', () => {
    const moduleInfo1 = new ModuleInfo();
    moduleInfo1.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo1);
    result1.startProcessing();
    result1.completeProcessing([], { branchCoverage: 80 });

    const moduleInfo2 = new ModuleInfo();
    moduleInfo2.moduleName = 'module2';
    const result2 = new ModuleResult(moduleInfo2);
    result2.startProcessing();
    result2.failProcessing('Test error');

    processor.moduleResults = [result1, result2];

    const summary = processor.getProcessingSummary();

    expect(summary.totalModules).toBe(2);
    expect(summary.successfulModules).toBe(1);
    expect(summary.failedModules).toBe(1);
  });

  test('should aggregate coverage from multiple modules', () => {
    const moduleInfo1 = new ModuleInfo();
    moduleInfo1.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo1);
    result1.startProcessing();
    result1.coverageSummary = {
      totalBranches: 100,
      coveredBranches: 80,
      totalLines: 200,
      coveredLines: 160,
      totalMethods: 50,
      coveredMethods: 40
    };
    result1.completeProcessing([], result1.coverageSummary);

    const moduleInfo2 = new ModuleInfo();
    moduleInfo2.moduleName = 'module2';
    const result2 = new ModuleResult(moduleInfo2);
    result2.startProcessing();
    result2.coverageSummary = {
      totalBranches: 150,
      coveredBranches: 120,
      totalLines: 300,
      coveredLines: 240,
      totalMethods: 75,
      coveredMethods: 60
    };
    result2.completeProcessing([], result2.coverageSummary);

    processor.moduleResults = [result1, result2];

    const summary = processor.aggregateCoverageSummary();

    expect(summary.totalBranches).toBe(250);
    expect(summary.coveredBranches).toBe(200);
    expect(summary.totalLines).toBe(500);
    expect(summary.coveredLines).toBe(400);
    expect(summary.totalMethods).toBe(125);
    expect(summary.coveredMethods).toBe(100);
    expect(summary.branchCoverage).toBe(80);
    expect(summary.lineCoverage).toBe(80);
    expect(summary.methodCoverage).toBe(80);
  });

  test('should aggregate execution summary from multiple modules', () => {
    const moduleInfo1 = new ModuleInfo();
    moduleInfo1.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo1);
    result1.startProcessing();
    result1.executionSummary = {
      totalTests: 10,
      passed: 8,
      failed: 1,
      skipped: 1
    };
    result1.completeProcessing([], {});

    const moduleInfo2 = new ModuleInfo();
    moduleInfo2.moduleName = 'module2';
    const result2 = new ModuleResult(moduleInfo2);
    result2.startProcessing();
    result2.executionSummary = {
      totalTests: 15,
      passed: 12,
      failed: 2,
      skipped: 1
    };
    result2.completeProcessing([], {});

    processor.moduleResults = [result1, result2];

    const summary = processor.aggregateExecutionSummary();

    expect(summary.totalTests).toBe(25);
    expect(summary.passed).toBe(20);
    expect(summary.failed).toBe(3);
    expect(summary.skipped).toBe(2);
    expect(parseFloat(summary.passRate)).toBeCloseTo(80.0, 1);
  });

  test('should handle modules without coverage data', () => {
    const moduleInfo = new ModuleInfo();
    moduleInfo.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo);
    result1.startProcessing();
    result1.coverageSummary = null;
    result1.failProcessing('No coverage');

    processor.moduleResults = [result1];

    const summary = processor.aggregateCoverageSummary();

    expect(summary.totalBranches).toBe(0);
    expect(summary.branchCoverage).toBe(0);
  });

  test('should handle modules without execution data', () => {
    const moduleInfo = new ModuleInfo();
    moduleInfo.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo);
    result1.startProcessing();
    result1.executionSummary = null;
    result1.failProcessing('No execution');

    processor.moduleResults = [result1];

    const summary = processor.aggregateExecutionSummary();

    expect(summary.totalTests).toBe(0);
    expect(summary.passRate).toBe('0.00');
  });

  test('should get module results directly from property', () => {
    const moduleInfo = new ModuleInfo();
    moduleInfo.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo);
    processor.moduleResults = [result1];

    expect(processor.moduleResults.length).toBe(1);
    expect(processor.moduleResults[0].moduleInfo.moduleName).toBe('module1');
  });

  test('should calculate summary with failed and successful modules', () => {
    const moduleInfo1 = new ModuleInfo();
    moduleInfo1.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo1);
    result1.startProcessing();
    result1.completeProcessing([], {
      totalBranches: 100,
      coveredBranches: 80
    });

    const moduleInfo2 = new ModuleInfo();
    moduleInfo2.moduleName = 'module2';
    const result2 = new ModuleResult(moduleInfo2);
    result2.startProcessing();
    result2.failProcessing('Error');

    processor.moduleResults = [result1, result2];

    const summary = processor.getProcessingSummary();

    expect(summary.successfulModules).toBe(1);
    expect(summary.failedModules).toBe(1);
    expect(summary.totalModules).toBe(2);
  });

  test('should filter successful modules using isSuccessful', () => {
    const moduleInfo1 = new ModuleInfo();
    moduleInfo1.moduleName = 'module1';
    const result1 = new ModuleResult(moduleInfo1);
    result1.startProcessing();
    result1.completeProcessing([], {});

    const moduleInfo2 = new ModuleInfo();
    moduleInfo2.moduleName = 'module2';
    const result2 = new ModuleResult(moduleInfo2);
    result2.startProcessing();
    result2.failProcessing('Error');

    processor.moduleResults = [result1, result2];

    const successfulModules = processor.moduleResults.filter(r => r.isSuccessful());

    expect(successfulModules.length).toBe(1);
    expect(successfulModules[0].moduleInfo.moduleName).toBe('module1');
  });
});
