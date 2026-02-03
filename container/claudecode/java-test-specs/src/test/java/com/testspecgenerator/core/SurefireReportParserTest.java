package com.testspecgenerator.core;

import com.testspecgenerator.model.TestCaseInfo;
import com.testspecgenerator.model.TestExecutionInfo;
import com.testspecgenerator.model.TestExecutionInfo.TestMethodResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Surefire Report Parser Service
 * @項目名 SurefireReportParser単体テスト
 * @試験内容 Maven Surefireレポート解析機能をテストする
 * @確認項目 正しくXMLレポートが解析されること
 * @テスト対象モジュール名 SurefireReportParser
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class SurefireReportParserTest {

    private SurefireReportParser parser;

    @TempDir
    Path tempDir;

    @BeforeEach
    void setUp() {
        parser = new SurefireReportParser();
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 有効なSurefireレポートの解析テスト
     * @試験内容 正常なSurefireレポートXMLファイルを解析する
     * @確認項目 正しく統計情報が抽出されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseSurefireReportsWithValidData() throws IOException {
        // Setup
        Path reportFile = createValidSurefireReport();
        List<Path> reportFiles = Arrays.asList(reportFile);

        // Execute
        List<TestExecutionInfo> results = parser.parseSurefireReports(reportFiles);

        // Verify
        assertEquals(1, results.size(), "1つのテストスイートが解析されること");

        TestExecutionInfo info = results.get(0);
        assertEquals("com.example.BasicCalculatorTest", info.getClassName());
        assertEquals(5, info.getTotalTests());
        assertEquals(4, info.getPassedTests());
        assertEquals(1, info.getFailedTests());
        assertEquals(0, info.getErrorTests());
        assertEquals(0, info.getSkippedTests());
        assertEquals(80.0, info.getSuccessRate(), 0.01);

        // メソッド結果の確認
        TestMethodResult methodResult = info.getMethodResult("testPositiveAddition");
        assertNotNull(methodResult);
        assertEquals("passed", methodResult.getStatus());
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 複数のSurefireレポートファイルの解析テスト
     * @試験内容 複数のSurefireレポートファイルを同時に解析する
     * @確認項目 全てのファイルが正しく処理されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseSurefireReportsWithMultipleFiles() throws IOException {
        // Setup
        Path reportFile1 = createValidSurefireReport();
        Path reportFile2 = createSecondSurefireReport();
        List<Path> reportFiles = Arrays.asList(reportFile1, reportFile2);

        // Execute
        List<TestExecutionInfo> results = parser.parseSurefireReports(reportFiles);

        // Verify
        assertEquals(2, results.size(), "2つのテストスイートが解析されること");

        // 最初のファイル
        TestExecutionInfo info1 = results.stream()
            .filter(info -> "com.example.BasicCalculatorTest".equals(info.getClassName()))
            .findFirst().orElse(null);
        assertNotNull(info1);
        assertEquals(5, info1.getTotalTests());

        // 2つ目のファイル
        TestExecutionInfo info2 = results.stream()
            .filter(info -> "com.example.StringValidatorTest".equals(info.getClassName()))
            .findFirst().orElse(null);
        assertNotNull(info2);
        assertEquals(3, info2.getTotalTests());
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 不正なXMLファイルでのエラーハンドリングテスト
     * @試験内容 不正な形式のXMLファイルを処理する
     * @確認項目 適切にエラーハンドリングされること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseSurefireReportsWithInvalidXml() throws IOException {
        // Setup
        Path invalidFile = tempDir.resolve("TEST-Invalid.xml");
        String invalidContent = """
            <invalid-xml>
                <not-a-testsuite>
                    <broken-structure/>
                </not-a-testsuite>
            </invalid-xml>
            """;
        Files.writeString(invalidFile, invalidContent);

        List<Path> reportFiles = Arrays.asList(invalidFile);

        // Execute
        List<TestExecutionInfo> results = parser.parseSurefireReports(reportFiles);

        // Verify - 不正なXMLは無視される
        assertEquals(0, results.size(), "不正なXMLファイルは結果に含まれないこと");
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 存在しないファイルでのエラーハンドリングテスト
     * @試験内容 存在しないファイルパスを処理する
     * @確認項目 エラーなく処理されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseSurefireReportsWithNonExistentFile() {
        // Setup
        Path nonExistentFile = tempDir.resolve("non-existent-file.xml");
        List<Path> reportFiles = Arrays.asList(nonExistentFile);

        // Execute
        List<TestExecutionInfo> results = parser.parseSurefireReports(reportFiles);

        // Verify
        assertEquals(0, results.size(), "存在しないファイルは結果に含まれないこと");
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 空のファイルリストでの処理テスト
     * @試験内容 空のファイルリストを処理する
     * @確認項目 正常に処理されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseSurefireReportsWithEmptyList() {
        // Setup
        List<Path> emptyList = new ArrayList<>();

        // Execute
        List<TestExecutionInfo> results = parser.parseSurefireReports(emptyList);

        // Verify
        assertEquals(0, results.size(), "空のリストでは結果も空であること");
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 テスト実行結果統合機能のテスト
     * @試験内容 TestCaseInfoリストにテスト実行結果を統合する
     * @確認項目 正しく実行結果が設定されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testMergeExecutionResults() throws IOException {
        // Setup
        List<TestCaseInfo> testCases = createSampleTestCases();

        Path reportFile = createValidSurefireReport();
        List<TestExecutionInfo> executionResults = parser.parseSurefireReports(Arrays.asList(reportFile));

        // Execute
        parser.mergeExecutionResults(testCases, executionResults);

        // Verify
        TestCaseInfo testCase = testCases.stream()
            .filter(tc -> "BasicCalculatorTest".equals(tc.getClassName()))
            .findFirst().orElse(null);

        assertNotNull(testCase);
        assertEquals(5, testCase.getTestsTotal());
        assertEquals(4, testCase.getTestsPassed());
        assertEquals("Partial", testCase.getTestExecutionStatus());
        assertEquals(80.0, testCase.getTestSuccessRate(), 0.01);
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 nullデータでの統合機能テスト
     * @試験内容 nullのテストケースや実行結果で統合処理を行う
     * @確認項目 エラーなく処理されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testMergeExecutionResultsWithNullData() {
        // Execute & Verify - nullデータでも例外が発生しないこと
        assertDoesNotThrow(() -> {
            parser.mergeExecutionResults(null, null);
        });

        assertDoesNotThrow(() -> {
            parser.mergeExecutionResults(new ArrayList<>(), null);
        });

        assertDoesNotThrow(() -> {
            parser.mergeExecutionResults(null, new ArrayList<>());
        });
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 実行結果が見つからない場合の統合テスト
     * @試験内容 対応するSurefireレポートがないテストケースの処理
     * @確認項目 デフォルト値が設定されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testMergeExecutionResultsWithNoMatchingReport() {
        // Setup
        List<TestCaseInfo> testCases = createSampleTestCases();
        List<TestExecutionInfo> emptyExecutionResults = new ArrayList<>();

        // Execute
        parser.mergeExecutionResults(testCases, emptyExecutionResults);

        // Verify - デフォルト値が設定されること
        for (TestCaseInfo testCase : testCases) {
            assertEquals(0, testCase.getTestsTotal());
            assertEquals(0, testCase.getTestsPassed());
            assertEquals("Unknown", testCase.getTestExecutionStatus());
            assertEquals(0.0, testCase.getTestSuccessRate(), 0.01);
        }
    }

    /**
     * @ソフトウェア・サービス Surefire Report Parser Service
     * @項目名 エラーとスキップを含むレポートの解析テスト
     * @試験内容 失敗、エラー、スキップしたテストを含むレポートを処理する
     * @確認項目 全ての状態が正しく解析されること
     * @テスト対象モジュール名 SurefireReportParser
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParseSurefireReportWithErrorsAndSkips() throws IOException {
        // Setup
        Path reportFile = createComplexSurefireReport();
        List<Path> reportFiles = Arrays.asList(reportFile);

        // Execute
        List<TestExecutionInfo> results = parser.parseSurefireReports(reportFiles);

        // Verify
        assertEquals(1, results.size());

        TestExecutionInfo info = results.get(0);
        assertEquals("com.example.ComplexTest", info.getClassName());
        assertEquals(6, info.getTotalTests());
        assertEquals(3, info.getPassedTests());
        assertEquals(1, info.getFailedTests());
        assertEquals(1, info.getErrorTests());
        assertEquals(1, info.getSkippedTests());
        assertEquals(50.0, info.getSuccessRate(), 0.01);

        // 個別メソッド結果の確認
        TestMethodResult passedMethod = info.getMethodResult("testSuccess");
        assertNotNull(passedMethod);
        assertEquals("passed", passedMethod.getStatus());

        TestMethodResult failedMethod = info.getMethodResult("testFailure");
        assertNotNull(failedMethod);
        assertEquals("failed", failedMethod.getStatus());
        assertEquals("Test failed deliberately", failedMethod.getErrorMessage());

        TestMethodResult errorMethod = info.getMethodResult("testError");
        assertNotNull(errorMethod);
        assertEquals("error", errorMethod.getStatus());
        assertEquals("java.lang.RuntimeException", errorMethod.getErrorType());

        TestMethodResult skippedMethod = info.getMethodResult("testSkipped");
        assertNotNull(skippedMethod);
        assertEquals("skipped", skippedMethod.getStatus());
    }

    // Helper methods

    private Path createValidSurefireReport() throws IOException {
        Path reportFile = tempDir.resolve("TEST-com.example.BasicCalculatorTest.xml");
        String content = """
            <?xml version="1.0" encoding="UTF-8"?>
            <testsuite xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xsi:noNamespaceSchemaLocation="https://maven.apache.org/surefire/maven-surefire-plugin/xsd/surefire-test-report.xsd"
                       name="com.example.BasicCalculatorTest" time="0.123" tests="5" errors="0" skipped="0" failures="1">
              <properties/>
              <testcase classname="com.example.BasicCalculatorTest" name="testPositiveAddition" time="0.025"/>
              <testcase classname="com.example.BasicCalculatorTest" name="testNegativeAddition" time="0.018"/>
              <testcase classname="com.example.BasicCalculatorTest" name="testZeroAddition" time="0.015"/>
              <testcase classname="com.example.BasicCalculatorTest" name="testMultiplication" time="0.020"/>
              <testcase classname="com.example.BasicCalculatorTest" name="testDivisionByZero" time="0.045">
                <failure message="Division by zero should throw exception" type="java.lang.AssertionError">
                  java.lang.AssertionError: Division by zero should throw exception
                  at com.example.BasicCalculatorTest.testDivisionByZero(BasicCalculatorTest.java:45)
                </failure>
              </testcase>
            </testsuite>
            """;
        Files.writeString(reportFile, content);
        return reportFile;
    }

    private Path createSecondSurefireReport() throws IOException {
        Path reportFile = tempDir.resolve("TEST-com.example.StringValidatorTest.xml");
        String content = """
            <?xml version="1.0" encoding="UTF-8"?>
            <testsuite name="com.example.StringValidatorTest" time="0.075" tests="3" errors="0" skipped="0" failures="0">
              <testcase classname="com.example.StringValidatorTest" name="testValidEmail" time="0.025"/>
              <testcase classname="com.example.StringValidatorTest" name="testInvalidEmail" time="0.025"/>
              <testcase classname="com.example.StringValidatorTest" name="testEmptyString" time="0.025"/>
            </testsuite>
            """;
        Files.writeString(reportFile, content);
        return reportFile;
    }

    private Path createComplexSurefireReport() throws IOException {
        Path reportFile = tempDir.resolve("TEST-com.example.ComplexTest.xml");
        String content = """
            <?xml version="1.0" encoding="UTF-8"?>
            <testsuite name="com.example.ComplexTest" time="0.200" tests="6" errors="1" skipped="1" failures="1">
              <testcase classname="com.example.ComplexTest" name="testSuccess" time="0.025"/>
              <testcase classname="com.example.ComplexTest" name="testSuccess2" time="0.020"/>
              <testcase classname="com.example.ComplexTest" name="testSuccess3" time="0.030"/>
              <testcase classname="com.example.ComplexTest" name="testFailure" time="0.040">
                <failure message="Test failed deliberately" type="java.lang.AssertionError">
                  java.lang.AssertionError: Test failed deliberately
                </failure>
              </testcase>
              <testcase classname="com.example.ComplexTest" name="testError" time="0.050">
                <error message="Unexpected error occurred" type="java.lang.RuntimeException">
                  java.lang.RuntimeException: Unexpected error occurred
                </error>
              </testcase>
              <testcase classname="com.example.ComplexTest" name="testSkipped" time="0.000">
                <skipped message="Test was skipped"/>
              </testcase>
            </testsuite>
            """;
        Files.writeString(reportFile, content);
        return reportFile;
    }

    private List<TestCaseInfo> createSampleTestCases() {
        List<TestCaseInfo> testCases = new ArrayList<>();

        TestCaseInfo testCase1 = new TestCaseInfo();
        testCase1.setClassName("BasicCalculatorTest");
        testCase1.setMethodName("testPositiveAddition");
        testCase1.setTestCase("正の数の加算テスト");

        TestCaseInfo testCase2 = new TestCaseInfo();
        testCase2.setClassName("BasicCalculatorTest");
        testCase2.setMethodName("testNegativeAddition");
        testCase2.setTestCase("負の数の加算テスト");

        TestCaseInfo testCase3 = new TestCaseInfo();
        testCase3.setClassName("StringValidatorTest");
        testCase3.setMethodName("testValidEmail");
        testCase3.setTestCase("有効なメールアドレスのテスト");

        testCases.add(testCase1);
        testCases.add(testCase2);
        testCases.add(testCase3);

        return testCases;
    }
}