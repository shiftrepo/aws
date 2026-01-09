package com.testspecgenerator.core;

import com.testspecgenerator.model.TestCaseInfo;
import com.testspecgenerator.model.CoverageInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 拡張JavaDocのHTMLレポートを生成するビルダークラス
 * テストケース情報とカバレッジ情報を統合した拡張JavaDocドキュメントを作成します
 */
public class EnhancedJavaDocBuilder {

    private static final Logger logger = LoggerFactory.getLogger(EnhancedJavaDocBuilder.class);

    private static final String OUTPUT_DIR = "enhanced-javadoc";
    private static final String COVERAGE_DIR = "coverage";
    private static final String SOURCE_DIR = "source";
    private static final String TEST_LINKS_DIR = "test-links";

    /**
     * 拡張JavaDocレポートを生成
     * @param testCases テストケース情報のリスト
     * @param coverageData カバレッジ情報のリスト
     * @return 生成成功時はtrue
     */
    public boolean generateEnhancedJavaDoc(List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        logger.info("拡張JavaDoc生成開始: {}", OUTPUT_DIR);

        try {
            // 出力ディレクトリを準備
            setupOutputDirectories();

            // クラス別にデータをグループ化
            Map<String, List<TestCaseInfo>> testsByClass = groupTestCasesByClass(testCases);
            Map<String, CoverageInfo> coverageByClass = groupCoverageByClass(coverageData);

            // メインインデックスページを生成
            generateIndexPage(testsByClass, coverageByClass);

            // 各クラスのページを生成
            generateClassPages(testsByClass, coverageByClass);

            // カバレッジレポートページを生成
            generateCoveragePages(coverageByClass);

            // テストリンクページを生成
            generateTestLinkPages(testsByClass);

            logger.info("✅ 拡張JavaDoc生成完了: {}", OUTPUT_DIR);
            return true;

        } catch (Exception e) {
            logger.error("❌ 拡張JavaDoc生成中にエラーが発生しました", e);
            return false;
        }
    }

    /**
     * 出力ディレクトリを設定
     */
    private void setupOutputDirectories() throws IOException {
        Path outputPath = Paths.get(OUTPUT_DIR);
        Path coveragePath = outputPath.resolve(COVERAGE_DIR);
        Path sourcePath = coveragePath.resolve(SOURCE_DIR);
        Path testLinksPath = outputPath.resolve(TEST_LINKS_DIR);
        Path comExamplePath = outputPath.resolve("com/example");

        // ディレクトリを作成
        Files.createDirectories(outputPath);
        Files.createDirectories(coveragePath);
        Files.createDirectories(sourcePath);
        Files.createDirectories(testLinksPath);
        Files.createDirectories(comExamplePath);
    }

    /**
     * テストケースをクラス名でグループ化
     */
    private Map<String, List<TestCaseInfo>> groupTestCasesByClass(List<TestCaseInfo> testCases) {
        return testCases.stream()
                .collect(Collectors.groupingBy(TestCaseInfo::getClassName));
    }

    /**
     * カバレッジ情報をクラス名でグループ化
     */
    private Map<String, CoverageInfo> groupCoverageByClass(List<CoverageInfo> coverageData) {
        Map<String, CoverageInfo> result = new HashMap<>();
        if (coverageData != null) {
            for (CoverageInfo coverage : coverageData) {
                String className = coverage.getClassName();
                if (className != null && !className.isEmpty()) {
                    result.put(className, coverage);
                }
            }
        }
        return result;
    }

    /**
     * メインインデックスページを生成
     */
    private void generateIndexPage(Map<String, List<TestCaseInfo>> testsByClass, Map<String, CoverageInfo> coverageByClass) throws IOException {
        StringBuilder html = new StringBuilder();

        html.append(generateHtmlHeader("Enhanced JavaDoc - カバレッジ統合レポート", getIndexPageStyle()));

        html.append("""
            <div class="container">
                <div class="header">
                    <h1 class="title">📊 Enhanced JavaDoc</h1>
                    <p class="subtitle">カバレッジ統合 + テストケースリンク付きドキュメント</p>
                </div>
            """);

        // 統計情報
        html.append(generateStatsGrid(testsByClass, coverageByClass));

        // クラス一覧セクション
        html.append(generateClassListSection(testsByClass, coverageByClass));

        // テストファイル一覧セクション
        html.append(generateTestFileSection(testsByClass));

        html.append(generateTimestamp());
        html.append("    </div>");
        html.append(generateHtmlFooter());

        // ファイル保存
        Path indexPath = Paths.get(OUTPUT_DIR, "index.html");
        Files.writeString(indexPath, html.toString());
    }

    /**
     * 統計情報グリッドを生成
     */
    private String generateStatsGrid(Map<String, List<TestCaseInfo>> testsByClass, Map<String, CoverageInfo> coverageByClass) {
        int sourceFiles = testsByClass.size();
        int totalTests = testsByClass.values().stream()
                .mapToInt(List::size)
                .sum();

        double avgCoverage = coverageByClass.values().stream()
                .mapToDouble(CoverageInfo::getBranchCoverage)
                .average()
                .orElse(0.0);

        String quality = avgCoverage >= 90 ? "⭐⭐⭐" : avgCoverage >= 70 ? "⭐⭐" : "⭐";

        return String.format("""
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">%d</div>
                    <div>ソースファイル</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">%d</div>
                    <div>テストケース</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">%.1f%%</div>
                    <div>平均カバレッジ</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">%s</div>
                    <div>品質評価</div>
                </div>
            </div>
            """, sourceFiles, totalTests, avgCoverage, quality);
    }

    /**
     * クラス一覧セクションを生成
     */
    private String generateClassListSection(Map<String, List<TestCaseInfo>> testsByClass, Map<String, CoverageInfo> coverageByClass) {
        StringBuilder section = new StringBuilder();

        section.append("""
            <div class="section">
                <h2>📁 ソースファイル</h2>
                <ul>
            """);

        // DEBUG: カバレッジマップのキーを出力
        logger.info("DEBUG: coverageByClass キー一覧:");
        for (String key : coverageByClass.keySet()) {
            logger.info("DEBUG: キー = {}", key);
        }

        for (String className : testsByClass.keySet().stream().sorted().collect(Collectors.toList())) {
            // テストクラス名から実装クラス名を推定 (TestサフィックスをTrim)
            String implClassName = className.endsWith("Test") ? className.substring(0, className.length() - 4) : className;
            logger.info("DEBUG: {} → {}", className, implClassName);

            // 実装クラス名に対応するカバレッジ情報を検索
            // 直接マッチ、または内部クラス（$記号を含む）も含めて検索
            CoverageInfo coverage = coverageByClass.get(implClassName);
            logger.info("DEBUG: 直接検索 {} → {}", implClassName, coverage != null ? "見つかった" : "null");

            if (coverage == null) {
                // 内部クラスを含む場合の検索 (例: DataStructures → DataStructures$MinHeap等)
                coverage = coverageByClass.entrySet().stream()
                    .filter(entry -> entry.getKey().startsWith(implClassName + "$") || entry.getKey().equals(implClassName))
                    .map(Map.Entry::getValue)
                    .findFirst()
                    .orElse(null);
                logger.info("DEBUG: 内部クラス検索 {} → {}", implClassName, coverage != null ? "見つかった" : "null");
            }

            String coverageText = "";
            String badgeClass = "";

            if (coverage != null) {
                double branchCoverage = coverage.getBranchCoverage();
                logger.info("DEBUG: {} のブランチカバレッジ = {}% (covered:{}, total:{})",
                    implClassName, branchCoverage, coverage.getBranchesCovered(), coverage.getBranchesTotal());

                // ブランチカバレッジが0の場合、命令カバレッジを代替使用
                if (branchCoverage == 0.0 && coverage.getInstructionCoverage() > 0) {
                    branchCoverage = coverage.getInstructionCoverage();
                    logger.info("DEBUG: {} ブランチカバレッジが0のため命令カバレッジを使用: {}%", implClassName, branchCoverage);
                } else if (branchCoverage == 0.0 && coverage.getInstructionCoverage() == 0.0) {
                    // 親クラスと内部クラスの両方が0の場合、内部クラスから最高のカバレッジを取得
                    double bestCoverage = coverageByClass.entrySet().stream()
                        .filter(entry -> entry.getKey().startsWith(implClassName + "$"))
                        .mapToDouble(entry -> Math.max(entry.getValue().getBranchCoverage(), entry.getValue().getInstructionCoverage()))
                        .max()
                        .orElse(0.0);
                    if (bestCoverage > 0) {
                        branchCoverage = bestCoverage;
                        logger.info("DEBUG: {} 内部クラスから最高カバレッジを使用: {}%", implClassName, branchCoverage);
                    }
                }

                coverageText = String.format("%.1f%%", branchCoverage);
                badgeClass = branchCoverage >= 80 ? "coverage-high" : "coverage-medium";
            } else {
                logger.info("DEBUG: {} カバレッジ情報なし", implClassName);
                coverageText = "0.0%";
                badgeClass = "coverage-low";
            }

            section.append(String.format(
                "<li><a href=\"com/example/%s.html\">%s</a><span class=\"coverage-badge %s\">%s</span></li>%n",
                className, className, badgeClass, coverageText
            ));
        }

        section.append("</ul></div>");
        return section.toString();
    }

    /**
     * テストファイルセクションを生成
     */
    private String generateTestFileSection(Map<String, List<TestCaseInfo>> testsByClass) {
        StringBuilder section = new StringBuilder();

        section.append("""
            <div class="section">
                <h2>🧪 テストファイル</h2>
                <ul>
            """);

        for (String className : testsByClass.keySet().stream().sorted().collect(Collectors.toList())) {
            List<TestCaseInfo> tests = testsByClass.get(className);
            int testCount = tests.size();

            section.append(String.format(
                "<li><a href=\"test-links/%s.html\">%s</a> <span class=\"test-count\">(%d テスト)</span></li>%n",
                className, className, testCount
            ));
        }

        section.append("</ul></div>");
        return section.toString();
    }

    /**
     * 各クラスページを生成
     */
    private void generateClassPages(Map<String, List<TestCaseInfo>> testsByClass, Map<String, CoverageInfo> coverageByClass) throws IOException {
        for (Map.Entry<String, List<TestCaseInfo>> entry : testsByClass.entrySet()) {
            String className = entry.getKey();
            List<TestCaseInfo> tests = entry.getValue();
            CoverageInfo coverage = coverageByClass.get(className);

            generateSingleClassPage(className, tests, coverage);
        }
    }

    /**
     * 単一クラスページを生成
     */
    private void generateSingleClassPage(String className, List<TestCaseInfo> tests, CoverageInfo coverage) throws IOException {
        StringBuilder html = new StringBuilder();

        html.append(generateHtmlHeader(className + " - Enhanced JavaDoc", getClassPageStyle()));

        html.append("<div class=\"container\">");
        html.append(String.format("""
            <div class="header">
                <h1 class="class-title">%s</h1>
                <p class="package-info">パッケージ: com.example</p>
                <p class="package-info">ソースファイル: %s.java</p>
            </div>
            """, className, className));

        // カバレッジセクション
        if (coverage != null) {
            html.append(generateCoverageSection(coverage));
        }

        // テストケースセクション
        html.append(generateTestCasesSection(tests));

        html.append(generateTimestamp());
        html.append("</div>");
        html.append(generateHtmlFooter());

        // ファイル保存
        Path classPath = Paths.get(OUTPUT_DIR, "com", "example", className + ".html");
        Files.writeString(classPath, html.toString());
    }

    /**
     * カバレッジセクションを生成
     */
    private String generateCoverageSection(CoverageInfo coverage) {
        String badgeClass = coverage.getBranchCoverage() >= 80 ? "coverage-high" :
                           coverage.getBranchCoverage() >= 60 ? "coverage-medium" : "coverage-low";

        return String.format("""
            <div class="coverage-section">
                <h3>📊 カバレッジ情報</h3>
                <div class="coverage-stats">
                    <span class="coverage-badge %s">ブランチ: %.1f%%</span>
                    <span class="coverage-badge coverage-medium">ライン: %.1f%%</span>
                    <span class="coverage-badge coverage-high">メソッド: %.1f%%</span>
                </div>
                <p><strong>詳細:</strong> <a href="../coverage/%s-coverage.html">カバレッジレポートを見る</a></p>
            </div>
            """, badgeClass, coverage.getBranchCoverage(), coverage.getLineCoverage(),
                 coverage.getMethodCoverage(), coverage.getClassName());
    }

    /**
     * テストケースセクションを生成
     */
    private String generateTestCasesSection(List<TestCaseInfo> tests) {
        StringBuilder section = new StringBuilder();

        section.append("""
            <div class="section">
                <h3>🧪 関連テストケース</h3>
            """);

        for (TestCaseInfo test : tests) {
            section.append(String.format("""
                <div class="method-section">
                    <h4>%s</h4>
                    <div class="method-signature">%s.%s()</div>
                    <p><strong>テストモジュール:</strong> %s</p>
                    <p><strong>テスト目的:</strong> %s</p>
                    <p><strong>実行結果:</strong> %s (成功率: %s)</p>
                </div>
                """, test.getTestCase(), test.getClassName(), test.getMethodName(),
                     test.getTestModule(), test.getTestPurpose(),
                     test.getTestExecutionDisplay(), test.getTestSuccessRateDisplay()));
        }

        section.append("</div>");
        return section.toString();
    }

    /**
     * カバレッジページを生成
     */
    private void generateCoveragePages(Map<String, CoverageInfo> coverageByClass) throws IOException {
        for (CoverageInfo coverage : coverageByClass.values()) {
            generateSingleCoveragePage(coverage);
        }
    }

    /**
     * 単一カバレッジページを生成
     */
    private void generateSingleCoveragePage(CoverageInfo coverage) throws IOException {
        StringBuilder html = new StringBuilder();

        html.append(generateHtmlHeader(coverage.getClassName() + " - カバレッジレポート", getClassPageStyle()));

        html.append("<div class=\"container\">");
        html.append(String.format("""
            <div class="header">
                <h1 class="class-title">%s - カバレッジレポート</h1>
                <p class="package-info">パッケージ: %s</p>
            </div>
            """, coverage.getClassName(), coverage.getPackageName()));

        // 詳細カバレッジ情報
        html.append(generateDetailedCoverageInfo(coverage));

        html.append(generateTimestamp());
        html.append("</div>");
        html.append(generateHtmlFooter());

        // ファイル保存
        Path coveragePath = Paths.get(OUTPUT_DIR, COVERAGE_DIR, coverage.getClassName() + "-coverage.html");
        Files.writeString(coveragePath, html.toString());
    }

    /**
     * 詳細カバレッジ情報を生成
     */
    private String generateDetailedCoverageInfo(CoverageInfo coverage) {
        return String.format("""
            <div class="coverage-section">
                <h3>📊 詳細カバレッジ統計</h3>
                <table class="coverage-table">
                    <tr><th>種類</th><th>カバー済み</th><th>総数</th><th>カバレッジ</th></tr>
                    <tr><td>ブランチ</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>
                    <tr><td>ライン</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>
                    <tr><td>メソッド</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>
                    <tr><td>命令</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>
                </table>
            </div>
            """,
            coverage.getBranchesCovered(), coverage.getBranchesTotal(), coverage.getBranchCoverage(),
            coverage.getLinesCovered(), coverage.getLinesTotal(), coverage.getLineCoverage(),
            coverage.getMethodsCovered(), coverage.getMethodsTotal(), coverage.getMethodCoverage(),
            coverage.getInstructionsCovered(), coverage.getInstructionsTotal(), coverage.getInstructionCoverage());
    }

    /**
     * テストリンクページを生成
     */
    private void generateTestLinkPages(Map<String, List<TestCaseInfo>> testsByClass) throws IOException {
        for (Map.Entry<String, List<TestCaseInfo>> entry : testsByClass.entrySet()) {
            String className = entry.getKey();
            List<TestCaseInfo> tests = entry.getValue();

            generateSingleTestLinkPage(className, tests);
        }
    }

    /**
     * 単一テストリンクページを生成
     */
    private void generateSingleTestLinkPage(String className, List<TestCaseInfo> tests) throws IOException {
        StringBuilder html = new StringBuilder();

        html.append(generateHtmlHeader(className + " - テストリンク", getClassPageStyle()));

        html.append("<div class=\"container\">");
        html.append(String.format("""
            <div class="header">
                <h1 class="class-title">%s - テストケース一覧</h1>
                <p class="package-info">テスト数: %d</p>
            </div>
            """, className, tests.size()));

        // テストケース一覧
        html.append("<div class=\"section\">");
        html.append("<h3>🧪 テストケース詳細</h3>");

        for (TestCaseInfo test : tests) {
            html.append(String.format("""
                <div class="test-case">
                    <h4>%s</h4>
                    <div class="test-details">
                        <p><strong>メソッド:</strong> %s</p>
                        <p><strong>カテゴリ:</strong> %s</p>
                        <p><strong>優先度:</strong> %s</p>
                        <p><strong>作成者:</strong> %s</p>
                        <p><strong>テスト概要:</strong> %s</p>
                        <p><strong>実行結果:</strong> %s (成功率: %s)</p>
                    </div>
                </div>
                """, test.getTestCase(), test.getMethodName(), test.getTestCategory(),
                     test.getPriority(), test.getCreator(), test.getTestOverview(),
                     test.getTestExecutionDisplay(), test.getTestSuccessRateDisplay()));
        }

        html.append("</div>");
        html.append(generateTimestamp());
        html.append("</div>");
        html.append(generateHtmlFooter());

        // ファイル保存
        Path testLinkPath = Paths.get(OUTPUT_DIR, TEST_LINKS_DIR, className + ".html");
        Files.writeString(testLinkPath, html.toString());
    }

    /**
     * HTMLヘッダーを生成
     */
    private String generateHtmlHeader(String title, String style) {
        return String.format("""
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>%s</title>
                %s
            </head>
            <body>
            """, title, style);
    }

    /**
     * HTMLフッターを生成
     */
    private String generateHtmlFooter() {
        return """
            </body>
            </html>
            """;
    }

    /**
     * タイムスタンプを生成
     */
    private String generateTimestamp() {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        return String.format("""
            <div class="timestamp">
                🕐 生成日時: %s | ⚡ Java Test Specification Generator v1.0.0
            </div>
            """, timestamp);
    }

    /**
     * インデックスページ用CSS
     */
    private String getIndexPageStyle() {
        return """
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; text-align: center; }
                .title { color: #007bff; margin: 0; font-size: 3em; }
                .subtitle { color: #6c757d; margin: 10px 0; font-size: 1.2em; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
                .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
                .stat-number { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
                .section { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 6px; }
                .section h2 { color: #007bff; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
                ul li { margin: 8px 0; font-size: 1.1em; }
                .coverage-badge { display: inline-block; padding: 4px 12px; border-radius: 15px; color: white; font-weight: bold; margin-left: 10px; font-size: 0.9em; }
                .coverage-high { background-color: #28a745; }
                .coverage-medium { background-color: #ffc107; }
                .coverage-low { background-color: #dc3545; }
                .test-count { color: #6c757d; font-size: 0.9em; }
                .timestamp { text-align: center; margin-top: 30px; color: #6c757d; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
            """;
    }

    /**
     * クラスページ用CSS
     */
    private String getClassPageStyle() {
        return """
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
                .class-title { color: #007bff; margin: 0; font-size: 2.5em; }
                .package-info { color: #6c757d; margin: 10px 0; font-size: 1.1em; }
                .coverage-section { background: #e3f2fd; padding: 20px; border-radius: 6px; margin: 20px 0; }
                .coverage-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; color: white; font-weight: bold; margin-right: 10px; }
                .coverage-high { background-color: #28a745; }
                .coverage-medium { background-color: #ffc107; }
                .coverage-low { background-color: #dc3545; }
                .section { margin: 30px 0; padding: 20px; border: 1px solid #dee2e6; border-radius: 6px; }
                .method-section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 6px; }
                .method-signature { font-family: 'Courier New', monospace; background: #e9ecef; padding: 10px; border-radius: 4px; }
                .test-case { margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 6px; }
                .test-details { margin-top: 10px; }
                .coverage-table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                .coverage-table th, .coverage-table td { border: 1px solid #dee2e6; padding: 8px; text-align: left; }
                .coverage-table th { background-color: #f8f9fa; }
                .timestamp { text-align: center; margin-top: 30px; color: #6c757d; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
            """;
    }
}