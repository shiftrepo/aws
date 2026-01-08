package com.javadocenhancer.model;

import java.nio.file.Path;

/**
 * 拡張JavaDoc生成の設定クラス
 *
 * CLIパラメータやインタラクティブモードで収集された設定を保持し、
 * 生成処理全体で参照される設定オブジェクト。
 */
public class JavaDocEnhancement {

    // 基本ディレクトリ設定
    private Path sourceDirectory;      // ソースディレクトリ（必須）
    private Path testDirectory;        // テストディレクトリ（オプション）
    private Path outputDirectory;      // 出力ディレクトリ（必須）

    // カバレッジ関連設定
    private Path coverageXmlFile;      // JaCoCo XMLファイル（オプション）
    private double highCoverageThreshold = 80.0;    // 高カバレッジ閾値
    private double mediumCoverageThreshold = 50.0;  // 中カバレッジ閾値

    // 機能フラグ
    private boolean includeSourceLinks = false;      // ソースコードリンクを含める
    private boolean generateCoverageCharts = false;  // カバレッジチャート生成
    private boolean skipCoverage = false;            // カバレッジ処理をスキップ

    // カバレッジ統合機能フラグ（ユーザー要件の4つ）
    private boolean enableInlineDisplay = true;      // インライン表示
    private boolean enableVisualHighlight = true;   // 視覚的ハイライト
    private boolean enableDetailedReports = true;   // 詳細レポート
    private boolean enableTestCaseLinks = true;     // テストケースリンク

    // ログ・デバッグ設定
    private String logLevel = "INFO";
    private boolean verboseOutput = false;

    /**
     * デフォルトコンストラクタ
     */
    public JavaDocEnhancement() {
        // デフォルト設定は既に定義済み
    }

    /**
     * 設定の検証を行う
     *
     * @return 検証が成功した場合true
     */
    public boolean isValid() {
        return sourceDirectory != null && outputDirectory != null;
    }

    /**
     * カバレッジ処理が有効かどうか
     *
     * @return カバレッジファイルが指定されており、スキップフラグがfalseの場合true
     */
    public boolean isCoverageEnabled() {
        return coverageXmlFile != null && !skipCoverage;
    }

    /**
     * テストケースリンク機能が有効かどうか
     *
     * @return テストディレクトリが指定されており、機能が有効な場合true
     */
    public boolean isTestLinkingEnabled() {
        return testDirectory != null && enableTestCaseLinks;
    }

    // Getter methods
    public Path getSourceDirectory() {
        return sourceDirectory;
    }

    public Path getTestDirectory() {
        return testDirectory;
    }

    public Path getOutputDirectory() {
        return outputDirectory;
    }

    public Path getCoverageXmlFile() {
        return coverageXmlFile;
    }

    public double getHighCoverageThreshold() {
        return highCoverageThreshold;
    }

    public double getMediumCoverageThreshold() {
        return mediumCoverageThreshold;
    }

    public boolean isIncludeSourceLinks() {
        return includeSourceLinks;
    }

    public boolean isGenerateCoverageCharts() {
        return generateCoverageCharts;
    }

    public boolean isSkipCoverage() {
        return skipCoverage;
    }

    public boolean isEnableInlineDisplay() {
        return enableInlineDisplay;
    }

    public boolean isEnableVisualHighlight() {
        return enableVisualHighlight;
    }

    public boolean isEnableDetailedReports() {
        return enableDetailedReports;
    }

    public boolean isEnableTestCaseLinks() {
        return enableTestCaseLinks;
    }

    public String getLogLevel() {
        return logLevel;
    }

    public boolean isVerboseOutput() {
        return verboseOutput;
    }

    // Setter methods
    public void setSourceDirectory(Path sourceDirectory) {
        this.sourceDirectory = sourceDirectory;
    }

    public void setTestDirectory(Path testDirectory) {
        this.testDirectory = testDirectory;
    }

    public void setOutputDirectory(Path outputDirectory) {
        this.outputDirectory = outputDirectory;
    }

    public void setCoverageXmlFile(Path coverageXmlFile) {
        this.coverageXmlFile = coverageXmlFile;
    }

    public void setHighCoverageThreshold(double highCoverageThreshold) {
        this.highCoverageThreshold = highCoverageThreshold;
    }

    public void setMediumCoverageThreshold(double mediumCoverageThreshold) {
        this.mediumCoverageThreshold = mediumCoverageThreshold;
    }

    public void setIncludeSourceLinks(boolean includeSourceLinks) {
        this.includeSourceLinks = includeSourceLinks;
    }

    public void setGenerateCoverageCharts(boolean generateCoverageCharts) {
        this.generateCoverageCharts = generateCoverageCharts;
    }

    public void setSkipCoverage(boolean skipCoverage) {
        this.skipCoverage = skipCoverage;
    }

    public void setEnableInlineDisplay(boolean enableInlineDisplay) {
        this.enableInlineDisplay = enableInlineDisplay;
    }

    public void setEnableVisualHighlight(boolean enableVisualHighlight) {
        this.enableVisualHighlight = enableVisualHighlight;
    }

    public void setEnableDetailedReports(boolean enableDetailedReports) {
        this.enableDetailedReports = enableDetailedReports;
    }

    public void setEnableTestCaseLinks(boolean enableTestCaseLinks) {
        this.enableTestCaseLinks = enableTestCaseLinks;
    }

    public void setLogLevel(String logLevel) {
        this.logLevel = logLevel;
    }

    public void setVerboseOutput(boolean verboseOutput) {
        this.verboseOutput = verboseOutput;
    }

    @Override
    public String toString() {
        return "JavaDocEnhancement{" +
                "sourceDirectory=" + sourceDirectory +
                ", testDirectory=" + testDirectory +
                ", outputDirectory=" + outputDirectory +
                ", coverageXmlFile=" + coverageXmlFile +
                ", highCoverageThreshold=" + highCoverageThreshold +
                ", mediumCoverageThreshold=" + mediumCoverageThreshold +
                ", includeSourceLinks=" + includeSourceLinks +
                ", generateCoverageCharts=" + generateCoverageCharts +
                ", skipCoverage=" + skipCoverage +
                ", enableInlineDisplay=" + enableInlineDisplay +
                ", enableVisualHighlight=" + enableVisualHighlight +
                ", enableDetailedReports=" + enableDetailedReports +
                ", enableTestCaseLinks=" + enableTestCaseLinks +
                ", logLevel='" + logLevel + '\'' +
                ", verboseOutput=" + verboseOutput +
                '}';
    }
}