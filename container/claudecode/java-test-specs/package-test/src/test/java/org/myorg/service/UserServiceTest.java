package org.myorg.service;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class UserServiceTest {

    /**
     * @ソフトウェア・サービス ユーザー管理サービス
     * @項目名 ユーザー処理テスト - 正常値
     * @試験内容 有効なユーザー名での処理をテスト
     * @確認項目 正常に処理されること
     * @テスト対象モジュール名 UserService
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 開発者
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 開発者
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessUserValid() {
        UserService service = new UserService();
        String result = service.processUser("john");
        assertEquals("Processed: JOHN", result);
    }

    /**
     * @ソフトウェア・サービス ユーザー管理サービス
     * @項目名 ユーザー処理テスト - 無効値
     * @試験内容 無効なユーザー名での処理をテスト
     * @確認項目 エラーメッセージが返されること
     * @テスト対象モジュール名 UserService
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 開発者
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 開発者
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessUserInvalid() {
        UserService service = new UserService();
        String result = service.processUser(null);
        assertEquals("Invalid user", result);
    }

    /**
     * @ソフトウェア・サービス ユーザー管理サービス
     * @項目名 スコア計算テスト
     * @試験内容 スコア計算処理をテスト
     * @確認項目 正しい計算結果が返されること
     * @テスト対象モジュール名 UserService
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 開発者
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 開発者
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testCalculateScore() {
        UserService service = new UserService();
        int result = service.calculateScore(5);
        assertEquals(55, result);
    }
}