package com.testspecgenerator.model;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Module Info Service
 * @項目名 ModuleInfo単体テスト
 * @試験内容 ModuleInfoデータクラスの機能をテストする
 * @確認項目 正しくデータが格納・取得されること
 * @テスト対象モジュール名 ModuleInfo
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class ModuleInfoTest {

    @TempDir
    Path tempDir;

    /**
     * @ソフトウェア・サービス Module Info Service
     * @項目名 有効なModuleInfoの作成テスト
     * @試験内容 正常なModuleInfoオブジェクトの作成をテストする
     * @確認項目 全てのプロパティが正しく設定されること
     * @テスト対象モジュール名 ModuleInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testValidModuleInfoCreation() {
        // Setup
        String moduleName = "test-module";
        Path moduleRoot = tempDir.resolve("test-module");
        Path sourceDir = moduleRoot.resolve("src/main/java");
        Path testDir = moduleRoot.resolve("src/test/java");
        Path coverageDir = moduleRoot.resolve("target/site/jacoco");
        Path pomPath = moduleRoot.resolve("pom.xml");

        // Execute
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName(moduleName)
            .moduleRoot(moduleRoot)
            .sourceDir(sourceDir)
            .testDir(testDir)
            .coverageDir(coverageDir)
            .pomPath(pomPath)
            .build();

        // Verify
        assertEquals(moduleName, moduleInfo.getModuleName());
        assertEquals(moduleRoot, moduleInfo.getModuleRoot());
        assertEquals(sourceDir, moduleInfo.getSourceDir());
        assertEquals(testDir, moduleInfo.getTestDir());
        assertEquals(coverageDir, moduleInfo.getCoverageDir());
        assertEquals(pomPath, moduleInfo.getPomPath());
        assertTrue(moduleInfo.isValid());
        assertNull(moduleInfo.getValidationError());
    }

    /**
     * @ソフトウェア・サービス Module Info Service
     * @項目名 無効なModuleInfoの作成テスト
     * @試験内容 エラー情報を持つModuleInfoオブジェクトの作成をテストする
     * @確認項目 無効フラグとエラーメッセージが正しく設定されること
     * @テスト対象モジュール名 ModuleInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testInvalidModuleInfoCreation() {
        // Setup
        String errorMessage = "Test validation error";

        // Execute
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("invalid-module")
            .validationError(errorMessage)
            .build();

        // Verify
        assertEquals("invalid-module", moduleInfo.getModuleName());
        assertFalse(moduleInfo.isValid());
        assertEquals(errorMessage, moduleInfo.getValidationError());
    }

    /**
     * @ソフトウェア・サービス Module Info Service
     * @項目名 equals/hashCodeテスト
     * @試験内容 equalsとhashCodeメソッドの動作をテストする
     * @確認項目 同じモジュール名とルートを持つオブジェクトが等価であること
     * @テスト対象モジュール名 ModuleInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testEqualsAndHashCode() {
        // Setup
        Path moduleRoot = tempDir.resolve("module");
        ModuleInfo module1 = ModuleInfo.builder()
            .moduleName("test")
            .moduleRoot(moduleRoot)
            .build();

        ModuleInfo module2 = ModuleInfo.builder()
            .moduleName("test")
            .moduleRoot(moduleRoot)
            .build();

        ModuleInfo module3 = ModuleInfo.builder()
            .moduleName("different")
            .moduleRoot(moduleRoot)
            .build();

        // Verify
        assertEquals(module1, module2);
        assertEquals(module1.hashCode(), module2.hashCode());
        assertNotEquals(module1, module3);
        assertNotEquals(module1, null);
        assertEquals(module1, module1);
    }

    /**
     * @ソフトウェア・サービス Module Info Service
     * @項目名 toStringテスト
     * @試験内容 toStringメソッドの動作をテストする
     * @確認項目 適切な文字列表現が返されること
     * @テスト対象モジュール名 ModuleInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testToString() {
        // Setup
        ModuleInfo moduleInfo = ModuleInfo.builder()
            .moduleName("test-module")
            .moduleRoot(tempDir.resolve("test"))
            .build();

        // Execute
        String toString = moduleInfo.toString();

        // Verify
        assertTrue(toString.contains("test-module"));
        assertTrue(toString.contains("valid=true"));
    }

    /**
     * @ソフトウェア・サービス Module Info Service
     * @項目名 isValidフラグの設定テスト
     * @試験内容 isValidフラグの明示的な設定をテストする
     * @確認項目 設定したフラグ値が正しく反映されること
     * @テスト対象モジュール名 ModuleInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testIsValidFlag() {
        // Test explicit valid setting
        ModuleInfo validModule = ModuleInfo.builder()
            .moduleName("valid")
            .isValid(true)
            .build();
        assertTrue(validModule.isValid());

        // Test explicit invalid setting
        ModuleInfo invalidModule = ModuleInfo.builder()
            .moduleName("invalid")
            .isValid(false)
            .build();
        assertFalse(invalidModule.isValid());
    }
}