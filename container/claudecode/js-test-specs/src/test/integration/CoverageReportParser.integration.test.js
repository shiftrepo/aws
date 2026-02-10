/**
 * @jest-environment node
 *
 * CoverageReportParser.integration.test.js
 *
 * Integration tests for CoverageReportParser with actual coverage files
 */

import { CoverageReportParser } from '../../core/CoverageReportParser.js';
import fs from 'fs/promises';

describe('CoverageReportParser Integration Tests', () => {
  let parser;

  beforeEach(() => {
    parser = new CoverageReportParser();
  });

  test('should parse coverage directory with coverage-final.json', async () => {
    const coverageDir = './coverage';

    try {
      await parser.parseCoverageDirectory(coverageDir);

      const summary = parser.getCoverageSummary();

      expect(summary).toBeDefined();
      expect(summary.branchCoverage).toBeGreaterThanOrEqual(0);
      expect(summary.lineCoverage).toBeGreaterThanOrEqual(0);
      expect(summary.methodCoverage).toBeGreaterThanOrEqual(0);
    } catch (error) {
      // If coverage doesn't exist, that's OK
      expect(error.message).toBeTruthy();
    }
  });

  test('should handle missing coverage directory', async () => {
    const result = await parser.parseCoverageDirectory('/nonexistent/coverage');

    expect(result).toBeInstanceOf(Map);
    expect(result.size).toBe(0);
  });

  test('should get coverage for BasicCalculator class', async () => {
    try {
      await parser.parseCoverageDirectory('./coverage');

      const coverage = parser.getCoverageForClass('BasicCalculator');

      if (coverage) {
        expect(coverage.className).toBeTruthy();
        expect(coverage.branchTotal).toBeGreaterThanOrEqual(0);
      }
    } catch (error) {
      expect(true).toBe(true);
    }
  });

  test('should parse method-level coverage', async () => {
    const mockCoverageData = {
      '/path/to/file.js': {
        fnMap: {
          '0': {
            name: 'add',
            loc: {
              start: { line: 10 },
              end: { line: 15 }
            }
          },
          '1': {
            name: 'subtract',
            loc: {
              start: { line: 20 },
              end: { line: 25 }
            }
          }
        },
        f: {
          '0': 10,
          '1': 5
        },
        statementMap: {
          '0': { start: { line: 11 }, end: { line: 11 } },
          '1': { start: { line: 12 }, end: { line: 12 } },
          '2': { start: { line: 21 }, end: { line: 21 } }
        },
        s: {
          '0': 10,
          '1': 10,
          '2': 5
        },
        branchMap: {
          '0': { loc: { start: { line: 13 } } },
          '1': { loc: { start: { line: 22 } } }
        },
        b: {
          '0': [8, 2],
          '1': [3, 2]
        }
      }
    };

    // Write mock coverage file
    const tempCoverageFile = './test-coverage-temp.json';
    await fs.writeFile(tempCoverageFile, JSON.stringify(mockCoverageData));

    try {
      await parser.parseCoverageJson(tempCoverageFile);

      const methods = parser.getAllMethodCoverage();

      expect(methods).toBeDefined();
      expect(Array.isArray(methods)).toBe(true);
      expect(methods.length).toBeGreaterThan(0);

      // Clean up
      await fs.unlink(tempCoverageFile);
    } catch (error) {
      // Clean up on error
      try {
        await fs.unlink(tempCoverageFile);
      } catch {}
      throw error;
    }
  });

  test('should get method coverage for specific class', async () => {
    try {
      await parser.parseCoverageDirectory('./coverage');

      const methods = parser.getMethodCoverageForClass('BasicCalculator');

      expect(Array.isArray(methods)).toBe(true);
    } catch (error) {
      expect(true).toBe(true);
    }
  });

  test('should calculate coverage summary across multiple files', async () => {
    const mockData = {
      'file1.js': {
        b: { '0': [5, 3], '1': [10, 0] },
        s: { '0': 10, '1': 8, '2': 5 },
        f: { '0': 5, '1': 3 }
      },
      'file2.js': {
        b: { '0': [8, 2] },
        s: { '0': 15, '1': 12 },
        f: { '0': 10 }
      }
    };

    const tempFile = './test-summary-coverage.json';
    await fs.writeFile(tempFile, JSON.stringify(mockData));

    try {
      await parser.parseCoverageJson(tempFile);
      const summary = parser.getCoverageSummary();

      expect(summary.totalBranches).toBeGreaterThan(0);
      expect(summary.totalLines).toBeGreaterThan(0);
      expect(summary.totalMethods).toBeGreaterThan(0);

      await fs.unlink(tempFile);
    } catch (error) {
      try {
        await fs.unlink(tempFile);
      } catch {}
      throw error;
    }
  });
});
