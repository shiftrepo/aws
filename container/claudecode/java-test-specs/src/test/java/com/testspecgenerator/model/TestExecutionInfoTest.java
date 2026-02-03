package com.testspecgenerator.model;

import com.testspecgenerator.model.TestExecutionInfo.TestMethodResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * @ソフトウェア・サービス Test Execution Info Service
 * @項目名 TestExecutionInfo単体テスト
 * @試験内容 テスト実行情報モデルクラスをテストする
 * @確認項目 正しく統計情報が計算・管理されること
 * @テスト対象モジュール名 TestExecutionInfo
 * @テスト実施ベースラインバージョン 1.0.0
 * @テストケース作成者 TestTeam
 * @テストケース作成日 2026-02-03
 * @テストケース修正者 TestTeam
 * @テストケース修正日 2026-02-03
 */
class TestExecutionInfoTest {

    private TestExecutionInfo testExecutionInfo;

    @BeforeEach
    void setUp() {
        testExecutionInfo = new TestExecutionInfo();
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 デフォルトコンストラクタのテスト
     * @試験内容 デフォルトコンストラクタで正しく初期化される
     * @確認項目 初期値が適切に設定されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testDefaultConstructor() {
        // Verify
        assertNotNull(testExecutionInfo.getMethodResults());
        assertTrue(testExecutionInfo.getMethodResults().isEmpty());
        assertNull(testExecutionInfo.getClassName());
        assertNull(testExecutionInfo.getTestSuite());
        assertEquals(0, testExecutionInfo.getTotalTests());
        assertEquals(0, testExecutionInfo.getPassedTests());
        assertEquals(0, testExecutionInfo.getFailedTests());
        assertEquals(0, testExecutionInfo.getSkippedTests());
        assertEquals(0, testExecutionInfo.getErrorTests());
        assertEquals(0.0, testExecutionInfo.getExecutionTime(), 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 パラメータありコンストラクタのテスト
     * @試験内容 パラメータありコンストラクタで正しく初期化される
     * @確認項目 指定した値が正しく設定されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testParameterizedConstructor() {
        // Execute
        TestExecutionInfo info = new TestExecutionInfo("com.example.TestClass", "TestSuite");

        // Verify
        assertEquals("com.example.TestClass", info.getClassName());
        assertEquals("TestSuite", info.getTestSuite());
        assertNotNull(info.getMethodResults());
        assertTrue(info.getMethodResults().isEmpty());
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 成功率計算のテスト（正常ケース）
     * @試験内容 総テスト数と成功テスト数から成功率を計算する
     * @確認項目 正しい成功率が計算されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetSuccessRateNormalCase() {
        // Setup
        testExecutionInfo.setTotalTests(10);
        testExecutionInfo.setPassedTests(8);

        // Execute
        double successRate = testExecutionInfo.getSuccessRate();

        // Verify
        assertEquals(80.0, successRate, 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 成功率計算のテスト（ゼロ除算ケース）
     * @試験内容 総テスト数が0の場合の成功率計算
     * @確認項目 0が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetSuccessRateZeroDivision() {
        // Setup
        testExecutionInfo.setTotalTests(0);
        testExecutionInfo.setPassedTests(0);

        // Execute
        double successRate = testExecutionInfo.getSuccessRate();

        // Verify
        assertEquals(0.0, successRate, 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 成功率計算のテスト（完全成功ケース）
     * @試験内容 全てのテストが成功した場合の成功率計算
     * @確認項目 100%が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetSuccessRatePerfectCase() {
        // Setup
        testExecutionInfo.setTotalTests(5);
        testExecutionInfo.setPassedTests(5);

        // Execute
        double successRate = testExecutionInfo.getSuccessRate();

        // Verify
        assertEquals(100.0, successRate, 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 テスト実行結果表示文字列のテスト
     * @試験内容 テスト実行結果の表示文字列を取得する
     * @確認項目 正しいフォーマットで返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetTestExecutionDisplay() {
        // Setup
        testExecutionInfo.setTotalTests(10);
        testExecutionInfo.setPassedTests(7);

        // Execute
        String display = testExecutionInfo.getTestExecutionDisplay();

        // Verify
        assertEquals("7/10", display);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 成功率表示文字列のテスト
     * @試験内容 成功率の表示文字列を取得する
     * @確認項目 正しいフォーマットで返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetSuccessRateDisplay() {
        // Setup
        testExecutionInfo.setTotalTests(8);
        testExecutionInfo.setPassedTests(6);

        // Execute
        String display = testExecutionInfo.getSuccessRateDisplay();

        // Verify
        assertEquals("75.0%", display);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 実行ステータス取得のテスト（全て成功）
     * @試験内容 全てのテストが成功した場合のステータス
     * @確認項目 "All Passed"が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetExecutionStatusAllPassed() {
        // Setup
        testExecutionInfo.setTotalTests(5);
        testExecutionInfo.setPassedTests(5);

        // Execute
        String status = testExecutionInfo.getExecutionStatus();

        // Verify
        assertEquals("All Passed", status);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 実行ステータス取得のテスト（全て失敗）
     * @試験内容 全てのテストが失敗した場合のステータス
     * @確認項目 "All Failed"が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetExecutionStatusAllFailed() {
        // Setup
        testExecutionInfo.setTotalTests(3);
        testExecutionInfo.setPassedTests(0);

        // Execute
        String status = testExecutionInfo.getExecutionStatus();

        // Verify
        assertEquals("All Failed", status);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 実行ステータス取得のテスト（部分成功）
     * @試験内容 一部のテストが成功した場合のステータス
     * @確認項目 "Partial"が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetExecutionStatusPartial() {
        // Setup
        testExecutionInfo.setTotalTests(10);
        testExecutionInfo.setPassedTests(7);

        // Execute
        String status = testExecutionInfo.getExecutionStatus();

        // Verify
        assertEquals("Partial", status);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 実行ステータス取得のテスト（未知）
     * @試験内容 総テスト数が0の場合のステータス
     * @確認項目 "Unknown"が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetExecutionStatusUnknown() {
        // Setup
        testExecutionInfo.setTotalTests(0);
        testExecutionInfo.setPassedTests(0);

        // Execute
        String status = testExecutionInfo.getExecutionStatus();

        // Verify
        assertEquals("Unknown", status);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 メソッド結果追加・取得のテスト
     * @試験内容 テストメソッドの結果を追加・取得する
     * @確認項目 正しく追加・取得できること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testAddAndGetMethodResult() {
        // Setup
        TestMethodResult result = new TestMethodResult("testMethod", "passed", 0.123);

        // Execute
        testExecutionInfo.addMethodResult("testMethod", result);
        TestMethodResult retrieved = testExecutionInfo.getMethodResult("testMethod");

        // Verify
        assertNotNull(retrieved);
        assertEquals("testMethod", retrieved.getMethodName());
        assertEquals("passed", retrieved.getStatus());
        assertEquals(0.123, retrieved.getTime(), 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 存在しないメソッド結果取得のテスト
     * @試験内容 存在しないメソッド名で結果を取得する
     * @確認項目 nullが返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testGetNonExistentMethodResult() {
        // Execute
        TestMethodResult result = testExecutionInfo.getMethodResult("nonExistentMethod");

        // Verify
        assertNull(result);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 メソッド結果セッター・ゲッターのテスト
     * @試験内容 メソッド結果Mapを直接設定・取得する
     * @確認項目 正しく設定・取得できること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testSetGetMethodResults() {
        // Setup
        Map<String, TestMethodResult> results = new HashMap<>();
        results.put("test1", new TestMethodResult("test1", "passed", 0.1));
        results.put("test2", new TestMethodResult("test2", "failed", 0.2));

        // Execute
        testExecutionInfo.setMethodResults(results);
        Map<String, TestMethodResult> retrieved = testExecutionInfo.getMethodResults();

        // Verify
        assertEquals(2, retrieved.size());
        assertTrue(retrieved.containsKey("test1"));
        assertTrue(retrieved.containsKey("test2"));
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 全フィールドセッター・ゲッターのテスト
     * @試験内容 全てのフィールドのセッター・ゲッターをテストする
     * @確認項目 正しく値が設定・取得できること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testAllSettersAndGetters() {
        // Execute & Verify
        testExecutionInfo.setClassName("TestClass");
        assertEquals("TestClass", testExecutionInfo.getClassName());

        testExecutionInfo.setTestSuite("TestSuite");
        assertEquals("TestSuite", testExecutionInfo.getTestSuite());

        testExecutionInfo.setTotalTests(100);
        assertEquals(100, testExecutionInfo.getTotalTests());

        testExecutionInfo.setPassedTests(80);
        assertEquals(80, testExecutionInfo.getPassedTests());

        testExecutionInfo.setFailedTests(15);
        assertEquals(15, testExecutionInfo.getFailedTests());

        testExecutionInfo.setSkippedTests(3);
        assertEquals(3, testExecutionInfo.getSkippedTests());

        testExecutionInfo.setErrorTests(2);
        assertEquals(2, testExecutionInfo.getErrorTests());

        testExecutionInfo.setExecutionTime(5.67);
        assertEquals(5.67, testExecutionInfo.getExecutionTime(), 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 toString()メソッドのテスト
     * @試験内容 toString()メソッドの動作を確認する
     * @確認項目 適切な文字列が返されること
     * @テスト対象モジュール名 TestExecutionInfo
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testToString() {
        // Setup
        testExecutionInfo.setClassName("com.example.TestClass");
        testExecutionInfo.setTotalTests(10);
        testExecutionInfo.setPassedTests(8);
        testExecutionInfo.setFailedTests(1);
        testExecutionInfo.setSkippedTests(1);
        testExecutionInfo.setErrorTests(0);
        testExecutionInfo.setExecutionTime(2.345);

        // Execute
        String toString = testExecutionInfo.toString();

        // Verify
        assertTrue(toString.contains("TestExecutionInfo"));
        assertTrue(toString.contains("com.example.TestClass"));
        assertTrue(toString.contains("tests=10"));
        assertTrue(toString.contains("passed=8"));
        assertTrue(toString.contains("failed=1"));
        assertTrue(toString.contains("skipped=1"));
        assertTrue(toString.contains("errors=0"));
        assertTrue(toString.contains("time=2.345"));
    }

    // TestMethodResult内部クラスのテスト

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 TestMethodResultのデフォルトコンストラクタテスト
     * @試験内容 TestMethodResultのデフォルトコンストラクタ
     * @確認項目 初期値が適切に設定されること
     * @テスト対象モジュール名 TestExecutionInfo.TestMethodResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testTestMethodResultDefaultConstructor() {
        // Execute
        TestMethodResult result = new TestMethodResult();

        // Verify
        assertEquals("unknown", result.getStatus());
        assertNull(result.getMethodName());
        assertEquals(0.0, result.getTime(), 0.001);
        assertNull(result.getErrorMessage());
        assertNull(result.getErrorType());
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 TestMethodResultのパラメータありコンストラクタテスト
     * @試験内容 TestMethodResultのパラメータありコンストラクタ
     * @確認項目 指定した値が正しく設定されること
     * @テスト対象モジュール名 TestExecutionInfo.TestMethodResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testTestMethodResultParameterizedConstructor() {
        // Execute
        TestMethodResult result = new TestMethodResult("testMethod", "passed", 1.23);

        // Verify
        assertEquals("testMethod", result.getMethodName());
        assertEquals("passed", result.getStatus());
        assertEquals(1.23, result.getTime(), 0.001);
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 TestMethodResultの状態判定メソッドテスト
     * @試験内容 isPassed, isFailed, isSkipped, isErrorメソッドのテスト
     * @確認項目 正しく状態が判定されること
     * @テスト対象モジュール名 TestExecutionInfo.TestMethodResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testTestMethodResultStatusMethods() {
        // Passed状態のテスト
        TestMethodResult passedResult = new TestMethodResult("test", "passed", 0.1);
        assertTrue(passedResult.isPassed());
        assertFalse(passedResult.isFailed());
        assertFalse(passedResult.isSkipped());
        assertFalse(passedResult.isError());

        // Failed状態のテスト
        TestMethodResult failedResult = new TestMethodResult("test", "failed", 0.1);
        assertFalse(failedResult.isPassed());
        assertTrue(failedResult.isFailed());
        assertFalse(failedResult.isSkipped());
        assertFalse(failedResult.isError());

        // Skipped状態のテスト
        TestMethodResult skippedResult = new TestMethodResult("test", "skipped", 0.1);
        assertFalse(skippedResult.isPassed());
        assertFalse(skippedResult.isFailed());
        assertTrue(skippedResult.isSkipped());
        assertFalse(skippedResult.isError());

        // Error状態のテスト
        TestMethodResult errorResult = new TestMethodResult("test", "error", 0.1);
        assertFalse(errorResult.isPassed());
        assertFalse(errorResult.isFailed());
        assertFalse(errorResult.isSkipped());
        assertTrue(errorResult.isError());
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 TestMethodResultの全セッター・ゲッターテスト
     * @試験内容 TestMethodResultの全フィールドのセッター・ゲッター
     * @確認項目 正しく値が設定・取得できること
     * @テスト対象モジュール名 TestExecutionInfo.TestMethodResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testTestMethodResultAllSettersAndGetters() {
        // Setup
        TestMethodResult result = new TestMethodResult();

        // Execute & Verify
        result.setMethodName("testMethodName");
        assertEquals("testMethodName", result.getMethodName());

        result.setStatus("failed");
        assertEquals("failed", result.getStatus());

        result.setTime(2.567);
        assertEquals(2.567, result.getTime(), 0.001);

        result.setErrorMessage("Test failed with assertion error");
        assertEquals("Test failed with assertion error", result.getErrorMessage());

        result.setErrorType("java.lang.AssertionError");
        assertEquals("java.lang.AssertionError", result.getErrorType());
    }

    /**
     * @ソフトウェア・サービス Test Execution Info Service
     * @項目名 TestMethodResultのtoString()メソッドテスト
     * @試験内容 TestMethodResultのtoString()メソッド
     * @確認項目 適切な文字列が返されること
     * @テスト対象モジュール名 TestExecutionInfo.TestMethodResult
     * @テスト実施ベースラインバージョン 1.0.0
     * @テストケース作成者 TestTeam
     * @テストケース作成日 2026-02-03
     * @テストケース修正者 TestTeam
     * @テストケース修正日 2026-02-03
     */
    @Test
    void testTestMethodResultToString() {
        // Setup
        TestMethodResult result = new TestMethodResult("testMethod", "passed", 1.234);

        // Execute
        String toString = result.toString();

        // Verify
        assertTrue(toString.contains("TestMethodResult"));
        assertTrue(toString.contains("method='testMethod'"));
        assertTrue(toString.contains("status='passed'"));
        assertTrue(toString.contains("time=1.234"));
    }
}