/**
 * @jest-environment node
 *
 * CoverageReportParser.test.js
 *
 * Unit tests for CoverageReportParser - focusing on method-level coverage
 */

import { CoverageReportParser } from '../../core/CoverageReportParser.js';
import { CoverageInfo } from '../../model/CoverageInfo.js';
import fs from 'fs/promises';

describe('CoverageReportParser', () => {
  let parser;

  beforeEach(() => {
    parser = new CoverageReportParser();
  });

  test('should initialize with empty coverage map', () => {
    expect(parser.coverageData).toBeDefined();
    expect(Object.keys(parser.coverageData).length).toBe(0);
  });

  test('should parse actual coverage file', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const summary = parser.getCoverageSummary();
    expect(summary).toBeDefined();
    expect(typeof summary.branchCoverage).toBe('number');
    expect(typeof summary.lineCoverage).toBe('number');
    expect(typeof summary.methodCoverage).toBe('number');
  });

  test('should handle non-existent coverage directory', async () => {
    await parser.parseCoverageDirectory('/nonexistent/coverage');

    const summary = parser.getCoverageSummary();
    expect(summary.branchCoverage).toBe(0);
    expect(summary.lineCoverage).toBe(0);
    expect(summary.methodCoverage).toBe(0);
  });

  test('should get coverage for specific class', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const coverage = parser.getCoverageForClass('BasicCalculator');

    if (coverage) {
      expect(coverage).toBeInstanceOf(CoverageInfo);
      expect(coverage.className).toBeTruthy();
    }
  });

  test('should return null for non-existent class', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const coverage = parser.getCoverageForClass('NonExistentClass12345');

    expect(coverage).toBeNull();
  });

  test('should parse method coverage from coverage data', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const methodCoverage = parser.getMethodCoverageForClass('BasicCalculator');

    if (methodCoverage && methodCoverage.length > 0) {
      expect(Array.isArray(methodCoverage)).toBe(true);
      methodCoverage.forEach(coverage => {
        expect(coverage).toBeInstanceOf(CoverageInfo);
        expect(coverage.methodName).toBeTruthy();
      });
    }
  });

  test('should get all method coverage', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const allMethodCoverage = parser.getAllMethodCoverage();

    expect(Array.isArray(allMethodCoverage)).toBe(true);
    if (allMethodCoverage.length > 0) {
      allMethodCoverage.forEach(coverage => {
        expect(coverage).toBeInstanceOf(CoverageInfo);
        expect(coverage.className).toBeTruthy();
      });
    }
  });

  test('should calculate coverage summary with multiple classes', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const summary = parser.getCoverageSummary();

    expect(summary.totalBranches).toBeGreaterThanOrEqual(0);
    expect(summary.coveredBranches).toBeGreaterThanOrEqual(0);
    expect(summary.totalLines).toBeGreaterThanOrEqual(0);
    expect(summary.coveredLines).toBeGreaterThanOrEqual(0);
  });

  test('should parse file-level coverage correctly', async () => {
    const mockCoverageInfo = new CoverageInfo();
    mockCoverageInfo.className = 'file';
    mockCoverageInfo.branchCovered = 1;
    mockCoverageInfo.branchTotal = 2;
    mockCoverageInfo.lineCovered = 1;
    mockCoverageInfo.lineTotal = 2;

    // Manually set coverage data using Map
    parser.coverageData = new Map();
    parser.coverageData.set('file', mockCoverageInfo);

    const coverage = parser.getCoverageForClass('file');

    expect(coverage).toBeDefined();
    if (coverage) {
      expect(coverage.lineCovered).toBeGreaterThanOrEqual(0);
      expect(coverage.lineTotal).toBeGreaterThanOrEqual(0);
    }
  });

  test('should handle empty coverage data gracefully', () => {
    parser.coverageData = new Map();

    const summary = parser.getCoverageSummary();

    expect(summary.branchCoverage).toBe(0);
    expect(summary.lineCoverage).toBe(0);
    expect(summary.methodCoverage).toBe(0);
  });

  test('should calculate branch coverage percentage correctly', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const summary = parser.getCoverageSummary();

    if (summary.totalBranches > 0) {
      const expectedPercentage = (summary.coveredBranches / summary.totalBranches) * 100;
      expect(summary.branchCoverage).toBeCloseTo(expectedPercentage, 2);
    }
  });

  test('should calculate line coverage percentage correctly', async () => {
    await parser.parseCoverageDirectory('./coverage');

    const summary = parser.getCoverageSummary();

    if (summary.totalLines > 0) {
      const expectedPercentage = (summary.coveredLines / summary.totalLines) * 100;
      expect(summary.lineCoverage).toBeCloseTo(expectedPercentage, 2);
    }
  });

  test('should parse method coverage with anonymous functions', () => {
    const mockFileData = {
      fnMap: {
        '0': { name: '', loc: { start: { line: 5 }, end: { line: 10 } } },
        '1': { name: 'namedFunction', loc: { start: { line: 15 }, end: { line: 20 } } }
      },
      f: { '0': 1, '1': 0 },
      statementMap: {
        '0': { start: { line: 5 }, end: { line: 5 } },
        '1': { start: { line: 6 }, end: { line: 6 } },
        '2': { start: { line: 15 }, end: { line: 15 } }
      },
      s: { '0': 1, '1': 1, '2': 0 },
      branchMap: {},
      b: {}
    };

    const methodCoverages = parser.parseMethodCoverage(mockFileData, 'TestClass');

    expect(Array.isArray(methodCoverages)).toBe(true);
    expect(methodCoverages.length).toBe(2);

    // Check anonymous function
    const anonymousFunc = methodCoverages.find(m => m.methodName.includes('anonymous'));
    expect(anonymousFunc).toBeDefined();

    // Check named function
    const namedFunc = methodCoverages.find(m => m.methodName === 'namedFunction');
    expect(namedFunc).toBeDefined();
  });

  test('should handle coverage data without function map', () => {
    const mockFileData = {
      fnMap: {},
      f: {},
      statementMap: {
        '0': { start: { line: 1 }, end: { line: 1 } }
      },
      s: { '0': 1 },
      branchMap: {},
      b: {}
    };

    const methodCoverages = parser.parseMethodCoverage(mockFileData, 'TestClass');

    expect(Array.isArray(methodCoverages)).toBe(true);
    expect(methodCoverages.length).toBe(0);
  });
});
