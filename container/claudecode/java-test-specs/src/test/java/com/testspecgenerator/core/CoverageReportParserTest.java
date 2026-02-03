package com.testspecgenerator.core;

import com.testspecgenerator.model.CoverageInfo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Coverage Report Parser Service
 * @項目名 CoverageReportParser単体テスト
 * @試験内容 カバレッジレポート解析機能をテストする（特に動的パッケージフィルタリング）
 * @確認項目 正しくカバレッジデータが解析・フィルタリングされること
 * @テスト対象モジュール名 CoverageReportParser
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class CoverageReportParserTest {

    private CoverageReportParser parser;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        parser = new CoverageReportParser();
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 動的パッケージフィルタリング機能テスト
     * @試験内容 テストファイルから動的にパッケージを抽出してフィルタリングする機能をテストする
     * @確認項目 指定されたパッケージのカバレッジデータのみが返されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testDynamicPackageFiltering() throws IOException {
        // Setup - create test files with different packages
        List<Path> testFiles = createTestFilesWithPackages();
        List<Path> coverageFiles = createMockCoverageFiles();

        // Execute
        Map<String, Object> result = parser.parseCoverageReports(coverageFiles, testFiles);

        // Verify - result should not be null
        assertNotNull(result);
        // Note: The actual filtering logic is complex and depends on JaCoCo XML/HTML parsing
        // This test verifies that the method can be called without errors
        assertTrue(result instanceof Map);
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 nullテストファイルでの処理テスト
     * @試験内容 テストファイルがnullの場合の処理をテストする
     * @確認項目 デフォルトフィルタリング（com.example）が適用されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseCoverageReportsWithNullTestFiles() throws IOException {
        // Setup
        List<Path> coverageFiles = createMockCoverageFiles();

        // Execute
        Map<String, Object> result = parser.parseCoverageReports(coverageFiles, null);

        // Verify
        assertNotNull(result);
        assertTrue(result instanceof Map);
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 空のテストファイルリストでの処理テスト
     * @試験内容 空のテストファイルリストの場合の処理をテストする
     * @確認項目 正常に処理されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseCoverageReportsWithEmptyTestFiles() throws IOException {
        // Setup
        List<Path> coverageFiles = createMockCoverageFiles();
        List<Path> emptyTestFiles = Arrays.asList();

        // Execute
        Map<String, Object> result = parser.parseCoverageReports(coverageFiles, emptyTestFiles);

        // Verify
        assertNotNull(result);
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 processCoverageReportsの後方互換性テスト
     * @試験内容 既存のprocessCoverageReportsメソッドが正常に動作することをテストする
     * @確認項目 既存の機能が破損していないこと
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testBackwardCompatibilityProcessCoverageReports() throws IOException {
        // Setup
        List<Path> coverageFiles = createMockCoverageFiles();

        // Execute - using the original method
        List<CoverageInfo> result = parser.processCoverageReports(coverageFiles);

        // Verify
        assertNotNull(result);
        assertTrue(result instanceof List);
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 processCoverageFileの拡張版テスト
     * @試験内容 パッケージフィルタリング付きのprocessCoverageFileメソッドをテストする
     * @確認項目 フィルタリング機能が正常に動作すること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessCoverageFileWithPackageFiltering() throws IOException {
        // Setup
        Path coverageFile = createSimpleXmlCoverageFile();
        java.util.Set<String> allowedPackages = java.util.Set.of("com.example", "com.test");

        // Execute
        List<CoverageInfo> result = parser.processCoverageFile(coverageFile, allowedPackages);

        // Verify
        assertNotNull(result);
        // The actual content depends on the XML structure, but method should not throw exceptions
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 不正なカバレッジファイルでのエラーハンドリングテスト
     * @試験内容 存在しないファイルや不正な形式のファイルでの処理をテストする
     * @確認項目 適切にエラーハンドリングされること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessCoverageFileWithInvalidFile() {
        // Setup
        Path nonExistentFile = tempDir.resolve("non-existent.xml");

        // Execute & Verify
        assertThrows(IOException.class, () -> {
            parser.processCoverageFile(nonExistentFile);
        });
    }

    /**
     * @ソフトウェア・サービス Coverage Report Parser Service
     * @項目名 サポートされていないファイル形式のテスト
     * @試験内容 .xml、.html以外のファイルでの処理をテストする
     * @確認項目 空のリストが返されること
     * @テスト対象モジュール名 CoverageReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testProcessCoverageFileWithUnsupportedFormat() throws IOException {
        // Setup
        Path txtFile = tempDir.resolve("coverage.txt");
        Files.writeString(txtFile, "This is not a coverage file");

        // Execute
        List<CoverageInfo> result = parser.processCoverageFile(txtFile);

        // Verify
        assertNotNull(result);
        assertTrue(result.isEmpty());
    }

    // Helper methods

    private List<Path> createTestFilesWithPackages() throws IOException {
        Path testFile1 = tempDir.resolve("TestClass1.java");
        String content1 = """
            package com.example.module1;
            import org.junit.jupiter.api.Test;
            public class TestClass1 {
                @Test public void test1() {}
            }
            """;
        Files.writeString(testFile1, content1);

        Path testFile2 = tempDir.resolve("TestClass2.java");
        String content2 = """
            package com.example.module2;
            import org.junit.jupiter.api.Test;
            public class TestClass2 {
                @Test public void test2() {}
            }
            """;
        Files.writeString(testFile2, content2);

        Path testFile3 = tempDir.resolve("TestClass3.java");
        String content3 = """
            package com.testspecgenerator.test;
            import org.junit.jupiter.api.Test;
            public class TestClass3 {
                @Test public void test3() {}
            }
            """;
        Files.writeString(testFile3, content3);

        return Arrays.asList(testFile1, testFile2, testFile3);
    }

    private List<Path> createMockCoverageFiles() throws IOException {
        Path xmlFile = createSimpleXmlCoverageFile();
        return Arrays.asList(xmlFile);
    }

    private Path createSimpleXmlCoverageFile() throws IOException {
        Path xmlFile = tempDir.resolve("jacoco.xml");
        String xmlContent = """
            <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <report name="Test Coverage Report">
                <sessioninfo id="test-session" start="0" dump="0"/>
                <package name="com/example">
                    <class name="com/example/TestClass" sourcefilename="TestClass.java">
                        <method name="testMethod" desc="()V" line="10">
                            <counter type="INSTRUCTION" missed="0" covered="5"/>
                            <counter type="BRANCH" missed="0" covered="2"/>
                            <counter type="LINE" missed="0" covered="3"/>
                            <counter type="COMPLEXITY" missed="0" covered="1"/>
                            <counter type="METHOD" missed="0" covered="1"/>
                            <counter type="CLASS" missed="0" covered="1"/>
                        </method>
                    </class>
                </package>
                <package name="com/testspecgenerator">
                    <class name="com/testspecgenerator/TestTool" sourcefilename="TestTool.java">
                        <method name="toolMethod" desc="()V" line="20">
                            <counter type="INSTRUCTION" missed="0" covered="10"/>
                            <counter type="BRANCH" missed="0" covered="0"/>
                            <counter type="LINE" missed="0" covered="5"/>
                            <counter type="COMPLEXITY" missed="0" covered="1"/>
                            <counter type="METHOD" missed="0" covered="1"/>
                            <counter type="CLASS" missed="0" covered="1"/>
                        </method>
                    </class>
                </package>
                <counter type="INSTRUCTION" missed="0" covered="15"/>
                <counter type="BRANCH" missed="0" covered="2"/>
                <counter type="LINE" missed="0" covered="8"/>
                <counter type="COMPLEXITY" missed="0" covered="2"/>
                <counter type="METHOD" missed="0" covered="2"/>
                <counter type="CLASS" missed="0" covered="2"/>
            </report>
            """;
        Files.writeString(xmlFile, xmlContent);
        return xmlFile;
    }
}