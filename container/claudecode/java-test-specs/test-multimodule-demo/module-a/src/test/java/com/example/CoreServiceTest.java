package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class CoreServiceTest {

    private CoreService coreService;

    @BeforeEach
    void setUp() {
        coreService = new CoreService();
    }

    /**
     * @ソフトウェア・サービス コア処理サービス
     * @項目名 データ処理テスト（正常系）
     * @試験内容 有効な文字列データの大文字変換処理を検証
     * @確認項目 入力文字列が正しく大文字に変換されること
     * @テスト対象モジュール名 CoreService
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleA開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessDataValid() {
        // Arrange
        String input = "hello world";

        // Act
        String result = coreService.processData(input);

        // Assert
        assertEquals("HELLO WORLD", result);
    }

    /**
     * @ソフトウェア・サービス コア処理サービス
     * @項目名 データ処理テスト（空文字系）
     * @試験内容 空文字・null入力時の処理を検証
     * @確認項目 空文字・nullに対して適切なデフォルト値が返されること
     * @テスト対象モジュール名 CoreService
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleA開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessDataEmpty() {
        // Test null input
        String result1 = coreService.processData(null);
        assertEquals("EMPTY", result1);

        // Test empty string
        String result2 = coreService.processData("");
        assertEquals("EMPTY", result2);
    }

    /**
     * @ソフトウェア・サービス コア処理サービス
     * @項目名 スコア計算テスト（境界値）
     * @試験内容 スコア計算の境界値処理を検証
     * @確認項目 境界値での正しい計算結果とクリッピング処理
     * @テスト対象モジュール名 CoreService
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 ModuleA開発チーム
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 テストチーム
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testCalculateScore() {
        // Test normal values
        assertEquals(20, coreService.calculateScore(10));
        assertEquals(100, coreService.calculateScore(50));

        // Test boundary values
        assertEquals(0, coreService.calculateScore(-5));   // Negative clipping
        assertEquals(100, coreService.calculateScore(150)); // Upper clipping
        assertEquals(0, coreService.calculateScore(0));     // Zero boundary
    }
}