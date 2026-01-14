import fs from 'fs/promises';
import { TestCaseInfo } from '../model/TestCaseInfo.js';

/**
 * JSDocアノテーションを解析してテスト情報を抽出するクラス
 */
export class AnnotationParser {
  constructor() {
    // 日本語アノテーション（優先）
    this.japaneseAnnotations = {
      'ソフトウェア・サービス': 'softwareService',
      '項目名': 'testItemName',
      '試験内容': 'testContent',
      '確認項目': 'confirmationItem',
      'テスト対象モジュール名': 'testModule',
      'テスト実施ベースラインバージョン': 'baselineVersion',
      'テストケース作成者': 'creator',
      'テストケース作成日': 'createdDate',
      'テストケース修正者': 'modifier',
      'テストケース修正日': 'modifiedDate',
    };

    // 英語アノテーション（後方互換性）
    this.englishAnnotations = {
      'TestModule': 'testModule',
      'TestCase': 'testItemName',
      'BaselineVersion': 'baselineVersion',
      'TestOverview': 'testContent',
      'Verification': 'confirmationItem',
      'Creator': 'creator',
      'CreatedDate': 'createdDate',
      'Modifier': 'modifier',
      'ModifiedDate': 'modifiedDate',
      'TestObjective': 'testContent',
      'ExpectedResult': 'confirmationItem',
    };

    this.encodings = ['utf8', 'utf-8'];
  }

  /**
   * ファイルからテストケース情報を解析
   * @param {string} filePath - 解析するファイルのパス
   * @returns {Promise<TestCaseInfo[]>} テストケース情報の配列
   */
  async parseFile(filePath) {
    try {
      const content = await this.readFileWithEncoding(filePath);
      return this.extractTestCases(content, filePath);
    } catch (error) {
      console.error(`ファイル解析エラー [${filePath}]:`, error.message);
      return [];
    }
  }

  /**
   * エンコーディングを試行してファイルを読み込む
   * @param {string} filePath - ファイルパス
   * @returns {Promise<string>} ファイル内容
   */
  async readFileWithEncoding(filePath) {
    for (const encoding of this.encodings) {
      try {
        return await fs.readFile(filePath, encoding);
      } catch (error) {
        if (encoding === this.encodings[this.encodings.length - 1]) {
          throw error;
        }
      }
    }
  }

  /**
   * テストケースを抽出
   * @param {string} content - ファイル内容
   * @param {string} filePath - ファイルパス
   * @returns {TestCaseInfo[]} テストケース情報の配列
   */
  extractTestCases(content, filePath) {
    const testCases = [];
    const className = this.extractClassName(filePath);

    // ファイルレベルのJSDocコメントを抽出
    const fileDocComment = this.extractFileDocComment(content);
    const fileAnnotations = this.parseAnnotations(fileDocComment);

    // テストメソッドを検出
    const testMethods = this.extractTestMethods(content);

    for (const testMethod of testMethods) {
      const testCase = new TestCaseInfo();
      testCase.filePath = filePath;
      testCase.className = className;
      testCase.methodName = testMethod.name;

      // ファイルレベルのアノテーションを適用
      this.applyAnnotations(testCase, fileAnnotations);

      // メソッドレベルのアノテーションを解析して適用（優先）
      const methodAnnotations = this.parseAnnotations(testMethod.docComment);
      this.applyAnnotations(testCase, methodAnnotations);

      testCases.push(testCase);
    }

    return testCases;
  }

  /**
   * クラス名を抽出
   * @param {string} filePath - ファイルパス
   * @returns {string} クラス名
   */
  extractClassName(filePath) {
    const fileName = filePath.split('/').pop().split('\\').pop();
    return fileName.replace(/\.(test|spec)\.(js|jsx|ts|tsx)$/, '');
  }

  /**
   * ファイルレベルのJSDocコメントを抽出
   * @param {string} content - ファイル内容
   * @returns {string} JSDocコメント
   */
  extractFileDocComment(content) {
    const fileDocPattern = /\/\*\*\s*\n([\s\S]*?)\*\//;
    const match = content.match(fileDocPattern);
    return match ? match[1] : '';
  }

  /**
   * テストメソッドを抽出
   * @param {string} content - ファイル内容
   * @returns {Array<{name: string, docComment: string}>} テストメソッド情報
   */
  extractTestMethods(content) {
    const testMethods = [];

    // Jest test() または it() 関数を検出
    const testPattern = /\/\*\*\s*\n([\s\S]*?)\*\/\s*(?:test|it)\s*\(\s*['"`](.*?)['"`]/g;
    let match;

    while ((match = testPattern.exec(content)) !== null) {
      testMethods.push({
        docComment: match[1],
        name: match[2],
      });
    }

    return testMethods;
  }

  /**
   * JSDocコメントからアノテーションを解析
   * @param {string} docComment - JSDocコメント
   * @returns {Object} アノテーション情報
   */
  parseAnnotations(docComment) {
    const annotations = {};

    // 日本語アノテーションを解析（優先）
    for (const [japaneseKey, fieldName] of Object.entries(this.japaneseAnnotations)) {
      const pattern = new RegExp(`@${japaneseKey}\\s+(.+?)(?=\\n|$)`, 'm');
      const match = docComment.match(pattern);
      if (match) {
        annotations[fieldName] = match[1].trim();
      }
    }

    // 英語アノテーションを解析（日本語がない場合のみ）
    for (const [englishKey, fieldName] of Object.entries(this.englishAnnotations)) {
      if (!annotations[fieldName]) {
        const pattern = new RegExp(`@${englishKey}\\s+(.+?)(?=\\n|$)`, 'm');
        const match = docComment.match(pattern);
        if (match) {
          annotations[fieldName] = match[1].trim();
        }
      }
    }

    return annotations;
  }

  /**
   * アノテーション情報をTestCaseInfoに適用
   * @param {TestCaseInfo} testCase - テストケース情報
   * @param {Object} annotations - アノテーション情報
   */
  applyAnnotations(testCase, annotations) {
    for (const [fieldName, value] of Object.entries(annotations)) {
      if (testCase.hasOwnProperty(fieldName) && value) {
        testCase[fieldName] = value;
      }
    }
  }

  /**
   * 複数ファイルを一括解析
   * @param {string[]} filePaths - ファイルパスの配列
   * @returns {Promise<TestCaseInfo[]>} 全テストケース情報
   */
  async parseFiles(filePaths) {
    const allTestCases = [];

    for (const filePath of filePaths) {
      const testCases = await this.parseFile(filePath);
      allTestCases.push(...testCases);
    }

    return allTestCases;
  }
}
