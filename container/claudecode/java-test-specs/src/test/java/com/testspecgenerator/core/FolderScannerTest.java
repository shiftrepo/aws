package com.testspecgenerator.core;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * FolderScannerクラスのJUnitテストケース
 */
class FolderScannerTest {

    private FolderScanner folderScanner;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        folderScanner = new FolderScanner();
    }

    @Test
    void testScanForJavaFiles() throws Exception {
        // テスト用のJavaファイルを作成
        Path testFile1 = tempDir.resolve("TestClass1.java");
        Path testFile2 = tempDir.resolve("TestClass2Test.java");
        Path normalFile = tempDir.resolve("RegularClass.java");
        Path nonJavaFile = tempDir.resolve("README.txt");

        Files.write(testFile1, "public class TestClass1 { @Test public void test() {} }".getBytes());
        Files.write(testFile2, "public class TestClass2Test { @Test public void test() {} }".getBytes());
        Files.write(normalFile, "public class RegularClass {}".getBytes());
        Files.write(nonJavaFile, "This is not a Java file".getBytes());

        // Javaファイルをスキャン
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);

        // 結果検証
        assertEquals(3, javaFiles.size(), "Javaファイルが3つ見つかること");
        assertTrue(javaFiles.contains(testFile1), "TestClass1.javaが含まれること");
        assertTrue(javaFiles.contains(testFile2), "TestClass2Test.javaが含まれること");
        assertTrue(javaFiles.contains(normalFile), "RegularClass.javaが含まれること");
        assertFalse(javaFiles.stream().anyMatch(p -> p.toString().endsWith(".txt")), "txtファイルは除外されること");
    }

    @Test
    void testScanForJavaFilesWithSubdirectories() throws Exception {
        // サブディレクトリを作成
        Path subDir1 = tempDir.resolve("subdir1");
        Path subDir2 = tempDir.resolve("subdir2");
        Files.createDirectories(subDir1);
        Files.createDirectories(subDir2);

        // 各ディレクトリにJavaファイルを作成
        Path rootFile = tempDir.resolve("RootTest.java");
        Path subFile1 = subDir1.resolve("Sub1Test.java");
        Path subFile2 = subDir2.resolve("Sub2Test.java");

        Files.write(rootFile, "public class RootTest { @Test public void test() {} }".getBytes());
        Files.write(subFile1, "public class Sub1Test { @Test public void test() {} }".getBytes());
        Files.write(subFile2, "public class Sub2Test { @Test public void test() {} }".getBytes());

        // Javaファイルをスキャン
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);

        // 結果検証
        assertEquals(3, javaFiles.size(), "サブディレクトリを含めて3つのJavaファイルが見つかること");
        assertTrue(javaFiles.contains(rootFile), "ルートディレクトリのファイルが含まれること");
        assertTrue(javaFiles.contains(subFile1), "subdir1のファイルが含まれること");
        assertTrue(javaFiles.contains(subFile2), "subdir2のファイルが含まれること");
    }

    @Test
    void testScanForCoverageReports() throws Exception {
        // カバレッジレポートファイルを作成
        Path jacocoXml = tempDir.resolve("jacoco-report.xml");
        Path coverageXml = tempDir.resolve("test-coverage.xml");
        Path indexHtml = tempDir.resolve("index.html");
        Path coverageHtml = tempDir.resolve("coverage-summary.html");
        Path nonCoverageFile = tempDir.resolve("other.xml");

        String xmlContent = """
            <?xml version="1.0" encoding="UTF-8"?>
            <report name="JaCoCo Coverage Report">
                <package name="com.example">
                    <class name="TestClass">
                        <method name="testMethod">
                            <counter type="BRANCH" missed="0" covered="4"/>
                        </method>
                    </class>
                </package>
            </report>
            """;

        String htmlContent = """
            <html>
            <head><title>Coverage Report</title></head>
            <body>
                <table>
                    <tr><td>TestClass</td><td>100%</td></tr>
                </table>
            </body>
            </html>
            """;

        Files.write(jacocoXml, xmlContent.getBytes());
        Files.write(coverageXml, xmlContent.getBytes());
        Files.write(indexHtml, htmlContent.getBytes());
        Files.write(coverageHtml, htmlContent.getBytes());
        Files.write(nonCoverageFile, "<xml>not coverage</xml>".getBytes());

        // カバレッジレポートをスキャン
        List<Path> coverageFiles = folderScanner.scanForCoverageReports(tempDir);

        // 結果検証
        assertEquals(4, coverageFiles.size(), "カバレッジファイルが4つ見つかること");
        assertTrue(coverageFiles.contains(jacocoXml), "jacoco-report.xmlが含まれること");
        assertTrue(coverageFiles.contains(coverageXml), "test-coverage.xmlが含まれること");
        assertTrue(coverageFiles.contains(indexHtml), "index.htmlが含まれること");
        assertTrue(coverageFiles.contains(coverageHtml), "coverage-summary.htmlが含まれること");
        assertFalse(coverageFiles.contains(nonCoverageFile), "一般的なXMLファイルは除外されること");
    }

    @Test
    void testScanEmptyDirectory() {
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);
        List<Path> coverageFiles = folderScanner.scanForCoverageReports(tempDir);

        assertTrue(javaFiles.isEmpty(), "空のディレクトリではJavaファイルは見つからない");
        assertTrue(coverageFiles.isEmpty(), "空のディレクトリではカバレッジファイルは見つからない");
    }

    @Test
    void testScanNonExistentDirectory() {
        Path nonExistentDir = tempDir.resolve("non_existent");

        List<Path> javaFiles = folderScanner.scanForJavaFiles(nonExistentDir);
        List<Path> coverageFiles = folderScanner.scanForCoverageReports(nonExistentDir);

        assertTrue(javaFiles.isEmpty(), "存在しないディレクトリではJavaファイルは見つからない");
        assertTrue(coverageFiles.isEmpty(), "存在しないディレクトリではカバレッジファイルは見つからない");
    }

    @Test
    void testExcludedDirectories() throws Exception {
        // 除外されるべきディレクトリを作成
        Path gitDir = tempDir.resolve(".git");
        Path targetDir = tempDir.resolve("target");
        Path nodeModulesDir = tempDir.resolve("node_modules");

        Files.createDirectories(gitDir);
        Files.createDirectories(targetDir);
        Files.createDirectories(nodeModulesDir);

        // 除外ディレクトリにJavaファイルを作成
        Path gitJava = gitDir.resolve("GitTest.java");
        Path targetJava = targetDir.resolve("TargetTest.java");
        Path nodeJava = nodeModulesDir.resolve("NodeTest.java");

        Files.write(gitJava, "public class GitTest {}".getBytes());
        Files.write(targetJava, "public class TargetTest {}".getBytes());
        Files.write(nodeJava, "public class NodeTest {}".getBytes());

        // 通常のディレクトリにもJavaファイルを作成
        Path normalJava = tempDir.resolve("NormalTest.java");
        Files.write(normalJava, "public class NormalTest {}".getBytes());

        // スキャン実行
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);

        // 結果検証
        assertEquals(1, javaFiles.size(), "除外ディレクトリのファイルは含まれない");
        assertTrue(javaFiles.contains(normalJava), "通常のJavaファイルは含まれる");
        assertFalse(javaFiles.contains(gitJava), ".gitディレクトリのファイルは除外される");
        assertFalse(javaFiles.contains(targetJava), "targetディレクトリのファイルは除外される");
        assertFalse(javaFiles.contains(nodeJava), "node_modulesディレクトリのファイルは除外される");
    }

    @Test
    void testLargeFileExclusion() throws Exception {
        // 通常サイズのファイル
        Path normalFile = tempDir.resolve("NormalTest.java");
        Files.write(normalFile, "public class NormalTest { @Test public void test() {} }".getBytes());

        // 大きなファイル（11MB、制限の10MBを超える）
        Path largeFile = tempDir.resolve("LargeTest.java");
        byte[] largeContent = new byte[11 * 1024 * 1024]; // 11MB
        Files.write(largeFile, largeContent, StandardOpenOption.CREATE);

        // スキャン実行
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);

        // 結果検証
        assertEquals(1, javaFiles.size(), "大きすぎるファイルは除外される");
        assertTrue(javaFiles.contains(normalFile), "通常サイズのファイルは含まれる");
        assertFalse(javaFiles.contains(largeFile), "大きすぎるファイルは除外される");
    }

    @Test
    void testGetStatistics() throws Exception {
        // テストファイルを作成
        Path testFile1 = tempDir.resolve("TestClass1.java");
        Path testFile2 = tempDir.resolve("RegularClass.java");
        Files.write(testFile1, "public class TestClass1Test {}".getBytes());
        Files.write(testFile2, "public class RegularClass {}".getBytes());

        // カバレッジファイルを作成
        Path jacocoXml = tempDir.resolve("jacoco.xml");
        Path coverageHtml = tempDir.resolve("coverage.html");
        Files.write(jacocoXml, "<report></report>".getBytes());
        Files.write(coverageHtml, "<html></html>".getBytes());

        // ファイルをスキャン
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);
        List<Path> coverageFiles = folderScanner.scanForCoverageReports(tempDir);

        // 統計情報を取得
        Map<String, Object> stats = folderScanner.getStatistics(javaFiles, coverageFiles);

        // 結果検証
        assertEquals(2, stats.get("javaFileCount"), "Javaファイル数が正しい");
        assertEquals(1, stats.get("testFileCount"), "テストファイル数が正しい");
        assertEquals(2, stats.get("coverageFileCount"), "カバレッジファイル数が正しい");
        assertEquals(1, stats.get("xmlCoverageCount"), "XMLカバレッジファイル数が正しい");
        assertEquals(1, stats.get("htmlCoverageCount"), "HTMLカバレッジファイル数が正しい");
        assertEquals(1, stats.get("directoryCount"), "ディレクトリ数が正しい");
    }

    @Test
    void testSortedResults() throws Exception {
        // アルファベット順でないファイル名で作成
        Path fileZ = tempDir.resolve("ZTest.java");
        Path fileA = tempDir.resolve("ATest.java");
        Path fileM = tempDir.resolve("MTest.java");

        Files.write(fileZ, "public class ZTest {}".getBytes());
        Files.write(fileA, "public class ATest {}".getBytes());
        Files.write(fileM, "public class MTest {}".getBytes());

        // スキャン実行
        List<Path> javaFiles = folderScanner.scanForJavaFiles(tempDir);

        // 結果がソートされていることを確認
        assertEquals(3, javaFiles.size());
        assertTrue(javaFiles.get(0).toString().contains("ATest.java"), "ファイルがソートされている");
        assertTrue(javaFiles.get(1).toString().contains("MTest.java"), "ファイルがソートされている");
        assertTrue(javaFiles.get(2).toString().contains("ZTest.java"), "ファイルがソートされている");
    }
}