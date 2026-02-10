/**
 * @jest-environment node
 *
 * CsvSheetBuilder.test.js
 *
 * Unit tests for CsvSheetBuilder - focusing on edge cases and branch coverage
 */

import { CsvSheetBuilder } from '../../core/CsvSheetBuilder.js';
import { TestCaseInfo } from '../../model/TestCaseInfo.js';
import { CoverageInfo } from '../../model/CoverageInfo.js';
import fs from 'fs/promises';

describe('CsvSheetBuilder', () => {
  let csvBuilder;

  beforeEach(() => {
    csvBuilder = new CsvSheetBuilder();
  });

  afterEach(async () => {
    // Clean up test files
    try {
      const files = await fs.readdir('./');
      for (const file of files) {
        if (file.startsWith('test-csv-') && file.endsWith('.csv')) {
          await fs.unlink(file);
        }
      }
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  test('should initialize CsvSheetBuilder', () => {
    expect(csvBuilder).toBeDefined();
  });

  test('should determine coverage status correctly for all ranges', () => {
    expect(csvBuilder.getCoverageStatus(95)).toBe('優秀');
    expect(csvBuilder.getCoverageStatus(90)).toBe('優秀');
    expect(csvBuilder.getCoverageStatus(85)).toBe('良好');
    expect(csvBuilder.getCoverageStatus(70)).toBe('良好');
    expect(csvBuilder.getCoverageStatus(65)).toBe('普通');
    expect(csvBuilder.getCoverageStatus(50)).toBe('普通');
    expect(csvBuilder.getCoverageStatus(45)).toBe('要改善');
    expect(csvBuilder.getCoverageStatus(0)).toBe('要改善');
  });

  test('should generate test details CSV with various test statuses', async () => {
    const testCase1 = new TestCaseInfo();
    testCase1.softwareService = 'テストサービス';
    testCase1.testItemName = 'テスト1';
    testCase1.testContent = 'テスト内容';
    testCase1.confirmationItem = '確認項目';
    testCase1.testModule = 'TestModule';
    testCase1.baselineVersion = '1.0.0';
    testCase1.creator = '作成者';
    testCase1.createdDate = '2026-01-01';

    const coverage1 = new CoverageInfo();
    coverage1.branchCovered = 95;
    coverage1.branchTotal = 100;
    testCase1.coverage = coverage1;

    const testCase2 = new TestCaseInfo();
    testCase2.softwareService = '';
    testCase2.testItemName = '';

    const testCases = [testCase1, testCase2];
    const outputPath = './test-csv-details.csv';

    await csvBuilder.generateTestDetailsCsv(outputPath, testCases);

    const content = await fs.readFile(outputPath, 'utf8');
    expect(content).toContain('番号');
    expect(content).toContain('テスト1');

    await fs.unlink(outputPath);
  });

  test('should generate summary CSV', async () => {
    const testCases = [];
    for (let i = 0; i < 10; i++) {
      const testCase = new TestCaseInfo();
      testCase.className = `Class${i}`;
      const coverage = new CoverageInfo();
      coverage.branchCovered = 80 + i;
      coverage.branchTotal = 100;
      testCase.coverage = coverage;
      testCases.push(testCase);
    }

    const coverageSummary = {
      branchCoverage: 85,
      lineCoverage: 88,
      methodCoverage: 92
    };
    const outputPath = './test-csv-summary.csv';

    await csvBuilder.generateSummaryCsv(outputPath, testCases, coverageSummary);

    const content = await fs.readFile(outputPath, 'utf8');
    expect(content).toContain('項目');
    expect(content).toContain('総テストケース数');

    await fs.unlink(outputPath);
  });

  test('should add UTF-8 BOM to CSV files', async () => {
    const testCases = [new TestCaseInfo()];
    const outputPath = './test-csv-bom.csv';

    await csvBuilder.generateTestDetailsCsv(outputPath, testCases);

    const buffer = await fs.readFile(outputPath);
    const content = buffer.toString('utf8');

    // Check for BOM
    expect(content.charCodeAt(0)).toBe(0xFEFF);

    await fs.unlink(outputPath);
  });

  test('should handle empty test cases array', async () => {
    const outputPath = './test-csv-empty.csv';

    await csvBuilder.generateTestDetailsCsv(outputPath, []);

    const content = await fs.readFile(outputPath, 'utf8');
    expect(content).toContain('番号');

    await fs.unlink(outputPath);
  });

  test('should generate all CSV files at once', async () => {
    const testCases = [
      (() => {
        const tc = new TestCaseInfo();
        tc.className = 'TestClass';
        const coverage = new CoverageInfo();
        coverage.branchCovered = 90;
        coverage.branchTotal = 100;
        tc.coverage = coverage;
        return tc;
      })()
    ];

    const coverageSummary = {
      branchCoverage: 90,
      lineCoverage: 92,
      methodCoverage: 95
    };

    const baseOutputPath = './test-all-csvs';

    const result = await csvBuilder.generateAllCsvFiles(testCases, coverageSummary, baseOutputPath);

    expect(result.testDetails).toBeDefined();
    expect(result.coverage).toBeDefined();

    // Verify files exist
    const testDetailsStats = await fs.stat(result.testDetails);
    expect(testDetailsStats.size).toBeGreaterThan(0);

    const coverageStats = await fs.stat(result.coverage);
    expect(coverageStats.size).toBeGreaterThan(0);

    // Clean up
    await fs.unlink(result.testDetails);
    await fs.unlink(result.coverage);
  });
});
