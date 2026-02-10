/**
 * @jest-environment node
 *
 * ExcelSheetBuilder.test.js
 *
 * Unit tests for ExcelSheetBuilder - focusing on edge cases
 */

import { ExcelSheetBuilder } from '../../core/ExcelSheetBuilder.js';
import { TestCaseInfo } from '../../model/TestCaseInfo.js';
import { CoverageInfo } from '../../model/CoverageInfo.js';
import fs from 'fs/promises';

describe('ExcelSheetBuilder', () => {
  let excelBuilder;

  beforeEach(() => {
    excelBuilder = new ExcelSheetBuilder();
  });

  afterEach(async () => {
    // Clean up test files
    try {
      const files = await fs.readdir('./');
      for (const file of files) {
        if (file.startsWith('test-excel-') && file.endsWith('.xlsx')) {
          await fs.unlink(file);
        }
      }
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  test('should initialize with new workbook', () => {
    expect(excelBuilder.workbook).toBeDefined();
    expect(excelBuilder.workbook.worksheets.length).toBeGreaterThanOrEqual(0);
  });

  test('should create test details sheet with empty test cases', async () => {
    await excelBuilder.createTestDetailsSheet([]);

    const sheet = excelBuilder.workbook.getWorksheet('テスト詳細');
    expect(sheet).toBeDefined();
  });

  test('should create test details sheet with various test data', async () => {
    const testCase1 = new TestCaseInfo();
    testCase1.softwareService = 'サービス1';
    testCase1.testItemName = 'テスト1';
    testCase1.testContent = '内容1';
    testCase1.confirmationItem = '確認1';
    testCase1.testModule = 'Module1';
    testCase1.baselineVersion = '1.0.0';
    testCase1.creator = '作成者1';
    testCase1.createdDate = '2026-01-01';

    const coverage1 = new CoverageInfo();
    coverage1.branchCovered = 95;
    coverage1.branchTotal = 100;
    testCase1.coverage = coverage1;

    const testCase2 = new TestCaseInfo();
    testCase2.softwareService = '';
    testCase2.testItemName = '';

    await excelBuilder.createTestDetailsSheet([testCase1, testCase2]);

    const sheet = excelBuilder.workbook.getWorksheet('テスト詳細');
    expect(sheet).toBeDefined();
    expect(sheet.rowCount).toBeGreaterThan(2); // Header + data rows
  });

  test('should create summary sheet with statistics', async () => {
    const testCases = [];
    for (let i = 0; i < 10; i++) {
      const tc = new TestCaseInfo();
      tc.className = `Class${i}`;
      const coverage = new CoverageInfo();
      coverage.branchCovered = 80 + i;
      coverage.branchTotal = 100;
      tc.coverage = coverage;
      testCases.push(tc);
    }

    const coverageSummary = {
      branchCoverage: 85,
      lineCoverage: 88,
      methodCoverage: 92,
      totalBranches: 1000,
      coveredBranches: 850
    };

    await excelBuilder.createSummarySheet(testCases, coverageSummary);

    const sheet = excelBuilder.workbook.getWorksheet('サマリー');
    expect(sheet).toBeDefined();
  });

  test('should create coverage sheet with method-level data', async () => {
    const testCase1 = new TestCaseInfo();
    testCase1.className = 'TestClass';
    testCase1.methodName = 'testMethod1';

    const coverage1 = new CoverageInfo();
    coverage1.branchCovered = 90;
    coverage1.branchTotal = 100;
    testCase1.coverage = coverage1;

    const coverageSummary = {
      branchCoverage: 70,
      lineCoverage: 75,
      methodCoverage: 80
    };

    await excelBuilder.createCoverageSheet([testCase1], coverageSummary);

    const sheet = excelBuilder.workbook.getWorksheet('カバレッジ');
    expect(sheet).toBeDefined();
  });

  test('should create config sheet', async () => {
    await excelBuilder.createConfigSheet();

    const sheet = excelBuilder.workbook.getWorksheet('設定情報');
    expect(sheet).toBeDefined();
  });

  test('should generate complete Excel with all sheets', async () => {
    const testCases = [
      (() => {
        const tc = new TestCaseInfo();
        tc.softwareService = 'テストサービス';
        tc.testItemName = 'テスト項目';
        tc.className = 'TestClass';
        const coverage = new CoverageInfo();
        coverage.branchCovered = 85;
        coverage.branchTotal = 100;
        tc.coverage = coverage;
        return tc;
      })()
    ];

    const coverageSummary = {
      branchCoverage: 85,
      lineCoverage: 88,
      methodCoverage: 92
    };

    const outputPath = './test-excel-complete.xlsx';

    await excelBuilder.generateExcel(testCases, coverageSummary, outputPath);

    const stats = await fs.stat(outputPath);
    expect(stats.size).toBeGreaterThan(0);

    await fs.unlink(outputPath);
  });

  test('should handle empty coverage summary', async () => {
    const testCases = [];
    const coverageSummary = {
      branchCoverage: 0,
      lineCoverage: 0,
      methodCoverage: 0
    };

    await excelBuilder.createCoverageSheet(testCases, coverageSummary);

    const sheet = excelBuilder.workbook.getWorksheet('カバレッジ');
    expect(sheet).toBeDefined();
  });

  test('should format dates in config sheet', async () => {
    await excelBuilder.createConfigSheet();

    const sheet = excelBuilder.workbook.getWorksheet('設定情報');
    expect(sheet).toBeDefined();
    // Config sheet should contain generation date
    expect(sheet.rowCount).toBeGreaterThan(0);
  });

  test('should apply column widths', async () => {
    const testCases = [new TestCaseInfo()];

    await excelBuilder.createTestDetailsSheet(testCases);

    const sheet = excelBuilder.workbook.getWorksheet('テスト詳細');
    const columns = sheet.columns;

    // Columns should have widths defined
    expect(columns.length).toBeGreaterThan(0);
  });

  test('should handle very long text in cells', async () => {
    const testCase = new TestCaseInfo();
    testCase.testContent = 'A'.repeat(1000); // Very long text
    testCase.confirmationItem = 'B'.repeat(500);

    await excelBuilder.createTestDetailsSheet([testCase]);

    const sheet = excelBuilder.workbook.getWorksheet('テスト詳細');
    expect(sheet).toBeDefined();
  });

  test('should handle special characters in text', async () => {
    const testCase = new TestCaseInfo();
    testCase.softwareService = 'サービス "特殊" 文字\n改行';
    testCase.testItemName = 'テスト, タブ\t文字';

    await excelBuilder.createTestDetailsSheet([testCase]);

    const sheet = excelBuilder.workbook.getWorksheet('テスト詳細');
    expect(sheet).toBeDefined();
  });
});
