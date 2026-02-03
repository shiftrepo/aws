package com.testspecgenerator.core;

import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.testspecgenerator.model.CoverageInfo;
import com.testspecgenerator.model.TestCaseInfo;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * JaCoCoカバレッジレポートを解析するクラス
 */
public class CoverageReportParser {

    private static final Logger logger = LoggerFactory.getLogger(CoverageReportParser.class);

    // XMLパーサー
    private final XmlMapper xmlMapper;

    // カバレッジデータの正規表現パターン
    private static final Pattern COVERAGE_PERCENTAGE_PATTERN = Pattern.compile(
            "(\\d+(?:\\.\\d+)?)%"
    );

    private static final Pattern BRANCH_COUNT_PATTERN = Pattern.compile(
            "(\\d+)/(\\d+)"
    );

    public CoverageReportParser() {
        this.xmlMapper = new XmlMapper();
    }

    /**
     * カバレッジレポートファイルのリストを処理
     */
    public List<CoverageInfo> processCoverageReports(List<Path> coverageFiles) {
        return processCoverageReports(coverageFiles, null);
    }

    /**
     * 複数のカバレッジレポートファイルを処理し、動的パッケージフィルタリングを適用
     */
    public Map<String, Object> parseCoverageReports(List<Path> coverageFiles, List<Path> testFiles) {
        List<CoverageInfo> coverageInfos = processCoverageReports(coverageFiles, testFiles);

        // Convert to Map format for compatibility
        Map<String, Object> coverageData = new java.util.HashMap<>();
        for (int i = 0; i < coverageInfos.size(); i++) {
            coverageData.put("coverage_" + i, convertCoverageInfoToMap(coverageInfos.get(i)));
        }

        return coverageData;
    }

    /**
     * 複数のカバレッジレポートファイルを処理し、動的パッケージフィルタリングを適用して結合された結果を返します
     */
    public List<CoverageInfo> processCoverageReports(List<Path> coverageFiles, List<Path> testFiles) {
        logger.info("カバレッジレポート処理開始: {}個のファイル", coverageFiles.size());

        List<CoverageInfo> coverageData = new ArrayList<>();

        for (int i = 0; i < coverageFiles.size(); i++) {
            Path coverageFile = coverageFiles.get(i);
            logger.debug("処理中: {} ({}/{})", coverageFile.getFileName(), i + 1, coverageFiles.size());

            try {
                List<CoverageInfo> fileCoverage = processCoverageFile(coverageFile);
                coverageData.addAll(fileCoverage);
            } catch (Exception e) {
                logger.warn("カバレッジファイル処理中にエラー: {} - {}", coverageFile, e.getMessage());
            }
        }

        logger.info("カバレッジレポート処理完了: {}個のエントリ抽出", coverageData.size());
        return coverageData;
    }

    /**
     * 単一のカバレッジレポートファイルを処理
     */
    public List<CoverageInfo> processCoverageFile(Path coverageFile) throws IOException {
        return processCoverageFile(coverageFile, null);
    }

    /**
     * 単一のカバレッジレポートファイルを処理し、動的パッケージフィルタリングを適用
     */
    public List<CoverageInfo> processCoverageFile(Path coverageFile, java.util.Set<String> allowedPackages) throws IOException {
        String fileName = coverageFile.getFileName().toString().toLowerCase();

        List<CoverageInfo> coverageInfos;
        if (fileName.endsWith(".xml")) {
            coverageInfos = parseXmlCoverageReport(coverageFile);
        } else if (fileName.endsWith(".html")) {
            coverageInfos = parseHtmlCoverageReport(coverageFile);
        } else {
            logger.warn("サポートされていないファイル形式: {}", coverageFile);
            return new ArrayList<>();
        }

        // 動的パッケージフィルタリング（ツール自体のパッケージは常に除外）
        List<CoverageInfo> filteredCoverage = new ArrayList<>();
        for (CoverageInfo coverage : coverageInfos) {
            String packageName = coverage.getPackageName();

            if (packageName != null) {
                // Always exclude tool's own package
                if (packageName.startsWith("com.testspecgenerator") || packageName.startsWith("com/testspecgenerator")) {
                    continue;
                }

                // If allowedPackages is provided, use dynamic filtering
                if (allowedPackages != null && !allowedPackages.isEmpty()) {
                    boolean isAllowed = false;
                    String normalizedPackage = packageName.replace('/', '.');

                    for (String allowedPackage : allowedPackages) {
                        if (normalizedPackage.startsWith(allowedPackage)) {
                            isAllowed = true;
                            break;
                        }
                    }

                    if (isAllowed) {
                        filteredCoverage.add(coverage);
                        logger.debug("カバレッジ追加: {}.{} (パッケージ: {})",
                            coverage.getClassName(), coverage.getMethodName(), packageName);
                    }
                } else {
                    // Fallback to com.example for backward compatibility
                    if (packageName.startsWith("com/example") || packageName.startsWith("com.example")) {
                        filteredCoverage.add(coverage);
                        logger.debug("カバレッジ追加: {}.{} (パッケージ: {})",
                            coverage.getClassName(), coverage.getMethodName(), packageName);
                    }
                }
            }
        }

        String filterDescription = (allowedPackages != null && !allowedPackages.isEmpty())
            ? allowedPackages.toString()
            : "com.example (default)";
        logger.info("カバレッジフィルタリング: 全{}個 -> {}: {}個",
            coverageInfos.size(), filterDescription, filteredCoverage.size());

        return filteredCoverage;
    }

    /**
     * JaCoCo XMLレポートを解析
     */
    private List<CoverageInfo> parseXmlCoverageReport(Path xmlFile) throws IOException {
        logger.debug("XMLカバレッジレポート解析: {}", xmlFile);

        List<CoverageInfo> coverageInfos = new ArrayList<>();
        String content = Files.readString(xmlFile, StandardCharsets.UTF_8);

        try {
            // JaCoCo XMLの構造を解析
            Document doc = Jsoup.parse(content, "", org.jsoup.parser.Parser.xmlParser());

            // パッケージ要素を検索
            Elements packages = doc.select("package");
            for (Element packageElement : packages) {
                String packageName = packageElement.attr("name");

                // パッケージレベルのカウンターは除外（クラス要素のみ処理）
                // クラス要素を検索
                Elements classes = packageElement.select("class");
                for (Element classElement : classes) {
                    String classPath = classElement.attr("name");
                    String className = extractClassNameFromPath(classPath);
                    String sourceFileName = classElement.attr("sourcefilename");

                    // メソッド要素を検索
                    Elements methods = classElement.select("method");
                    for (Element methodElement : methods) {
                        String methodName = methodElement.attr("name");
                        int line = parseIntAttribute(methodElement.attr("line"), 0);

                        // メソッド名の特殊文字をデコード
                        String displayMethodName = decodeMethodName(methodName);

                        CoverageInfo coverageInfo = new CoverageInfo(className, displayMethodName);
                        coverageInfo.setPackageName(packageName);
                        coverageInfo.setReportType("XML");

                        // ソースファイル名の設定（nullチェックと特殊ケースの処理）
                        String finalSourceFile = "";
                        if (sourceFileName != null && !sourceFileName.isEmpty()) {
                            finalSourceFile = sourceFileName;
                        } else if (className != null && !className.isEmpty()) {
                            // ソースファイル名が取得できない場合はクラス名から推測
                            finalSourceFile = className + ".java";
                        }
                        coverageInfo.setSourceFile(finalSourceFile);

                        // カウンター要素からメトリクスを抽出
                        Elements counters = methodElement.select("counter");
                        for (Element counter : counters) {
                            String type = counter.attr("type");
                            int missed = parseIntAttribute(counter.attr("missed"), 0);
                            int covered = parseIntAttribute(counter.attr("covered"), 0);

                            switch (type) {
                                case "INSTRUCTION":
                                    coverageInfo.setInstructionInfo(covered, covered + missed);
                                    break;
                                case "BRANCH":
                                    coverageInfo.setBranchInfo(covered, covered + missed);
                                    break;
                                case "LINE":
                                    coverageInfo.setLineInfo(covered, covered + missed);
                                    break;
                                case "METHOD":
                                    coverageInfo.setMethodInfo(covered, covered + missed);
                                    break;
                            }
                        }

                        coverageInfos.add(coverageInfo);
                        logger.debug("XMLカバレッジ抽出: {}.{} - ブランチ: {:.1f}%",
                                className, methodName, coverageInfo.getBranchCoverage());
                    }
                }
            }

        } catch (Exception e) {
            logger.error("XMLカバレッジレポート解析エラー: {}", xmlFile, e);
            throw new IOException("XMLレポート解析に失敗しました", e);
        }

        return coverageInfos;
    }

    /**
     * JaCoCo HTMLレポートを解析
     * 注：HTMLレポートはXMLレポートより精度が低いため、可能な限りXMLレポートを使用することを推奨
     */
    private List<CoverageInfo> parseHtmlCoverageReport(Path htmlFile) throws IOException {
        logger.debug("HTMLカバレッジレポート解析: {}", htmlFile);

        List<CoverageInfo> coverageInfos = new ArrayList<>();

        // HTMLレポートの処理は複雑で不正確なため、スキップすることを推奨
        // XMLレポートが利用可能な場合はそちらを優先する
        logger.warn("HTMLレポートのパースはスキップされました。XMLレポートを使用してください: {}", htmlFile);

        // HTMLレポートのパースを無効化（XMLレポートのみ使用）
        return coverageInfos;
    }

    /**
     * HTMLセルからカバレッジ情報を解析
     */
    private void parseCoverageCell(String cellText, CoverageInfo coverageInfo, int columnIndex) {
        // カバレッジパーセンテージを抽出
        Matcher percentMatcher = COVERAGE_PERCENTAGE_PATTERN.matcher(cellText);
        if (percentMatcher.find()) {
            double percentage = Double.parseDouble(percentMatcher.group(1));

            // 列インデックスに基づいてカバレッジタイプを判定
            switch (columnIndex) {
                case 1: // 通常は命令カバレッジ
                    // パーセンテージから逆算（概算）
                    int totalInstructions = 100;
                    int coveredInstructions = (int) (percentage * totalInstructions / 100);
                    coverageInfo.setInstructionInfo(coveredInstructions, totalInstructions);
                    break;
                case 2: // 通常はブランチカバレッジ
                    // x/y 形式があるかチェック
                    Matcher branchMatcher = BRANCH_COUNT_PATTERN.matcher(cellText);
                    if (branchMatcher.find()) {
                        int covered = Integer.parseInt(branchMatcher.group(1));
                        int total = Integer.parseInt(branchMatcher.group(2));
                        coverageInfo.setBranchInfo(covered, total);
                    } else {
                        // パーセンテージから逆算
                        int totalBranches = 100;
                        int coveredBranches = (int) (percentage * totalBranches / 100);
                        coverageInfo.setBranchInfo(coveredBranches, totalBranches);
                    }
                    break;
                case 3: // 通常はラインカバレッジ
                    int totalLines = 100;
                    int coveredLines = (int) (percentage * totalLines / 100);
                    coverageInfo.setLineInfo(coveredLines, totalLines);
                    break;
            }
        }
    }

    /**
     * カバレッジデータをテストケースにマージ
     */
    public void mergeCoverageWithTestCases(List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        logger.debug("カバレッジデータマージ開始: テストケース{}個, カバレッジ{}個", testCases.size(), coverageData.size());

        // カバレッジデータをマップ化（高速検索用）
        // キーをメソッド名のみにし、複数のクラス名パターンに対応
        Map<String, List<CoverageInfo>> coverageByMethod = new HashMap<>();
        for (CoverageInfo coverage : coverageData) {
            String methodKey = coverage.getMethodName();
            coverageByMethod.computeIfAbsent(methodKey, k -> new ArrayList<>()).add(coverage);

            // クラス名もキーとして保存（完全一致用）
            String fullKey = coverage.getClassName() + "." + coverage.getMethodName();
            coverageByMethod.computeIfAbsent(fullKey, k -> new ArrayList<>()).add(coverage);
        }

        // 各テストケースに対応するカバレッジ情報を検索
        for (TestCaseInfo testCase : testCases) {
            // テストクラス名から実装クラス名を推定（"Test"を除去）
            String implClassName = testCase.getClassName().replace("Test", "");
            String testMethodName = testCase.getMethodName();

            // テストメソッド名から実際のメソッド名を推定
            // 例: testAdd -> add, testDivideByZero -> divide
            String targetMethodName = testMethodName;
            if (targetMethodName.startsWith("test")) {
                targetMethodName = targetMethodName.substring(4);
                if (targetMethodName.length() > 0) {
                    targetMethodName = Character.toLowerCase(targetMethodName.charAt(0)) +
                                     (targetMethodName.length() > 1 ? targetMethodName.substring(1) : "");
                }
                // キャメルケースから実際のメソッド名を抽出（例: testDivideByZero -> divide）
                if (targetMethodName.contains("_")) {
                    targetMethodName = targetMethodName.substring(0, targetMethodName.indexOf("_"));
                } else if (targetMethodName.matches(".*[A-Z].*")) {
                    // 大文字で始まる部分までを取得
                    for (int i = 1; i < targetMethodName.length(); i++) {
                        if (Character.isUpperCase(targetMethodName.charAt(i))) {
                            targetMethodName = targetMethodName.substring(0, i);
                            break;
                        }
                    }
                }
            }

            // 複数のパターンで検索
            CoverageInfo coverage = null;

            // 1. 実装クラス名 + メソッド名で検索
            String implKey = implClassName + "." + targetMethodName;
            List<CoverageInfo> candidates = coverageByMethod.get(implKey);
            if (candidates != null && !candidates.isEmpty()) {
                coverage = candidates.get(0);
                logger.debug("カバレッジマッチ（実装クラス）: {} -> {}", testCase.getMethodName(), implKey);
            }

            // 2. メソッド名のみで検索（クラス名が一致しない場合）
            if (coverage == null) {
                candidates = coverageByMethod.get(targetMethodName);
                if (candidates != null && !candidates.isEmpty()) {
                    // パッケージ名を考慮してベストマッチを探す
                    for (CoverageInfo candidate : candidates) {
                        if (candidate.getClassName().equals(implClassName) ||
                            candidate.getClassName().endsWith(implClassName)) {
                            coverage = candidate;
                            logger.debug("カバレッジマッチ（メソッド名）: {} -> {}.{}",
                                testCase.getMethodName(), candidate.getClassName(), targetMethodName);
                            break;
                        }
                    }
                    // それでも見つからない場合は最初の候補を使用
                    if (coverage == null && !candidates.isEmpty()) {
                        coverage = candidates.get(0);
                        logger.debug("カバレッジマッチ（メソッド名のみ）: {} -> {}.{}",
                            testCase.getMethodName(), coverage.getClassName(), targetMethodName);
                    }
                }
            }

            if (coverage != null) {
                // カバレッジ情報をテストケースに設定
                testCase.setCoveragePercent(coverage.getBranchCoverage());
                testCase.setBranchesCovered(coverage.getBranchesCovered());
                testCase.setBranchesTotal(coverage.getBranchesTotal());

                logger.debug("カバレッジマージ完了: {} -> {:.1f}%",
                        testCase.getMethodName(), testCase.getCoveragePercent());
            } else {
                logger.debug("カバレッジ情報が見つかりません: {} (探索: {})",
                    testCase.getMethodName(), implKey);
            }
        }
    }

    /**
     * クラスパスからクラス名を抽出
     */
    private String extractClassNameFromPath(String classPath) {
        if (classPath == null || classPath.isEmpty()) {
            return "";
        }

        // パッケージパス区切りの最後の要素を取得
        String[] parts = classPath.split("/");
        String className = parts[parts.length - 1];

        // 内部クラスの場合の処理
        // 注：匿名内部クラスは元のまま残す（FolderScanner$1など）
        // ただし、通常の内部クラスは親クラス名を返す

        return className;
    }

    /**
     * メソッド名の特殊文字をデコード
     */
    private String decodeMethodName(String methodName) {
        if (methodName == null) {
            return "";
        }

        // JaCoCo特殊メソッド名の処理
        switch (methodName) {
            case "&lt;init&gt;":
                return "<init>";  // コンストラクタ
            case "&lt;clinit&gt;":
                return "static {...}";  // static初期化ブロック
            default:
                // &lt; と &gt; をデコード
                return methodName.replace("&lt;", "<").replace("&gt;", ">");
        }
    }

    /**
     * メソッド名からクラス名を抽出
     */
    private String extractClassFromMethod(String methodSignature) {
        // メソッドシグネチャーからクラス名部分を抽出
        if (methodSignature.contains(".")) {
            int lastDot = methodSignature.lastIndexOf('.');
            return methodSignature.substring(0, lastDot);
        }
        return "";
    }

    /**
     * 文字列を整数に変換（エラー時はデフォルト値）
     */
    private int parseIntAttribute(String value, int defaultValue) {
        if (value == null || value.isEmpty()) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return defaultValue;
        }
    }

    /**
     * カバレッジデータの統計情報を取得
     */
    public Map<String, Object> getStatistics(List<CoverageInfo> coverageData) {
        Map<String, Object> stats = new HashMap<>();

        stats.put("totalEntries", coverageData.size());

        // レポートタイプ別統計
        long xmlReports = coverageData.stream()
                .mapToLong(c -> "XML".equals(c.getReportType()) ? 1 : 0)
                .sum();
        stats.put("xmlReports", xmlReports);
        stats.put("htmlReports", coverageData.size() - xmlReports);

        // カバレッジ統計
        OptionalDouble avgBranchCoverage = coverageData.stream()
                .mapToDouble(CoverageInfo::getBranchCoverage)
                .average();
        stats.put("averageBranchCoverage", avgBranchCoverage.orElse(0.0));

        // 高カバレッジケース数（80%以上）
        long highCoverageCount = coverageData.stream()
                .mapToLong(c -> c.getBranchCoverage() >= 80.0 ? 1 : 0)
                .sum();
        stats.put("highCoverageCount", highCoverageCount);

        return stats;
    }

    /**
     * カバレッジ解析サマリーをログ出力
     */
    public void logCoverageSummary(List<CoverageInfo> coverageData) {
        Map<String, Object> stats = getStatistics(coverageData);

        logger.info("=== カバレッジ解析サマリー ===");
        logger.info("総エントリ数: {}", stats.get("totalEntries"));
        logger.info("XMLレポート: {}, HTMLレポート: {}", stats.get("xmlReports"), stats.get("htmlReports"));
        logger.info("平均ブランチカバレッジ: {:.1f}%", stats.get("averageBranchCoverage"));
        logger.info("高カバレッジ（80%以上）: {}個", stats.get("highCoverageCount"));
    }

    /**
     * Extract package names from test files for dynamic filtering
     */
    private java.util.Set<String> getFilteredPackageNames(List<Path> testFiles) {
        java.util.Set<String> packageNames = new java.util.HashSet<>();

        if (testFiles == null || testFiles.isEmpty()) {
            return packageNames;
        }

        for (Path testFile : testFiles) {
            try {
                String packageName = extractPackageFromFile(testFile);
                if (packageName != null && !packageName.isEmpty()) {
                    packageNames.add(packageName);
                    logger.debug("パッケージ名抽出: {} -> {}", testFile.getFileName(), packageName);
                }
            } catch (Exception e) {
                logger.debug("パッケージ名抽出失敗: {} - {}", testFile, e.getMessage());
            }
        }

        logger.info("動的パッケージ検出完了: {} unique packages from {} test files",
                   packageNames.size(), testFiles.size());
        return packageNames;
    }

    /**
     * Extract package name from a Java file
     */
    private String extractPackageFromFile(Path javaFile) throws java.io.IOException {
        try (java.io.BufferedReader reader = Files.newBufferedReader(javaFile)) {
            return reader.lines()
                .limit(50) // Only check first 50 lines for package declaration
                .filter(line -> line.trim().startsWith("package "))
                .map(line -> line.trim().replaceFirst("package\\s+", "").replaceAll(";.*", ""))
                .findFirst()
                .orElse(null);
        }
    }

    /**
     * Convert CoverageInfo to Map for compatibility with existing code
     */
    private Map<String, Object> convertCoverageInfoToMap(CoverageInfo coverage) {
        Map<String, Object> map = new java.util.HashMap<>();
        map.put("className", coverage.getClassName());
        map.put("methodName", coverage.getMethodName());
        map.put("packageName", coverage.getPackageName());
        map.put("branchCoverage", coverage.getBranchCoverage());
        map.put("lineCoverage", coverage.getLineCoverage());
        map.put("instructionCoverage", coverage.getInstructionCoverage());
        map.put("branchesCovered", coverage.getBranchesCovered());
        map.put("branchesTotal", coverage.getBranchesTotal());
        map.put("linesCovered", coverage.getLinesCovered());
        map.put("linesTotal", coverage.getLinesTotal());
        return map;
    }
}