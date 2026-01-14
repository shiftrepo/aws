package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス 計算サービス
 * @項目名 基本演算機能テスト
 * @試験内容 加減乗除、絶対値、最大値/最小値、階乗、素数判定、フィボナッチ、GCD/LCM、累乗、平方根、パーセンテージの各機能を検証
 * @確認項目 各演算が正しく実行され、エッジケースおよび例外処理が適切に動作することを確認
 * @テスト対象モジュール名 BasicCalculator
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 開発チーム
 * @テストケース作成日 2026-01-07
 * @テストケース修正者 開発チーム
 * @テストケース修正日 2026-01-14
 */
@DisplayName("BasicCalculator 基本機能テストスイート")
public class BasicCalculatorTest {

    private BasicCalculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new BasicCalculator();
    }

    /**
     * @項目名 加算機能テスト
     * @試験内容 正の数、負の数、ゼロ、最大値を含む加算演算を実行
     * @確認項目 すべての加算結果が数学的に正しいことを確認
     */
    @Test
    @DisplayName("加算機能のテスト")
    void testAddition() {
        assertEquals(5, calculator.add(2, 3));
        assertEquals(0, calculator.add(0, 0));
        assertEquals(-5, calculator.add(-2, -3));
        assertEquals(1, calculator.add(-2, 3));
        assertEquals(Integer.MAX_VALUE, calculator.add(Integer.MAX_VALUE, 0));
    }

    /**
     * @項目名 減算機能テスト
     * @試験内容 正の数、負の数、ゼロを含む減算演算を実行
     * @確認項目 すべての減算結果が数学的に正しいことを確認
     */
    @Test
    @DisplayName("減算機能のテスト")
    void testSubtraction() {
        assertEquals(-1, calculator.subtract(2, 3));
        assertEquals(0, calculator.subtract(5, 5));
        assertEquals(1, calculator.subtract(-2, -3));
        assertEquals(-5, calculator.subtract(-2, 3));
    }

    /**
     * @TestCase testMultiplication
     * @TestType Functional
     * @TestObjective 乗算機能のテスト
     * @ExpectedResult 正しい乗算結果
     */
    @Test
    @DisplayName("乗算機能のテスト")
    void testMultiplication() {
        assertEquals(6, calculator.multiply(2, 3));
        assertEquals(0, calculator.multiply(0, 100));
        assertEquals(6, calculator.multiply(-2, -3));
        assertEquals(-6, calculator.multiply(-2, 3));
        assertEquals(1, calculator.multiply(1, 1));
    }

    /**
     * @項目名 除算機能テスト
     * @試験内容 正の数、負の数、小数を含む除算演算を実行し、ゼロ除算の例外処理を検証
     * @確認項目 正しい除算結果とゼロ除算時のArithmeticException発生を確認
     */
    @Test
    @DisplayName("除算機能のテスト")
    void testDivision() {
        assertEquals(2.0, calculator.divide(6, 3), 0.001);
        assertEquals(-2.0, calculator.divide(6, -3), 0.001);
        assertEquals(0.5, calculator.divide(1, 2), 0.001);
        assertEquals(3.333333, calculator.divide(10, 3), 0.001);

        // ゼロ除算のテスト
        assertThrows(ArithmeticException.class, () -> calculator.divide(5, 0));
        assertThrows(ArithmeticException.class, () -> calculator.divide(0, 0));
    }

    /**
     * @TestCase testAbsoluteValue
     * @TestType Functional
     * @TestObjective 絶対値機能のテスト
     * @ExpectedResult 正しい絶対値
     */
    @Test
    @DisplayName("絶対値機能のテスト")
    void testAbsoluteValue() {
        assertEquals(5, calculator.abs(5));
        assertEquals(5, calculator.abs(-5));
        assertEquals(0, calculator.abs(0));
        assertEquals(Integer.MAX_VALUE, calculator.abs(Integer.MAX_VALUE));
    }

    /**
     * @TestCase testMaxMin
     * @TestType Functional
     * @TestObjective 最大値・最小値機能のテスト
     * @ExpectedResult 正しい最大値・最小値
     */
    @Test
    @DisplayName("最大値・最小値機能のテスト")
    void testMaxMin() {
        // 最大値テスト
        assertEquals(5, calculator.max(3, 5));
        assertEquals(5, calculator.max(5, 3));
        assertEquals(5, calculator.max(5, 5));
        assertEquals(0, calculator.max(0, -5));
        assertEquals(-1, calculator.max(-1, -5));

        // 最小値テスト
        assertEquals(3, calculator.min(3, 5));
        assertEquals(3, calculator.min(5, 3));
        assertEquals(5, calculator.min(5, 5));
        assertEquals(-5, calculator.min(0, -5));
        assertEquals(-5, calculator.min(-1, -5));
    }

    /**
     * @TestCase testFactorial
     * @TestType Functional
     * @TestObjective 階乗機能のテスト
     * @ExpectedResult 正しい階乗計算
     */
    @Test
    @DisplayName("階乗機能のテスト")
    void testFactorial() {
        assertEquals(1, calculator.factorial(0));
        assertEquals(1, calculator.factorial(1));
        assertEquals(2, calculator.factorial(2));
        assertEquals(6, calculator.factorial(3));
        assertEquals(24, calculator.factorial(4));
        assertEquals(120, calculator.factorial(5));
        assertEquals(3628800, calculator.factorial(10));

        // 負の数のテスト
        assertThrows(IllegalArgumentException.class, () -> calculator.factorial(-1));
        assertThrows(IllegalArgumentException.class, () -> calculator.factorial(-10));
    }

    /**
     * @TestCase testIsPrime
     * @TestType Functional
     * @TestObjective 素数判定機能のテスト
     * @ExpectedResult 正しい素数判定
     */
    @Test
    @DisplayName("素数判定機能のテスト")
    void testIsPrime() {
        // 素数でない
        assertFalse(calculator.isPrime(0));
        assertFalse(calculator.isPrime(1));
        assertFalse(calculator.isPrime(-5));
        assertFalse(calculator.isPrime(4));
        assertFalse(calculator.isPrime(6));
        assertFalse(calculator.isPrime(8));
        assertFalse(calculator.isPrime(9));
        assertFalse(calculator.isPrime(10));

        // 素数
        assertTrue(calculator.isPrime(2));
        assertTrue(calculator.isPrime(3));
        assertTrue(calculator.isPrime(5));
        assertTrue(calculator.isPrime(7));
        assertTrue(calculator.isPrime(11));
        assertTrue(calculator.isPrime(13));
        assertTrue(calculator.isPrime(17));
        assertTrue(calculator.isPrime(19));
        assertTrue(calculator.isPrime(23));
        assertTrue(calculator.isPrime(29));
    }

    /**
     * @TestCase testFibonacci
     * @TestType Functional
     * @TestObjective フィボナッチ数列のテスト
     * @ExpectedResult 正しいフィボナッチ数
     */
    @Test
    @DisplayName("フィボナッチ数列のテスト")
    void testFibonacci() {
        assertEquals(0, calculator.fibonacci(0));
        assertEquals(1, calculator.fibonacci(1));
        assertEquals(1, calculator.fibonacci(2));
        assertEquals(2, calculator.fibonacci(3));
        assertEquals(3, calculator.fibonacci(4));
        assertEquals(5, calculator.fibonacci(5));
        assertEquals(8, calculator.fibonacci(6));
        assertEquals(13, calculator.fibonacci(7));
        assertEquals(21, calculator.fibonacci(8));
        assertEquals(34, calculator.fibonacci(9));
        assertEquals(55, calculator.fibonacci(10));

        // 負の数のテスト
        assertThrows(IllegalArgumentException.class, () -> calculator.fibonacci(-1));
    }

    /**
     * @TestCase testGcdLcm
     * @TestType Functional
     * @TestObjective 最大公約数と最小公倍数のテスト
     * @ExpectedResult 正しいGCDとLCM
     */
    @Test
    @DisplayName("最大公約数と最小公倍数のテスト")
    void testGcdLcm() {
        // GCDテスト
        assertEquals(6, calculator.gcd(12, 18));
        assertEquals(1, calculator.gcd(17, 19));
        assertEquals(5, calculator.gcd(10, 15));
        assertEquals(12, calculator.gcd(12, 0));
        assertEquals(12, calculator.gcd(0, 12));
        assertEquals(7, calculator.gcd(-14, 21));
        assertEquals(7, calculator.gcd(14, -21));

        // LCMテスト
        assertEquals(36, calculator.lcm(12, 18));
        assertEquals(323, calculator.lcm(17, 19));
        assertEquals(30, calculator.lcm(10, 15));
        assertEquals(0, calculator.lcm(0, 12));
        assertEquals(0, calculator.lcm(12, 0));
        assertEquals(42, calculator.lcm(-14, 21));
        assertEquals(42, calculator.lcm(14, -21));
    }

    /**
     * @TestCase testPower
     * @TestType Functional
     * @TestObjective 累乗計算のテスト
     * @ExpectedResult 正しい累乗結果
     */
    @Test
    @DisplayName("累乗計算のテスト")
    void testPower() {
        assertEquals(1.0, calculator.power(5, 0), 0.001);
        assertEquals(5.0, calculator.power(5, 1), 0.001);
        assertEquals(25.0, calculator.power(5, 2), 0.001);
        assertEquals(125.0, calculator.power(5, 3), 0.001);
        assertEquals(0.2, calculator.power(5, -1), 0.001);
        assertEquals(0.04, calculator.power(5, -2), 0.001);
        assertEquals(8.0, calculator.power(2, 3), 0.001);
        assertEquals(0.125, calculator.power(2, -3), 0.001);
        assertEquals(1.0, calculator.power(1, 100), 0.001);
        assertEquals(1.0, calculator.power(100, 0), 0.001);
    }

    /**
     * @TestCase testSqrt
     * @TestType Functional
     * @TestObjective 平方根計算のテスト
     * @ExpectedResult 正しい平方根
     */
    @Test
    @DisplayName("平方根計算のテスト")
    void testSqrt() {
        assertEquals(0.0, calculator.sqrt(0), 0.001);
        assertEquals(1.0, calculator.sqrt(1), 0.001);
        assertEquals(2.0, calculator.sqrt(4), 0.001);
        assertEquals(3.0, calculator.sqrt(9), 0.001);
        assertEquals(4.0, calculator.sqrt(16), 0.001);
        assertEquals(5.0, calculator.sqrt(25), 0.001);
        assertEquals(10.0, calculator.sqrt(100), 0.001);
        assertEquals(1.414, calculator.sqrt(2), 0.001);
        assertEquals(1.732, calculator.sqrt(3), 0.001);

        // 負の数のテスト
        assertThrows(IllegalArgumentException.class, () -> calculator.sqrt(-1));
        assertThrows(IllegalArgumentException.class, () -> calculator.sqrt(-16));
    }

    /**
     * @TestCase testPercentage
     * @TestType Functional
     * @TestObjective パーセンテージ計算のテスト
     * @ExpectedResult 正しいパーセンテージ
     */
    @Test
    @DisplayName("パーセンテージ計算のテスト")
    void testPercentage() {
        assertEquals(50.0, calculator.percentage(50, 100), 0.001);
        assertEquals(25.0, calculator.percentage(25, 100), 0.001);
        assertEquals(100.0, calculator.percentage(100, 100), 0.001);
        assertEquals(0.0, calculator.percentage(0, 100), 0.001);
        assertEquals(200.0, calculator.percentage(200, 100), 0.001);
        assertEquals(33.333, calculator.percentage(10, 30), 0.001);

        // ゼロ除算のテスト
        assertThrows(ArithmeticException.class, () -> calculator.percentage(50, 0));
    }
}