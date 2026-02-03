package com.testspecgenerator.core;

import com.testspecgenerator.model.ModuleInfo;
import com.testspecgenerator.model.ModuleResult;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Multi Module Processor Service
 * @項目名 MultiModuleProcessor単体テスト
 * @試験内容 マルチモジュール処理機能をテストする
 * @確認項目 正しくモジュールが処理され、レポートが生成されること
 * @テスト対象モジュール名 MultiModuleProcessor
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class MultiModuleProcessorTest {

    private MultiModuleProcessor processor;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        processor = new MultiModuleProcessor();
    }

    @AfterEach
    void tearDown() {
        if (processor != null) {
            processor.shutdown();
        }
    }

    /**
     * @ソフトウェア・サービス Multi Module Processor Service
     * @項目名 有効なモジュールの処理テスト
     * @試験内容 有効なモジュールのリストを処理する
     * @確認項目 全てのモジュールが正しく処理されること
     * @テスト対象モジュール名 MultiModuleProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessAllModulesWithValidModules() throws IOException {
        // Setup
        List<ModuleInfo> modules = createValidModules();
        Path outputDir = tempDir.resolve("output");

        // Execute
        List<ModuleResult> results = processor.processAllModules(modules, outputDir, false);

        // Verify
        assertEquals(2, results.size());
        assertTrue(results.stream().allMatch(ModuleResult::isSuccessful));

        // Verify output directory structure
        assertTrue(Files.exists(outputDir));
        assertTrue(Files.exists(outputDir.resolve("combined-report.xlsx")));
        assertTrue(Files.exists(outputDir.resolve("modules-summary.json")));
        assertTrue(Files.exists(outputDir.resolve("module-a").resolve("report.xlsx")));
        assertTrue(Files.exists(outputDir.resolve("module-b").resolve("report.xlsx")));
    }

    /**
     * @ソフトウェア・サービス Multi Module Processor Service
     * @項目名 CSV出力ありでのモジュール処理テスト
     * @試験内容 CSV出力を有効にしてモジュールを処理する
     * @確認項目 ExcelとCSVファイルの両方が生成されること
     * @テスト対象モジュール名 MultiModuleProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessAllModulesWithCsvOutput() throws IOException {
        // Setup
        List<ModuleInfo> modules = createValidModules();
        Path outputDir = tempDir.resolve("csv-output");

        // Execute
        List<ModuleResult> results = processor.processAllModules(modules, outputDir, true);

        // Verify
        assertEquals(2, results.size());

        // Verify Excel files
        assertTrue(Files.exists(outputDir.resolve("combined-report.xlsx")));
        assertTrue(Files.exists(outputDir.resolve("module-a").resolve("report.xlsx")));

        // Verify CSV files
        assertTrue(Files.exists(outputDir.resolve("combined-report_test_details.csv")));
        assertTrue(Files.exists(outputDir.resolve("combined-report_coverage.csv")));
    }

    /**
     * @ソフトウェア・サービス Multi Module Processor Service
     * @項目名 無効なモジュールを含む場合の処理テスト
     * @試験内容 無効なモジュールを含むリストを処理する
     * @確認項目 有効なモジュールのみ処理され、無効なものはスキップされること
     * @テスト対象モジュール名 MultiModuleProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessAllModulesWithInvalidModule() throws IOException {
        // Setup
        List<ModuleInfo> modules = Arrays.asList(
            createValidModule("valid-module"),
            createInvalidModule("invalid-module", "Test validation error")
        );
        Path outputDir = tempDir.resolve("mixed-output");

        // Execute
        List<ModuleResult> results = processor.processAllModules(modules, outputDir, false);

        // Verify
        assertEquals(2, results.size());

        // Find valid and invalid results
        ModuleResult validResult = results.stream()
            .filter(r -> "valid-module".equals(r.getModuleInfo().getModuleName()))
            .findFirst().orElse(null);
        ModuleResult invalidResult = results.stream()
            .filter(r -> "invalid-module".equals(r.getModuleInfo().getModuleName()))
            .findFirst().orElse(null);

        assertNotNull(validResult);
        assertNotNull(invalidResult);

        assertTrue(validResult.isSuccessful());
        assertEquals(ModuleResult.ProcessingStatus.SKIPPED, invalidResult.getProcessingStatus());
        assertEquals("Test validation error", invalidResult.getErrorMessage());
    }

    /**
     * @ソフトウェア・サービス Multi Module Processor Service
     * @項目名 空のモジュールリストの処理テスト
     * @試験内容 空のモジュールリストを処理する
     * @確認項目 空のリストが正常に処理されること
     * @テスト対象モジュール名 MultiModuleProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessAllModulesWithEmptyList() throws IOException {
        // Setup
        Path outputDir = tempDir.resolve("empty-output");

        // Execute
        List<ModuleResult> results = processor.processAllModules(Arrays.asList(), outputDir, false);

        // Verify
        assertTrue(results.isEmpty());
        assertTrue(Files.exists(outputDir));  // Output directory should still be created
    }

    /**
     * @ソフトウェア・サービス Multi Module Processor Service
     * @項目名 プロセッサのシャットダウンテスト
     * @試験内容 プロセッサの正常なシャットダウンをテストする
     * @確認項目 リソースが正しく解放されること
     * @テスト対象モジュール名 MultiModuleProcessor
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessorShutdown() {
        // Execute
        processor.shutdown();

        // Verify - no exception should be thrown
        // We can't easily verify that the executor is shutdown without access to internal state
        // But the test passes if no exception occurs

        // Multiple shutdown calls should be safe
        assertDoesNotThrow(() -> processor.shutdown());
    }

    // Helper methods for creating test data

    private List<ModuleInfo> createValidModules() throws IOException {
        return Arrays.asList(
            createValidModule("module-a"),
            createValidModule("module-b")
        );
    }

    private ModuleInfo createValidModule(String moduleName) throws IOException {
        Path moduleRoot = tempDir.resolve(moduleName);
        Path testDir = moduleRoot.resolve("src/test/java");
        Files.createDirectories(testDir);

        // Create a simple test file
        String testContent = String.format("""
            package com.example;
            import org.junit.jupiter.api.Test;
            import static org.junit.jupiter.api.Assertions.*;
            /**
             * @ソフトウェア・サービス %s Service
             * @項目名 %sテスト
             * @試験内容 テスト内容
             * @確認項目 成功すること
             * @テスト対象モジュール名 %s
             * @テスト実施ベースラインバージョン 1.0.0
             * @テストケース作成者 TestTeam
             * @テストケース作成日 2026-02-03
             * @テストケース修正者 TestTeam
             * @テストケース修正日 2026-02-03
             */
            public class %sTest {
                @Test public void test() { assertTrue(true); }
            }
            """, moduleName, moduleName, moduleName, toCamelCase(moduleName));

        Files.writeString(testDir.resolve(toCamelCase(moduleName) + "Test.java"), testContent);

        return ModuleInfo.builder()
            .moduleName(moduleName)
            .moduleRoot(moduleRoot)
            .sourceDir(moduleRoot.resolve("src/main/java"))
            .testDir(testDir)
            .coverageDir(moduleRoot.resolve("target/site/jacoco"))
            .pomPath(moduleRoot.resolve("pom.xml"))
            .build();
    }

    private ModuleInfo createInvalidModule(String moduleName, String errorMessage) {
        return ModuleInfo.builder()
            .moduleName(moduleName)
            .moduleRoot(tempDir.resolve(moduleName))
            .validationError(errorMessage)
            .build();
    }

    private String toCamelCase(String input) {
        StringBuilder result = new StringBuilder();
        boolean capitalizeNext = true;

        for (char c : input.toCharArray()) {
            if (c == '-' || c == '_') {
                capitalizeNext = true;
            } else if (capitalizeNext) {
                result.append(Character.toUpperCase(c));
                capitalizeNext = false;
            } else {
                result.append(c);
            }
        }

        return result.toString();
    }
}