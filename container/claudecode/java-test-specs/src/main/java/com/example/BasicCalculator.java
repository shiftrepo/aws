package com.example;

/**
 * 基本的な計算機能を提供するサンプルクラス
 * C1カバレッジテストのデモンストレーション用
 */
public class BasicCalculator {

    /**
     * 2つの数値を加算
     */
    public int add(int a, int b) {
        return a + b;
    }

    /**
     * 2つの数値を減算
     */
    public int subtract(int a, int b) {
        return a - b;
    }

    /**
     * 2つの数値を乗算
     */
    public int multiply(int a, int b) {
        return a * b;
    }

    /**
     * 2つの数値を除算
     * @throws ArithmeticException ゼロ除算の場合
     */
    public double divide(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("ゼロ除算はできません");
        }
        return a / b;
    }

    /**
     * 数値の絶対値を返す
     */
    public int abs(int value) {
        if (value < 0) {
            return -value;
        } else {
            return value;
        }
    }

    /**
     * 最大値を返す
     */
    public int max(int a, int b) {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }

    /**
     * 最小値を返す
     */
    public int min(int a, int b) {
        if (a < b) {
            return a;
        } else {
            return b;
        }
    }

    /**
     * 階乗を計算
     */
    public long factorial(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("負の数の階乗は計算できません");
        }
        if (n == 0 || n == 1) {
            return 1;
        }
        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    /**
     * 指定された数が素数かどうかを判定
     */
    public boolean isPrime(int n) {
        if (n <= 1) {
            return false;
        }
        if (n == 2) {
            return true;
        }
        if (n % 2 == 0) {
            return false;
        }
        for (int i = 3; i * i <= n; i += 2) {
            if (n % i == 0) {
                return false;
            }
        }
        return true;
    }

    /**
     * フィボナッチ数を計算
     */
    public int fibonacci(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("負の数のフィボナッチ数は計算できません");
        }
        if (n <= 1) {
            return n;
        }
        int prev = 0;
        int curr = 1;
        for (int i = 2; i <= n; i++) {
            int temp = curr;
            curr = prev + curr;
            prev = temp;
        }
        return curr;
    }

    /**
     * 最大公約数を計算（ユークリッドの互除法）
     */
    public int gcd(int a, int b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }

    /**
     * 最小公倍数を計算
     */
    public int lcm(int a, int b) {
        if (a == 0 || b == 0) {
            return 0;
        }
        return Math.abs(a * b) / gcd(a, b);
    }

    /**
     * 累乗を計算
     */
    public double power(double base, int exponent) {
        if (exponent == 0) {
            return 1;
        }
        if (exponent < 0) {
            return 1 / power(base, -exponent);
        }
        double result = 1;
        for (int i = 0; i < exponent; i++) {
            result *= base;
        }
        return result;
    }

    /**
     * 平方根を計算（バビロニア法）
     */
    public double sqrt(double n) {
        if (n < 0) {
            throw new IllegalArgumentException("負の数の平方根は計算できません");
        }
        if (n == 0) {
            return 0;
        }
        double x = n;
        double y = 1;
        double epsilon = 0.00001;
        while (x - y > epsilon) {
            x = (x + y) / 2;
            y = n / x;
        }
        return x;
    }

    /**
     * パーセンテージ計算
     */
    public double percentage(double value, double total) {
        if (total == 0) {
            throw new ArithmeticException("全体値が0の場合、パーセンテージは計算できません");
        }
        return (value / total) * 100;
    }
}