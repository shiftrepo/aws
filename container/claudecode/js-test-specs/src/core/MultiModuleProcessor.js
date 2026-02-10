/**
 * MultiModuleProcessor.js
 *
 * Processes multiple modules in parallel using worker threads.
 * Aggregates results from all modules and generates combined reports.
 *
 * @module core/MultiModuleProcessor
 */

import { Worker } from 'worker_threads';
import path from 'path';
import { ModuleResult } from '../model/ModuleResult.js';
import { ExcelSheetBuilder } from './ExcelSheetBuilder.js';
import { CsvSheetBuilder } from './CsvSheetBuilder.js';
import { logger } from '../util/Logger.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Multi-module processor
 * Handles parallel processing of modules in monorepo
 */
export class MultiModuleProcessor {
  constructor(options = {}) {
    this.options = {
      maxConcurrency: options.maxConcurrency || 4,
      timeout: options.timeout || 300000, // 5 minutes default
      ...options
    };
    this.moduleResults = [];
  }

  /**
   * Process multiple modules in parallel
   * @param {Array<ModuleInfo>} modules - Array of module information
   * @param {Object} options - Processing options
   * @returns {Promise<Array<ModuleResult>>}
   */
  async processModules(modules, options = {}) {
    logger.info('Multi-module processing started', {
      moduleCount: modules.length,
      maxConcurrency: this.options.maxConcurrency
    });

    const results = [];
    const startTime = Date.now();

    // Process modules in batches to respect concurrency limit
    for (let i = 0; i < modules.length; i += this.options.maxConcurrency) {
      const batch = modules.slice(i, i + this.options.maxConcurrency);
      logger.info('Processing module batch', {
        batchNumber: Math.floor(i / this.options.maxConcurrency) + 1,
        batchSize: batch.length
      });

      const batchResults = await Promise.all(
        batch.map(module => this.processModule(module, options))
      );

      results.push(...batchResults);
    }

    const endTime = Date.now();
    const totalTime = ((endTime - startTime) / 1000).toFixed(2);

    logger.info('Multi-module processing completed', {
      totalModules: modules.length,
      successful: results.filter(r => r.isSuccessful()).length,
      failed: results.filter(r => !r.isSuccessful()).length,
      totalTime: `${totalTime}s`
    });

    this.moduleResults = results;
    return results;
  }

  /**
   * Process a single module
   * @param {ModuleInfo} moduleInfo - Module information
   * @param {Object} options - Processing options
   * @returns {Promise<ModuleResult>}
   */
  async processModule(moduleInfo, options = {}) {
    const moduleResult = new ModuleResult(moduleInfo);
    moduleResult.startProcessing();

    logger.info('Processing module', {
      module: moduleInfo.moduleName,
      path: moduleInfo.modulePath
    });

    try {
      // Use worker thread for isolation
      const workerResult = await this.runWorker(moduleInfo, options);

      // Set results from worker
      moduleResult.setTestCases(workerResult.testCases || []);
      moduleResult.setCoverageSummary(workerResult.coverageSummary || {});
      moduleResult.setExecutionSummary(workerResult.executionSummary || {});

      if (workerResult.warnings && workerResult.warnings.length > 0) {
        workerResult.warnings.forEach(w => moduleResult.addWarning(w));
      }

      moduleResult.completeProcessing();

      logger.info('Module processing completed', {
        module: moduleInfo.moduleName,
        testCases: moduleResult.testCases.length,
        time: `${moduleResult.processingTime}s`
      });
    } catch (error) {
      moduleResult.failProcessing(error);
      logger.error('Module processing failed', {
        module: moduleInfo.moduleName,
        error: error.message
      });
    }

    return moduleResult;
  }

  /**
   * Run worker thread for module processing
   * @param {ModuleInfo} moduleInfo - Module information
   * @param {Object} options - Processing options
   * @returns {Promise<Object>}
   */
  async runWorker(moduleInfo, options) {
    return new Promise((resolve, reject) => {
      const workerPath = path.join(__dirname, '../workers/moduleProcessor.js');

      logger.debug('Starting worker thread', {
        module: moduleInfo.moduleName,
        workerPath
      });

      const worker = new Worker(workerPath, {
        workerData: {
          moduleInfo: moduleInfo.toJSON(),
          options
        }
      });

      const timeout = setTimeout(() => {
        worker.terminate();
        reject(new Error(`Worker timeout after ${this.options.timeout}ms`));
      }, this.options.timeout);

      worker.on('message', (result) => {
        clearTimeout(timeout);
        resolve(result);
      });

      worker.on('error', (error) => {
        clearTimeout(timeout);
        reject(error);
      });

      worker.on('exit', (code) => {
        clearTimeout(timeout);
        if (code !== 0) {
          reject(new Error(`Worker stopped with exit code ${code}`));
        }
      });
    });
  }

  /**
   * Generate combined report from all modules
   * @param {string} outputDir - Output directory for reports
   * @param {Object} options - Report options
   * @returns {Promise<Object>}
   */
  async generateCombinedReport(outputDir, options = {}) {
    logger.info('Generating combined report', { outputDir });

    try {
      // Aggregate all test cases
      const allTestCases = [];
      for (const result of this.moduleResults) {
        if (result.isSuccessful()) {
          // Add module name to each test case for identification
          result.testCases.forEach(tc => {
            tc.moduleName = result.moduleInfo.moduleName;
            allTestCases.push(tc);
          });
        }
      }

      // Aggregate coverage summary
      const combinedCoverageSummary = this.aggregateCoverageSummary();

      // Aggregate execution summary
      const combinedExecutionSummary = this.aggregateExecutionSummary();

      // Generate combined Excel
      const combinedExcelPath = path.join(outputDir, 'combined_test_specification.xlsx');
      const excelBuilder = new ExcelSheetBuilder();
      await excelBuilder.generateExcel(allTestCases, combinedCoverageSummary, combinedExcelPath);

      // Generate combined CSV if requested
      let csvPaths = null;
      if (options.csvOutput) {
        const csvBuilder = new CsvSheetBuilder();
        csvPaths = await csvBuilder.generateAllCsvFiles(
          allTestCases,
          combinedCoverageSummary,
          combinedExcelPath
        );
      }

      logger.info('Combined report generated', {
        excelPath: combinedExcelPath,
        csvPaths,
        totalTestCases: allTestCases.length
      });

      return {
        excelPath: combinedExcelPath,
        csvPaths,
        testCaseCount: allTestCases.length,
        coverageSummary: combinedCoverageSummary,
        executionSummary: combinedExecutionSummary
      };
    } catch (error) {
      logger.error('Combined report generation failed', error);
      throw error;
    }
  }

  /**
   * Generate per-module reports
   * @param {string} outputDir - Output directory for reports
   * @param {Object} options - Report options
   * @returns {Promise<Array>}
   */
  async generateModuleReports(outputDir, options = {}) {
    logger.info('Generating per-module reports', { outputDir });

    const reportPaths = [];

    for (const result of this.moduleResults) {
      if (!result.isSuccessful()) {
        logger.warn('Skipping failed module', { module: result.moduleInfo.moduleName });
        continue;
      }

      try {
        const moduleName = result.moduleInfo.moduleName.replace(/[@/]/g, '_');
        const moduleExcelPath = path.join(outputDir, `${moduleName}_test_specification.xlsx`);

        const excelBuilder = new ExcelSheetBuilder();
        await excelBuilder.generateExcel(
          result.testCases,
          result.coverageSummary,
          moduleExcelPath
        );

        let csvPaths = null;
        if (options.csvOutput) {
          const csvBuilder = new CsvSheetBuilder();
          csvPaths = await csvBuilder.generateAllCsvFiles(
            result.testCases,
            result.coverageSummary,
            moduleExcelPath
          );
        }

        reportPaths.push({
          module: result.moduleInfo.moduleName,
          excelPath: moduleExcelPath,
          csvPaths
        });

        logger.info('Module report generated', {
          module: result.moduleInfo.moduleName,
          excelPath: moduleExcelPath
        });
      } catch (error) {
        logger.error('Module report generation failed', {
          module: result.moduleInfo.moduleName,
          error: error.message
        });
      }
    }

    return reportPaths;
  }

  /**
   * Aggregate coverage summary from all modules
   * @returns {Object}
   */
  aggregateCoverageSummary() {
    let totalBranches = 0;
    let coveredBranches = 0;
    let totalLines = 0;
    let coveredLines = 0;
    let totalMethods = 0;
    let coveredMethods = 0;

    for (const result of this.moduleResults) {
      if (result.isSuccessful()) {
        const summary = result.coverageSummary;
        totalBranches += summary.totalBranches || 0;
        coveredBranches += summary.coveredBranches || 0;
        totalLines += summary.totalLines || 0;
        coveredLines += summary.coveredLines || 0;
        totalMethods += summary.totalMethods || 0;
        coveredMethods += summary.coveredMethods || 0;
      }
    }

    return {
      branchCoverage: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 0,
      lineCoverage: totalLines > 0 ? (coveredLines / totalLines) * 100 : 0,
      methodCoverage: totalMethods > 0 ? (coveredMethods / totalMethods) * 100 : 0,
      totalBranches,
      coveredBranches,
      totalLines,
      coveredLines,
      totalMethods,
      coveredMethods
    };
  }

  /**
   * Aggregate execution summary from all modules
   * @returns {Object}
   */
  aggregateExecutionSummary() {
    let totalTests = 0;
    let passed = 0;
    let failed = 0;
    let skipped = 0;

    for (const result of this.moduleResults) {
      if (result.isSuccessful()) {
        const summary = result.executionSummary;
        totalTests += summary.totalTests || 0;
        passed += summary.passed || 0;
        failed += summary.failed || 0;
        skipped += summary.skipped || 0;
      }
    }

    return {
      totalTests,
      passed,
      failed,
      skipped,
      passRate: totalTests > 0 ? ((passed / totalTests) * 100).toFixed(2) : '0.00'
    };
  }

  /**
   * Get processing summary
   * @returns {Object}
   */
  getProcessingSummary() {
    return {
      totalModules: this.moduleResults.length,
      successfulModules: this.moduleResults.filter(r => r.isSuccessful()).length,
      failedModules: this.moduleResults.filter(r => !r.isSuccessful()).length,
      totalTestCases: this.moduleResults.reduce((sum, r) => sum + r.testCases.length, 0),
      combinedCoverage: this.aggregateCoverageSummary(),
      combinedExecution: this.aggregateExecutionSummary()
    };
  }
}
