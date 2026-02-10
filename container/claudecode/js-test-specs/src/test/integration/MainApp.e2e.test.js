/**
 * @jest-environment node
 *
 * MainApp.e2e.test.js
 *
 * End-to-end tests for the main application workflow
 */

import { FolderScanner } from '../../core/FolderScanner.js';
import { AnnotationParser } from '../../core/AnnotationParser.js';
import { CoverageReportParser } from '../../core/CoverageReportParser.js';
import { TestExecutionParser } from '../../core/TestExecutionParser.js';
import { ExcelSheetBuilder } from '../../core/ExcelSheetBuilder.js';
import { CsvSheetBuilder } from '../../core/CsvSheetBuilder.js';
import fs from 'fs/promises';

describe('Main Application E2E Tests', () => {
  const testSourceDir = './src/test';
  const testCoverageDir = './coverage';
  const testOutputPath = './e2e-test-output.xlsx';

  afterEach(async () => {
    // Clean up generated files
    try {
      await fs.unlink(testOutputPath);
      await fs.unlink('./e2e-test-output_test_details.csv');
      await fs.unlink('./e2e-test-output_coverage.csv');
    } catch {}
  });

  test('should complete full workflow: scan -> parse -> coverage -> generate', async () => {
    // Step 1: Scan for test files
    const scanner = new FolderScanner();
    const testFiles = await scanner.findTestFiles(testSourceDir);

    expect(testFiles.length).toBeGreaterThan(0);

    // Step 2: Parse annotations
    const parser = new AnnotationParser();
    const testCases = await parser.parseFiles(testFiles);

    expect(testCases.length).toBeGreaterThan(0);

    // Step 3: Parse coverage (if available)
    let coverageSummary = {
      branchCoverage: 0,
      lineCoverage: 0,
      methodCoverage: 0,
      totalBranches: 0,
      coveredBranches: 0
    };

    try {
      const coverageParser = new CoverageReportParser();
      await coverageParser.parseCoverageDirectory(testCoverageDir);
      coverageSummary = coverageParser.getCoverageSummary();

      // Integrate coverage with test cases
      for (const testCase of testCases) {
        const coverage = coverageParser.getCoverageForClass(testCase.className);
        if (coverage) {
          testCase.setCoverageInfo(coverage.branchCovered, coverage.branchTotal);
        }
      }
    } catch (error) {
      // Coverage not available, continue without it
    }

    // Step 4: Parse test execution results (if available)
    try {
      const executionParser = new TestExecutionParser();
      await executionParser.parseTestResults('./test-results.json');

      for (const testCase of testCases) {
        const executionInfo = executionParser.getExecutionInfo(
          testCase.className,
          testCase.methodName
        );
        if (executionInfo) {
          testCase.setDetailedExecutionInfo(executionInfo);
        }
      }
    } catch (error) {
      // Test results not available, continue without them
    }

    // Step 5: Generate Excel
    const excelBuilder = new ExcelSheetBuilder();
    await excelBuilder.generateExcel(testCases, coverageSummary, testOutputPath);

    // Verify Excel was created
    const excelStats = await fs.stat(testOutputPath);
    expect(excelStats.size).toBeGreaterThan(0);

    // Step 6: Generate CSV
    const csvBuilder = new CsvSheetBuilder();
    const csvPaths = await csvBuilder.generateAllCsvFiles(
      testCases,
      coverageSummary,
      testOutputPath
    );

    // Verify CSV files were created
    const testDetailStats = await fs.stat(csvPaths.testDetails);
    expect(testDetailStats.size).toBeGreaterThan(0);

    const coverageStatsFile = await fs.stat(csvPaths.coverage);
    expect(coverageStatsFile.size).toBeGreaterThan(0);
  });

  test('should handle workflow without coverage', async () => {
    const scanner = new FolderScanner();
    const testFiles = await scanner.findTestFiles(testSourceDir);

    const parser = new AnnotationParser();
    const testCases = await parser.parseFiles(testFiles);

    const coverageSummary = {
      branchCoverage: 0,
      lineCoverage: 0,
      methodCoverage: 0
    };

    const excelBuilder = new ExcelSheetBuilder();
    await excelBuilder.generateExcel(testCases, coverageSummary, testOutputPath);

    const stats = await fs.stat(testOutputPath);
    expect(stats.size).toBeGreaterThan(0);
  });

  test('should handle workflow with only test discovery', async () => {
    const scanner = new FolderScanner();
    const testFiles = await scanner.findTestFiles(testSourceDir);

    expect(testFiles.length).toBeGreaterThan(0);

    // Verify all found files are test files
    for (const file of testFiles) {
      const isTestFile = /\.(test|spec)\.(js|jsx|ts|tsx)$/.test(file);
      expect(isTestFile).toBe(true);
    }
  });

  test('should verify directory and file existence checks', async () => {
    const scanner = new FolderScanner();

    // Test directory existence
    const srcExists = await scanner.directoryExists('./src');
    expect(srcExists).toBe(true);

    const fakeExists = await scanner.directoryExists('/fake/directory');
    expect(fakeExists).toBe(false);

    // Test file existence
    const packageExists = await scanner.fileExists('./package.json');
    expect(packageExists).toBe(true);

    const fakeFileExists = await scanner.fileExists('/fake/file.js');
    expect(fakeFileExists).toBe(false);
  });
});
