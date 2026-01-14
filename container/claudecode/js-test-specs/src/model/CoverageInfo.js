/**
 * カバレッジ情報を格納するデータモデル
 */
export class CoverageInfo {
  constructor() {
    this.packageName = '';
    this.className = '';
    this.methodName = '';

    // カバレッジメトリクス
    this.instructionCovered = 0;
    this.instructionTotal = 0;
    this.branchCovered = 0;
    this.branchTotal = 0;
    this.lineCovered = 0;
    this.lineTotal = 0;
    this.methodCovered = 0;
    this.methodTotal = 0;
    this.classCovered = 0;
    this.classTotal = 0;
  }

  /**
   * ブランチカバレッジ率を計算
   * @returns {number}
   */
  getBranchCoveragePercent() {
    return this.branchTotal > 0 ? (this.branchCovered / this.branchTotal) * 100 : 0;
  }

  /**
   * 行カバレッジ率を計算
   * @returns {number}
   */
  getLineCoveragePercent() {
    return this.lineTotal > 0 ? (this.lineCovered / this.lineTotal) * 100 : 0;
  }

  /**
   * 命令カバレッジ率を計算
   * @returns {number}
   */
  getInstructionCoveragePercent() {
    return this.instructionTotal > 0 ? (this.instructionCovered / this.instructionTotal) * 100 : 0;
  }

  /**
   * メソッドカバレッジ率を計算
   * @returns {number}
   */
  getMethodCoveragePercent() {
    return this.methodTotal > 0 ? (this.methodCovered / this.methodTotal) * 100 : 0;
  }

  /**
   * クラスカバレッジ率を計算
   * @returns {number}
   */
  getClassCoveragePercent() {
    return this.classTotal > 0 ? (this.classCovered / this.classTotal) * 100 : 0;
  }

  /**
   * カバレッジステータスを取得
   * @returns {string}
   */
  getCoverageStatus() {
    const branchPercent = this.getBranchCoveragePercent();
    if (branchPercent >= 90) return '優秀';
    if (branchPercent >= 70) return '良好';
    if (branchPercent >= 50) return '普通';
    if (branchPercent > 0) return '要改善';
    return 'カバレッジなし';
  }

  /**
   * オブジェクトを文字列として表示
   * @returns {string}
   */
  toString() {
    return `CoverageInfo{` +
      `packageName='${this.packageName}', ` +
      `className='${this.className}', ` +
      `methodName='${this.methodName}', ` +
      `branchCoverage=${this.getBranchCoveragePercent().toFixed(2)}%, ` +
      `lineCoverage=${this.getLineCoveragePercent().toFixed(2)}%}`;
  }
}
