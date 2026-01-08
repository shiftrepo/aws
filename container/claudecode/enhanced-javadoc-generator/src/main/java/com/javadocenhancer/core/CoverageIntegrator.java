package com.javadocenhancer.core;

import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.javadocenhancer.model.CoverageMetrics;
import com.javadocenhancer.model.SourceMethodInfo;
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
import java.util.regex.Pattern;

/**
 * カバレッジ統合クラス
 *
 * 既存のCoverageReportParserをベースに、拡張JavaDoc生成のために
 * JaCoCoカバレッジデータを解析・統合します。
 */
public class CoverageIntegrator {

    private static final Logger logger = LoggerFactory.getLogger(CoverageIntegrator.class);

    // XMLパーサー
    private final XmlMapper xmlMapper;

    // カバレッジファイルのパターン
    private static final Set<String> COVERAGE_FILE_PATTERNS = Set.of(
            "jacoco*.xml",
            "*coverage*.xml",
            "index.html",
            "*coverage*.html"
    );

    // 対象パッケージフィルタ（設定可能）
    private Set<String> targetPackages = new HashSet<>();

    /**
     * コンストラクタ
     */
    public CoverageIntegrator() {
        this.xmlMapper = new XmlMapper();
    }

    /**
     * 対象パッケージの設定
     *
     * @param packagePrefixes 対象パッケージのプレフィックス一覧
     */
    public void setTargetPackages(Set<String> packagePrefixes) {
        this.targetPackages = packagePrefixes != null ? new HashSet<>(packagePrefixes) : new HashSet<>();
        logger.info("対象パッケージフィルタ設定: {}", targetPackages);
    }

    /**
     * カバレッジファイルを処理してメトリクスを抽出
     *
     * @param coverageFile カバレッジファイル（JaCoCo XML/HTML）
     * @return カバレッジメトリクスのリスト
     */
    public List<CoverageMetrics> processCoverageFile(Path coverageFile) throws IOException {
        logger.info("カバレッジファイル処理開始: {}", coverageFile);

        if (!Files.exists(coverageFile)) {
            throw new IllegalArgumentException("カバレッジファイルが存在しません: " + coverageFile);
        }

        String fileName = coverageFile.getFileName().toString().toLowerCase();
        List<CoverageMetrics> metrics;

        if (fileName.endsWith(".xml")) {
            metrics = parseXmlCoverageReport(coverageFile);
        } else if (fileName.endsWith(".html")) {
            metrics = parseHtmlCoverageReport(coverageFile);
        } else {
            throw new IllegalArgumentException("サポートされていないファイル形式: " + coverageFile);
        }

        // パッケージフィルタリング
        List<CoverageMetrics> filteredMetrics = applyPackageFiltering(metrics);

        logger.info("カバレッジファイル処理完了: {}個のメトリクスを抽出（フィルタ後: {}個）",
                metrics.size(), filteredMetrics.size());

        return filteredMetrics;
    }

    /**
     * ソースメソッド情報にカバレッジメトリクスを統合
     *
     * @param sourceMethodInfos ソースメソッド情報のリスト
     * @param coverageMetrics カバレッジメトリクスのリスト
     */
    public void integrateCoverageMetrics(List<SourceMethodInfo> sourceMethodInfos,
                                       List<CoverageMetrics> coverageMetrics) {
        logger.info("カバレッジメトリクス統合開始: ソース{}個, カバレッジ{}個",
                sourceMethodInfos.size(), coverageMetrics.size());

        // カバレッジメトリクスをマップ化（高速検索用）
        Map<String, List<CoverageMetrics>> coverageByMethod = buildCoverageMap(coverageMetrics);

        int integratedCount = 0;

        for (SourceMethodInfo sourceInfo : sourceMethodInfos) {
            CoverageMetrics matchedCoverage = findMatchingCoverage(sourceInfo, coverageByMethod);

            if (matchedCoverage != null) {
                sourceInfo.setCoverageMetrics(matchedCoverage);
                integratedCount++;
                logger.debug("カバレッジ統合: {}.{} -> {:.1f}%",
                        sourceInfo.getClassName(), sourceInfo.getMethodName(),
                        matchedCoverage.getOverallCoverage());
            } else {
                logger.debug("カバレッジ未発見: {}.{}",
                        sourceInfo.getClassName(), sourceInfo.getMethodName());
            }
        }

        logger.info("カバレッジメトリクス統合完了: {}個のメソッドに統合", integratedCount);
    }

    /**
     * JaCoCo XMLレポートの解析
     */
    private List<CoverageMetrics> parseXmlCoverageReport(Path xmlFile) throws IOException {
        logger.debug("XMLカバレッジレポート解析: {}", xmlFile);

        List<CoverageMetrics> metrics = new ArrayList<>();
        String content = Files.readString(xmlFile, StandardCharsets.UTF_8);

        try {
            Document doc = Jsoup.parse(content, "", org.jsoup.parser.Parser.xmlParser());

            // パッケージ要素を検索
            Elements packages = doc.select("package");
            for (Element packageElement : packages) {
                String packageName = packageElement.attr("name");

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

                        CoverageMetrics metric = new CoverageMetrics(className, displayMethodName);
                        metric.setPackageName(packageName);
                        metric.setReportType("XML");

                        // ソースファイル名の設定
                        if (sourceFileName != null && !sourceFileName.isEmpty()) {
                            metric.setSourceFile(sourceFileName);
                        } else if (className != null && !className.isEmpty()) {
                            metric.setSourceFile(className + ".java");
                        }

                        // カウンター要素からメトリクスを抽出
                        parseCounterElements(methodElement, metric);

                        metrics.add(metric);
                        logger.debug("XMLカバレッジ抽出: {}.{} - 総合: {:.1f}%",
                                className, displayMethodName, metric.getOverallCoverage());
                    }
                }
            }

        } catch (Exception e) {
            logger.error("XMLカバレッジレポート解析エラー: {}", xmlFile, e);
            throw new IOException("XMLレポート解析に失敗しました: " + e.getMessage(), e);
        }

        return metrics;
    }

    /**
     * カウンター要素の解析
     */
    private void parseCounterElements(Element methodElement, CoverageMetrics metric) {
        Elements counters = methodElement.select("counter");
        for (Element counter : counters) {
            String type = counter.attr("type");
            int missed = parseIntAttribute(counter.attr("missed"), 0);
            int covered = parseIntAttribute(counter.attr("covered"), 0);

            switch (type) {
                case "INSTRUCTION":
                    metric.setInstructionInfo(covered, covered + missed);
                    break;
                case "BRANCH":
                    metric.setBranchInfo(covered, covered + missed);
                    break;
                case "LINE":
                    metric.setLineInfo(covered, covered + missed);
                    break;
                case "METHOD":
                    metric.setMethodInfo(covered, covered + missed);
                    break;
            }
        }
    }

    /**
     * JaCoCo HTMLレポートの解析（基本的なサポートのみ）
     */
    private List<CoverageMetrics> parseHtmlCoverageReport(Path htmlFile) throws IOException {
        logger.debug("HTMLカバレッジレポート解析: {}", htmlFile);
        logger.warn("HTMLレポートのサポートは限定的です。XMLレポートの使用を推奨します: {}", htmlFile);

        // HTMLレポートの解析は複雑で不正確なため、基本的なサポートのみ提供
        return new ArrayList<>();
    }

    /**
     * カバレッジメトリクスのマップ構築
     */
    private Map<String, List<CoverageMetrics>> buildCoverageMap(List<CoverageMetrics> metrics) {
        Map<String, List<CoverageMetrics>> coverageMap = new HashMap<>();

        for (CoverageMetrics metric : metrics) {
            // メソッド名のみでマッピング
            String methodKey = metric.getMethodName();
            coverageMap.computeIfAbsent(methodKey, k -> new ArrayList<>()).add(metric);

            // クラス名 + メソッド名でもマッピング
            String fullKey = metric.getClassName() + "." + metric.getMethodName();
            coverageMap.computeIfAbsent(fullKey, k -> new ArrayList<>()).add(metric);

            // パッケージ名 + クラス名 + メソッド名でもマッピング
            if (metric.getPackageName() != null) {
                String packageKey = metric.getPackageName().replace("/", ".") + "." +
                                  metric.getClassName() + "." + metric.getMethodName();
                coverageMap.computeIfAbsent(packageKey, k -> new ArrayList<>()).add(metric);
            }
        }

        return coverageMap;
    }

    /**
     * ソースメソッド情報にマッチするカバレッジメトリクスの検索
     */
    private CoverageMetrics findMatchingCoverage(SourceMethodInfo sourceInfo,
                                               Map<String, List<CoverageMetrics>> coverageMap) {
        // 1. 完全修飾名での検索
        String fullyQualified = sourceInfo.getFullyQualifiedMethodName();
        List<CoverageMetrics> candidates = coverageMap.get(fullyQualified);
        if (candidates != null && !candidates.isEmpty()) {
            return getBestMatch(candidates, sourceInfo);
        }

        // 2. クラス名.メソッド名での検索
        String classMethod = sourceInfo.getClassName() + "." + sourceInfo.getMethodName();
        candidates = coverageMap.get(classMethod);
        if (candidates != null && !candidates.isEmpty()) {
            return getBestMatch(candidates, sourceInfo);
        }

        // 3. メソッド名のみでの検索
        candidates = coverageMap.get(sourceInfo.getMethodName());
        if (candidates != null && !candidates.isEmpty()) {
            // クラス名での追加フィルタリング
            for (CoverageMetrics candidate : candidates) {
                if (candidate.getClassName() != null &&
                    candidate.getClassName().equals(sourceInfo.getClassName())) {
                    return candidate;
                }
            }
            // クラス名が一致しない場合は最初の候補を返す
            return candidates.get(0);
        }

        return null;
    }

    /**
     * 最適なマッチの選択
     */
    private CoverageMetrics getBestMatch(List<CoverageMetrics> candidates, SourceMethodInfo sourceInfo) {
        if (candidates.size() == 1) {
            return candidates.get(0);
        }

        // 複数候補がある場合は、クラス名とパッケージ名で絞り込み
        for (CoverageMetrics candidate : candidates) {
            if (candidate.getClassName() != null &&
                candidate.getClassName().equals(sourceInfo.getClassName()) &&
                candidate.getPackageName() != null &&
                sourceInfo.getPackageName() != null &&
                candidate.getPackageName().replace("/", ".").equals(sourceInfo.getPackageName())) {
                return candidate;
            }
        }

        // 完全一致しない場合は最初の候補を返す
        return candidates.get(0);
    }

    /**
     * パッケージフィルタリングの適用
     */
    private List<CoverageMetrics> applyPackageFiltering(List<CoverageMetrics> metrics) {
        if (targetPackages.isEmpty()) {
            return metrics; // フィルタなしの場合はそのまま返す
        }

        List<CoverageMetrics> filtered = new ArrayList<>();
        for (CoverageMetrics metric : metrics) {
            if (shouldIncludeMetric(metric)) {
                filtered.add(metric);
            }
        }

        return filtered;
    }

    /**
     * メトリクスを含めるかどうかの判定
     */
    private boolean shouldIncludeMetric(CoverageMetrics metric) {
        if (targetPackages.isEmpty()) {
            return true;
        }

        String packageName = metric.getPackageName();
        if (packageName == null) {
            return false;
        }

        // パッケージ名の正規化（/ → .）
        String normalizedPackage = packageName.replace("/", ".");

        // 対象パッケージのプレフィックスにマッチするかチェック
        for (String targetPrefix : targetPackages) {
            if (normalizedPackage.startsWith(targetPrefix)) {
                return true;
            }
        }

        return false;
    }

    /**
     * ユーティリティメソッド群
     */

    private String extractClassNameFromPath(String classPath) {
        if (classPath == null || classPath.isEmpty()) {
            return "";
        }
        String[] parts = classPath.split("/");
        return parts[parts.length - 1];
    }

    private String decodeMethodName(String methodName) {
        if (methodName == null) {
            return "";
        }

        switch (methodName) {
            case "&lt;init&gt;":
                return "<init>";
            case "&lt;clinit&gt;":
                return "static {...}";
            default:
                return methodName.replace("&lt;", "<").replace("&gt;", ">");
        }
    }

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
     * カバレッジ統計情報の取得
     */
    public Map<String, Object> getCoverageStatistics(List<CoverageMetrics> metrics) {
        Map<String, Object> stats = new HashMap<>();

        stats.put("totalMethods", metrics.size());

        // カバレッジ分布
        int highCoverage = 0;
        int mediumCoverage = 0;
        int lowCoverage = 0;
        int noCoverage = 0;

        double totalCoverage = 0.0;
        for (CoverageMetrics metric : metrics) {
            double coverage = metric.getOverallCoverage();
            totalCoverage += coverage;

            if (coverage == 0.0) {
                noCoverage++;
            } else if (coverage >= 80.0) {
                highCoverage++;
            } else if (coverage >= 50.0) {
                mediumCoverage++;
            } else {
                lowCoverage++;
            }
        }

        stats.put("averageCoverage", metrics.isEmpty() ? 0.0 : totalCoverage / metrics.size());
        stats.put("highCoverageCount", highCoverage);
        stats.put("mediumCoverageCount", mediumCoverage);
        stats.put("lowCoverageCount", lowCoverage);
        stats.put("noCoverageCount", noCoverage);

        return stats;
    }

    /**
     * 統計情報のログ出力
     */
    public void logCoverageStatistics(List<CoverageMetrics> metrics) {
        Map<String, Object> stats = getCoverageStatistics(metrics);

        logger.info("=== カバレッジ統計サマリー ===");
        logger.info("総メソッド数: {}", stats.get("totalMethods"));
        logger.info("平均カバレッジ: {:.1f}%", stats.get("averageCoverage"));
        logger.info("高カバレッジ（80%以上）: {}個", stats.get("highCoverageCount"));
        logger.info("中カバレッジ（50-79%）: {}個", stats.get("mediumCoverageCount"));
        logger.info("低カバレッジ（1-49%）: {}個", stats.get("lowCoverageCount"));
        logger.info("未カバー（0%）: {}個", stats.get("noCoverageCount"));
    }

    /**
     * JavaDocGeneratorMain用の簡単なカバレッジ統合メソッド
     */
    public void integrateCoverageData(Path coverageXmlFile, List<Path> sourceFiles) {
        try {
            if (!Files.exists(coverageXmlFile)) {
                logger.warn("カバレッジファイルが存在しません: {}", coverageXmlFile);
                return;
            }

            logger.info("カバレッジファイル解析開始: {}", coverageXmlFile);

            // カバレッジメトリクスを抽出
            List<CoverageMetrics> metrics = processCoverageFile(coverageXmlFile);

            // 統計情報をログ出力
            logCoverageStatistics(metrics);

            logger.info("カバレッジ統合完了: {}個のメトリクス処理, {}個のソースファイル",
                    metrics.size(), sourceFiles.size());

        } catch (Exception e) {
            logger.error("カバレッジ統合中にエラーが発生しました", e);
        }
    }
}