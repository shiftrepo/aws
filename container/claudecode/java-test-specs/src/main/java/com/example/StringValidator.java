package com.example;

import java.util.regex.Pattern;

/**
 * 文字列検証機能を提供するサンプルクラス
 * 各種バリデーションルールのデモンストレーション用
 */
public class StringValidator {

    // 正規表現パターン
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
        "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
    );

    private static final Pattern PHONE_PATTERN = Pattern.compile(
        "^(\\+81|0)\\d{1,4}-?\\d{1,4}-?\\d{4}$"
    );

    private static final Pattern URL_PATTERN = Pattern.compile(
        "^(https?|ftp)://[A-Za-z0-9.-]+(:[0-9]+)?(/.*)?$"
    );

    /**
     * 文字列が空またはnullかをチェック
     */
    public boolean isEmpty(String str) {
        return str == null || str.trim().isEmpty();
    }

    /**
     * 文字列の長さが指定範囲内かチェック
     */
    public boolean isLengthInRange(String str, int min, int max) {
        if (str == null) {
            return false;
        }
        int length = str.length();
        return length >= min && length <= max;
    }

    /**
     * メールアドレスの形式チェック
     */
    public boolean isValidEmail(String email) {
        if (email == null) {
            return false;
        }
        return EMAIL_PATTERN.matcher(email).matches();
    }

    /**
     * 電話番号の形式チェック（日本形式）
     */
    public boolean isValidPhoneNumber(String phone) {
        if (phone == null) {
            return false;
        }
        // ハイフンやスペースを削除
        String cleaned = phone.replaceAll("[\\s-]", "");
        return PHONE_PATTERN.matcher(cleaned).matches();
    }

    /**
     * URLの形式チェック
     */
    public boolean isValidUrl(String url) {
        if (url == null) {
            return false;
        }
        return URL_PATTERN.matcher(url).matches();
    }

    /**
     * 数値のみで構成されているかチェック
     */
    public boolean isNumeric(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }
        for (char c : str.toCharArray()) {
            if (!Character.isDigit(c)) {
                return false;
            }
        }
        return true;
    }

    /**
     * アルファベットのみで構成されているかチェック
     */
    public boolean isAlphabetic(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }
        for (char c : str.toCharArray()) {
            if (!Character.isLetter(c)) {
                return false;
            }
        }
        return true;
    }

    /**
     * 英数字のみで構成されているかチェック
     */
    public boolean isAlphanumeric(String str) {
        if (str == null || str.isEmpty()) {
            return false;
        }
        for (char c : str.toCharArray()) {
            if (!Character.isLetterOrDigit(c)) {
                return false;
            }
        }
        return true;
    }

    /**
     * パスワードの強度チェック
     * 8文字以上、大文字、小文字、数字、特殊文字を含む
     */
    public boolean isStrongPassword(String password) {
        if (password == null || password.length() < 8) {
            return false;
        }

        boolean hasUpper = false;
        boolean hasLower = false;
        boolean hasDigit = false;
        boolean hasSpecial = false;

        for (char c : password.toCharArray()) {
            if (Character.isUpperCase(c)) {
                hasUpper = true;
            } else if (Character.isLowerCase(c)) {
                hasLower = true;
            } else if (Character.isDigit(c)) {
                hasDigit = true;
            } else if (!Character.isLetterOrDigit(c)) {
                hasSpecial = true;
            }
        }

        return hasUpper && hasLower && hasDigit && hasSpecial;
    }

    /**
     * 郵便番号の形式チェック（日本形式 xxx-xxxx）
     */
    public boolean isValidPostalCode(String postalCode) {
        if (postalCode == null) {
            return false;
        }
        return postalCode.matches("^\\d{3}-?\\d{4}$");
    }

    /**
     * クレジットカード番号の簡易チェック（Luhnアルゴリズム）
     */
    public boolean isValidCreditCard(String cardNumber) {
        if (cardNumber == null) {
            return false;
        }

        // スペースとハイフンを削除
        String cleaned = cardNumber.replaceAll("[\\s-]", "");

        if (!cleaned.matches("^\\d{13,19}$")) {
            return false;
        }

        // Luhnアルゴリズム
        int sum = 0;
        boolean alternate = false;
        for (int i = cleaned.length() - 1; i >= 0; i--) {
            int n = Integer.parseInt(cleaned.substring(i, i + 1));
            if (alternate) {
                n *= 2;
                if (n > 9) {
                    n = (n % 10) + 1;
                }
            }
            sum += n;
            alternate = !alternate;
        }
        return (sum % 10 == 0);
    }

    /**
     * IPアドレスの形式チェック（IPv4）
     */
    public boolean isValidIPv4(String ip) {
        if (ip == null) {
            return false;
        }

        String[] parts = ip.split("\\.");
        if (parts.length != 4) {
            return false;
        }

        for (String part : parts) {
            try {
                int value = Integer.parseInt(part);
                if (value < 0 || value > 255) {
                    return false;
                }
            } catch (NumberFormatException e) {
                return false;
            }
        }
        return true;
    }

    /**
     * 日付文字列の形式チェック（yyyy-MM-dd）
     */
    public boolean isValidDateFormat(String date) {
        if (date == null) {
            return false;
        }

        if (!date.matches("^\\d{4}-\\d{2}-\\d{2}$")) {
            return false;
        }

        String[] parts = date.split("-");
        int year = Integer.parseInt(parts[0]);
        int month = Integer.parseInt(parts[1]);
        int day = Integer.parseInt(parts[2]);

        if (month < 1 || month > 12) {
            return false;
        }
        if (day < 1 || day > 31) {
            return false;
        }

        // 月別の日数チェック（簡易版）
        if ((month == 4 || month == 6 || month == 9 || month == 11) && day > 30) {
            return false;
        }
        if (month == 2 && day > 29) {
            return false;
        }

        return true;
    }

    /**
     * HTMLタグを含んでいるかチェック
     */
    public boolean containsHtml(String str) {
        if (str == null) {
            return false;
        }
        return str.matches(".*<[^>]+>.*");
    }

    /**
     * SQLインジェクションのリスクがある文字列かチェック
     */
    public boolean isSqlInjectionRisk(String str) {
        if (str == null) {
            return false;
        }
        String lower = str.toLowerCase();
        return lower.contains("drop") ||
               lower.contains("delete") ||
               lower.contains("insert") ||
               lower.contains("update") ||
               lower.contains("select") ||
               lower.contains("--") ||
               lower.contains("/*") ||
               lower.contains("*/") ||
               lower.contains("'") ||
               lower.contains(";");
    }
}