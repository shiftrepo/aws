import { BasicCalculator } from '../../main/example/BasicCalculator.js';

/**
 * @ソフトウェア・サービス 計算サービス
 * @項目名 基本演算機能テスト
 * @試験内容 加減乗除、絶対値、最大値/最小値、階乗、素数判定、フィボナッチ、GCD/LCM、累乗、平方根、パーセンテージの各機能を検証
 * @確認項目 各演算が正しく実行され、エッジケースおよび例外処理が適切に動作することを確認
 * @テスト対象モジュール名 BasicCalculator
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 開発チーム
 * @テストケース作成日 2026-01-14
 * @テストケース修正者 開発チーム
 * @テストケース修正日 2026-01-14
 */
describe('BasicCalculator 基本機能テストスイート', () => {
  let calculator;

  beforeEach(() => {
    calculator = new BasicCalculator();
  });

  /**
   * @項目名 加算機能テスト
   * @試験内容 正の数、負の数、ゼロ、最大値を含む加算演算を実行
   * @確認項目 すべての加算結果が数学的に正しいことを確認
   */
  test('加算機能のテスト', () => {
    expect(calculator.add(2, 3)).toBe(5);
    expect(calculator.add(0, 0)).toBe(0);
    expect(calculator.add(-2, -3)).toBe(-5);
    expect(calculator.add(-2, 3)).toBe(1);
    expect(calculator.add(Number.MAX_SAFE_INTEGER, 0)).toBe(Number.MAX_SAFE_INTEGER);
  });

  /**
   * @項目名 減算機能テスト
   * @試験内容 正の数、負の数、ゼロを含む減算演算を実行
   * @確認項目 すべての減算結果が数学的に正しいことを確認
   */
  test('減算機能のテスト', () => {
    expect(calculator.subtract(2, 3)).toBe(-1);
    expect(calculator.subtract(5, 5)).toBe(0);
    expect(calculator.subtract(-2, -3)).toBe(1);
    expect(calculator.subtract(-2, 3)).toBe(-5);
  });

  /**
   * @TestCase testMultiplication
   * @TestType Functional
   * @TestObjective 乗算機能のテスト
   * @ExpectedResult 正しい乗算結果
   */
  test('乗算機能のテスト', () => {
    expect(calculator.multiply(2, 3)).toBe(6);
    expect(calculator.multiply(0, 100)).toBe(0);
    expect(calculator.multiply(-2, -3)).toBe(6);
    expect(calculator.multiply(-2, 3)).toBe(-6);
    expect(calculator.multiply(1, 1)).toBe(1);
  });

  /**
   * @項目名 除算機能テスト
   * @試験内容 正の数、負の数、小数を含む除算演算を実行し、ゼロ除算の例外処理を検証
   * @確認項目 正しい除算結果とゼロ除算時のError発生を確認
   */
  test('除算機能のテスト', () => {
    expect(calculator.divide(6, 3)).toBeCloseTo(2.0, 3);
    expect(calculator.divide(6, -3)).toBeCloseTo(-2.0, 3);
    expect(calculator.divide(1, 2)).toBeCloseTo(0.5, 3);
    expect(calculator.divide(10, 3)).toBeCloseTo(3.333333, 3);

    // ゼロ除算のテスト
    expect(() => calculator.divide(5, 0)).toThrow('ゼロ除算はできません');
    expect(() => calculator.divide(0, 0)).toThrow('ゼロ除算はできません');
  });

  /**
   * @TestCase testAbsoluteValue
   * @TestType Functional
   * @TestObjective 絶対値機能のテスト
   * @ExpectedResult 正しい絶対値
   */
  test('絶対値機能のテスト', () => {
    expect(calculator.abs(5)).toBe(5);
    expect(calculator.abs(-5)).toBe(5);
    expect(calculator.abs(0)).toBe(0);
    expect(calculator.abs(Number.MAX_SAFE_INTEGER)).toBe(Number.MAX_SAFE_INTEGER);
  });

  /**
   * @TestCase testMaxMin
   * @TestType Functional
   * @TestObjective 最大値・最小値機能のテスト
   * @ExpectedResult 正しい最大値・最小値
   */
  test('最大値・最小値機能のテスト', () => {
    // 最大値テスト
    expect(calculator.max(3, 5)).toBe(5);
    expect(calculator.max(5, 3)).toBe(5);
    expect(calculator.max(5, 5)).toBe(5);
    expect(calculator.max(-3, -5)).toBe(-3);
    expect(calculator.max(0, -5)).toBe(0);

    // 最小値テスト
    expect(calculator.min(3, 5)).toBe(3);
    expect(calculator.min(5, 3)).toBe(3);
    expect(calculator.min(5, 5)).toBe(5);
    expect(calculator.min(-3, -5)).toBe(-5);
    expect(calculator.min(0, -5)).toBe(-5);
  });

  /**
   * @項目名 階乗機能テスト
   * @試験内容 0から10までの階乗計算および負の数の例外処理を検証
   * @確認項目 正しい階乗計算結果と負の数入力時のError発生を確認
   */
  test('階乗機能のテスト', () => {
    expect(calculator.factorial(0)).toBe(1);
    expect(calculator.factorial(1)).toBe(1);
    expect(calculator.factorial(5)).toBe(120);
    expect(calculator.factorial(10)).toBe(3628800);

    // 負の数のテスト
    expect(() => calculator.factorial(-1)).toThrow('負の数の階乗は計算できません');
    expect(() => calculator.factorial(-5)).toThrow('負の数の階乗は計算できません');
  });

  /**
   * @項目名 素数判定機能テスト
   * @試験内容 2から100までの範囲で素数判定を実行
   * @確認項目 素数と合成数が正しく判定されることを確認
   */
  test('素数判定機能のテスト', () => {
    // 素数
    expect(calculator.isPrime(2)).toBe(true);
    expect(calculator.isPrime(3)).toBe(true);
    expect(calculator.isPrime(5)).toBe(true);
    expect(calculator.isPrime(7)).toBe(true);
    expect(calculator.isPrime(11)).toBe(true);
    expect(calculator.isPrime(13)).toBe(true);
    expect(calculator.isPrime(17)).toBe(true);
    expect(calculator.isPrime(19)).toBe(true);
    expect(calculator.isPrime(97)).toBe(true);

    // 素数でない
    expect(calculator.isPrime(0)).toBe(false);
    expect(calculator.isPrime(1)).toBe(false);
    expect(calculator.isPrime(4)).toBe(false);
    expect(calculator.isPrime(6)).toBe(false);
    expect(calculator.isPrime(8)).toBe(false);
    expect(calculator.isPrime(9)).toBe(false);
    expect(calculator.isPrime(100)).toBe(false);
  });

  /**
   * @項目名 フィボナッチ数列機能テスト
   * @試験内容 0から15までのフィボナッチ数を計算し、負の数の例外処理を検証
   * @確認項目 正しいフィボナッチ数列の生成と負の数入力時のError発生を確認
   */
  test('フィボナッチ数列機能のテスト', () => {
    expect(calculator.fibonacci(0)).toBe(0);
    expect(calculator.fibonacci(1)).toBe(1);
    expect(calculator.fibonacci(2)).toBe(1);
    expect(calculator.fibonacci(3)).toBe(2);
    expect(calculator.fibonacci(4)).toBe(3);
    expect(calculator.fibonacci(5)).toBe(5);
    expect(calculator.fibonacci(6)).toBe(8);
    expect(calculator.fibonacci(10)).toBe(55);
    expect(calculator.fibonacci(15)).toBe(610);

    // 負の数のテスト
    expect(() => calculator.fibonacci(-1)).toThrow('負の数のフィボナッチ数は計算できません');
  });

  /**
   * @項目名 最大公約数機能テスト
   * @試験内容 正の数、負の数を含むGCD計算を実行
   * @確認項目 ユークリッドの互除法による正しいGCD計算を確認
   */
  test('最大公約数機能のテスト', () => {
    expect(calculator.gcd(12, 18)).toBe(6);
    expect(calculator.gcd(48, 18)).toBe(6);
    expect(calculator.gcd(100, 50)).toBe(50);
    expect(calculator.gcd(7, 13)).toBe(1);
    expect(calculator.gcd(-12, 18)).toBe(6);
    expect(calculator.gcd(12, -18)).toBe(6);
    expect(calculator.gcd(-12, -18)).toBe(6);
  });

  /**
   * @項目名 最小公倍数機能テスト
   * @試験内容 正の数、負の数、ゼロを含むLCM計算を実行
   * @確認項目 正しいLCM計算結果を確認
   */
  test('最小公倍数機能のテスト', () => {
    expect(calculator.lcm(12, 18)).toBe(36);
    expect(calculator.lcm(4, 6)).toBe(12);
    expect(calculator.lcm(7, 13)).toBe(91);
    expect(calculator.lcm(0, 5)).toBe(0);
    expect(calculator.lcm(5, 0)).toBe(0);
    expect(calculator.lcm(-12, 18)).toBe(36);
  });

  /**
   * @項目名 累乗機能テスト
   * @試験内容 正の指数、ゼロ指数、負の指数を含む累乗計算を実行
   * @確認項目 正しい累乗計算結果を確認
   */
  test('累乗機能のテスト', () => {
    expect(calculator.power(2, 0)).toBe(1);
    expect(calculator.power(2, 3)).toBe(8);
    expect(calculator.power(5, 2)).toBe(25);
    expect(calculator.power(3, 4)).toBe(81);
    expect(calculator.power(10, 3)).toBe(1000);
    expect(calculator.power(2, -2)).toBeCloseTo(0.25, 3);
    expect(calculator.power(5, -1)).toBeCloseTo(0.2, 3);
  });

  /**
   * @項目名 平方根機能テスト
   * @試験内容 バビロニア法による平方根計算および負の数の例外処理を検証
   * @確認項目 正しい平方根計算結果と負の数入力時のError発生を確認
   */
  test('平方根機能のテスト', () => {
    expect(calculator.sqrt(0)).toBeCloseTo(0, 4);
    expect(calculator.sqrt(1)).toBeCloseTo(1, 4);
    expect(calculator.sqrt(4)).toBeCloseTo(2, 4);
    expect(calculator.sqrt(9)).toBeCloseTo(3, 4);
    expect(calculator.sqrt(16)).toBeCloseTo(4, 4);
    expect(calculator.sqrt(25)).toBeCloseTo(5, 4);
    expect(calculator.sqrt(2)).toBeCloseTo(1.41421, 4);

    // 負の数のテスト
    expect(() => calculator.sqrt(-1)).toThrow('負の数の平方根は計算できません');
    expect(() => calculator.sqrt(-25)).toThrow('負の数の平方根は計算できません');
  });

  /**
   * @項目名 パーセンテージ計算機能テスト
   * @試験内容 部分値と全体値からパーセンテージを計算し、ゼロ除算の例外処理を検証
   * @確認項目 正しいパーセンテージ計算結果とゼロ除算時のError発生を確認
   */
  test('パーセンテージ計算機能のテスト', () => {
    expect(calculator.percentage(25, 100)).toBeCloseTo(25.0, 3);
    expect(calculator.percentage(50, 200)).toBeCloseTo(25.0, 3);
    expect(calculator.percentage(75, 150)).toBeCloseTo(50.0, 3);
    expect(calculator.percentage(1, 3)).toBeCloseTo(33.333333, 3);
    expect(calculator.percentage(0, 100)).toBeCloseTo(0, 3);

    // ゼロ除算のテスト
    expect(() => calculator.percentage(50, 0)).toThrow('全体値が0の場合、パーセンテージは計算できません');
  });
});
