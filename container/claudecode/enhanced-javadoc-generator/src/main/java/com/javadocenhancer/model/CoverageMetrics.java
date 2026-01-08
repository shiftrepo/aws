package com.javadocenhancer.model;

/**
 * カバレッジメトリクス情報クラス
 *
 * JaCoCoレポートから抽出されたカバレッジ情報を保持し、
 * 拡張JavaDoc生成で使用されるカバレッジデータを管理します。
 */
public class CoverageMetrics {

    // 基本識別情報
    private String className;           // クラス名
    private String methodName;          // メソッド名
    private String packageName;         // パッケージ名
    private String sourceFile;          // ソースファイル名

    // カバレッジメトリクス
    private int branchesCovered = 0;    // カバーされたブランチ数
    private int branchesTotal = 0;      // 総ブランチ数
    private int linesCovered = 0;       // カバーされた行数
    private int linesTotal = 0;         // 総行数
    private int instructionsCovered = 0; // カバーされた命令数
    private int instructionsTotal = 0;   // 総命令数
    private int methodsCovered = 0;      // カバーされたメソッド数（通常1または0）
    private int methodsTotal = 1;        // 総メソッド数（通常1）

    // メタ情報
    private String reportType = "XML";   // レポートタイプ（XML/HTML）
    private long extractedTime = System.currentTimeMillis(); // 抽出時刻

    /**
     * デフォルトコンストラクタ
     */
    public CoverageMetrics() {
    }

    /**
     * 基本情報付きコンストラクタ
     *
     * @param className クラス名
     * @param methodName メソッド名
     */
    public CoverageMetrics(String className, String methodName) {
        this.className = className;
        this.methodName = methodName;
    }

    /**
     * ブランチカバレッジ率を計算
     *
     * @return ブランチカバレッジ率（0.0-100.0）
     */
    public double getBranchCoverage() {
        if (branchesTotal == 0) {
            return 0.0;
        }
        return (double) branchesCovered / branchesTotal * 100.0;
    }

    /**
     * 行カバレッジ率を計算
     *
     * @return 行カバレッジ率（0.0-100.0）
     */
    public double getLineCoverage() {
        if (linesTotal == 0) {
            return 0.0;
        }
        return (double) linesCovered / linesTotal * 100.0;
    }

    /**
     * 命令カバレッジ率を計算
     *
     * @return 命令カバレッジ率（0.0-100.0）
     */
    public double getInstructionCoverage() {
        if (instructionsTotal == 0) {
            return 0.0;
        }
        return (double) instructionsCovered / instructionsTotal * 100.0;
    }

    /**
     * メソッドカバレッジ率を計算
     *
     * @return メソッドカバレッジ率（0.0-100.0）
     */
    public double getMethodCoverage() {
        if (methodsTotal == 0) {
            return 0.0;
        }
        return (double) methodsCovered / methodsTotal * 100.0;
    }

    /**
     * 総合カバレッジ率を計算（ブランチとラインの平均）
     *
     * @return 総合カバレッジ率（0.0-100.0）
     */
    public double getOverallCoverage() {
        double branchCov = getBranchCoverage();
        double lineCov = getLineCoverage();

        if (branchesTotal == 0 && linesTotal == 0) {
            return 0.0;
        } else if (branchesTotal == 0) {
            return lineCov;
        } else if (linesTotal == 0) {
            return branchCov;
        } else {
            return (branchCov + lineCov) / 2.0;
        }
    }

    /**
     * カバレッジレベルを取得
     *
     * @param highThreshold 高カバレッジ閾値
     * @param mediumThreshold 中カバレッジ閾値
     * @return カバレッジレベル（HIGH, MEDIUM, LOW, NONE）
     */
    public CoverageLevel getCoverageLevel(double highThreshold, double mediumThreshold) {
        double overall = getOverallCoverage();

        if (overall == 0.0) {
            return CoverageLevel.NONE;
        } else if (overall >= highThreshold) {
            return CoverageLevel.HIGH;
        } else if (overall >= mediumThreshold) {
            return CoverageLevel.MEDIUM;
        } else {
            return CoverageLevel.LOW;
        }
    }

    /**
     * カバレッジ表示用文字列（ブランチ）
     *
     * @return "カバー数/総数 (率%)" 形式
     */
    public String getBranchCoverageDisplay() {
        if (branchesTotal == 0) {
            return "0/0 (0.0%)";
        }
        return String.format("%d/%d (%.1f%%)", branchesCovered, branchesTotal, getBranchCoverage());
    }

    /**
     * カバレッジ表示用文字列（行）
     *
     * @return "カバー数/総数 (率%)" 形式
     */
    public String getLineCoverageDisplay() {
        if (linesTotal == 0) {
            return "0/0 (0.0%)";
        }
        return String.format("%d/%d (%.1f%%)", linesCovered, linesTotal, getLineCoverage());
    }

    /**
     * 簡潔なカバレッジサマリー文字列
     *
     * @return "ブランチ: X% | 行: Y%" 形式
     */
    public String getCoverageSummary() {
        return String.format("ブランチ: %.1f%% | 行: %.1f%%", getBranchCoverage(), getLineCoverage());
    }

    /**
     * ブランチ情報の設定
     */
    public void setBranchInfo(int covered, int total) {
        this.branchesCovered = Math.max(0, covered);
        this.branchesTotal = Math.max(0, total);
    }

    /**
     * 行情報の設定
     */
    public void setLineInfo(int covered, int total) {
        this.linesCovered = Math.max(0, covered);
        this.linesTotal = Math.max(0, total);
    }

    /**
     * 命令情報の設定
     */
    public void setInstructionInfo(int covered, int total) {
        this.instructionsCovered = Math.max(0, covered);
        this.instructionsTotal = Math.max(0, total);
    }

    /**
     * メソッド情報の設定
     */
    public void setMethodInfo(int covered, int total) {
        this.methodsCovered = Math.max(0, covered);
        this.methodsTotal = Math.max(1, total); // メソッド総数は最低1
    }

    /**
     * カバレッジレベル列挙型
     */
    public enum CoverageLevel {
        HIGH("high", "高カバレッジ", "#d4edda"),
        MEDIUM("medium", "中カバレッジ", "#fff3cd"),
        LOW("low", "低カバレッジ", "#f8d7da"),
        NONE("none", "未カバー", "#f8f9fa");

        private final String cssClass;
        private final String displayName;
        private final String color;

        CoverageLevel(String cssClass, String displayName, String color) {
            this.cssClass = cssClass;
            this.displayName = displayName;
            this.color = color;
        }

        public String getCssClass() {
            return cssClass;
        }

        public String getDisplayName() {
            return displayName;
        }

        public String getColor() {
            return color;
        }
    }

    // Getter methods
    public String getClassName() {
        return className;
    }

    public String getMethodName() {
        return methodName;
    }

    public String getPackageName() {
        return packageName;
    }

    public String getSourceFile() {
        return sourceFile;
    }

    public int getBranchesCovered() {
        return branchesCovered;
    }

    public int getBranchesTotal() {
        return branchesTotal;
    }

    public int getLinesCovered() {
        return linesCovered;
    }

    public int getLinesTotal() {
        return linesTotal;
    }

    public int getInstructionsCovered() {
        return instructionsCovered;
    }

    public int getInstructionsTotal() {
        return instructionsTotal;
    }

    public int getMethodsCovered() {
        return methodsCovered;
    }

    public int getMethodsTotal() {
        return methodsTotal;
    }

    public String getReportType() {
        return reportType;
    }

    public long getExtractedTime() {
        return extractedTime;
    }

    // Setter methods
    public void setClassName(String className) {
        this.className = className;
    }

    public void setMethodName(String methodName) {
        this.methodName = methodName;
    }

    public void setPackageName(String packageName) {
        this.packageName = packageName;
    }

    public void setSourceFile(String sourceFile) {
        this.sourceFile = sourceFile;
    }

    public void setReportType(String reportType) {
        this.reportType = reportType;
    }

    public void setExtractedTime(long extractedTime) {
        this.extractedTime = extractedTime;
    }

    @Override
    public String toString() {
        return "CoverageMetrics{" +
                "className='" + className + '\'' +
                ", methodName='" + methodName + '\'' +
                ", packageName='" + packageName + '\'' +
                ", branchCoverage=" + String.format("%.1f%%", getBranchCoverage()) +
                ", lineCoverage=" + String.format("%.1f%%", getLineCoverage()) +
                ", overallCoverage=" + String.format("%.1f%%", getOverallCoverage()) +
                '}';
    }
}