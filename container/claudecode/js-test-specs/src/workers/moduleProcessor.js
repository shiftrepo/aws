/**
 * moduleProcessor.js
 *
 * Worker thread for processing individual modules.
 * Runs the complete test specification generation pipeline for a single module.
 *
 * @module workers/moduleProcessor
 */

import { parentPort, workerData } from 'worker_threads';
import { FolderScanner } from '../core/FolderScanner.js';
import { AnnotationParser } from '../core/AnnotationParser.js';
import { CoverageReportParser } from '../core/CoverageReportParser.js';
import { TestExecutionParser } from '../core/TestExecutionParser.js';
import path from 'path';
import fs from 'fs/promises';

/**
 * Process module in worker thread
 */
async function processModule() {
  try {
    const { moduleInfo, options } = workerData;

    const result = {
      testCases: [],
      coverageSummary: {
        branchCoverage: 0,
        lineCoverage: 0,
        methodCoverage: 0,
        totalBranches: 0,
        coveredBranches: 0
      },
      executionSummary: {
        totalTests: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        passRate: 0
      },
      warnings: []
    };

    // Step 1: Scan for test files
    const scanner = new FolderScanner();
    const testFiles = await scanner.findTestFiles(moduleInfo.testDirectory);

    if (testFiles.length === 0) {
      result.warnings.push(`No test files found in ${moduleInfo.testDirectory}`);
      parentPort.postMessage(result);
      return;
    }

    // Step 2: Parse annotations
    const parser = new AnnotationParser();
    const testCases = await parser.parseFiles(testFiles);

    if (testCases.length === 0) {
      result.warnings.push(`No test cases extracted from ${testFiles.length} test files`);
    }

    result.testCases = testCases;

    // Step 3: Parse coverage if available
    if (options.parseCoverage !== false) {
      try {
        const coverageDir = moduleInfo.coverageDirectory;
        const coveragePath = path.join(coverageDir, 'coverage-final.json');
        await fs.access(coveragePath);

        const coverageParser = new CoverageReportParser();
        await coverageParser.parseCoverageDirectory(coverageDir);
        result.coverageSummary = coverageParser.getCoverageSummary();

        // Integrate coverage with test cases
        for (const testCase of testCases) {
          const coverage = coverageParser.getCoverageForClass(testCase.className);
          if (coverage) {
            testCase.setCoverageInfo(coverage.branchCovered, coverage.branchTotal);
          }
        }
      } catch (error) {
        result.warnings.push(`Coverage not available: ${error.message}`);
      }
    }

    // Step 4: Parse test execution results if available
    if (options.parseExecution !== false) {
      try {
        const testResultsPath = path.join(moduleInfo.modulePath, 'test-results.json');
        await fs.access(testResultsPath);

        const executionParser = new TestExecutionParser();
        await executionParser.parseTestResults(testResultsPath);
        result.executionSummary = executionParser.getExecutionSummary();

        // Integrate execution results with test cases
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
        result.warnings.push(`Test execution results not available: ${error.message}`);
      }
    }

    // Send result back to main thread
    parentPort.postMessage(result);
  } catch (error) {
    // Send error back to main thread
    parentPort.postMessage({
      error: {
        message: error.message,
        stack: error.stack
      }
    });
  }
}

// Start processing
processModule();
