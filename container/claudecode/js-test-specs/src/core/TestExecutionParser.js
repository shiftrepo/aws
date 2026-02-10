/**
 * TestExecutionParser.js
 *
 * Parses Jest test execution results from JSON output.
 * Extracts test status (passed/failed/skipped), duration, and error information.
 *
 * @module core/TestExecutionParser
 */

import fs from 'fs/promises';
import { logger } from '../util/Logger.js';

/**
 * Test execution result parser
 * Parses Jest JSON output to extract test execution information
 */
export class TestExecutionParser {
  constructor() {
    this.testResults = new Map();
  }

  /**
   * Parse Jest JSON results file
   * @param {string} jsonPath - Path to test-results.json
   * @returns {Promise<Map<string, Object>>} Map of test results by test name
   */
  async parseTestResults(jsonPath) {
    try {
      logger.info('Test execution results parsing started', { jsonPath });

      const content = await fs.readFile(jsonPath, 'utf8');
      const results = JSON.parse(content);

      logger.debug('Jest results parsed', {
        numTotalTests: results.numTotalTests,
        numPassedTests: results.numPassedTests,
        numFailedTests: results.numFailedTests,
        numPendingTests: results.numPendingTests
      });

      // Process each test suite
      if (results.testResults && Array.isArray(results.testResults)) {
        for (const testSuite of results.testResults) {
          await this.parseTestSuite(testSuite);
        }
      }

      logger.info('Test execution results parsing completed', {
        totalTests: this.testResults.size
      });

      return this.testResults;
    } catch (error) {
      logger.error('Test execution results parsing error', error);
      return new Map();
    }
  }

  /**
   * Parse individual test suite
   * @param {Object} testSuite - Test suite object from Jest results
   */
  async parseTestSuite(testSuite) {
    try {
      const filePath = testSuite.name;
      const assertionResults = testSuite.assertionResults || [];

      logger.debug('Parsing test suite', {
        filePath,
        testCount: assertionResults.length,
        status: testSuite.status
      });

      for (const assertion of assertionResults) {
        const testName = assertion.title || assertion.fullName;
        const testKey = this.createTestKey(filePath, testName);

        const executionInfo = {
          testName,
          filePath,
          status: this.normalizeStatus(assertion.status),
          duration: assertion.duration || 0,
          errorMessage: this.extractErrorMessage(assertion),
          errorType: this.extractErrorType(assertion),
          failureMessages: assertion.failureMessages || [],
          ancestorTitles: assertion.ancestorTitles || [],
          fullName: assertion.fullName || testName
        };

        this.testResults.set(testKey, executionInfo);

        logger.debug('Test execution info extracted', {
          testKey,
          status: executionInfo.status,
          duration: executionInfo.duration
        });
      }
    } catch (error) {
      logger.warn('Test suite parsing error', {
        file: testSuite.name,
        error: error.message
      });
    }
  }

  /**
   * Create unique test key from file path and test name
   * @param {string} filePath - Test file path
   * @param {string} testName - Test name
   * @returns {string} Unique test key
   */
  createTestKey(filePath, testName) {
    // Extract just the filename without path
    const fileName = filePath.split('/').pop().split('\\').pop();
    // Remove .test.js or .spec.js extension
    const className = fileName.replace(/\.(test|spec)\.(js|jsx|ts|tsx)$/, '');
    return `${className}::${testName}`;
  }

  /**
   * Normalize Jest test status to standardized format
   * @param {string} jestStatus - Jest status (passed, failed, pending, skipped, todo, disabled)
   * @returns {string} Normalized status (PASS, FAIL, SKIP, ERROR)
   */
  normalizeStatus(jestStatus) {
    if (!jestStatus) return 'UNKNOWN';

    const status = jestStatus.toLowerCase();

    switch (status) {
      case 'passed':
        return 'PASS';
      case 'failed':
        return 'FAIL';
      case 'pending':
      case 'skipped':
      case 'todo':
      case 'disabled':
        return 'SKIP';
      default:
        return 'ERROR';
    }
  }

  /**
   * Extract error message from assertion
   * @param {Object} assertion - Jest assertion result
   * @returns {string} Error message
   */
  extractErrorMessage(assertion) {
    if (!assertion.failureMessages || assertion.failureMessages.length === 0) {
      return '';
    }

    // Get first failure message and clean it up
    let message = assertion.failureMessages[0] || '';

    // Remove ANSI color codes
    message = message.replace(/\u001b\[\d+m/g, '');

    // Truncate long messages
    const maxLength = 500;
    if (message.length > maxLength) {
      message = message.substring(0, maxLength) + '...';
    }

    return message.trim();
  }

  /**
   * Extract error type from assertion
   * @param {Object} assertion - Jest assertion result
   * @returns {string} Error type
   */
  extractErrorType(assertion) {
    if (!assertion.failureMessages || assertion.failureMessages.length === 0) {
      return '';
    }

    const message = assertion.failureMessages[0] || '';

    // Try to extract error type from message
    const errorTypeMatch = message.match(/Error: (\w+Error)/);
    if (errorTypeMatch) {
      return errorTypeMatch[1];
    }

    // Check for assertion errors
    if (message.includes('expect(')) {
      return 'AssertionError';
    }

    return 'TestError';
  }

  /**
   * Get execution info for a specific test
   * @param {string} className - Class name
   * @param {string} testName - Test name
   * @returns {Object|null} Test execution info
   */
  getExecutionInfo(className, testName) {
    const testKey = `${className}::${testName}`;
    return this.testResults.get(testKey) || null;
  }

  /**
   * Get all execution info
   * @returns {Map<string, Object>} All test execution info
   */
  getAllExecutionInfo() {
    return this.testResults;
  }

  /**
   * Get execution summary statistics
   * @returns {Object} Summary statistics
   */
  getExecutionSummary() {
    let passed = 0;
    let failed = 0;
    let skipped = 0;
    let error = 0;
    let totalDuration = 0;

    for (const [key, info] of this.testResults.entries()) {
      totalDuration += info.duration || 0;

      switch (info.status) {
        case 'PASS':
          passed++;
          break;
        case 'FAIL':
          failed++;
          break;
        case 'SKIP':
          skipped++;
          break;
        case 'ERROR':
          error++;
          break;
      }
    }

    return {
      totalTests: this.testResults.size,
      passed,
      failed,
      skipped,
      error,
      totalDuration: totalDuration.toFixed(2),
      passRate: this.testResults.size > 0
        ? ((passed / this.testResults.size) * 100).toFixed(2)
        : '0.00'
    };
  }
}
