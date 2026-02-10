/**
 * AnnotationParser.test.js
 *
 * Unit tests for AnnotationParser
 */

import { AnnotationParser } from '../../core/AnnotationParser.js';

describe('AnnotationParser', () => {
  let parser;

  beforeEach(() => {
    parser = new AnnotationParser();
  });

  test('should initialize with Japanese and English annotations', () => {
    expect(parser.japaneseAnnotations).toBeDefined();
    expect(parser.englishAnnotations).toBeDefined();
    expect(parser.japaneseAnnotations['ソフトウェア・サービス']).toBe('softwareService');
    expect(parser.englishAnnotations['TestModule']).toBe('testModule');
  });

  test('should extract class name from file path', () => {
    const className = parser.extractClassName('/path/to/MyClass.test.js');
    expect(className).toBe('MyClass');
  });

  test('should extract class name with spec extension', () => {
    const className = parser.extractClassName('/path/to/MyComponent.spec.jsx');
    expect(className).toBe('MyComponent');
  });

  test('should extract test methods from content', () => {
    const content = `
/**
 * @ソフトウェア・サービス テストサービス
 * @項目名 テスト1
 */
test('test case 1', () => {
  expect(true).toBe(true);
});

/**
 * @TestModule MyModule
 */
it('test case 2', () => {
  expect(1).toBe(1);
});
    `;

    const methods = parser.extractTestMethods(content);

    expect(methods).toHaveLength(2);
    expect(methods[0].name).toBe('test case 1');
    expect(methods[1].name).toBe('test case 2');
  });

  test('should parse Japanese annotations', () => {
    const docComment = `
 * @ソフトウェア・サービス 計算サービス
 * @項目名 加算テスト
 * @試験内容 加算機能をテスト
 * @確認項目 正しく加算される
    `;

    const annotations = parser.parseAnnotations(docComment);

    expect(annotations.softwareService).toBe('計算サービス');
    expect(annotations.testItemName).toBe('加算テスト');
    expect(annotations.testContent).toBe('加算機能をテスト');
    expect(annotations.confirmationItem).toBe('正しく加算される');
  });

  test('should parse English annotations', () => {
    const docComment = `
 * @TestModule Calculator
 * @TestCase Addition Test
 * @TestObjective Test addition feature
 * @ExpectedResult Adds correctly
    `;

    const annotations = parser.parseAnnotations(docComment);

    expect(annotations.testModule).toBe('Calculator');
    expect(annotations.testItemName).toBe('Addition Test');
    expect(annotations.testContent).toBe('Test addition feature');
    expect(annotations.confirmationItem).toBe('Adds correctly');
  });

  test('should prioritize Japanese over English annotations', () => {
    const docComment = `
 * @ソフトウェア・サービス 日本語サービス
 * @TestModule EnglishModule
 * @項目名 日本語項目
 * @TestCase EnglishCase
    `;

    const annotations = parser.parseAnnotations(docComment);

    expect(annotations.softwareService).toBe('日本語サービス');
    expect(annotations.testItemName).toBe('日本語項目');
    expect(annotations.testModule).toBe('EnglishModule'); // No Japanese equivalent, so English is used
  });

  test('should extract test cases from content', () => {
    const content = `
/**
 * @ソフトウェア・サービス サービス1
 * @項目名 テスト項目1
 */
test('test 1', () => {});

/**
 * @TestModule Module2
 */
test('test 2', () => {});
    `;

    const testCases = parser.extractTestCases(content, '/path/to/TestFile.test.js');

    expect(testCases).toHaveLength(2);
    expect(testCases[0].className).toBe('TestFile');
    expect(testCases[0].methodName).toBe('test 1');
    expect(testCases[0].softwareService).toBe('サービス1');
    expect(testCases[1].methodName).toBe('test 2');
    expect(testCases[1].testModule).toBe('Module2');
  });

  test('should extract file-level JSDoc comment', () => {
    const content = `
/**
 * File-level comment
 * @TestModule SharedModule
 */

test('test 1', () => {});
    `;

    const fileDoc = parser.extractFileDocComment(content);
    expect(fileDoc).toContain('File-level comment');
    expect(fileDoc).toContain('@TestModule SharedModule');
  });

  test('should apply file-level annotations to all test cases', () => {
    const content = `
/**
 * @テスト対象モジュール名 SharedModule
 * @テスト実施ベースラインバージョン 1.0.0
 */

/**
 * @項目名 個別テスト1
 */
test('test 1', () => {});

/**
 * @項目名 個別テスト2
 */
test('test 2', () => {});
    `;

    const testCases = parser.extractTestCases(content, '/path/to/Test.test.js');

    expect(testCases).toHaveLength(2);
    expect(testCases[0].testModule).toBe('SharedModule');
    expect(testCases[0].baselineVersion).toBe('1.0.0');
    expect(testCases[0].testItemName).toBe('個別テスト1');
    expect(testCases[1].testModule).toBe('SharedModule');
    expect(testCases[1].testItemName).toBe('個別テスト2');
  });

  test('should apply annotations to test case info', () => {
    const annotations = {
      softwareService: 'サービス',
      testItemName: 'テスト名',
      testModule: 'モジュール'
    };

    const testCase = {
      softwareService: '',
      testItemName: '',
      testModule: ''
    };

    parser.applyAnnotations(testCase, annotations);

    expect(testCase.softwareService).toBe('サービス');
    expect(testCase.testItemName).toBe('テスト名');
    expect(testCase.testModule).toBe('モジュール');
  });
});
