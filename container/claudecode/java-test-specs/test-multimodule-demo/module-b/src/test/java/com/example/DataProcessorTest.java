package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;

public class DataProcessorTest {

    private DataProcessor dataProcessor;

    @BeforeEach
    void setUp() {
        dataProcessor = new DataProcessor();
    }

    /**
     * @ソフトウェア・サービス データ処理サービス
     * @項目名 データフィルタリングテスト
     * @試験内容 有効なデータのみを抽出するフィルタリング処理を検証
     * @確認項目 null・空文字・空白文字が適切に除外され、有効データのみが残ること
     * @テスト対象モジュール名 DataProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleB開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testFilterValid() {
        // Arrange
        List<String> input = Arrays.asList("valid", null, "", "  ", "another valid", "  trimmed  ");

        // Act
        List<String> result = dataProcessor.filterValid(input);

        // Assert
        assertEquals(3, result.size());
        assertTrue(result.contains("valid"));
        assertTrue(result.contains("another valid"));
        assertTrue(result.contains("trimmed"));
    }

    /**
     * @ソフトウェア・サービス データ処理サービス
     * @項目名 メールバリデーションテスト（正常系）
     * @試験内容 有効なメールアドレス形式の検証処理をテスト
     * @確認項目 正しいメールアドレス形式がtrueと判定されること
     * @テスト対象モジュール名 DataProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleB開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testValidateEmailValid() {
        // Valid email addresses
        assertTrue(dataProcessor.validateEmail("user@example.com"));
        assertTrue(dataProcessor.validateEmail("test.email@domain.org"));
        assertTrue(dataProcessor.validateEmail("admin@company.co.jp"));
    }

    /**
     * @ソフトウェア・サービス データ処理サービス
     * @項目名 メールバリデーションテスト（異常系）
     * @試験内容 無効なメールアドレス形式の検証処理をテスト
     * @確認項目 無効なメールアドレス形式がfalseと判定されること
     * @テスト対象モジュール名 DataProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleB開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testValidateEmailInvalid() {
        // Invalid email addresses
        assertFalse(dataProcessor.validateEmail(null));
        assertFalse(dataProcessor.validateEmail(""));
        assertFalse(dataProcessor.validateEmail("notanemail"));
        assertFalse(dataProcessor.validateEmail("@nodomain"));
        assertFalse(dataProcessor.validateEmail("noat.com"));
        assertFalse(dataProcessor.validateEmail("user@@domain.com"));
        assertFalse(dataProcessor.validateEmail("user@"));
    }

    /**
     * @ソフトウェア・サービス データ処理サービス
     * @項目名 平均値計算テスト
     * @試験内容 数値リストの平均値計算処理を検証
     * @確認項目 正しい平均値が計算され、null値は適切に処理されること
     * @テスト対象モジュール名 DataProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleB開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testCalculateAverage() {
        // Normal case
        List<Integer> numbers1 = Arrays.asList(10, 20, 30);
        assertEquals(20.0, dataProcessor.calculateAverage(numbers1), 0.001);

        // With null values
        List<Integer> numbers2 = Arrays.asList(10, null, 20, 30);
        assertEquals(15.0, dataProcessor.calculateAverage(numbers2), 0.001);

        // Empty list
        assertEquals(0.0, dataProcessor.calculateAverage(new ArrayList<>()), 0.001);
        assertEquals(0.0, dataProcessor.calculateAverage(null), 0.001);

        // Single value
        List<Integer> numbers3 = Arrays.asList(42);
        assertEquals(42.0, dataProcessor.calculateAverage(numbers3), 0.001);
    }
}