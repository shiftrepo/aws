/**
 * CoverageInfo.test.js
 *
 * Unit tests for CoverageInfo model
 */

import { CoverageInfo } from '../../model/CoverageInfo.js';

describe('CoverageInfo', () => {
  let coverage;

  beforeEach(() => {
    coverage = new CoverageInfo();
  });

  test('should initialize with default values', () => {
    expect(coverage.packageName).toBe('');
    expect(coverage.className).toBe('');
    expect(coverage.methodName).toBe('');
    expect(coverage.branchCovered).toBe(0);
    expect(coverage.branchTotal).toBe(0);
    expect(coverage.lineCovered).toBe(0);
    expect(coverage.lineTotal).toBe(0);
  });

  test('should calculate branch coverage percent', () => {
    coverage.branchCovered = 80;
    coverage.branchTotal = 100;
    expect(coverage.getBranchCoveragePercent()).toBe(80);
  });

  test('should return 0 for branch coverage when total is 0', () => {
    coverage.branchCovered = 0;
    coverage.branchTotal = 0;
    expect(coverage.getBranchCoveragePercent()).toBe(0);
  });

  test('should calculate line coverage percent', () => {
    coverage.lineCovered = 150;
    coverage.lineTotal = 200;
    expect(coverage.getLineCoveragePercent()).toBe(75);
  });

  test('should return 0 for line coverage when total is 0', () => {
    coverage.lineCovered = 0;
    coverage.lineTotal = 0;
    expect(coverage.getLineCoveragePercent()).toBe(0);
  });

  test('should calculate instruction coverage percent', () => {
    coverage.instructionCovered = 450;
    coverage.instructionTotal = 500;
    expect(coverage.getInstructionCoveragePercent()).toBe(90);
  });

  test('should calculate method coverage percent', () => {
    coverage.methodCovered = 18;
    coverage.methodTotal = 20;
    expect(coverage.getMethodCoveragePercent()).toBe(90);
  });

  test('should calculate class coverage percent', () => {
    coverage.classCovered = 9;
    coverage.classTotal = 10;
    expect(coverage.getClassCoveragePercent()).toBe(90);
  });

  test('should return 優秀 status for >= 90%', () => {
    coverage.branchCovered = 95;
    coverage.branchTotal = 100;
    expect(coverage.getCoverageStatus()).toBe('優秀');
  });

  test('should return 良好 status for 70-89%', () => {
    coverage.branchCovered = 75;
    coverage.branchTotal = 100;
    expect(coverage.getCoverageStatus()).toBe('良好');
  });

  test('should return 普通 status for 50-69%', () => {
    coverage.branchCovered = 60;
    coverage.branchTotal = 100;
    expect(coverage.getCoverageStatus()).toBe('普通');
  });

  test('should return 要改善 status for 1-49%', () => {
    coverage.branchCovered = 30;
    coverage.branchTotal = 100;
    expect(coverage.getCoverageStatus()).toBe('要改善');
  });

  test('should return カバレッジなし status for 0%', () => {
    coverage.branchCovered = 0;
    coverage.branchTotal = 100;
    expect(coverage.getCoverageStatus()).toBe('カバレッジなし');
  });

  test('should generate toString output', () => {
    coverage.packageName = 'com.example';
    coverage.className = 'MyClass';
    coverage.methodName = 'myMethod';
    coverage.branchCovered = 80;
    coverage.branchTotal = 100;
    coverage.lineCovered = 150;
    coverage.lineTotal = 200;

    const str = coverage.toString();
    expect(str).toContain('com.example');
    expect(str).toContain('MyClass');
    expect(str).toContain('myMethod');
    expect(str).toContain('80.00%');
    expect(str).toContain('75.00%');
  });
});
