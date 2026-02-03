package com.testspecgenerator.core;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Folder Scanner Service
 * @項目名 FolderScanner単体テスト
 * @試験内容 フォルダスキャン機能をテストする
 * @確認項目 正しくJavaファイルとカバレッジファイルが検出されること
 * @テスト対象モジュール名 FolderScanner
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class FolderScannerTest {

    private FolderScanner scanner;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        scanner = new FolderScanner();
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 Javaファイルスキャンの基本テスト
     * @試験内容 指定ディレクトリ内のJavaファイルを検出する
     * @確認項目 全てのJavaファイルが正しく検出されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForJavaFilesBasic() throws IOException {
        // Setup
        createJavaFiles();

        // Execute
        List<Path> javaFiles = scanner.scanForJavaFiles(tempDir);

        // Verify
        assertEquals(3, javaFiles.size(), "3つのJavaファイルが検出されること");

        boolean foundTestClass = javaFiles.stream().anyMatch(p -> p.getFileName().toString().equals("TestClass.java"));
        boolean foundCalculator = javaFiles.stream().anyMatch(p -> p.getFileName().toString().equals("Calculator.java"));
        boolean foundValidator = javaFiles.stream().anyMatch(p -> p.getFileName().toString().equals("Validator.java"));

        assertTrue(foundTestClass, "TestClass.javaが検出されること");
        assertTrue(foundCalculator, "Calculator.javaが検出されること");
        assertTrue(foundValidator, "Validator.javaが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 空ディレクトリのスキャンテスト
     * @試験内容 Javaファイルが存在しないディレクトリをスキャンする
     * @確認項目 空のリストが返されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForJavaFilesEmptyDirectory() throws IOException {
        // Execute
        List<Path> javaFiles = scanner.scanForJavaFiles(tempDir);

        // Verify
        assertEquals(0, javaFiles.size(), "空のディレクトリでは0ファイルが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 非Javaファイルの除外テスト
     * @試験内容 .java以外のファイルは検出されないことを確認
     * @確認項目 Javaファイルのみが検出されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForJavaFilesExcludesNonJavaFiles() throws IOException {
        // Setup
        Files.writeString(tempDir.resolve("Test.java"), "public class Test {}");
        Files.writeString(tempDir.resolve("test.txt"), "This is not a Java file");
        Files.writeString(tempDir.resolve("readme.md"), "# README");
        Files.writeString(tempDir.resolve("script.py"), "print('Hello Python')");

        // Execute
        List<Path> javaFiles = scanner.scanForJavaFiles(tempDir);

        // Verify
        assertEquals(1, javaFiles.size(), "Javaファイルのみが検出されること");
        assertTrue(javaFiles.get(0).getFileName().toString().equals("Test.java"), "Test.javaが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 ネストされたディレクトリのスキャンテスト
     * @試験内容 サブディレクトリ内のJavaファイルも検出する
     * @確認項目 再帰的にJavaファイルが検出されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForJavaFilesNestedDirectories() throws IOException {
        // Setup
        Path subDir1 = tempDir.resolve("com/example");
        Path subDir2 = tempDir.resolve("org/test");
        Files.createDirectories(subDir1);
        Files.createDirectories(subDir2);

        Files.writeString(tempDir.resolve("Root.java"), "public class Root {}");
        Files.writeString(subDir1.resolve("Example.java"), "package com.example; public class Example {}");
        Files.writeString(subDir2.resolve("TestUtil.java"), "package org.test; public class TestUtil {}");

        // Execute
        List<Path> javaFiles = scanner.scanForJavaFiles(tempDir);

        // Verify
        assertEquals(3, javaFiles.size(), "ネストされたディレクトリ内のJavaファイルも検出されること");

        boolean foundRoot = javaFiles.stream().anyMatch(p -> p.getFileName().toString().equals("Root.java"));
        boolean foundExample = javaFiles.stream().anyMatch(p -> p.getFileName().toString().equals("Example.java"));
        boolean foundTestUtil = javaFiles.stream().anyMatch(p -> p.getFileName().toString().equals("TestUtil.java"));

        assertTrue(foundRoot, "Root.javaが検出されること");
        assertTrue(foundExample, "Example.javaが検出されること");
        assertTrue(foundTestUtil, "TestUtil.javaが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 カバレッジファイルスキャンの基本テスト
     * @試験内容 指定ディレクトリ内のカバレッジファイルを検出する
     * @確認項目 XMLとHTMLカバレッジファイルが検出されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForCoverageReportsBasic() throws IOException {
        // Setup
        createCoverageFiles();

        // Execute
        List<Path> coverageFiles = scanner.scanForCoverageReports(tempDir);

        // Verify
        assertEquals(4, coverageFiles.size(), "4つのカバレッジファイルが検出されること");

        boolean foundJacocoXml = coverageFiles.stream().anyMatch(p -> p.getFileName().toString().equals("jacoco.xml"));
        boolean foundIndexHtml = coverageFiles.stream().anyMatch(p -> p.getFileName().toString().equals("index.html"));
        boolean foundCoverageXml = coverageFiles.stream().anyMatch(p -> p.getFileName().toString().equals("coverage.xml"));
        boolean foundReportHtml = coverageFiles.stream().anyMatch(p -> p.getFileName().toString().equals("coverage-report.html"));

        assertTrue(foundJacocoXml, "jacoco.xmlが検出されること");
        assertTrue(foundIndexHtml, "index.htmlが検出されること");
        assertTrue(foundCoverageXml, "coverage.xmlが検出されること");
        assertTrue(foundReportHtml, "coverage-report.htmlが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 targetディレクトリ含有テスト
     * @試験内容 カバレッジレポートスキャン時にtargetディレクトリも含むこと
     * @確認項目 targetディレクトリ内のJaCoCoレポートも検出されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForCoverageReportsIncludesTarget() throws IOException {
        // Setup - 通常のカバレッジファイル
        Files.writeString(tempDir.resolve("coverage.xml"), "<coverage/>");

        // Setup - targetディレクトリ内のJaCoCoレポート（実際の構造）
        Path targetDir = tempDir.resolve("target/site/jacoco");
        Files.createDirectories(targetDir);
        Files.writeString(targetDir.resolve("jacoco.xml"), "<report/>");

        // Execute
        List<Path> coverageFiles = scanner.scanForCoverageReports(tempDir);

        // Verify - targetディレクトリ内のJaCoCoファイルも検出されることを確認
        boolean foundTargetFile = coverageFiles.stream()
            .anyMatch(p -> p.toString().contains("/target/") || p.toString().contains("\\target\\"));
        assertTrue(foundTargetFile, "targetディレクトリ内のJaCoCoファイルも検出されること");

        // 通常のカバレッジファイルが検出されることを確認
        boolean foundCoverageXml = coverageFiles.stream()
            .anyMatch(p -> p.getFileName().toString().equals("coverage.xml"));
        assertTrue(foundCoverageXml, "通常のカバレッジファイルが検出されること");

        // 両方のファイルが検出されることを確認
        assertEquals(2, coverageFiles.size(), "2つのカバレッジファイルが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 カバレッジファイルの存在しない場合のテスト
     * @試験内容 カバレッジファイルが存在しないディレクトリをスキャンする
     * @確認項目 空のリストが返されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanForCoverageReportsNoneFound() throws IOException {
        // Setup - カバレッジファイル以外のファイルを作成
        Files.writeString(tempDir.resolve("test.txt"), "Not a coverage file");
        Files.writeString(tempDir.resolve("data.json"), "{}");

        // Execute
        List<Path> coverageFiles = scanner.scanForCoverageReports(tempDir);

        // Verify
        assertEquals(0, coverageFiles.size(), "カバレッジファイルがない場合は0ファイルが検出されること");
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 存在しないディレクトリのスキャンテスト
     * @試験内容 存在しないディレクトリを指定してスキャンする
     * @確認項目 エラーなく処理され、空のリストが返されること
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanNonExistentDirectory() {
        // Setup
        Path nonExistentDir = tempDir.resolve("does-not-exist");

        // Execute & Verify - 例外が投げられないことを確認
        assertDoesNotThrow(() -> {
            List<Path> javaFiles = scanner.scanForJavaFiles(nonExistentDir);
            assertEquals(0, javaFiles.size(), "存在しないディレクトリでは0ファイルが検出されること");
        });

        assertDoesNotThrow(() -> {
            List<Path> coverageFiles = scanner.scanForCoverageReports(nonExistentDir);
            assertEquals(0, coverageFiles.size(), "存在しないディレクトリでは0ファイルが検出されること");
        });
    }

    /**
     * @ソフトウェア・サービス Folder Scanner Service
     * @項目名 大量ファイルでのスキャンテスト
     * @試験内容 多数のファイルが存在するディレクトリをスキャンする
     * @確認項目 パフォーマンスに問題がないこと
     * @テスト対象モジュール名 FolderScanner
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testScanWithManyFiles() throws IOException {
        // Setup - 50個のJavaファイルと25個のカバレッジファイルを作成
        for (int i = 1; i <= 50; i++) {
            Files.writeString(tempDir.resolve("Class" + i + ".java"),
                "public class Class" + i + " {}");
        }

        for (int i = 1; i <= 25; i++) {
            Files.writeString(tempDir.resolve("coverage" + i + ".xml"),
                "<coverage/>");
        }

        // Execute
        long startTime = System.currentTimeMillis();
        List<Path> javaFiles = scanner.scanForJavaFiles(tempDir);
        List<Path> coverageFiles = scanner.scanForCoverageReports(tempDir);
        long endTime = System.currentTimeMillis();

        // Verify
        assertEquals(50, javaFiles.size(), "50個のJavaファイルが検出されること");
        assertEquals(25, coverageFiles.size(), "25個のカバレッジファイルが検出されること");
        assertTrue(endTime - startTime < 2000, "処理時間が妥当な範囲内であること"); // 2秒以内
    }

    // Helper methods

    private void createJavaFiles() throws IOException {
        Files.writeString(tempDir.resolve("TestClass.java"), """
            package com.example;
            import org.junit.jupiter.api.Test;

            /**
             * @ソフトウェア・サービス Test Service
             * @項目名 テストケース
             * @試験内容 基本テスト
             * @確認項目 成功すること
             * @テスト対象モジュール名 TestModule
             * @テスト実施ベースラインバージョン 1.0.0
             * @テストケース作成者 TestTeam
             * @テストケース作成日 2026-02-03
             * @テストケース修正者 TestTeam
             * @テストケース修正日 2026-02-03
             */
            public class TestClass {
                @Test public void testMethod() {}
            }
            """);

        Files.writeString(tempDir.resolve("Calculator.java"), """
            package com.example;
            public class Calculator {
                public int add(int a, int b) { return a + b; }
            }
            """);

        Files.writeString(tempDir.resolve("Validator.java"), """
            package com.example;
            public class Validator {
                public boolean isValid(String input) { return input != null; }
            }
            """);
    }

    private void createCoverageFiles() throws IOException {
        // XML形式のカバレッジファイル
        Files.writeString(tempDir.resolve("jacoco.xml"), """
            <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <report name="Coverage Report">
                <package name="com/example">
                    <class name="com/example/TestClass">
                        <method name="testMethod">
                            <counter type="INSTRUCTION" missed="0" covered="5"/>
                            <counter type="BRANCH" missed="0" covered="2"/>
                        </method>
                    </class>
                </package>
            </report>
            """);

        Files.writeString(tempDir.resolve("coverage.xml"), """
            <?xml version="1.0" encoding="UTF-8"?>
            <coverage version="1.0">
                <classes>
                    <class name="Calculator" filename="Calculator.java"/>
                </classes>
            </coverage>
            """);

        // HTML形式のカバレッジファイル
        Files.writeString(tempDir.resolve("index.html"), """
            <!DOCTYPE html>
            <html>
            <head><title>Coverage Report</title></head>
            <body><h1>Coverage Report</h1></body>
            </html>
            """);

        Files.writeString(tempDir.resolve("coverage-report.html"), """
            <html><body><h1>Coverage Results</h1></body></html>
            """);
    }
}