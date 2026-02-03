package com.testspecgenerator.core;

import com.testspecgenerator.model.ModuleInfo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Maven Module Analyzer Service
 * @項目名 MavenModuleAnalyzer単体テスト
 * @試験内容 Maven マルチモジュールプロジェクトの解析機能をテストする
 * @確認項目 正しくモジュールが検出・検証されること
 * @テスト対象モジュール名 MavenModuleAnalyzer
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class MavenModuleAnalyzerTest {

    private MavenModuleAnalyzer analyzer;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        analyzer = new MavenModuleAnalyzer();
    }

    /**
     * @ソフトウェア・サービス Maven Module Analyzer Service
     * @項目名 正常なマルチモジュールプロジェクト解析
     * @試験内容 正常なマルチモジュールプロジェクトを解析する
     * @確認項目 全てのモジュールが正しく検出されること
     * @テスト対象モジュール名 MavenModuleAnalyzer
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testAnalyzeValidMultiModuleProject() throws IOException {
        // Setup - create valid multi-module structure
        createValidMultiModuleProject();

        // Execute
        List<ModuleInfo> modules = analyzer.analyzeProject(tempDir);

        // Verify
        assertEquals(2, modules.size());

        ModuleInfo moduleA = modules.stream()
            .filter(m -> "module-a".equals(m.getModuleName()))
            .findFirst().orElse(null);
        assertNotNull(moduleA);
        assertTrue(moduleA.isValid());

        ModuleInfo moduleB = modules.stream()
            .filter(m -> "module-b".equals(m.getModuleName()))
            .findFirst().orElse(null);
        assertNotNull(moduleB);
        assertTrue(moduleB.isValid());
    }

    /**
     * @ソフトウェア・サービス Maven Module Analyzer Service
     * @項目名 pom.xmlが存在しない場合のエラーハンドリング
     * @試験内容 pom.xmlが存在しない場合の処理をテストする
     * @確認項目 適切な例外が発生すること
     * @テスト対象モジュール名 MavenModuleAnalyzer
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testAnalyzeProjectWithoutPom() {
        // Execute & Verify
        IOException exception = assertThrows(IOException.class, () -> {
            analyzer.analyzeProject(tempDir);
        });
        assertTrue(exception.getMessage().contains("Parent pom.xml not found"));
    }

    /**
     * @ソフトウェア・サービス Maven Module Analyzer Service
     * @項目名 モジュールなしのプロジェクト解析
     * @試験内容 モジュールタグが存在しないプロジェクトを解析する
     * @確認項目 空のモジュールリストが返されること
     * @テスト対象モジュール名 MavenModuleAnalyzer
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testAnalyzeProjectWithoutModules() throws IOException {
        // Setup
        createPomWithoutModules();

        // Execute
        List<ModuleInfo> modules = analyzer.analyzeProject(tempDir);

        // Verify
        assertTrue(modules.isEmpty());
    }

    /**
     * @ソフトウェア・サービス Maven Module Analyzer Service
     * @項目名 無効なモジュール構造の検証
     * @試験内容 モジュールディレクトリが存在しない場合の処理をテストする
     * @確認項目 無効なモジュールとしてマークされること
     * @テスト対象モジュール名 MavenModuleAnalyzer
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testAnalyzeProjectWithInvalidModule() throws IOException {
        // Setup - create pom with non-existent module
        createPomWithInvalidModule();

        // Execute
        List<ModuleInfo> modules = analyzer.analyzeProject(tempDir);

        // Verify
        assertEquals(1, modules.size());
        ModuleInfo module = modules.get(0);
        assertFalse(module.isValid());
        assertTrue(module.getValidationError().contains("Module directory does not exist"));
    }

    /**
     * @ソフトウェア・サービス Maven Module Analyzer Service
     * @項目名 単一モジュールプロジェクト検出テスト
     * @試験内容 マルチモジュールプロジェクトかどうかの判定をテストする
     * @確認項目 正しく判定されること
     * @テスト対象モジュール名 MavenModuleAnalyzer
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testIsMultiModuleProject() throws IOException {
        // Test without pom.xml
        assertFalse(MavenModuleAnalyzer.isMultiModuleProject(tempDir));

        // Test with single module pom.xml
        createPomWithoutModules();
        assertFalse(MavenModuleAnalyzer.isMultiModuleProject(tempDir));

        // Test with multi-module pom.xml
        createValidMultiModuleProject();
        assertTrue(MavenModuleAnalyzer.isMultiModuleProject(tempDir));
    }

    /**
     * @ソフトウェア・サービス Maven Module Analyzer Service
     * @項目名 extractModulesメソッドのテスト
     * @試験内容 pom.xmlからモジュール名を抽出する機能をテストする
     * @確認項目 正しくモジュール名が抽出されること
     * @テスト対象モジュール名 MavenModuleAnalyzer
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testExtractModules() throws IOException {
        // Setup
        createValidMultiModuleProject();
        Path pomFile = tempDir.resolve("pom.xml");

        // Execute
        List<String> modules = analyzer.extractModules(pomFile);

        // Verify
        assertEquals(2, modules.size());
        assertTrue(modules.contains("module-a"));
        assertTrue(modules.contains("module-b"));
    }

    // Helper methods
    private void createValidMultiModuleProject() throws IOException {
        // Create parent pom.xml
        String parentPom = """
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modelVersion>4.0.0</modelVersion>
                <groupId>com.test</groupId>
                <artifactId>test-parent</artifactId>
                <version>1.0.0</version>
                <packaging>pom</packaging>
                <modules>
                    <module>module-a</module>
                    <module>module-b</module>
                </modules>
            </project>
            """;
        Files.writeString(tempDir.resolve("pom.xml"), parentPom);

        // Create module directories and pom files
        createModuleStructure("module-a");
        createModuleStructure("module-b");
    }

    private void createModuleStructure(String moduleName) throws IOException {
        Path moduleDir = tempDir.resolve(moduleName);
        Files.createDirectories(moduleDir.resolve("src/test/java"));

        String modulePom = String.format("""
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modelVersion>4.0.0</modelVersion>
                <artifactId>%s</artifactId>
                <packaging>jar</packaging>
            </project>
            """, moduleName);
        Files.writeString(moduleDir.resolve("pom.xml"), modulePom);
    }

    private void createPomWithoutModules() throws IOException {
        String singlePom = """
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modelVersion>4.0.0</modelVersion>
                <groupId>com.test</groupId>
                <artifactId>test-single</artifactId>
                <version>1.0.0</version>
                <packaging>jar</packaging>
            </project>
            """;
        Files.writeString(tempDir.resolve("pom.xml"), singlePom);
    }

    private void createPomWithInvalidModule() throws IOException {
        String invalidPom = """
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modelVersion>4.0.0</modelVersion>
                <groupId>com.test</groupId>
                <artifactId>test-invalid</artifactId>
                <version>1.0.0</version>
                <packaging>pom</packaging>
                <modules>
                    <module>non-existent-module</module>
                </modules>
            </project>
            """;
        Files.writeString(tempDir.resolve("pom.xml"), invalidPom);
    }
}