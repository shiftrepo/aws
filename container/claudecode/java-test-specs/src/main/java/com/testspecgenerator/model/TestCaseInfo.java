package com.testspecgenerator.model;

import java.time.LocalDateTime;
import java.util.Objects;

/**
 * テストケース情報を格納するデータクラス
 */
public class TestCaseInfo {

    // ファイル情報
    private String filePath;
    private String className;
    private String methodName;

    // アノテーション情報
    private String testModule = "Not Specified";
    private String testCase = "Not Specified";
    private String baselineVersion = "Not Specified";
    private String testOverview = "Not Specified";
    private String testPurpose = "Not Specified";
    private String testProcess = "Not Specified";
    private String testResults = "Not Specified";
    private String creator = "Not Specified";
    private String createdDate = "Not Specified";
    private String modifier = "Not Specified";
    private String modifiedDate = "Not Specified";
    private String testCategory = "Not Specified";
    private String priority = "Not Specified";
    private String requirements = "Not Specified";
    private String dependencies = "Not Specified";

    // カバレッジ情報
    private double coveragePercent = 0.0;
    private int branchesCovered = 0;
    private int branchesTotal = 0;
    private String coverageStatus = "Unknown";

    // テスト実行結果情報
    private int testsTotal = 0;
    private int testsPassed = 0;
    private String testExecutionStatus = "Unknown";
    private double testSuccessRate = 0.0;

    // メタデータ
    private LocalDateTime extractedAt;
    private String sourceFilePath;

    // デフォルトコンストラクタ
    public TestCaseInfo() {
        this.extractedAt = LocalDateTime.now();
    }

    // 基本情報コンストラクタ
    public TestCaseInfo(String filePath, String className, String methodName) {
        this();
        this.filePath = filePath;
        this.className = className;
        this.methodName = methodName;
        this.sourceFilePath = filePath;
    }

    // Getter/Setter メソッド

    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) { this.filePath = filePath; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getMethodName() { return methodName; }
    public void setMethodName(String methodName) { this.methodName = methodName; }

    public String getTestModule() { return testModule; }
    public void setTestModule(String testModule) { this.testModule = testModule; }

    public String getTestCase() { return testCase; }
    public void setTestCase(String testCase) { this.testCase = testCase; }

    public String getBaselineVersion() { return baselineVersion; }
    public void setBaselineVersion(String baselineVersion) { this.baselineVersion = baselineVersion; }

    public String getTestOverview() { return testOverview; }
    public void setTestOverview(String testOverview) { this.testOverview = testOverview; }

    public String getTestPurpose() { return testPurpose; }
    public void setTestPurpose(String testPurpose) { this.testPurpose = testPurpose; }

    public String getTestProcess() { return testProcess; }
    public void setTestProcess(String testProcess) { this.testProcess = testProcess; }

    public String getTestResults() { return testResults; }
    public void setTestResults(String testResults) { this.testResults = testResults; }

    public String getCreator() { return creator; }
    public void setCreator(String creator) { this.creator = creator; }

    public String getCreatedDate() { return createdDate; }
    public void setCreatedDate(String createdDate) { this.createdDate = createdDate; }

    public String getModifier() { return modifier; }
    public void setModifier(String modifier) { this.modifier = modifier; }

    public String getModifiedDate() { return modifiedDate; }
    public void setModifiedDate(String modifiedDate) { this.modifiedDate = modifiedDate; }

    public String getTestCategory() { return testCategory; }
    public void setTestCategory(String testCategory) { this.testCategory = testCategory; }

    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }

    public String getRequirements() { return requirements; }
    public void setRequirements(String requirements) { this.requirements = requirements; }

    public String getDependencies() { return dependencies; }
    public void setDependencies(String dependencies) { this.dependencies = dependencies; }

    public double getCoveragePercent() { return coveragePercent; }
    public void setCoveragePercent(double coveragePercent) {
        this.coveragePercent = coveragePercent;
        updateCoverageStatus();
    }

    public int getBranchesCovered() { return branchesCovered; }
    public void setBranchesCovered(int branchesCovered) { this.branchesCovered = branchesCovered; }

    public int getBranchesTotal() { return branchesTotal; }
    public void setBranchesTotal(int branchesTotal) { this.branchesTotal = branchesTotal; }

    public String getCoverageStatus() { return coverageStatus; }
    public void setCoverageStatus(String coverageStatus) { this.coverageStatus = coverageStatus; }

    public LocalDateTime getExtractedAt() { return extractedAt; }
    public void setExtractedAt(LocalDateTime extractedAt) { this.extractedAt = extractedAt; }

    public String getSourceFilePath() { return sourceFilePath; }
    public void setSourceFilePath(String sourceFilePath) { this.sourceFilePath = sourceFilePath; }

    public int getTestsTotal() { return testsTotal; }
    public void setTestsTotal(int testsTotal) { this.testsTotal = testsTotal; }

    public int getTestsPassed() { return testsPassed; }
    public void setTestsPassed(int testsPassed) { this.testsPassed = testsPassed; }

    public String getTestExecutionStatus() { return testExecutionStatus; }
    public void setTestExecutionStatus(String testExecutionStatus) { this.testExecutionStatus = testExecutionStatus; }

    public double getTestSuccessRate() { return testSuccessRate; }
    public void setTestSuccessRate(double testSuccessRate) { this.testSuccessRate = testSuccessRate; }

    // ヘルパーメソッド

    /**
     * カバレッジ情報を設定し、ステータスを更新
     */
    public void setCoverageInfo(int covered, int total) {
        this.branchesCovered = covered;
        this.branchesTotal = total;
        if (total > 0) {
            this.coveragePercent = (double) covered / total * 100.0;
        } else {
            this.coveragePercent = 0.0;
        }
        updateCoverageStatus();
    }

    /**
     * カバレッジパーセントに基づいてステータスを更新
     */
    private void updateCoverageStatus() {
        if (coveragePercent >= 95.0) {
            this.coverageStatus = "Excellent";
        } else if (coveragePercent >= 80.0) {
            this.coverageStatus = "Good";
        } else if (coveragePercent >= 60.0) {
            this.coverageStatus = "Fair";
        } else if (coveragePercent > 0.0) {
            this.coverageStatus = "Poor";
        } else {
            this.coverageStatus = "No Coverage";
        }
    }

    /**
     * ブランチカバレッジの表示文字列を取得
     */
    public String getBranchCoverageDisplay() {
        if (branchesTotal > 0) {
            return String.format("%d/%d", branchesCovered, branchesTotal);
        } else {
            return "N/A";
        }
    }

    /**
     * カバレッジパーセントの表示文字列を取得
     */
    public String getCoveragePercentDisplay() {
        if (branchesTotal > 0) {
            return String.format("%.1f%%", coveragePercent);
        } else {
            return "N/A";
        }
    }

    /**
     * 完全修飾メソッド名を取得
     */
    public String getFullMethodName() {
        return className + "." + methodName;
    }

    /**
     * テスト実行結果の表示文字列を取得（例: "8/10"）
     */
    public String getTestExecutionDisplay() {
        if (testsTotal > 0) {
            return String.format("%d/%d", testsPassed, testsTotal);
        } else {
            return "N/A";
        }
    }

    /**
     * テスト成功率の表示文字列を取得（例: "80.0%"）
     */
    public String getTestSuccessRateDisplay() {
        if (testsTotal > 0) {
            return String.format("%.1f%%", testSuccessRate);
        } else {
            return "N/A";
        }
    }

    // equals, hashCode, toString

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        TestCaseInfo that = (TestCaseInfo) o;
        return Objects.equals(filePath, that.filePath) &&
               Objects.equals(className, that.className) &&
               Objects.equals(methodName, that.methodName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(filePath, className, methodName);
    }

    @Override
    public String toString() {
        return String.format("TestCaseInfo{className='%s', methodName='%s', testModule='%s', testCase='%s', coverage=%.1f%%}",
                className, methodName, testModule, testCase, coveragePercent);
    }
}