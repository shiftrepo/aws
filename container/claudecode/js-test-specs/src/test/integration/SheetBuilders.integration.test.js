/**
 * @jest-environment node
 *
 * SheetBuilders.integration.test.js
 *
 * Integration tests for ExcelSheetBuilder and CsvSheetBuilder
 */

import { ExcelSheetBuilder } from '../../core/ExcelSheetBuilder.js';
import { CsvSheetBuilder } from '../../core/CsvSheetBuilder.js';
import { TestCaseInfo } from '../../model/TestCaseInfo.js';
import fs from 'fs/promises';

describe('ExcelSheetBuilder Integration Tests', () => {
  let excelBuilder;
  let testCases;
  let coverageSummary;

  beforeEach(() => {
    excelBuilder = new ExcelSheetBuilder();

    // Create sample test cases
    const testCase1 = new TestCaseInfo();
    testCase1.className = 'TestClass';
    testCase1.methodName = 'test1';
    testCase1.softwareService = 'テストサービス';
    testCase1.testItemName = 'テスト項目1';
    testCase1.testContent = 'テスト内容1';
    testCase1.confirmationItem = '確認項目1';
    testCase1.testModule = 'TestModule';
    testCase1.setCoverageInfo(80, 100);
    testCase1.setDetailedExecutionInfo({
      status: 'PASS',
      duration: 123
    });

    const testCase2 = new TestCaseInfo();
    testCase2.className = 'TestClass';
    testCase2.methodName = 'test2';
    testCase2.softwareService = 'テストサービス';
    testCase2.testItemName = 'テスト項目2';
    testCase2.setCoverageInfo(60, 100);
    testCase2.setDetailedExecutionInfo({
      status: 'FAIL',
      duration: 50,
      errorMessage: 'Test failed'
    });

    testCases = [testCase1, testCase2];

    coverageSummary = {
      branchCoverage: 75,
      lineCoverage: 80,
      methodCoverage: 85,
      totalBranches: 100,
      coveredBranches: 75
    };
  });

  afterEach(async () => {
    // Clean up generated files
    try {
      await fs.unlink('./test-output.xlsx');
    } catch {}
  });

  test('should generate Excel file with all sheets', async () => {
    const outputPath = './test-output.xlsx';

    await excelBuilder.generateExcel(testCases, coverageSummary, outputPath);

    // Verify file was created
    const stats = await fs.stat(outputPath);
    expect(stats.size).toBeGreaterThan(0);
  });

  test('should create test details sheet', async () => {
    await excelBuilder.createTestDetailsSheet(testCases);

    expect(excelBuilder.workbook.worksheets.length).toBeGreaterThan(0);
    const sheet = excelBuilder.workbook.getWorksheet('テスト詳細');
    expect(sheet).toBeDefined();
  });

  test('should create summary sheet', async () => {
    await excelBuilder.createSummarySheet(testCases, coverageSummary);

    const sheet = excelBuilder.workbook.getWorksheet('サマリー');
    expect(sheet).toBeDefined();
  });

  test('should create coverage sheet', async () => {
    await excelBuilder.createCoverageSheet(testCases, null);

    const sheet = excelBuilder.workbook.getWorksheet('カバレッジ');
    expect(sheet).toBeDefined();
  });

  test('should create config sheet', async () => {
    await excelBuilder.createConfigSheet();

    const sheet = excelBuilder.workbook.getWorksheet('設定情報');
    expect(sheet).toBeDefined();
  });
});

describe('CsvSheetBuilder Integration Tests', () => {
  let csvBuilder;
  let testCases;
  let coverageSummary;

  beforeEach(() => {
    csvBuilder = new CsvSheetBuilder();

    // Create sample test cases
    const testCase1 = new TestCaseInfo();
    testCase1.className = 'TestClass';
    testCase1.methodName = 'test1';
    testCase1.softwareService = 'サービス';
    testCase1.testItemName = 'テスト1';
    testCase1.setCoverageInfo(90, 100);

    const testCase2 = new TestCaseInfo();
    testCase2.className = 'TestClass';
    testCase2.methodName = 'test2';
    testCase2.setCoverageInfo(70, 100);

    testCases = [testCase1, testCase2];

    coverageSummary = {
      branchCoverage: 80,
      lineCoverage: 85,
      methodCoverage: 75,
      totalBranches: 100,
      coveredBranches: 80
    };
  });

  afterEach(async () => {
    // Clean up generated files
    try {
      await fs.unlink('./test-csv_test_details.csv');
      await fs.unlink('./test-csv_coverage.csv');
    } catch {}
  });

  test('should generate all CSV files', async () => {
    const result = await csvBuilder.generateAllCsvFiles(
      testCases,
      coverageSummary,
      './test-csv.csv'
    );

    expect(result.testDetails).toBeDefined();
    expect(result.coverage).toBeDefined();

    // Verify files were created
    const testDetailsStats = await fs.stat(result.testDetails);
    expect(testDetailsStats.size).toBeGreaterThan(0);

    const coverageStats = await fs.stat(result.coverage);
    expect(coverageStats.size).toBeGreaterThan(0);
  });

  test('should generate test details CSV', async () => {
    const outputPath = './test-csv_test_details.csv';

    await csvBuilder.generateTestDetailsCsv(outputPath, testCases);

    // Verify file was created
    const stats = await fs.stat(outputPath);
    expect(stats.size).toBeGreaterThan(0);

    // Read and verify content
    const content = await fs.readFile(outputPath, 'utf8');
    expect(content).toContain('FQN');
    expect(content).toContain('テスト1');
  });

  test('should generate coverage CSV', async () => {
    const outputPath = './test-csv_coverage.csv';

    await csvBuilder.generateCoverageCsv(outputPath, testCases, coverageSummary);

    // Verify file was created
    const stats = await fs.stat(outputPath);
    expect(stats.size).toBeGreaterThan(0);

    // Read and verify content
    const content = await fs.readFile(outputPath, 'utf8');
    expect(content).toContain('クラス名');
    expect(content).toContain('TestClass');
  });

  test('should add UTF-8 BOM to CSV files', async () => {
    const outputPath = './test-csv_test_details.csv';

    await csvBuilder.generateTestDetailsCsv(outputPath, testCases);

    // Read file as buffer to check BOM
    const buffer = await fs.readFile(outputPath);
    const content = buffer.toString('utf8');

    // Check for BOM
    expect(content.charCodeAt(0)).toBe(0xFEFF);
  });

  test('should determine correct coverage status', () => {
    expect(csvBuilder.getCoverageStatus(95)).toBe('優秀');
    expect(csvBuilder.getCoverageStatus(75)).toBe('良好');
    expect(csvBuilder.getCoverageStatus(55)).toBe('普通');
    expect(csvBuilder.getCoverageStatus(30)).toBe('要改善');
  });

  test('should generate summary CSV', async () => {
    const outputPath = './test-summary.csv';

    await csvBuilder.generateSummaryCsv(outputPath, testCases, coverageSummary);

    // Verify file was created
    const stats = await fs.stat(outputPath);
    expect(stats.size).toBeGreaterThan(0);

    // Clean up
    await fs.unlink(outputPath);
  });
});
