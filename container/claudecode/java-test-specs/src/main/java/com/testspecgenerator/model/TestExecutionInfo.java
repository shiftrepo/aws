package com.testspecgenerator.model;

import java.util.HashMap;
import java.util.Map;

/**
 * テスト実行結果情報を格納するモデルクラス
 * Maven Surefireレポート（TEST-*.xml）から取得した情報を保持します
 */
public class TestExecutionInfo {

    private String className;
    private String testSuite;
    private int totalTests;
    private int passedTests;
    private int failedTests;
    private int skippedTests;
    private int errorTests;
    private double executionTime;
    private Map<String, TestMethodResult> methodResults;

    /**
     * デフォルトコンストラクタ
     */
    public TestExecutionInfo() {
        this.methodResults = new HashMap<>();
    }

    /**
     * 基本情報コンストラクタ
     */
    public TestExecutionInfo(String className, String testSuite) {
        this();
        this.className = className;
        this.testSuite = testSuite;
    }

    /**
     * テスト成功率を計算
     * @return 成功率（パーセント）
     */
    public double getSuccessRate() {
        if (totalTests == 0) {
            return 0.0;
        }
        return (double) passedTests / totalTests * 100.0;
    }

    /**
     * テスト実行結果の表示文字列を取得（例: "8/10"）
     * @return 実行結果の表示文字列
     */
    public String getTestExecutionDisplay() {
        return String.format("%d/%d", passedTests, totalTests);
    }

    /**
     * テスト成功率の表示文字列を取得（例: "80.0%"）
     * @return 成功率の表示文字列
     */
    public String getSuccessRateDisplay() {
        return String.format("%.1f%%", getSuccessRate());
    }

    /**
     * 全体のテスト実行ステータスを取得
     * @return "All Passed", "Partial", "All Failed", "Unknown"
     */
    public String getExecutionStatus() {
        if (totalTests == 0) {
            return "Unknown";
        } else if (passedTests == totalTests) {
            return "All Passed";
        } else if (passedTests == 0) {
            return "All Failed";
        } else {
            return "Partial";
        }
    }

    /**
     * テストメソッドの結果を追加
     */
    public void addMethodResult(String methodName, TestMethodResult result) {
        methodResults.put(methodName, result);
    }

    /**
     * テストメソッドの結果を取得
     */
    public TestMethodResult getMethodResult(String methodName) {
        return methodResults.get(methodName);
    }

    // Getter/Setter メソッド

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getTestSuite() { return testSuite; }
    public void setTestSuite(String testSuite) { this.testSuite = testSuite; }

    public int getTotalTests() { return totalTests; }
    public void setTotalTests(int totalTests) { this.totalTests = totalTests; }

    public int getPassedTests() { return passedTests; }
    public void setPassedTests(int passedTests) { this.passedTests = passedTests; }

    public int getFailedTests() { return failedTests; }
    public void setFailedTests(int failedTests) { this.failedTests = failedTests; }

    public int getSkippedTests() { return skippedTests; }
    public void setSkippedTests(int skippedTests) { this.skippedTests = skippedTests; }

    public int getErrorTests() { return errorTests; }
    public void setErrorTests(int errorTests) { this.errorTests = errorTests; }

    public double getExecutionTime() { return executionTime; }
    public void setExecutionTime(double executionTime) { this.executionTime = executionTime; }

    public Map<String, TestMethodResult> getMethodResults() { return methodResults; }
    public void setMethodResults(Map<String, TestMethodResult> methodResults) {
        this.methodResults = methodResults;
    }

    /**
     * 個別のテストメソッドの実行結果を表す内部クラス
     */
    public static class TestMethodResult {
        private String methodName;
        private String status; // "passed", "failed", "skipped", "error"
        private double time;
        private String errorMessage;
        private String errorType;

        /**
         * デフォルトコンストラクタ
         */
        public TestMethodResult() {
            this.status = "unknown";
        }

        /**
         * 基本情報コンストラクタ
         */
        public TestMethodResult(String methodName, String status, double time) {
            this.methodName = methodName;
            this.status = status;
            this.time = time;
        }

        /**
         * テストが成功したかどうかを判定
         */
        public boolean isPassed() {
            return "passed".equals(status);
        }

        /**
         * テストが失敗したかどうかを判定
         */
        public boolean isFailed() {
            return "failed".equals(status);
        }

        /**
         * テストがスキップされたかどうかを判定
         */
        public boolean isSkipped() {
            return "skipped".equals(status);
        }

        /**
         * テストがエラーになったかどうかを判定
         */
        public boolean isError() {
            return "error".equals(status);
        }

        // Getter/Setter メソッド

        public String getMethodName() { return methodName; }
        public void setMethodName(String methodName) { this.methodName = methodName; }

        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public double getTime() { return time; }
        public void setTime(double time) { this.time = time; }

        public String getErrorMessage() { return errorMessage; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

        public String getErrorType() { return errorType; }
        public void setErrorType(String errorType) { this.errorType = errorType; }

        @Override
        public String toString() {
            return String.format("TestMethodResult{method='%s', status='%s', time=%.3f}",
                methodName, status, time);
        }
    }

    @Override
    public String toString() {
        return String.format("TestExecutionInfo{class='%s', tests=%d, passed=%d, failed=%d, skipped=%d, errors=%d, time=%.3f}",
            className, totalTests, passedTests, failedTests, skippedTests, errorTests, executionTime);
    }
}