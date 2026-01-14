/**
 * テスト実行情報を格納するデータモデル
 */
export class TestExecutionInfo {
  constructor() {
    this.testSuiteName = '';
    this.testsTotal = 0;
    this.testsPassed = 0;
    this.testsFailed = 0;
    this.testsSkipped = 0;
    this.executionTime = 0;
  }

  /**
   * テスト成功率を計算
   * @returns {number}
   */
  getSuccessRate() {
    return this.testsTotal > 0 ? (this.testsPassed / this.testsTotal) * 100 : 0;
  }

  /**
   * テスト実行ステータスを取得
   * @returns {string}
   */
  getExecutionStatus() {
    if (this.testsTotal === 0) return 'N/A';
    if (this.testsFailed === 0 && this.testsSkipped === 0) return '成功';
    if (this.testsFailed > 0) return '失敗';
    return '一部スキップ';
  }

  /**
   * オブジェクトを文字列として表示
   * @returns {string}
   */
  toString() {
    return `TestExecutionInfo{` +
      `testSuiteName='${this.testSuiteName}', ` +
      `total=${this.testsTotal}, ` +
      `passed=${this.testsPassed}, ` +
      `failed=${this.testsFailed}, ` +
      `skipped=${this.testsSkipped}, ` +
      `successRate=${this.getSuccessRate().toFixed(2)}%}`;
  }
}
