/**
 * CsvSheetBuilder.js
 *
 * Generates CSV files for test details and coverage information.
 * Provides an alternative output format to Excel for easier data processing.
 *
 * @module core/CsvSheetBuilder
 */

import { createObjectCsvWriter } from 'csv-writer';
import path from 'path';
import { logger } from '../util/Logger.js';

/**
 * CSV generation class
 * Generates Test Details and Coverage CSV files with UTF-8 BOM encoding
 */
export class CsvSheetBuilder {
  constructor() {
    this.encoding = 'utf8';
  }

  /**
   * Generate all CSV files (Test Details and Coverage)
   * @param {Array} testCases - Test case information array
   * @param {Object} coverageSummary - Coverage summary
   * @param {string} baseOutputPath - Base output file path (without extension)
   * @returns {Promise<Object>} Paths to generated CSV files
   */
  async generateAllCsvFiles(testCases, coverageSummary, baseOutputPath) {
    try {
      const baseName = baseOutputPath.replace(/\.xlsx?$/i, '');

      const testDetailsPath = `${baseName}_test_details.csv`;
      const coveragePath = `${baseName}_coverage.csv`;

      await this.generateTestDetailsCsv(testDetailsPath, testCases);
      await this.generateCoverageCsv(coveragePath, testCases, coverageSummary);

      logger.info('CSV生成完了', { testDetailsPath, coveragePath });

      return {
        testDetails: testDetailsPath,
        coverage: coveragePath
      };
    } catch (error) {
      logger.error('CSV生成エラー', error);
      throw error;
    }
  }

  /**
   * Generate Test Details CSV
   * @param {string} outputPath - Output file path
   * @param {Array} testCases - Test case information array
   * @returns {Promise<void>}
   */
  async generateTestDetailsCsv(outputPath, testCases) {
    try {
      logger.debug('Test Details CSV生成開始', { outputPath, testCaseCount: testCases.length });

      const csvWriter = createObjectCsvWriter({
        path: outputPath,
        header: [
          { id: 'number', title: '番号' },
          { id: 'softwareService', title: 'ソフトウェア・サービス' },
          { id: 'testItemName', title: '項目名' },
          { id: 'testContent', title: '試験内容' },
          { id: 'confirmationItem', title: '確認項目' },
          { id: 'testModule', title: 'テスト対象モジュール名' },
          { id: 'baselineVersion', title: 'テスト実施ベースラインバージョン' },
          { id: 'creator', title: 'テストケース作成者' },
          { id: 'createdDate', title: 'テストケース作成日' },
          { id: 'modifier', title: 'テストケース修正者' },
          { id: 'modifiedDate', title: 'テストケース修正日' },
          { id: 'coverageStatus', title: 'カバレッジ状況' }
        ],
        encoding: 'utf8',
        append: false
      });

      const records = testCases.map((testCase, index) => ({
        number: index + 1,
        softwareService: testCase.softwareService || '',
        testItemName: testCase.testItemName || testCase.methodName || '',
        testContent: testCase.testContent || '',
        confirmationItem: testCase.confirmationItem || '',
        testModule: testCase.testModule || testCase.className || '',
        baselineVersion: testCase.baselineVersion || '',
        creator: testCase.creator || '',
        createdDate: testCase.createdDate || '',
        modifier: testCase.modifier || '',
        modifiedDate: testCase.modifiedDate || '',
        coverageStatus: testCase.coverageStatus || 'N/A'
      }));

      await csvWriter.writeRecords(records);

      // Add UTF-8 BOM for Excel compatibility
      await this.addUtf8Bom(outputPath);

      logger.info('Test Details CSV生成完了', { outputPath, recordCount: records.length });
    } catch (error) {
      logger.error('Test Details CSV生成エラー', { outputPath, error: error.message });
      throw error;
    }
  }

  /**
   * Generate Coverage CSV
   * @param {string} outputPath - Output file path
   * @param {Array} testCases - Test case information array
   * @param {Object} coverageSummary - Coverage summary
   * @returns {Promise<void>}
   */
  async generateCoverageCsv(outputPath, testCases, coverageSummary) {
    try {
      logger.debug('Coverage CSV生成開始', { outputPath });

      const csvWriter = createObjectCsvWriter({
        path: outputPath,
        header: [
          { id: 'className', title: 'クラス名' },
          { id: 'branchCovered', title: 'ブランチカバー数' },
          { id: 'branchTotal', title: 'ブランチ総数' },
          { id: 'branchPercent', title: 'ブランチカバレッジ(%)' },
          { id: 'lineCovered', title: '行カバー数' },
          { id: 'lineTotal', title: '行総数' },
          { id: 'linePercent', title: '行カバレッジ(%)' },
          { id: 'methodCovered', title: 'メソッドカバー数' },
          { id: 'methodTotal', title: 'メソッド総数' },
          { id: 'methodPercent', title: 'メソッドカバレッジ(%)' },
          { id: 'status', title: 'ステータス' }
        ],
        encoding: 'utf8',
        append: false
      });

      // Aggregate coverage by class
      const classMap = new Map();

      for (const testCase of testCases) {
        const className = testCase.className || 'Unknown';

        if (!classMap.has(className)) {
          classMap.set(className, {
            className,
            branchCovered: 0,
            branchTotal: 0,
            lineCovered: 0,
            lineTotal: 0,
            methodCovered: 0,
            methodTotal: 0
          });
        }

        const classData = classMap.get(className);

        // Accumulate coverage data from CoverageInfo object
        if (testCase.coverage) {
          classData.branchCovered += testCase.coverage.branchCovered || 0;
          classData.branchTotal += testCase.coverage.branchTotal || 0;
          classData.lineCovered += testCase.coverage.lineCovered || 0;
          classData.lineTotal += testCase.coverage.lineTotal || 0;
          classData.methodCovered += testCase.coverage.methodCovered || 0;
          classData.methodTotal += testCase.coverage.methodTotal || 0;
        }
      }

      const records = Array.from(classMap.values()).map(classData => {
        const branchPercent = classData.branchTotal > 0
          ? ((classData.branchCovered / classData.branchTotal) * 100).toFixed(2)
          : '0.00';
        const linePercent = classData.lineTotal > 0
          ? ((classData.lineCovered / classData.lineTotal) * 100).toFixed(2)
          : '0.00';
        const methodPercent = classData.methodTotal > 0
          ? ((classData.methodCovered / classData.methodTotal) * 100).toFixed(2)
          : '0.00';

        const avgPercent = (parseFloat(branchPercent) + parseFloat(linePercent) + parseFloat(methodPercent)) / 3;
        const status = this.getCoverageStatus(avgPercent);

        return {
          className: classData.className,
          branchCovered: classData.branchCovered,
          branchTotal: classData.branchTotal,
          branchPercent,
          lineCovered: classData.lineCovered,
          lineTotal: classData.lineTotal,
          linePercent,
          methodCovered: classData.methodCovered,
          methodTotal: classData.methodTotal,
          methodPercent,
          status
        };
      });

      await csvWriter.writeRecords(records);

      // Add UTF-8 BOM for Excel compatibility
      await this.addUtf8Bom(outputPath);

      logger.info('Coverage CSV生成完了', { outputPath, recordCount: records.length });
    } catch (error) {
      logger.error('Coverage CSV生成エラー', { outputPath, error: error.message });
      throw error;
    }
  }

  /**
   * Add UTF-8 BOM to file for Excel compatibility
   * @param {string} filePath - File path
   * @returns {Promise<void>}
   */
  async addUtf8Bom(filePath) {
    try {
      const fs = await import('fs/promises');
      const content = await fs.readFile(filePath, 'utf8');

      // Add BOM if not present
      if (!content.startsWith('\uFEFF')) {
        await fs.writeFile(filePath, '\uFEFF' + content, 'utf8');
      }
    } catch (error) {
      logger.warn('UTF-8 BOM追加に失敗', { filePath, error: error.message });
    }
  }

  /**
   * Determine coverage status based on percentage
   * @param {number} percent - Coverage percentage
   * @returns {string} Status string
   */
  getCoverageStatus(percent) {
    if (percent >= 90) return '優秀';
    if (percent >= 70) return '良好';
    if (percent >= 50) return '普通';
    return '要改善';
  }

  /**
   * Generate summary CSV (overall statistics)
   * @param {string} outputPath - Output file path
   * @param {Array} testCases - Test case information array
   * @param {Object} coverageSummary - Coverage summary
   * @returns {Promise<void>}
   */
  async generateSummaryCsv(outputPath, testCases, coverageSummary) {
    try {
      logger.debug('Summary CSV生成開始', { outputPath });

      const csvWriter = createObjectCsvWriter({
        path: outputPath,
        header: [
          { id: 'metric', title: '項目' },
          { id: 'value', title: '値' }
        ],
        encoding: 'utf8',
        append: false
      });

      const records = [
        { metric: '総テストケース数', value: testCases.length },
        { metric: '総テストファイル数', value: new Set(testCases.map(tc => tc.filePath)).size },
        { metric: 'ブランチカバレッジ', value: `${coverageSummary.branchCoverage.toFixed(2)}%` },
        { metric: '行カバレッジ', value: `${coverageSummary.lineCoverage.toFixed(2)}%` },
        { metric: 'メソッドカバレッジ', value: `${coverageSummary.methodCoverage.toFixed(2)}%` },
        { metric: '生成日時', value: new Date().toISOString() }
      ];

      await csvWriter.writeRecords(records);

      // Add UTF-8 BOM for Excel compatibility
      await this.addUtf8Bom(outputPath);

      logger.info('Summary CSV生成完了', { outputPath });
    } catch (error) {
      logger.error('Summary CSV生成エラー', { outputPath, error: error.message });
      throw error;
    }
  }
}
