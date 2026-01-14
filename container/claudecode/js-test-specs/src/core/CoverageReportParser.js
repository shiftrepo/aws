import fs from 'fs/promises';
import { JSDOM } from 'jsdom';
import { CoverageInfo } from '../model/CoverageInfo.js';

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
        const coverageInfo = new CoverageInfo();

        // ファイルパスからクラス名を抽出
        const fileName = filePath.split('/').pop().split('\\').pop();
        coverageInfo.className = fileName.replace(/\.(js|jsx|ts|tsx)$/, '');

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

        coverageMap.set(coverageInfo.className, coverageInfo);
      }

      this.coverageData = coverageMap;
      return coverageMap;
    } catch (error) {
      console.error('JSONカバレッジ解析エラー:', error.message);
      return new Map();
    }
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
      console.error('HTMLカバレッジ解析エラー:', error.message);
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
        console.log('coverage-final.jsonを解析中...');
        return await this.parseCoverageJson(jsonPath);
      } catch {
        // JSONファイルがない場合はHTMLを試行
      }

      // HTMLレポートを試行
      const htmlPath = `${coverageDir}/lcov-report/index.html`;
      try {
        await fs.access(htmlPath);
        console.log('HTMLカバレッジレポートを解析中...');
        return await this.parseCoverageHtml(htmlPath);
      } catch {
        console.warn('カバレッジファイルが見つかりません');
      }

      return new Map();
    } catch (error) {
      console.error('カバレッジディレクトリ解析エラー:', error.message);
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
