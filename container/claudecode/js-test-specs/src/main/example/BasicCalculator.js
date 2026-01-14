/**
 * 基本的な計算機能を提供するサンプルクラス
 * C1カバレッジテストのデモンストレーション用
 */
export class BasicCalculator {
  /**
   * 2つの数値を加算
   * @param {number} a - 加算する数値1
   * @param {number} b - 加算する数値2
   * @returns {number} 加算結果
   */
  add(a, b) {
    return a + b;
  }

  /**
   * 2つの数値を減算
   * @param {number} a - 減算される数値
   * @param {number} b - 減算する数値
   * @returns {number} 減算結果
   */
  subtract(a, b) {
    return a - b;
  }

  /**
   * 2つの数値を乗算
   * @param {number} a - 乗算する数値1
   * @param {number} b - 乗算する数値2
   * @returns {number} 乗算結果
   */
  multiply(a, b) {
    return a * b;
  }

  /**
   * 2つの数値を除算
   * @param {number} a - 除算される数値
   * @param {number} b - 除算する数値
   * @returns {number} 除算結果
   * @throws {Error} ゼロ除算の場合
   */
  divide(a, b) {
    if (b === 0) {
      throw new Error('ゼロ除算はできません');
    }
    return a / b;
  }

  /**
   * 数値の絶対値を返す
   * @param {number} value - 数値
   * @returns {number} 絶対値
   */
  abs(value) {
    if (value < 0) {
      return -value;
    } else {
      return value;
    }
  }

  /**
   * 最大値を返す
   * @param {number} a - 比較する数値1
   * @param {number} b - 比較する数値2
   * @returns {number} 最大値
   */
  max(a, b) {
    if (a > b) {
      return a;
    } else {
      return b;
    }
  }

  /**
   * 最小値を返す
   * @param {number} a - 比較する数値1
   * @param {number} b - 比較する数値2
   * @returns {number} 最小値
   */
  min(a, b) {
    if (a < b) {
      return a;
    } else {
      return b;
    }
  }

  /**
   * 階乗を計算
   * @param {number} n - 階乗を計算する数値
   * @returns {number} 階乗の結果
   * @throws {Error} 負の数の場合
   */
  factorial(n) {
    if (n < 0) {
      throw new Error('負の数の階乗は計算できません');
    }
    if (n === 0 || n === 1) {
      return 1;
    }
    let result = 1;
    for (let i = 2; i <= n; i++) {
      result *= i;
    }
    return result;
  }

  /**
   * 指定された数が素数かどうかを判定
   * @param {number} n - 判定する数値
   * @returns {boolean} 素数ならtrue、そうでなければfalse
   */
  isPrime(n) {
    if (n <= 1) {
      return false;
    }
    if (n === 2) {
      return true;
    }
    if (n % 2 === 0) {
      return false;
    }
    for (let i = 3; i * i <= n; i += 2) {
      if (n % i === 0) {
        return false;
      }
    }
    return true;
  }

  /**
   * フィボナッチ数を計算
   * @param {number} n - フィボナッチ数列の位置
   * @returns {number} フィボナッチ数
   * @throws {Error} 負の数の場合
   */
  fibonacci(n) {
    if (n < 0) {
      throw new Error('負の数のフィボナッチ数は計算できません');
    }
    if (n <= 1) {
      return n;
    }
    let prev = 0;
    let curr = 1;
    for (let i = 2; i <= n; i++) {
      const temp = curr;
      curr = prev + curr;
      prev = temp;
    }
    return curr;
  }

  /**
   * 最大公約数を計算（ユークリッドの互除法）
   * @param {number} a - 数値1
   * @param {number} b - 数値2
   * @returns {number} 最大公約数
   */
  gcd(a, b) {
    a = Math.abs(a);
    b = Math.abs(b);
    while (b !== 0) {
      const temp = b;
      b = a % b;
      a = temp;
    }
    return a;
  }

  /**
   * 最小公倍数を計算
   * @param {number} a - 数値1
   * @param {number} b - 数値2
   * @returns {number} 最小公倍数
   */
  lcm(a, b) {
    if (a === 0 || b === 0) {
      return 0;
    }
    return Math.abs(a * b) / this.gcd(a, b);
  }

  /**
   * 累乗を計算
   * @param {number} base - 基数
   * @param {number} exponent - 指数
   * @returns {number} 累乗の結果
   */
  power(base, exponent) {
    if (exponent === 0) {
      return 1;
    }
    if (exponent < 0) {
      return 1 / this.power(base, -exponent);
    }
    let result = 1;
    for (let i = 0; i < exponent; i++) {
      result *= base;
    }
    return result;
  }

  /**
   * 平方根を計算（バビロニア法）
   * @param {number} n - 平方根を計算する数値
   * @returns {number} 平方根
   * @throws {Error} 負の数の場合
   */
  sqrt(n) {
    if (n < 0) {
      throw new Error('負の数の平方根は計算できません');
    }
    if (n === 0) {
      return 0;
    }
    let x = n;
    let y = 1;
    const epsilon = 0.00001;
    while (x - y > epsilon) {
      x = (x + y) / 2;
      y = n / x;
    }
    return x;
  }

  /**
   * パーセンテージ計算
   * @param {number} value - 部分値
   * @param {number} total - 全体値
   * @returns {number} パーセンテージ
   * @throws {Error} 全体値が0の場合
   */
  percentage(value, total) {
    if (total === 0) {
      throw new Error('全体値が0の場合、パーセンテージは計算できません');
    }
    return (value / total) * 100;
  }
}
