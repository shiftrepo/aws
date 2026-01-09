package com.testspecgenerator.model;

import java.util.Objects;

/**
 * カバレッジ情報を格納するデータクラス
 */
public class CoverageInfo {

    private String className;
    private String methodName;
    private String packageName;

    // カバレッジメトリクス
    private int instructionsCovered = 0;
    private int instructionsTotal = 0;
    private int branchesCovered = 0;
    private int branchesTotal = 0;
    private int linesCovered = 0;
    private int linesTotal = 0;
    private int methodsCovered = 0;
    private int methodsTotal = 0;

    // 計算されたパーセンテージ
    private double instructionCoverage = 0.0;
    private double branchCoverage = 0.0;
    private double lineCoverage = 0.0;
    private double methodCoverage = 0.0;

    // メタデータ
    private String sourceFile;
    private String reportType; // "XML" or "HTML"

    // JaCoCoの詳細情報
    private int complexityCovered = 0;
    private int complexityTotal = 0;
    private double complexityCoverage = 0.0;
    private String sessionId;
    private String executionTime;
    private String jacocoVersion;

    // 生データ（将来の拡張用）
    private String rawXmlData;
    private String rawHtmlData;

    // デフォルトコンストラクタ
    public CoverageInfo() {
    }

    // 基本情報コンストラクタ
    public CoverageInfo(String className, String methodName) {
        this.className = className;
        this.methodName = methodName;
    }

    // Getter/Setter メソッド

    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }

    public String getMethodName() { return methodName; }
    public void setMethodName(String methodName) { this.methodName = methodName; }

    public String getPackageName() { return packageName; }
    public void setPackageName(String packageName) { this.packageName = packageName; }

    public int getInstructionsCovered() { return instructionsCovered; }
    public void setInstructionsCovered(int instructionsCovered) {
        this.instructionsCovered = instructionsCovered;
        updateInstructionCoverage();
    }

    public int getInstructionsTotal() { return instructionsTotal; }
    public void setInstructionsTotal(int instructionsTotal) {
        this.instructionsTotal = instructionsTotal;
        updateInstructionCoverage();
    }

    public int getBranchesCovered() { return branchesCovered; }
    public void setBranchesCovered(int branchesCovered) {
        this.branchesCovered = branchesCovered;
        updateBranchCoverage();
    }

    public int getBranchesTotal() { return branchesTotal; }
    public void setBranchesTotal(int branchesTotal) {
        this.branchesTotal = branchesTotal;
        updateBranchCoverage();
    }

    public int getLinesCovered() { return linesCovered; }
    public void setLinesCovered(int linesCovered) {
        this.linesCovered = linesCovered;
        updateLineCoverage();
    }

    public int getLinesTotal() { return linesTotal; }
    public void setLinesTotal(int linesTotal) {
        this.linesTotal = linesTotal;
        updateLineCoverage();
    }

    public int getMethodsCovered() { return methodsCovered; }
    public void setMethodsCovered(int methodsCovered) {
        this.methodsCovered = methodsCovered;
        updateMethodCoverage();
    }

    public int getMethodsTotal() { return methodsTotal; }
    public void setMethodsTotal(int methodsTotal) {
        this.methodsTotal = methodsTotal;
        updateMethodCoverage();
    }

    public double getInstructionCoverage() { return instructionCoverage; }
    public double getBranchCoverage() { return branchCoverage; }
    public double getLineCoverage() { return lineCoverage; }
    public double getMethodCoverage() { return methodCoverage; }

    public String getSourceFile() { return sourceFile; }
    public void setSourceFile(String sourceFile) { this.sourceFile = sourceFile; }

    public String getReportType() { return reportType; }
    public void setReportType(String reportType) { this.reportType = reportType; }

    public int getComplexityCovered() { return complexityCovered; }
    public void setComplexityCovered(int complexityCovered) {
        this.complexityCovered = complexityCovered;
        updateComplexityCoverage();
    }

    public int getComplexityTotal() { return complexityTotal; }
    public void setComplexityTotal(int complexityTotal) {
        this.complexityTotal = complexityTotal;
        updateComplexityCoverage();
    }

    public double getComplexityCoverage() { return complexityCoverage; }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getExecutionTime() { return executionTime; }
    public void setExecutionTime(String executionTime) { this.executionTime = executionTime; }

    public String getJacocoVersion() { return jacocoVersion; }
    public void setJacocoVersion(String jacocoVersion) { this.jacocoVersion = jacocoVersion; }

    public String getRawXmlData() { return rawXmlData; }
    public void setRawXmlData(String rawXmlData) { this.rawXmlData = rawXmlData; }

    public String getRawHtmlData() { return rawHtmlData; }
    public void setRawHtmlData(String rawHtmlData) { this.rawHtmlData = rawHtmlData; }

    // ヘルパーメソッド

    /**
     * 命令カバレッジ情報を設定
     */
    public void setInstructionInfo(int covered, int total) {
        this.instructionsCovered = covered;
        this.instructionsTotal = total;
        updateInstructionCoverage();
    }

    /**
     * ブランチカバレッジ情報を設定
     */
    public void setBranchInfo(int covered, int total) {
        this.branchesCovered = covered;
        this.branchesTotal = total;
        updateBranchCoverage();
    }

    /**
     * ラインカバレッジ情報を設定
     */
    public void setLineInfo(int covered, int total) {
        this.linesCovered = covered;
        this.linesTotal = total;
        updateLineCoverage();
    }

    /**
     * メソッドカバレッジ情報を設定
     */
    public void setMethodInfo(int covered, int total) {
        this.methodsCovered = covered;
        this.methodsTotal = total;
        updateMethodCoverage();
    }

    /**
     * 複雑度カバレッジ情報を設定
     */
    public void setComplexityInfo(int covered, int total) {
        this.complexityCovered = covered;
        this.complexityTotal = total;
        updateComplexityCoverage();
    }

    // カバレッジ計算メソッド

    private void updateInstructionCoverage() {
        this.instructionCoverage = calculateCoverage(instructionsCovered, instructionsTotal);
    }

    private void updateBranchCoverage() {
        this.branchCoverage = calculateCoverage(branchesCovered, branchesTotal);
    }

    private void updateLineCoverage() {
        this.lineCoverage = calculateCoverage(linesCovered, linesTotal);
    }

    private void updateMethodCoverage() {
        this.methodCoverage = calculateCoverage(methodsCovered, methodsTotal);
    }

    private void updateComplexityCoverage() {
        this.complexityCoverage = calculateCoverage(complexityCovered, complexityTotal);
    }

    private double calculateCoverage(int covered, int total) {
        if (total > 0) {
            return (double) covered / total * 100.0;
        }
        return 0.0;
    }

    // 表示用メソッド

    /**
     * 完全修飾メソッド名を取得
     */
    public String getFullMethodName() {
        if (packageName != null && !packageName.isEmpty()) {
            return packageName + "." + className + "." + methodName;
        } else {
            return className + "." + methodName;
        }
    }

    /**
     * ブランチカバレッジの表示文字列を取得
     */
    public String getBranchCoverageDisplay() {
        if (branchesTotal > 0) {
            return String.format("%.1f%% (%d/%d)", branchCoverage, branchesCovered, branchesTotal);
        } else {
            return "0.0%";
        }
    }

    /**
     * 命令カバレッジの表示文字列を取得
     */
    public String getInstructionCoverageDisplay() {
        if (instructionsTotal > 0) {
            return String.format("%.1f%% (%d/%d)", instructionCoverage, instructionsCovered, instructionsTotal);
        } else {
            return "0.0%";
        }
    }

    /**
     * ラインカバレッジの表示文字列を取得
     */
    public String getLineCoverageDisplay() {
        if (linesTotal > 0) {
            return String.format("%.1f%% (%d/%d)", lineCoverage, linesCovered, linesTotal);
        } else {
            return "0.0%";
        }
    }

    /**
     * カバレッジステータスを取得
     */
    public String getCoverageStatus() {
        double coverage = Math.max(Math.max(branchCoverage, instructionCoverage), lineCoverage);

        if (coverage >= 95.0) {
            return "Excellent";
        } else if (coverage >= 80.0) {
            return "Good";
        } else if (coverage >= 60.0) {
            return "Fair";
        } else if (coverage > 0.0) {
            return "Poor";
        } else {
            return "No Coverage";
        }
    }

    /**
     * プライマリカバレッジメトリック（C1カバレッジ＝ブランチカバレッジ）を取得
     */
    public double getPrimaryCoverage() {
        // C1カバレッジ（条件判定カバレッジ）として、ブランチカバレッジを使用
        return branchCoverage;
    }

    // equals, hashCode, toString

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CoverageInfo that = (CoverageInfo) o;
        return Objects.equals(className, that.className) &&
               Objects.equals(methodName, that.methodName) &&
               Objects.equals(packageName, that.packageName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(className, methodName, packageName);
    }

    @Override
    public String toString() {
        return String.format("CoverageInfo{className='%s', methodName='%s', branchCoverage=%.1f%%, " +
                "instructionCoverage=%.1f%%, reportType='%s'}",
                className, methodName, branchCoverage, instructionCoverage, reportType);
    }
}