import ExcelJS from 'exceljs';

/**
 * Excelワークブックを生成するクラス
 */
export class ExcelSheetBuilder {
  constructor() {
    this.workbook = new ExcelJS.Workbook();
  }

  /**
   * テスト仕様書Excelを生成
   * @param {Array} testCases - テストケース情報の配列
   * @param {Object} coverageSummary - カバレッジサマリー
   * @param {string} outputPath - 出力ファイルパス
   * @returns {Promise<void>}
   */
  async generateExcel(testCases, coverageSummary, outputPath) {
    // シート1: テスト詳細
    await this.createTestDetailsSheet(testCases);

    // シート2: サマリー
    await this.createSummarySheet(testCases, coverageSummary);

    // シート3: カバレッジ
    await this.createCoverageSheet(testCases);

    // シート4: 設定情報
    await this.createConfigSheet();

    // ファイル保存
    await this.workbook.xlsx.writeFile(outputPath);
    console.log(`Excel生成完了: ${outputPath}`);
  }

  /**
   * テスト詳細シートを作成
   * @param {Array} testCases - テストケース情報の配列
   */
  async createTestDetailsSheet(testCases) {
    const sheet = this.workbook.addWorksheet('テスト詳細');

    // ヘッダー行
    const headers = [
      '番号',
      'ソフトウェア・サービス',
      '項目名',
      '試験内容',
      '確認項目',
      'テスト対象モジュール名',
      'テスト実施ベースラインバージョン',
      'テストケース作成者',
      'テストケース作成日',
      'テストケース修正者',
      'テストケース修正日',
      'カバレッジ率',
      'カバレッジステータス',
    ];

    sheet.addRow(headers);

    // ヘッダースタイル
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF4472C4' },
    };
    headerRow.alignment = { horizontal: 'center', vertical: 'middle' };

    // データ行
    testCases.forEach((testCase, index) => {
      const row = sheet.addRow([
        index + 1,
        testCase.softwareService,
        testCase.testItemName,
        testCase.testContent,
        testCase.confirmationItem,
        testCase.testModule,
        testCase.baselineVersion,
        testCase.creator,
        testCase.createdDate,
        testCase.modifier,
        testCase.modifiedDate,
        testCase.getCoverageDisplay(),
        testCase.coverageStatus,
      ]);

      // 偶数行に薄い青色の背景
      if (index % 2 === 0) {
        row.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFE7F3FF' },
        };
      }
    });

    // 列幅自動調整
    sheet.columns.forEach((column) => {
      column.width = 20;
    });
    sheet.getColumn(3).width = 30; // 項目名
    sheet.getColumn(4).width = 40; // 試験内容
    sheet.getColumn(5).width = 40; // 確認項目
  }

  /**
   * サマリーシートを作成
   * @param {Array} testCases - テストケース情報の配列
   * @param {Object} coverageSummary - カバレッジサマリー
   */
  async createSummarySheet(testCases, coverageSummary) {
    const sheet = this.workbook.addWorksheet('サマリー');

    sheet.addRow(['テスト仕様書サマリー']);
    sheet.getRow(1).font = { size: 16, bold: true };
    sheet.addRow([]);

    // 基本統計
    sheet.addRow(['総テストケース数', testCases.length]);
    sheet.addRow(['ファイル数', new Set(testCases.map((t) => t.filePath)).size]);
    sheet.addRow([]);

    // カバレッジサマリー
    sheet.addRow(['カバレッジサマリー']);
    sheet.getRow(6).font = { bold: true, size: 14 };
    sheet.addRow(['ブランチカバレッジ', `${coverageSummary.branchCoverage?.toFixed(2) || 0}%`]);
    sheet.addRow(['行カバレッジ', `${coverageSummary.lineCoverage?.toFixed(2) || 0}%`]);
    sheet.addRow(['メソッドカバレッジ', `${coverageSummary.methodCoverage?.toFixed(2) || 0}%`]);
    sheet.addRow([
      'カバーされたブランチ',
      `${coverageSummary.coveredBranches || 0} / ${coverageSummary.totalBranches || 0}`,
    ]);

    sheet.addRow([]);
    sheet.addRow(['生成日時', new Date().toLocaleString('ja-JP')]);

    // 列幅調整
    sheet.getColumn(1).width = 30;
    sheet.getColumn(2).width = 30;

    // スタイリング
    for (let i = 3; i <= 10; i++) {
      const row = sheet.getRow(i);
      if (i % 2 === 0) {
        row.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFFFF2CC' },
        };
      }
    }
  }

  /**
   * カバレッジシートを作成
   * @param {Array} testCases - テストケース情報の配列
   */
  async createCoverageSheet(testCases) {
    const sheet = this.workbook.addWorksheet('カバレッジ');

    // ヘッダー行
    const headers = [
      'クラス名',
      'メソッド名',
      'ブランチカバレッジ',
      'カバーされたブランチ',
      '総ブランチ数',
      'カバレッジステータス',
    ];

    sheet.addRow(headers);

    // ヘッダースタイル
    const headerRow = sheet.getRow(1);
    headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    headerRow.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF70AD47' },
    };
    headerRow.alignment = { horizontal: 'center', vertical: 'middle' };

    // データ行
    testCases.forEach((testCase, index) => {
      const row = sheet.addRow([
        testCase.className,
        testCase.methodName,
        `${testCase.coveragePercent.toFixed(2)}%`,
        testCase.branchesCovered,
        testCase.branchesTotal,
        testCase.coverageStatus,
      ]);

      // カバレッジステータスに応じた色分け
      const statusCell = row.getCell(6);
      switch (testCase.coverageStatus) {
        case '優秀':
          statusCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFC6EFCE' },
          };
          break;
        case '良好':
          statusCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFFFFCC' },
          };
          break;
        case '要改善':
          statusCell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFFFC7CE' },
          };
          break;
      }

      // 偶数行に薄い緑色の背景
      if (index % 2 === 0) {
        for (let i = 1; i <= 5; i++) {
          row.getCell(i).fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFE2EFDA' },
          };
        }
      }
    });

    // 列幅自動調整
    sheet.columns.forEach((column) => {
      column.width = 25;
    });
  }

  /**
   * 設定情報シートを作成
   */
  async createConfigSheet() {
    const sheet = this.workbook.addWorksheet('設定情報');

    sheet.addRow(['処理設定情報']);
    sheet.getRow(1).font = { size: 16, bold: true };
    sheet.addRow([]);

    sheet.addRow(['ツール名', 'JavaScript Test Specification Generator']);
    sheet.addRow(['バージョン', '1.0.0']);
    sheet.addRow(['実行日時', new Date().toLocaleString('ja-JP')]);
    sheet.addRow(['Node.jsバージョン', process.version]);
    sheet.addRow(['プラットフォーム', process.platform]);
    sheet.addRow([]);

    sheet.addRow(['機能']);
    sheet.getRow(9).font = { bold: true };
    sheet.addRow(['・JSDocアノテーションからテスト仕様書を自動生成']);
    sheet.addRow(['・Jestカバレッジレポートとの統合']);
    sheet.addRow(['・日本語および英語アノテーションのサポート']);
    sheet.addRow(['・Excel形式での出力（4シート構成）']);

    // 列幅調整
    sheet.getColumn(1).width = 30;
    sheet.getColumn(2).width = 50;

    // スタイリング
    for (let i = 3; i <= 7; i++) {
      const row = sheet.getRow(i);
      row.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFDAE3F3' },
      };
    }
  }
}
