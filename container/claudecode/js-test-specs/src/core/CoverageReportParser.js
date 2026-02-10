import fs from 'fs/promises';
import { JSDOM } from 'jsdom';
import { CoverageInfo } from '../model/CoverageInfo.js';
import { logger } from '../util/Logger.js';

/**
 * Jestカバレッジレポートを解析するクラス
 */
export class CoverageReportParser {
  constructor() {
    this.coverageData = new Map();
  }

  /**
   * coverage-final.jsonファイルを解析
   * @param {string} jsonPath - coverage-final.jsonのパス
   * @returns {Promise<Map<string, CoverageInfo>>} カバレッジ情報のマップ
   */
  async parseCoverageJson(jsonPath) {
    try {
      const content = await fs.readFile(jsonPath, 'utf8');
      const coverageData = JSON.parse(content);

      const coverageMap = new Map();

      for (const [filePath, fileData] of Object.entries(coverageData)) {
        // ファイルパスからクラス名を抽出
        const fileName = filePath.split('/').pop().split('\\').pop();
        const className = fileName.replace(/\.(js|jsx|ts|tsx)$/, '');

        // Always create file-level coverage info
        const coverageInfo = new CoverageInfo();
        coverageInfo.className = className;
        coverageInfo.methodName = '';

        // ブランチカバレッジ
        if (fileData.b) {
          const branches = Object.values(fileData.b);
          const totalBranches = branches.flat().length;
          const coveredBranches = branches.flat().filter(count => count > 0).length;
          coverageInfo.branchTotal = totalBranches;
          coverageInfo.branchCovered = coveredBranches;
        }

        // 行カバレッジ
        if (fileData.s) {
          const statements = Object.values(fileData.s);
          coverageInfo.lineTotal = statements.length;
          coverageInfo.lineCovered = statements.filter(count => count > 0).length;
        }

        // 関数カバレッジ
        if (fileData.f) {
          const functions = Object.values(fileData.f);
          coverageInfo.methodTotal = functions.length;
          coverageInfo.methodCovered = functions.filter(count => count > 0).length;
        }

        // Add file-level coverage
        coverageMap.set(className, coverageInfo);

        // Parse method-level coverage if fnMap exists
        if (fileData.fnMap && fileData.f) {
          const methodCoverages = this.parseMethodCoverage(fileData, className);

          for (const methodCoverage of methodCoverages) {
            const key = `${className}.${methodCoverage.methodName}`;
            coverageMap.set(key, methodCoverage);
          }
        }
      }

      this.coverageData = coverageMap;
      return coverageMap;
    } catch (error) {
      logger.error('JSONカバレッジ解析エラー', { error: error.message });
      return new Map();
    }
  }

  /**
   * Parse method-level coverage from coverage data
   * @param {Object} fileData - File coverage data
   * @param {string} className - Class name
   * @returns {Array<CoverageInfo>} Array of method-level coverage info
   */
  parseMethodCoverage(fileData, className) {
    const methodCoverages = [];

    try {
      const fnMap = fileData.fnMap || {};
      const fnExecutionCounts = fileData.f || {};
      const statementMap = fileData.statementMap || {};
      const statements = fileData.s || {};
      const branchMap = fileData.branchMap || {};
      const branches = fileData.b || {};

      // Process each function in fnMap
      for (const [fnId, fnInfo] of Object.entries(fnMap)) {
        const coverageInfo = new CoverageInfo();
        coverageInfo.className = className;
        coverageInfo.methodName = fnInfo.name || `anonymous_${fnId}`;

        // Method execution coverage
        const executionCount = fnExecutionCounts[fnId] || 0;
        coverageInfo.methodCovered = executionCount > 0 ? 1 : 0;
        coverageInfo.methodTotal = 1;

        // Calculate line coverage for this method
        const fnStartLine = fnInfo.loc?.start?.line || 0;
        const fnEndLine = fnInfo.loc?.end?.line || 0;

        let methodLineCovered = 0;
        let methodLineTotal = 0;

        for (const [stmtId, stmtInfo] of Object.entries(statementMap)) {
          const stmtStartLine = stmtInfo.start?.line || 0;
          const stmtEndLine = stmtInfo.end?.line || 0;

          // Check if statement is within function bounds
          if (stmtStartLine >= fnStartLine && stmtEndLine <= fnEndLine) {
            methodLineTotal++;
            if (statements[stmtId] > 0) {
              methodLineCovered++;
            }
          }
        }

        coverageInfo.lineCovered = methodLineCovered;
        coverageInfo.lineTotal = methodLineTotal;

        // Calculate branch coverage for this method
        let methodBranchCovered = 0;
        let methodBranchTotal = 0;

        for (const [branchId, branchInfo] of Object.entries(branchMap)) {
          const branchLine = branchInfo.loc?.start?.line || 0;

          // Check if branch is within function bounds
          if (branchLine >= fnStartLine && branchLine <= fnEndLine) {
            const branchCounts = branches[branchId] || [];
            methodBranchTotal += branchCounts.length;
            methodBranchCovered += branchCounts.filter(count => count > 0).length;
          }
        }

        coverageInfo.branchCovered = methodBranchCovered;
        coverageInfo.branchTotal = methodBranchTotal;

        methodCoverages.push(coverageInfo);
      }

      logger.debug('メソッドレベルカバレッジ解析完了', {
        className,
        methodCount: methodCoverages.length
      });
    } catch (error) {
      logger.warn('メソッドレベルカバレッジ解析エラー', {
        className,
        error: error.message
      });
    }

    return methodCoverages;
  }

  /**
   * HTMLカバレッジレポートを解析（フォールバック）
   * @param {string} htmlPath - index.htmlのパス
   * @returns {Promise<Map<string, CoverageInfo>>} カバレッジ情報のマップ
   */
  async parseCoverageHtml(htmlPath) {
    try {
      const content = await fs.readFile(htmlPath, 'utf8');
      const dom = new JSDOM(content);
      const document = dom.window.document;

      const coverageMap = new Map();

      // テーブル行を解析
      const rows = document.querySelectorAll('table tbody tr');

      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length < 4) continue;

        const coverageInfo = new CoverageInfo();

        // ファイル名
        const fileNameCell = cells[0];
        const fileName = fileNameCell.textContent.trim();
        coverageInfo.className = fileName.replace(/\.(js|jsx|ts|tsx)$/, '');

        // ブランチカバレッジ（通常3番目のセル）
        const branchCell = cells[2];
        const branchText = branchCell.textContent.trim();
        const branchMatch = branchText.match(/(\d+)\/(\d+)/);
        if (branchMatch) {
          coverageInfo.branchCovered = parseInt(branchMatch[1], 10);
          coverageInfo.branchTotal = parseInt(branchMatch[2], 10);
        }

        // 行カバレッジ（通常4番目のセル）
        const lineCell = cells[3];
        const lineText = lineCell.textContent.trim();
        const lineMatch = lineText.match(/(\d+)\/(\d+)/);
        if (lineMatch) {
          coverageInfo.lineCovered = parseInt(lineMatch[1], 10);
          coverageInfo.lineTotal = parseInt(lineMatch[2], 10);
        }

        coverageMap.set(coverageInfo.className, coverageInfo);
      }

      this.coverageData = coverageMap;
      return coverageMap;
    } catch (error) {
      logger.error('HTMLカバレッジ解析エラー', { error: error.message });
      return new Map();
    }
  }

  /**
   * カバレッジディレクトリから自動的に適切なファイルを検出して解析
   * @param {string} coverageDir - カバレッジディレクトリのパス
   * @returns {Promise<Map<string, CoverageInfo>>} カバレッジ情報のマップ
   */
  async parseCoverageDirectory(coverageDir) {
    try {
      // coverage-final.jsonを優先
      const jsonPath = `${coverageDir}/coverage-final.json`;
      try {
        await fs.access(jsonPath);
        logger.info('coverage-final.jsonを解析中', { path: jsonPath });
        return await this.parseCoverageJson(jsonPath);
      } catch {
        // JSONファイルがない場合はHTMLを試行
      }

      // HTMLレポートを試行
      const htmlPath = `${coverageDir}/lcov-report/index.html`;
      try {
        await fs.access(htmlPath);
        logger.info('HTMLカバレッジレポートを解析中', { path: htmlPath });
        return await this.parseCoverageHtml(htmlPath);
      } catch {
        logger.warn('カバレッジファイルが見つかりません', { coverageDir });
      }

      return new Map();
    } catch (error) {
      logger.error('カバレッジディレクトリ解析エラー', { error: error.message });
      return new Map();
    }
  }

  /**
   * クラス名に対応するカバレッジ情報を取得
   * @param {string} className - クラス名
   * @returns {CoverageInfo|null} カバレッジ情報
   */
  getCoverageForClass(className) {
    // 完全一致を試行
    if (this.coverageData.has(className)) {
      return this.coverageData.get(className);
    }

    // 部分一致を試行
    for (const [key, value] of this.coverageData.entries()) {
      if (key.includes(className) || className.includes(key)) {
        return value;
      }
    }

    return null;
  }

  /**
   * Get method-level coverage for a class
   * @param {string} className - Class name
   * @returns {Array<CoverageInfo>} Array of method-level coverage info
   */
  getMethodCoverageForClass(className) {
    const methodCoverages = [];

    for (const [key, value] of this.coverageData.entries()) {
      // Check if key matches pattern: className.methodName
      if (key.startsWith(className + '.')) {
        methodCoverages.push(value);
      }
    }

    return methodCoverages;
  }

  /**
   * Get all method-level coverage data
   * @returns {Array<CoverageInfo>} Array of all method-level coverage info
   */
  getAllMethodCoverage() {
    const methodCoverages = [];

    for (const [key, value] of this.coverageData.entries()) {
      // Check if this is method-level coverage (contains a dot)
      if (key.includes('.') && value.methodName) {
        methodCoverages.push(value);
      }
    }

    return methodCoverages;
  }

  /**
   * 全体のカバレッジサマリーを取得
   * @returns {Object} カバレッジサマリー
   */
  getCoverageSummary() {
    let totalBranches = 0;
    let coveredBranches = 0;
    let totalLines = 0;
    let coveredLines = 0;
    let totalMethods = 0;
    let coveredMethods = 0;

    for (const coverage of this.coverageData.values()) {
      totalBranches += coverage.branchTotal;
      coveredBranches += coverage.branchCovered;
      totalLines += coverage.lineTotal;
      coveredLines += coverage.lineCovered;
      totalMethods += coverage.methodTotal;
      coveredMethods += coverage.methodCovered;
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
      coveredMethods,
    };
  }
}
