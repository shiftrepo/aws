/**
 * ModuleResult.js
 *
 * Data model for module processing results.
 * Stores test cases, coverage data, and execution metrics for each module.
 *
 * @module model/ModuleResult
 */

/**
 * Module processing result model
 * Contains all processing results for a single module
 */
export class ModuleResult {
  constructor(moduleInfo) {
    this.moduleInfo = moduleInfo;
    this.testCases = [];
    this.coverageSummary = {
      branchCoverage: 0,
      lineCoverage: 0,
      methodCoverage: 0,
      totalBranches: 0,
      coveredBranches: 0,
      totalLines: 0,
      coveredLines: 0,
      totalMethods: 0,
      coveredMethods: 0
    };
    this.executionSummary = {
      totalTests: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      passRate: 0
    };
    this.status = 'pending'; // pending, processing, success, failed
    this.processingTime = 0;
    this.error = null;
    this.warnings = [];
  }

  /**
   * Set test cases for this module
   * @param {Array} testCases - Array of TestCaseInfo objects
   */
  setTestCases(testCases) {
    this.testCases = testCases || [];
  }

  /**
   * Set coverage summary
   * @param {Object} summary - Coverage summary object
   */
  setCoverageSummary(summary) {
    this.coverageSummary = { ...this.coverageSummary, ...summary };
  }

  /**
   * Set execution summary
   * @param {Object} summary - Execution summary object
   */
  setExecutionSummary(summary) {
    this.executionSummary = { ...this.executionSummary, ...summary };
  }

  /**
   * Mark processing as started
   */
  startProcessing() {
    this.status = 'processing';
    this.startTime = Date.now();
  }

  /**
   * Mark processing as completed successfully
   */
  completeProcessing() {
    this.status = 'success';
    this.endTime = Date.now();
    this.processingTime = (this.endTime - this.startTime) / 1000;
  }

  /**
   * Mark processing as failed
   * @param {Error} error - Error that occurred
   */
  failProcessing(error) {
    this.status = 'failed';
    this.endTime = Date.now();
    this.processingTime = (this.endTime - this.startTime) / 1000;
    this.error = {
      message: error.message,
      stack: error.stack
    };
  }

  /**
   * Add a warning
   * @param {string} warning - Warning message
   */
  addWarning(warning) {
    this.warnings.push(warning);
  }

  /**
   * Check if processing was successful
   * @returns {boolean}
   */
  isSuccessful() {
    return this.status === 'success';
  }

  /**
   * Get result summary
   * @returns {Object}
   */
  getSummary() {
    return {
      moduleName: this.moduleInfo.moduleName,
      status: this.status,
      testCaseCount: this.testCases.length,
      branchCoverage: this.coverageSummary.branchCoverage.toFixed(2) + '%',
      passRate: this.executionSummary.passRate.toFixed(2) + '%',
      processingTime: this.processingTime.toFixed(2) + 's',
      warnings: this.warnings.length,
      hasError: this.error !== null
    };
  }

  /**
   * Convert to JSON representation
   * @returns {Object}
   */
  toJSON() {
    return {
      moduleInfo: this.moduleInfo.toJSON(),
      testCaseCount: this.testCases.length,
      coverageSummary: this.coverageSummary,
      executionSummary: this.executionSummary,
      status: this.status,
      processingTime: this.processingTime,
      error: this.error,
      warnings: this.warnings
    };
  }

  /**
   * Convert to string representation
   * @returns {string}
   */
  toString() {
    return `ModuleResult{` +
      `module='${this.moduleInfo.moduleName}', ` +
      `status=${this.status}, ` +
      `testCases=${this.testCases.length}, ` +
      `coverage=${this.coverageSummary.branchCoverage.toFixed(2)}%}`;
  }
}
