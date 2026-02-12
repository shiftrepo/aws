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
    private String packageName = "未指定";  // パッケージ名

    // アノテーション情報
    private String softwareService = "未指定";  // ソフトウェア・サービス
    private String testItemName = "標準";  // 項目名
    private String testContent = "自動実行";  // 試験内容
    private String confirmationItem = "成功";  // 確認項目
    private String testModule = "General";  // テスト対象モジュール名
    private String baselineVersion = "1.0.0";  // テスト実施ベースラインバージョン
    private String creator = "TestTeam";  // テストケース作成者
    private String createdDate = "2026-01-09";  // テストケース作成日
    private String modifier = "TestTeam";  // テストケース修正者
    private String modifiedDate = "2026-01-09";  // テストケース修正日

    // 旧フィールド（互換性のため残す）
    private String testCase = "Standard";
    private String testOverview = "テスト実行中";
    private String testPurpose = "機能検証";
    private String testProcess = "自動実行";
    private String testResults = "成功";
    private String testCategory = "Unit";
    private String priority = "Medium";
    private String requirements = "基本機能";
    private String dependencies = "なし";

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

    // 新規追加フィールド（19列対応）
    private String testExecutionDate = "";  // テスト実施実績日（カバレッジファイルの作成日）
    private String testResult = "";  // テスト結果（OK/NG）
    private String testExecutor = "CI";  // テスト実施者（固定値）
    private String testVerifier = "";  // テスト検証者（空欄）
    private String handoverRequired = "";  // 申し送り有無（空欄）
    private String handoverTestTiming = "";  // 申し送りテスト実施タイミング（空欄）
    private String handoverTestSchedule = "";  // 申し送りテスト実施時期(予定)（空欄）
    private String remarks = "";  // 備考（空欄）

    // メタデータ
    private LocalDateTime extractedAt;
    private String sourceFilePath;

    // デフォルトコンストラクタ
    public TestCaseInfo() {
        this.extractedAt = LocalDateTime.now();
    }

    // 基本情報コンストラクタ（後方互換性のため残す）
    public TestCaseInfo(String filePath, String className, String methodName) {
        this();
        this.filePath = filePath;
        this.className = className;
        this.methodName = methodName;
        this.sourceFilePath = filePath;
    }

    // 基本情報コンストラクタ（パッケージ名付き）
    public TestCaseInfo(String filePath, String className, String methodName, String packageName) {
        this(filePath, className, methodName);
        this.packageName = packageName != null ? packageName : "未指定";
    }

    // Getter/Setter メソッド

    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) { this.filePath = filePath; }

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getMethodName() { return methodName; }
    public void setMethodName(String methodName) { this.methodName = methodName; }

    public String getPackageName() { return packageName; }
    public void setPackageName(String packageName) { this.packageName = packageName; }

    // 新しい日本語フィールドのGetter/Setter
    public String getSoftwareService() { return softwareService; }
    public void setSoftwareService(String softwareService) { this.softwareService = softwareService; }

    public String getTestItemName() { return testItemName; }
    public void setTestItemName(String testItemName) { this.testItemName = testItemName; }

    public String getTestContent() { return testContent; }
    public void setTestContent(String testContent) { this.testContent = testContent; }

    public String getConfirmationItem() { return confirmationItem; }
    public void setConfirmationItem(String confirmationItem) { this.confirmationItem = confirmationItem; }

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

    // 新規追加フィールドのGetter/Setter（19列対応）
    public String getTestExecutionDate() { return testExecutionDate; }
    public void setTestExecutionDate(String testExecutionDate) { this.testExecutionDate = testExecutionDate; }

    public String getTestResult() { return testResult; }
    public void setTestResult(String testResult) { this.testResult = testResult; }

    public String getTestExecutor() { return testExecutor; }
    public void setTestExecutor(String testExecutor) { this.testExecutor = testExecutor; }

    public String getTestVerifier() { return testVerifier; }
    public void setTestVerifier(String testVerifier) { this.testVerifier = testVerifier; }

    public String getHandoverRequired() { return handoverRequired; }
    public void setHandoverRequired(String handoverRequired) { this.handoverRequired = handoverRequired; }

    public String getHandoverTestTiming() { return handoverTestTiming; }
    public void setHandoverTestTiming(String handoverTestTiming) { this.handoverTestTiming = handoverTestTiming; }

    public String getHandoverTestSchedule() { return handoverTestSchedule; }
    public void setHandoverTestSchedule(String handoverTestSchedule) { this.handoverTestSchedule = handoverTestSchedule; }

    public String getRemarks() { return remarks; }
    public void setRemarks(String remarks) { this.remarks = remarks; }

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
            return "0/0";
        }
    }

    /**
     * カバレッジパーセントの表示文字列を取得
     */
    public String getCoveragePercentDisplay() {
        if (branchesTotal > 0) {
            return String.format("%.1f%%", coveragePercent);
        } else {
            return "0/0";
        }
    }

    /**
     * 完全修飾メソッド名を取得
     */
    public String getFullMethodName() {
        return className + "." + methodName;
    }

    /**
     * 完全修飾クラス名を取得（FQCN: Fully Qualified Class Name）
     * 形式: パッケージ名.クラス名.メソッド名
     */
    public String getFullyQualifiedName() {
        if (packageName != null && !packageName.isEmpty() && !"未指定".equals(packageName)) {
            return packageName + "." + className + "." + methodName;
        } else {
            return "未指定." + className + "." + methodName;
        }
    }

    /**
     * テスト実行結果の表示文字列を取得（例: "8/10"）
     */
    public String getTestExecutionDisplay() {
        if (testsTotal > 0) {
            return String.format("%d/%d", testsPassed, testsTotal);
        } else {
            return "0/0";
        }
    }

    /**
     * テスト成功率の表示文字列を取得（例: "80.0%"）
     */
    public String getTestSuccessRateDisplay() {
        if (testsTotal > 0) {
            return String.format("%.1f%%", testSuccessRate);
        } else {
            return "0/0";
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