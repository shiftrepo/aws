package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * @TestModule StringValidationModule
 * @TestCase StringValidationRules
 * @BaselineVersion 1.0.0
 * @TestType Comprehensive string validation testing for C1 coverage
 * @TestObjective Verify string validation rules with boundary conditions
 * @PreCondition Input validation patterns must handle various string formats
 * @ExpectedResult All validation rules should work correctly
 * @TestData DeveloperTeam
 * @CreatedDate 2026-01-07
 */
@DisplayName("StringValidator Test Suite with Full Coverage")
public class StringValidatorTest {

    private StringValidator validator;

    @BeforeEach
    void setUp() {
        validator = new StringValidator();
    }

    /**
     * @TestCase testIsEmpty
     * @TestType Functional
     * @TestObjective 空文字列チェック機能のテスト
     * @ExpectedResult 正しい空文字列判定
     */
    @Test
    @DisplayName("空文字列チェック機能のテスト")
    void testIsEmpty() {
        assertTrue(validator.isEmpty(null));
        assertTrue(validator.isEmpty(""));
        assertTrue(validator.isEmpty("   "));
        assertTrue(validator.isEmpty("\t"));
        assertTrue(validator.isEmpty("\n"));

        assertFalse(validator.isEmpty("a"));
        assertFalse(validator.isEmpty(" a "));
        assertFalse(validator.isEmpty("test"));
    }

    /**
     * @TestCase testIsLengthInRange
     * @TestType Boundary Testing
     * @TestObjective 文字列長範囲チェックのテスト
     * @ExpectedResult 正しい範囲判定
     */
    @Test
    @DisplayName("文字列長範囲チェックのテスト")
    void testIsLengthInRange() {
        assertFalse(validator.isLengthInRange(null, 1, 10));

        assertTrue(validator.isLengthInRange("", 0, 10));
        assertFalse(validator.isLengthInRange("", 1, 10));

        assertTrue(validator.isLengthInRange("hello", 5, 10));
        assertTrue(validator.isLengthInRange("hello", 3, 5));
        assertTrue(validator.isLengthInRange("hello", 5, 5));

        assertFalse(validator.isLengthInRange("hello", 6, 10));
        assertFalse(validator.isLengthInRange("hello", 1, 4));
    }

    /**
     * @TestCase testIsValidEmail
     * @TestType Pattern Matching
     * @TestObjective メールアドレス形式チェックのテスト
     * @ExpectedResult 正しいメール形式判定
     */
    @Test
    @DisplayName("メールアドレス形式チェックのテスト")
    void testIsValidEmail() {
        // 有効なメールアドレス
        assertTrue(validator.isValidEmail("test@example.com"));
        assertTrue(validator.isValidEmail("user.name@example.co.jp"));
        assertTrue(validator.isValidEmail("user+tag@example.com"));
        assertTrue(validator.isValidEmail("123@example.com"));

        // 無効なメールアドレス
        assertFalse(validator.isValidEmail(null));
        assertFalse(validator.isValidEmail(""));
        assertFalse(validator.isValidEmail("invalid"));
        assertFalse(validator.isValidEmail("@example.com"));
        assertFalse(validator.isValidEmail("user@"));
        assertFalse(validator.isValidEmail("user@.com"));
        assertFalse(validator.isValidEmail("user@example"));
        assertFalse(validator.isValidEmail("user space@example.com"));
    }

    /**
     * @TestCase testIsValidPhoneNumber
     * @TestType Pattern Matching
     * @TestObjective 電話番号形式チェックのテスト（日本形式）
     * @ExpectedResult 正しい電話番号判定
     */
    @Test
    @DisplayName("電話番号形式チェックのテスト")
    void testIsValidPhoneNumber() {
        // 有効な電話番号
        assertTrue(validator.isValidPhoneNumber("090-1234-5678"));
        assertTrue(validator.isValidPhoneNumber("09012345678"));
        assertTrue(validator.isValidPhoneNumber("03-1234-5678"));
        assertTrue(validator.isValidPhoneNumber("0312345678"));
        assertTrue(validator.isValidPhoneNumber("+81-90-1234-5678"));
        assertTrue(validator.isValidPhoneNumber("+819012345678"));

        // 無効な電話番号
        assertFalse(validator.isValidPhoneNumber(null));
        assertFalse(validator.isValidPhoneNumber(""));
        assertFalse(validator.isValidPhoneNumber("123"));
        assertFalse(validator.isValidPhoneNumber("abc-defg-hijk"));
    }

    /**
     * @TestCase testIsValidUrl
     * @TestType Pattern Matching
     * @TestObjective URL形式チェックのテスト
     * @ExpectedResult 正しいURL判定
     */
    @Test
    @DisplayName("URL形式チェックのテスト")
    void testIsValidUrl() {
        // 有効なURL
        assertTrue(validator.isValidUrl("http://example.com"));
        assertTrue(validator.isValidUrl("https://example.com"));
        assertTrue(validator.isValidUrl("https://example.com/path"));
        assertTrue(validator.isValidUrl("https://example.com:8080"));
        assertTrue(validator.isValidUrl("https://example.com:8080/path"));
        assertTrue(validator.isValidUrl("ftp://example.com"));

        // 無効なURL
        assertFalse(validator.isValidUrl(null));
        assertFalse(validator.isValidUrl(""));
        assertFalse(validator.isValidUrl("example.com"));
        assertFalse(validator.isValidUrl("//example.com"));
        assertFalse(validator.isValidUrl("file:///path"));
    }

    /**
     * @TestCase testIsNumeric
     * @TestType Character Validation
     * @TestObjective 数値文字列チェックのテスト
     * @ExpectedResult 正しい数値判定
     */
    @Test
    @DisplayName("数値文字列チェックのテスト")
    void testIsNumeric() {
        assertTrue(validator.isNumeric("123"));
        assertTrue(validator.isNumeric("0"));
        assertTrue(validator.isNumeric("9999999"));

        assertFalse(validator.isNumeric(null));
        assertFalse(validator.isNumeric(""));
        assertFalse(validator.isNumeric("12.3"));
        assertFalse(validator.isNumeric("-123"));
        assertFalse(validator.isNumeric("123a"));
        assertFalse(validator.isNumeric("a123"));
        assertFalse(validator.isNumeric("1 2 3"));
    }

    /**
     * @TestCase testIsAlphabetic
     * @TestType Character Validation
     * @TestObjective アルファベット文字列チェックのテスト
     * @ExpectedResult 正しいアルファベット判定
     */
    @Test
    @DisplayName("アルファベット文字列チェックのテスト")
    void testIsAlphabetic() {
        assertTrue(validator.isAlphabetic("abc"));
        assertTrue(validator.isAlphabetic("ABC"));
        assertTrue(validator.isAlphabetic("AbCdEf"));

        assertFalse(validator.isAlphabetic(null));
        assertFalse(validator.isAlphabetic(""));
        assertFalse(validator.isAlphabetic("abc123"));
        assertFalse(validator.isAlphabetic("123"));
        assertFalse(validator.isAlphabetic("abc "));
        assertFalse(validator.isAlphabetic("abc-def"));
    }

    /**
     * @TestCase testIsAlphanumeric
     * @TestType Character Validation
     * @TestObjective 英数字文字列チェックのテスト
     * @ExpectedResult 正しい英数字判定
     */
    @Test
    @DisplayName("英数字文字列チェックのテスト")
    void testIsAlphanumeric() {
        assertTrue(validator.isAlphanumeric("abc123"));
        assertTrue(validator.isAlphanumeric("ABC"));
        assertTrue(validator.isAlphanumeric("123"));
        assertTrue(validator.isAlphanumeric("a1b2c3"));

        assertFalse(validator.isAlphanumeric(null));
        assertFalse(validator.isAlphanumeric(""));
        assertFalse(validator.isAlphanumeric("abc-123"));
        assertFalse(validator.isAlphanumeric("abc 123"));
        assertFalse(validator.isAlphanumeric("abc_123"));
        assertFalse(validator.isAlphanumeric("abc.123"));
    }

    /**
     * @TestCase testIsStrongPassword
     * @TestType Security Validation
     * @TestObjective パスワード強度チェックのテスト
     * @ExpectedResult 正しいパスワード強度判定
     */
    @Test
    @DisplayName("パスワード強度チェックのテスト")
    void testIsStrongPassword() {
        // 強いパスワード
        assertTrue(validator.isStrongPassword("Abc123!@"));
        assertTrue(validator.isStrongPassword("Password1!"));
        assertTrue(validator.isStrongPassword("MyP@ssw0rd"));

        // 弱いパスワード
        assertFalse(validator.isStrongPassword(null));
        assertFalse(validator.isStrongPassword(""));
        assertFalse(validator.isStrongPassword("short"));
        assertFalse(validator.isStrongPassword("abc12345")); // 大文字なし
        assertFalse(validator.isStrongPassword("ABC12345")); // 小文字なし
        assertFalse(validator.isStrongPassword("Abcdefgh")); // 数字なし
        assertFalse(validator.isStrongPassword("Abc12345")); // 特殊文字なし
        assertFalse(validator.isStrongPassword("12345678")); // 文字なし
    }

    /**
     * @TestCase testIsValidPostalCode
     * @TestType Pattern Matching
     * @TestObjective 郵便番号形式チェックのテスト
     * @ExpectedResult 正しい郵便番号判定
     */
    @Test
    @DisplayName("郵便番号形式チェックのテスト")
    void testIsValidPostalCode() {
        assertTrue(validator.isValidPostalCode("123-4567"));
        assertTrue(validator.isValidPostalCode("1234567"));

        assertFalse(validator.isValidPostalCode(null));
        assertFalse(validator.isValidPostalCode(""));
        assertFalse(validator.isValidPostalCode("123"));
        assertFalse(validator.isValidPostalCode("12-34567"));
        assertFalse(validator.isValidPostalCode("1234-567"));
        assertFalse(validator.isValidPostalCode("abc-defg"));
    }

    /**
     * @TestCase testIsValidCreditCard
     * @TestType Algorithm Validation
     * @TestObjective クレジットカード番号チェックのテスト（Luhnアルゴリズム）
     * @ExpectedResult 正しいカード番号判定
     */
    @Test
    @DisplayName("クレジットカード番号チェックのテスト")
    void testIsValidCreditCard() {
        // 有効なカード番号（テスト用）
        assertTrue(validator.isValidCreditCard("4532015112830366")); // Visa
        assertTrue(validator.isValidCreditCard("5425233430109903")); // MasterCard
        assertTrue(validator.isValidCreditCard("4532-0151-1283-0366")); // With hyphens
        assertTrue(validator.isValidCreditCard("4532 0151 1283 0366")); // With spaces

        // 無効なカード番号
        assertFalse(validator.isValidCreditCard(null));
        assertFalse(validator.isValidCreditCard(""));
        assertFalse(validator.isValidCreditCard("1234567890123456"));
        assertFalse(validator.isValidCreditCard("123")); // Too short
        assertFalse(validator.isValidCreditCard("12345678901234567890")); // Too long
        assertFalse(validator.isValidCreditCard("abcd-efgh-ijkl-mnop"));
    }

    /**
     * @TestCase testIsValidIPv4
     * @TestType Pattern Matching
     * @TestObjective IPv4アドレス形式チェックのテスト
     * @ExpectedResult 正しいIPアドレス判定
     */
    @Test
    @DisplayName("IPv4アドレス形式チェックのテスト")
    void testIsValidIPv4() {
        // 有効なIPアドレス
        assertTrue(validator.isValidIPv4("192.168.0.1"));
        assertTrue(validator.isValidIPv4("10.0.0.1"));
        assertTrue(validator.isValidIPv4("172.16.0.1"));
        assertTrue(validator.isValidIPv4("0.0.0.0"));
        assertTrue(validator.isValidIPv4("255.255.255.255"));

        // 無効なIPアドレス
        assertFalse(validator.isValidIPv4(null));
        assertFalse(validator.isValidIPv4(""));
        assertFalse(validator.isValidIPv4("256.0.0.1")); // > 255
        assertFalse(validator.isValidIPv4("192.168.0")); // 不完全
        assertFalse(validator.isValidIPv4("192.168.0.1.1")); // 多すぎ
        assertFalse(validator.isValidIPv4("192.168.-1.1")); // 負の値
        assertFalse(validator.isValidIPv4("192.168.a.1")); // 文字
    }

    /**
     * @TestCase testIsValidDateFormat
     * @TestType Date Validation
     * @TestObjective 日付形式チェックのテスト
     * @ExpectedResult 正しい日付形式判定
     */
    @Test
    @DisplayName("日付形式チェックのテスト")
    void testIsValidDateFormat() {
        // 有効な日付
        assertTrue(validator.isValidDateFormat("2024-01-01"));
        assertTrue(validator.isValidDateFormat("2024-12-31"));
        assertTrue(validator.isValidDateFormat("2024-02-29")); // うるう年
        assertTrue(validator.isValidDateFormat("2024-04-30"));

        // 無効な日付
        assertFalse(validator.isValidDateFormat(null));
        assertFalse(validator.isValidDateFormat(""));
        assertFalse(validator.isValidDateFormat("2024-13-01")); // 月が無効
        assertFalse(validator.isValidDateFormat("2024-00-01")); // 月が無効
        assertFalse(validator.isValidDateFormat("2024-01-32")); // 日が無効
        assertFalse(validator.isValidDateFormat("2024-01-00")); // 日が無効
        assertFalse(validator.isValidDateFormat("2024-02-30")); // 2月30日
        assertFalse(validator.isValidDateFormat("2024-04-31")); // 4月31日
        assertFalse(validator.isValidDateFormat("2024/01/01")); // 形式違い
        assertFalse(validator.isValidDateFormat("01-01-2024")); // 形式違い
    }

    /**
     * @TestCase testContainsHtml
     * @TestType Security Validation
     * @TestObjective HTMLタグ検出のテスト
     * @ExpectedResult 正しいHTMLタグ検出
     */
    @Test
    @DisplayName("HTMLタグ検出のテスト")
    void testContainsHtml() {
        assertTrue(validator.containsHtml("<div>test</div>"));
        assertTrue(validator.containsHtml("Hello <b>world</b>"));
        assertTrue(validator.containsHtml("<br>"));
        assertTrue(validator.containsHtml("<img src='test.jpg'>"));

        assertFalse(validator.containsHtml(null));
        assertFalse(validator.containsHtml(""));
        assertFalse(validator.containsHtml("plain text"));
        assertFalse(validator.containsHtml("a < b"));
        assertFalse(validator.containsHtml("a > b"));
    }

    /**
     * @TestCase testIsSqlInjectionRisk
     * @TestType Security Validation
     * @TestObjective SQLインジェクションリスク検出のテスト
     * @ExpectedResult 正しいSQLインジェクションリスク検出
     */
    @Test
    @DisplayName("SQLインジェクションリスク検出のテスト")
    void testIsSqlInjectionRisk() {
        assertTrue(validator.isSqlInjectionRisk("DROP TABLE users"));
        assertTrue(validator.isSqlInjectionRisk("1' OR '1'='1"));
        assertTrue(validator.isSqlInjectionRisk("DELETE FROM users"));
        assertTrue(validator.isSqlInjectionRisk("INSERT INTO users"));
        assertTrue(validator.isSqlInjectionRisk("UPDATE users SET"));
        assertTrue(validator.isSqlInjectionRisk("SELECT * FROM"));
        assertTrue(validator.isSqlInjectionRisk("-- comment"));
        assertTrue(validator.isSqlInjectionRisk("/* comment */"));
        assertTrue(validator.isSqlInjectionRisk("value; DROP TABLE"));

        assertFalse(validator.isSqlInjectionRisk(null));
        assertFalse(validator.isSqlInjectionRisk(""));
        assertFalse(validator.isSqlInjectionRisk("normal text"));
        assertFalse(validator.isSqlInjectionRisk("user input"));
    }
}