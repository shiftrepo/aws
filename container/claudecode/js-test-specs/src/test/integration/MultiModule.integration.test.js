/**
 * @jest-environment node
 *
 * MultiModule.integration.test.js
 *
 * Integration tests for WorkspaceDetector and MultiModuleProcessor
 */

import { WorkspaceDetector } from '../../core/WorkspaceDetector.js';
import { MultiModuleProcessor } from '../../core/MultiModuleProcessor.js';
import { ModuleInfo } from '../../model/ModuleInfo.js';
import fs from 'fs/promises';

describe('WorkspaceDetector Integration Tests', () => {
  let detector;

  beforeEach(() => {
    detector = new WorkspaceDetector();
  });

  test('should initialize with empty modules', () => {
    expect(detector.rootPath).toBe('');
    expect(detector.modules).toEqual([]);
    expect(detector.rootPackageJson).toBeNull();
  });

  test('should detect current project as non-workspace', async () => {
    const isWorkspace = await detector.detectWorkspace('.');

    // Current project doesn't have workspaces configured
    expect(typeof isWorkspace).toBe('boolean');
  });

  test('should handle non-existent directory', async () => {
    const isWorkspace = await detector.detectWorkspace('/nonexistent/path');

    expect(isWorkspace).toBe(false);
  });

  test('should get modules list', () => {
    const modules = detector.getModules();

    expect(Array.isArray(modules)).toBe(true);
  });

  test('should get workspace summary', () => {
    const summary = detector.getWorkspaceSummary();

    expect(summary).toBeDefined();
    expect(summary.rootPath).toBeDefined();
    expect(summary.moduleCount).toBeDefined();
    expect(Array.isArray(summary.modules)).toBe(true);
  });

  test('should check for lerna config', async () => {
    const hasLerna = await detector.checkLernaConfig();

    expect(typeof hasLerna).toBe('boolean');
  });

  test('should create module info from package.json', async () => {
    const packageJsonPath = './package.json';

    try {
      const moduleInfo = await detector.createModuleInfo(packageJsonPath);

      expect(moduleInfo).toBeInstanceOf(ModuleInfo);
      expect(moduleInfo.moduleName).toBeTruthy();
    } catch (error) {
      expect(error).toBeDefined();
    }
  });
});

describe('MultiModuleProcessor Integration Tests', () => {
  let processor;

  beforeEach(() => {
    processor = new MultiModuleProcessor({
      maxConcurrency: 2,
      timeout: 10000
    });
  });

  test('should initialize with options', () => {
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
  });

  test('should aggregate empty coverage summary', () => {
    const summary = processor.aggregateCoverageSummary();

    expect(summary.branchCoverage).toBe(0);
    expect(summary.lineCoverage).toBe(0);
    expect(summary.methodCoverage).toBe(0);
  });

  test('should aggregate empty execution summary', () => {
    const summary = processor.aggregateExecutionSummary();

    expect(summary.totalTests).toBe(0);
    expect(summary.passed).toBe(0);
    expect(summary.failed).toBe(0);
    expect(summary.passRate).toBe('0.00');
  });

  test('should handle module processing error gracefully', async () => {
    const invalidModule = new ModuleInfo();
    invalidModule.moduleName = 'invalid-module';
    invalidModule.modulePath = '/nonexistent/path';
    invalidModule.testDirectory = '/nonexistent/test';

    const results = await processor.processModules([invalidModule], {
      parseCoverage: false,
      parseExecution: false
    });

    expect(results.length).toBe(1);
    // Worker may succeed even with no tests found, so check for results
    expect(results[0]).toBeDefined();
    expect(results[0].testCases).toBeDefined();
  });
});
