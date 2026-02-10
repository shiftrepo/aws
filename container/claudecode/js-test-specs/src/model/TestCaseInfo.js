/**
 * テストケース情報を格納するデータモデル
 */
export class TestCaseInfo {
  constructor() {
    // ファイル情報
    this.filePath = '';
    this.className = '';
    this.methodName = '';

    // アノテーションフィールド (日本語)
    this.softwareService = 'N/A';
    this.testItemName = 'N/A';
    this.testContent = 'N/A';
    this.confirmationItem = 'N/A';
    this.testModule = 'N/A';
    this.baselineVersion = 'N/A';
    this.creator = 'N/A';
    this.createdDate = 'N/A';
    this.modifier = 'N/A';
    this.modifiedDate = 'N/A';

    // カバレッジ情報
    this.coveragePercent = 0.0;
    this.branchesCovered = 0;
    this.branchesTotal = 0;
    this.coverageStatus = 'カバレッジなし';
    this.coverage = null; // CoverageInfo object with full coverage data

    // テスト実行情報
    this.testsTotal = 0;
    this.testsPassed = 0;
    this.testExecutionStatus = 'N/A';
    this.testSuccessRate = 0.0;
    this.executionDuration = 0;
    this.errorMessage = '';
    this.errorType = '';
  }

  /**
   * カバレッジ情報を設定
   * @param {number} covered - カバーされたブランチ数
   * @param {number} total - 総ブランチ数
   */
  setCoverageInfo(covered, total) {
    this.branchesCovered = covered;
    this.branchesTotal = total;
    if (total > 0) {
      this.coveragePercent = (covered / total) * 100;
      this.updateCoverageStatus();
    }
  }

  /**
   * カバレッジステータスを更新
   */
  updateCoverageStatus() {
    if (this.coveragePercent >= 90) {
      this.coverageStatus = '優秀';
    } else if (this.coveragePercent >= 70) {
      this.coverageStatus = '良好';
    } else if (this.coveragePercent >= 50) {
      this.coverageStatus = '普通';
    } else if (this.coveragePercent > 0) {
      this.coverageStatus = '要改善';
    } else {
      this.coverageStatus = 'カバレッジなし';
    }
  }

  /**
   * テスト実行情報を設定
   * @param {number} total - 総テスト数
   * @param {number} passed - 成功したテスト数
   */
  setTestExecutionInfo(total, passed) {
    this.testsTotal = total;
    this.testsPassed = passed;
    if (total > 0) {
      this.testSuccessRate = (passed / total) * 100;
      this.testExecutionStatus = passed === total ? '成功' : '一部失敗';
    }
  }

  /**
   * Set detailed execution information from Jest results
   * @param {Object} executionInfo - Execution info from TestExecutionParser
   */
  setDetailedExecutionInfo(executionInfo) {
    if (!executionInfo) {
      this.testExecutionStatus = 'N/A';
      return;
    }

    this.testExecutionStatus = executionInfo.status || 'N/A';
    this.executionDuration = executionInfo.duration || 0;
    this.errorMessage = executionInfo.errorMessage || '';
    this.errorType = executionInfo.errorType || '';

    // Set success rate based on status
    if (executionInfo.status === 'PASS') {
      this.testsTotal = 1;
      this.testsPassed = 1;
      this.testSuccessRate = 100;
    } else if (executionInfo.status === 'FAIL') {
      this.testsTotal = 1;
      this.testsPassed = 0;
      this.testSuccessRate = 0;
    } else if (executionInfo.status === 'SKIP') {
      this.testsTotal = 1;
      this.testsPassed = 0;
      this.testSuccessRate = 0;
    }
  }

  /**
   * Get execution status display with icon
   * @returns {string}
   */
  getExecutionStatusDisplay() {
    switch (this.testExecutionStatus) {
      case 'PASS':
        return '✓ PASS';
      case 'FAIL':
        return '✗ FAIL';
      case 'SKIP':
        return '○ SKIP';
      case 'ERROR':
        return '⚠ ERROR';
      default:
        return 'N/A';
    }
  }

  /**
   * カバレッジ率の表示用フォーマット
   * @returns {string}
   */
  getCoverageDisplay() {
    return `${this.coveragePercent.toFixed(2)}% (${this.branchesCovered}/${this.branchesTotal})`;
  }

  /**
   * テスト成功率の表示用フォーマット
   * @returns {string}
   */
  getTestSuccessDisplay() {
    return `${this.testSuccessRate.toFixed(2)}% (${this.testsPassed}/${this.testsTotal})`;
  }

  /**
   * オブジェクトを文字列として表示
   * @returns {string}
   */
  toString() {
    return `TestCaseInfo{` +
      `filePath='${this.filePath}', ` +
      `className='${this.className}', ` +
      `methodName='${this.methodName}', ` +
      `testItemName='${this.testItemName}', ` +
      `coveragePercent=${this.coveragePercent.toFixed(2)}%, ` +
      `testSuccessRate=${this.testSuccessRate.toFixed(2)}%}`;
  }
}
