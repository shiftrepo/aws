package com.testspecgenerator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

import static org.junit.jupiter.api.Assertions.*;

/**
 * TestSpecificationGeneratorMainクラスのJUnitテストケース
 */
class TestSpecificationGeneratorMainTest {

    private TestSpecificationGeneratorMain app;
    private ByteArrayOutputStream outputStream;
    private PrintStream originalOut;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        app = new TestSpecificationGeneratorMain();

        // 標準出力をキャプチャするためのセットアップ
        outputStream = new ByteArrayOutputStream();
        originalOut = System.out;
        System.setOut(new PrintStream(outputStream));
    }

    @Test
    void testMainWithValidArguments() throws Exception {
        // テスト用のJavaファイルを作成
        Path javaFile = tempDir.resolve("TestClass.java");
        String javaContent = """
            /**
             * @TestModule TestModule
             * @TestCase TestCase1
             * @TestOverview Test overview description
             */
            public class TestClass {
                @Test
                public void testMethod() {
                    // テスト実装
                }
            }
            """;
        Files.write(javaFile, javaContent.getBytes(), StandardOpenOption.CREATE);

        // 出力ファイルパス
        Path outputFile = tempDir.resolve("test_output.xlsx");

        // テスト実行
        String[] args = {
            "--source-dir", tempDir.toString(),
            "--output", outputFile.toString(),
            "--no-coverage"
        };

        boolean result = app.generateTestSpecification(
            tempDir.toString(),
            outputFile.toString(),
            false,
            false
        );

        // 結果検証
        assertTrue(result, "テスト仕様書生成が成功すること");
        assertTrue(Files.exists(outputFile), "出力ファイルが作成されること");
        assertTrue(Files.size(outputFile) > 0, "出力ファイルにデータが含まれること");
    }

    @Test
    void testGenerateTestSpecificationWithEmptyDirectory() {
        Path outputFile = tempDir.resolve("empty_output.xlsx");

        boolean result = app.generateTestSpecification(
            tempDir.toString(),
            outputFile.toString(),
            false,
            false
        );

        // 空のディレクトリの場合は失敗するはず
        assertFalse(result, "Javaファイルが存在しない場合は失敗すること");
    }

    @Test
    void testGenerateTestSpecificationWithNonExistentDirectory() {
        Path nonExistentDir = tempDir.resolve("non_existent");
        Path outputFile = tempDir.resolve("output.xlsx");

        boolean result = app.generateTestSpecification(
            nonExistentDir.toString(),
            outputFile.toString(),
            false,
            false
        );

        assertFalse(result, "存在しないディレクトリの場合は失敗すること");
    }

    @Test
    void testGenerateTestSpecificationWithCoverage() throws Exception {
        // テスト用のJavaファイルを作成
        Path javaFile = tempDir.resolve("CoverageTestClass.java");
        String javaContent = """
            /**
             * @TestModule CoverageModule
             * @TestCase CoverageTest
             */
            public class CoverageTestClass {
                @Test
                public void testWithCoverage() {
                    if (true) {
                        System.out.println("branch 1");
                    } else {
                        System.out.println("branch 2");
                    }
                }
            }
            """;
        Files.write(javaFile, javaContent.getBytes(), StandardOpenOption.CREATE);

        // カバレッジレポートファイルを作成
        Path coverageDir = tempDir.resolve("coverage-reports");
        Files.createDirectories(coverageDir);

        Path coverageFile = coverageDir.resolve("jacoco-report.xml");
        String coverageContent = """
            <?xml version="1.0" encoding="UTF-8"?>
            <report name="JaCoCo Coverage Report">
                <package name="com.testspecgenerator">
                    <class name="CoverageTestClass">
                        <method name="testWithCoverage" line="10">
                            <counter type="INSTRUCTION" missed="2" covered="8"/>
                            <counter type="BRANCH" missed="1" covered="3"/>
                            <counter type="LINE" missed="1" covered="4"/>
                        </method>
                    </class>
                </package>
            </report>
            """;
        Files.write(coverageFile, coverageContent.getBytes(), StandardOpenOption.CREATE);

        Path outputFile = tempDir.resolve("coverage_output.xlsx");

        boolean result = app.generateTestSpecification(
            tempDir.toString(),
            outputFile.toString(),
            true,
            false
        );

        assertTrue(result, "カバレッジ付きでテスト仕様書生成が成功すること");
        assertTrue(Files.exists(outputFile), "カバレッジ付き出力ファイルが作成されること");
    }

    @Test
    void testMultipleTestFiles() throws Exception {
        // 複数のJavaテストファイルを作成
        for (int i = 1; i <= 3; i++) {
            Path javaFile = tempDir.resolve("TestClass" + i + ".java");
            String javaContent = String.format("""
                /**
                 * @TestModule Module%d
                 * @TestCase TestCase%d
                 * @TestOverview Test overview for class %d
                 */
                public class TestClass%d {
                    @Test
                    public void testMethod%d() {
                        // テスト実装 %d
                    }

                    @ParameterizedTest
                    public void parameterizedTest%d() {
                        // パラメータ化テスト %d
                    }
                }
                """, i, i, i, i, i, i, i, i);
            Files.write(javaFile, javaContent.getBytes(), StandardOpenOption.CREATE);
        }

        Path outputFile = tempDir.resolve("multiple_output.xlsx");

        boolean result = app.generateTestSpecification(
            tempDir.toString(),
            outputFile.toString(),
            false,
            false
        );

        assertTrue(result, "複数ファイルでテスト仕様書生成が成功すること");
        assertTrue(Files.exists(outputFile), "複数ファイル用出力ファイルが作成されること");

        // ファイルサイズが適切であることを確認（複数のテストケースがあるので大きくなるはず）
        long fileSize = Files.size(outputFile);
        assertTrue(fileSize > 5000, "複数のテストケースを含むファイルは適切なサイズであること: " + fileSize + " bytes");
    }

    @Test
    void testJavaFileWithoutAnnotations() throws Exception {
        // アノテーションのないJavaファイルを作成
        Path javaFile = tempDir.resolve("NoAnnotationTest.java");
        String javaContent = """
            public class NoAnnotationTest {
                @Test
                public void testWithoutAnnotations() {
                    // アノテーションなしのテスト
                }
            }
            """;
        Files.write(javaFile, javaContent.getBytes(), StandardOpenOption.CREATE);

        Path outputFile = tempDir.resolve("no_annotation_output.xlsx");

        boolean result = app.generateTestSpecification(
            tempDir.toString(),
            outputFile.toString(),
            false,
            false
        );

        assertTrue(result, "アノテーションなしでもテスト仕様書生成が成功すること");
        assertTrue(Files.exists(outputFile), "アノテーションなし出力ファイルが作成されること");
    }

    @Test
    void testInvalidOutputPath() throws Exception {
        // テスト用のJavaファイルを作成
        Path javaFile = tempDir.resolve("TestClass.java");
        String javaContent = """
            public class TestClass {
                @Test
                public void testMethod() {
                }
            }
            """;
        Files.write(javaFile, javaContent.getBytes(), StandardOpenOption.CREATE);

        // 無効な出力パス（存在しないディレクトリ）
        Path invalidOutputFile = tempDir.resolve("non_existent_dir").resolve("output.xlsx");

        boolean result = app.generateTestSpecification(
            tempDir.toString(),
            invalidOutputFile.toString(),
            false,
            false
        );

        // 無効な出力パスの場合は失敗するかもしれません（実装に依存）
        // ここではファイル作成の試行を確認
        assertFalse(Files.exists(invalidOutputFile), "無効なパスにはファイルが作成されないこと");
    }

    void restoreSystemOut() {
        System.setOut(originalOut);
    }
}