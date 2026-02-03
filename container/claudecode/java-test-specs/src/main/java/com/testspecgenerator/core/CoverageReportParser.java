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
        logger.info("[Coverage Debug] Processing coverage reports started: {} files", coverageFiles.size());
        logger.debug("[Coverage Debug] Input files: {}", coverageFiles.stream().map(Path::toString).toList());

        List<CoverageInfo> coverageData = new ArrayList<>();

        // Validate input files first
        if (coverageFiles.isEmpty()) {
            logger.warn("[Coverage Debug] No coverage files provided - coverage data will be empty");
            return coverageData;
        }

        for (int i = 0; i < coverageFiles.size(); i++) {
            Path coverageFile = coverageFiles.get(i);
            logger.debug("[Coverage Debug] Processing file {}/{}: {}", i + 1, coverageFiles.size(), coverageFile.getFileName());
            logger.debug("[Coverage Debug] File path: {}", coverageFile.toAbsolutePath());

            try {
                // Check file exists and size
                if (!Files.exists(coverageFile)) {
                    logger.error("[Coverage Debug] File does not exist: {}", coverageFile);
                    continue;
                }

                long fileSize = Files.size(coverageFile);
                logger.debug("[Coverage Debug] File size: {} bytes", fileSize);

                if (fileSize == 0) {
                    logger.warn("[Coverage Debug] File is empty: {} - skipping", coverageFile);
                    continue;
                }

                List<CoverageInfo> fileCoverage = processCoverageFile(coverageFile);
                logger.debug("[Coverage Debug] Extracted {} entries from file: {}", fileCoverage.size(), coverageFile.getFileName());
                coverageData.addAll(fileCoverage);

            } catch (Exception e) {
                logger.error("[Coverage Debug] Error processing coverage file: {} - Error: {} - Cause: {}",
                    coverageFile, e.getMessage(), e.getCause() != null ? e.getCause().getMessage() : "No specific cause");
                logger.debug("[Coverage Debug] Full stack trace for file: {}", coverageFile, e);
            }
        }

        logger.info("[Coverage Debug] Processing completed: {} total entries extracted from {} files",
            coverageData.size(), coverageFiles.size());

        // Log statistics about extracted data
        if (!coverageData.isEmpty()) {
            Map<String, Long> typeStats = coverageData.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                    CoverageInfo::getReportType,
                    java.util.stream.Collectors.counting()));
            logger.debug("[Coverage Debug] Report type statistics: {}", typeStats);

            Map<String, Long> packageStats = coverageData.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                    CoverageInfo::getPackageName,
                    java.util.stream.Collectors.counting()));
            logger.debug("[Coverage Debug] Package distribution: {}", packageStats);
        } else {
            logger.warn("[Coverage Debug] No coverage data extracted - possible reasons:");
            logger.warn("[Coverage Debug] 1. XML files do not contain JaCoCo coverage data");
            logger.warn("[Coverage Debug] 2. Files are in unsupported format (HTML-only without XML)");
            logger.warn("[Coverage Debug] 3. Package filtering excluded all entries");
            logger.warn("[Coverage Debug] 4. XML structure does not match expected JaCoCo format");
            logger.warn("[Coverage Debug] Recommendation: Run 'mvn test jacoco:report' to generate proper XML reports");
        }

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
        logger.debug("[Coverage Debug] Processing single file: {} (type: {})", fileName,
            fileName.endsWith(".xml") ? "XML" : fileName.endsWith(".html") ? "HTML" : "UNKNOWN");

        List<CoverageInfo> coverageInfos;
        if (fileName.endsWith(".xml")) {
            logger.debug("[Coverage Debug] Parsing XML coverage report: {}", coverageFile);
            coverageInfos = parseXmlCoverageReport(coverageFile);
            logger.debug("[Coverage Debug] XML parsing result: {} entries extracted", coverageInfos.size());
        } else if (fileName.endsWith(".html")) {
            logger.debug("[Coverage Debug] HTML file detected: {} - HTML parsing is disabled", coverageFile);
            logger.warn("[Coverage Debug] HTML reports are not processed - use XML reports instead");
            logger.warn("[Coverage Debug] Reason: HTML parsing is unreliable and inaccurate compared to XML");
            logger.warn("[Coverage Debug] Solution: Run 'mvn test jacoco:report' to generate XML reports");
            coverageInfos = parseHtmlCoverageReport(coverageFile);
        } else {
            logger.warn("[Coverage Debug] Unsupported file format: {} - Expected .xml or .html", coverageFile);
            logger.warn("[Coverage Debug] File will be skipped - no coverage data extracted");
            return new ArrayList<>();
        }

        logger.debug("[Coverage Debug] Starting package filtering - Raw entries: {}", coverageInfos.size());
        if (coverageInfos.isEmpty()) {
            logger.warn("[Coverage Debug] No coverage entries found in file: {}", coverageFile);
            logger.warn("[Coverage Debug] Possible reasons:");
            logger.warn("[Coverage Debug] 1. File is not a valid JaCoCo report");
            logger.warn("[Coverage Debug] 2. File structure does not match expected XML format");
            logger.warn("[Coverage Debug] 3. File contains no coverage data");
            return coverageInfos;
        }

        // Package filtering: Only exclude tool's own packages - include ALL user packages
        List<CoverageInfo> filteredCoverage = new ArrayList<>();
        int excludedToolPackages = 0;
        int excludedByPackageFilter = 0;

        for (CoverageInfo coverage : coverageInfos) {
            String packageName = coverage.getPackageName();
            logger.trace("[Coverage Debug] Evaluating entry: {}.{} in package: {}",
                coverage.getClassName(), coverage.getMethodName(), packageName);

            if (packageName != null) {
                // Always exclude tool's own package
                if (packageName.startsWith("com.testspecgenerator") || packageName.startsWith("com/testspecgenerator")) {
                    excludedToolPackages++;
                    logger.trace("[Coverage Debug] Excluded tool package: {}", packageName);
                    continue;
                }

                // If allowedPackages is provided, use dynamic filtering
                if (allowedPackages != null && !allowedPackages.isEmpty()) {
                    boolean isAllowed = false;
                    String normalizedPackage = packageName.replace('/', '.');
                    logger.trace("[Coverage Debug] Checking package '{}' against allowed: {}", normalizedPackage, allowedPackages);

                    for (String allowedPackage : allowedPackages) {
                        if (normalizedPackage.startsWith(allowedPackage)) {
                            isAllowed = true;
                            logger.trace("[Coverage Debug] Package match found: '{}' matches '{}'", normalizedPackage, allowedPackage);
                            break;
                        }
                    }

                    if (isAllowed) {
                        filteredCoverage.add(coverage);
                        logger.debug("[Coverage Debug] Coverage entry added: {}.{} (package: {}, branch: {:.1f}%)",
                            coverage.getClassName(), coverage.getMethodName(), packageName, coverage.getBranchCoverage());
                    } else {
                        excludedByPackageFilter++;
                        logger.trace("[Coverage Debug] Excluded by package filter: {}", normalizedPackage);
                    }
                } else {
                    // No package filtering - include ALL packages except tool's own packages
                    logger.trace("[Coverage Debug] No package filter applied - including all packages for: {}", packageName);
                    filteredCoverage.add(coverage);
                    logger.debug("[Coverage Debug] Coverage entry added (no filtering): {}.{} (package: {}, branch: {:.1f}%)",
                        coverage.getClassName(), coverage.getMethodName(), packageName, coverage.getBranchCoverage());
                }
            } else {
                logger.debug("[Coverage Debug] Skipping entry with null package: {}.{}",
                    coverage.getClassName(), coverage.getMethodName());
            }
        }

        String filterDescription = (allowedPackages != null && !allowedPackages.isEmpty())
            ? allowedPackages.toString()
            : "ALL PACKAGES (no filtering)";
        logger.info("[Coverage Debug] Filtering completed: Total: {} -> Filtered: {} (Filter: {})",
            coverageInfos.size(), filteredCoverage.size(), filterDescription);
        logger.debug("[Coverage Debug] Filter statistics: Tool packages excluded: {}, Package filter excluded: {}",
            excludedToolPackages, excludedByPackageFilter);

        if (filteredCoverage.isEmpty() && !coverageInfos.isEmpty()) {
            logger.warn("[Coverage Debug] All coverage entries were filtered out!");
            logger.warn("[Coverage Debug] Original packages found:");
            Set<String> originalPackages = coverageInfos.stream()
                .map(CoverageInfo::getPackageName)
                .filter(Objects::nonNull)
                .collect(java.util.stream.Collectors.toSet());
            originalPackages.forEach(pkg -> logger.warn("[Coverage Debug] - {}", pkg));
            logger.warn("[Coverage Debug] Applied filter: {}", filterDescription);
            logger.warn("[Coverage Debug] Note: Tool accepts ALL packages except com.testspecgenerator (tool's own packages)");
        }

        return filteredCoverage;
    }

    /**
     * JaCoCo XMLレポートを解析
     */
    private List<CoverageInfo> parseXmlCoverageReport(Path xmlFile) throws IOException {
        logger.debug("[Coverage Debug] Starting XML coverage report analysis: {}", xmlFile);

        List<CoverageInfo> coverageInfos = new ArrayList<>();

        try {
            String content = Files.readString(xmlFile, StandardCharsets.UTF_8);
            logger.debug("[Coverage Debug] File content length: {} characters", content.length());

            // Check if content looks like XML
            if (!content.trim().startsWith("<?xml") && !content.trim().startsWith("<report")) {
                logger.error("[Coverage Debug] File does not appear to be XML format: {}", xmlFile);
                logger.error("[Coverage Debug] File starts with: '{}'", content.length() > 100 ? content.substring(0, 100) + "..." : content);
                throw new IOException("File is not in XML format");
            }

            // JaCoCo XMLの構造を解析
            logger.debug("[Coverage Debug] Parsing XML content with JSoup XML parser");
            Document doc = Jsoup.parse(content, "", org.jsoup.parser.Parser.xmlParser());

            // Check if it's a JaCoCo report
            Element reportElement = doc.selectFirst("report");
            if (reportElement == null) {
                logger.error("[Coverage Debug] Not a JaCoCo XML report - missing <report> element");
                logger.error("[Coverage Debug] Root element: {}", doc.children().isEmpty() ? "None" : doc.children().first().tagName());
                throw new IOException("Not a valid JaCoCo XML report format");
            }

            String reportName = reportElement.attr("name");
            logger.debug("[Coverage Debug] JaCoCo report found: '{}'", reportName);

            // パッケージ要素を検索
            Elements packages = doc.select("package");
            logger.debug("[Coverage Debug] Found {} packages in XML report", packages.size());

            if (packages.isEmpty()) {
                logger.warn("[Coverage Debug] No packages found in XML report - report may be empty");
                logger.warn("[Coverage Debug] This can happen if no tests were executed or no code was covered");
                return coverageInfos;
            }

            int totalClasses = 0;
            int totalMethods = 0;

            for (int pkgIndex = 0; pkgIndex < packages.size(); pkgIndex++) {
                Element packageElement = packages.get(pkgIndex);
                String packageName = packageElement.attr("name");
                logger.debug("[Coverage Debug] Processing package {}/{}: '{}'", pkgIndex + 1, packages.size(), packageName);

                // クラス要素を検索
                Elements classes = packageElement.select("class");
                totalClasses += classes.size();
                logger.debug("[Coverage Debug] Package '{}' contains {} classes", packageName, classes.size());

                if (classes.isEmpty()) {
                    logger.warn("[Coverage Debug] No class elements found in package '{}'", packageName);
                    logger.debug("[Coverage Debug] Package element HTML: {}", packageElement.html().substring(0, Math.min(200, packageElement.html().length())));
                }

                for (int classIndex = 0; classIndex < classes.size(); classIndex++) {
                    Element classElement = classes.get(classIndex);
                    String classPath = classElement.attr("name");
                    String className = extractClassNameFromPath(classPath);
                    String sourceFileName = classElement.attr("sourcefilename");

                    // Enhanced debug logging for null investigation
                    logger.debug("[Coverage Debug] RAW CLASS DATA - classPath='{}', className='{}', sourceFile='{}'",
                        classPath, className, sourceFileName);
                    logger.trace("[Coverage Debug] Processing class {}/{} in package '{}': '{}' (source: '{}')",
                        classIndex + 1, classes.size(), packageName, className, sourceFileName);

                    // メソッド要素を検索
                    Elements methods = classElement.select("method");
                    totalMethods += methods.size();
                    logger.trace("[Coverage Debug] Class '{}' contains {} methods", className, methods.size());

                    for (int methodIndex = 0; methodIndex < methods.size(); methodIndex++) {
                        Element methodElement = methods.get(methodIndex);
                        String methodName = methodElement.attr("name");
                        int line = parseIntAttribute(methodElement.attr("line"), 0);

                        logger.trace("[Coverage Debug] Processing method {}/{}: '{}' (line: {})",
                            methodIndex + 1, methods.size(), methodName, line);

                        // メソッド名の特殊文字をデコード
                        String displayMethodName = decodeMethodName(methodName);
                        if (!methodName.equals(displayMethodName)) {
                            logger.trace("[Coverage Debug] Method name decoded: '{}' -> '{}'", methodName, displayMethodName);
                        }

                        // Null safety checks
                        String safeClassName = (className != null && !className.isEmpty()) ? className : "UnknownClass";
                        String safeMethodName = (displayMethodName != null && !displayMethodName.isEmpty()) ? displayMethodName : "unknownMethod";

                        CoverageInfo coverageInfo = new CoverageInfo(safeClassName, safeMethodName);
                        coverageInfo.setPackageName(packageName);
                        coverageInfo.setReportType("XML");

                        // ソースファイル名の設定（nullチェックと特殊ケースの処理）
                        String finalSourceFile = "";
                        if (sourceFileName != null && !sourceFileName.isEmpty()) {
                            finalSourceFile = sourceFileName;
                        } else if (className != null && !className.isEmpty()) {
                            // ソースファイル名が取得できない場合はクラス名から推測
                            finalSourceFile = className + ".java";
                            logger.trace("[Coverage Debug] Source file name inferred: '{}'", finalSourceFile);
                        }
                        coverageInfo.setSourceFile(finalSourceFile);

                        // カウンター要素からメトリクスを抽出
                        Elements counters = methodElement.select("counter");
                        logger.trace("[Coverage Debug] Method '{}' has {} counters", displayMethodName, counters.size());

                        if (counters.isEmpty()) {
                            logger.trace("[Coverage Debug] No counters found for method '{}' - method may not be covered", displayMethodName);
                        }

                        for (Element counter : counters) {
                            String type = counter.attr("type");
                            int missed = parseIntAttribute(counter.attr("missed"), 0);
                            int covered = parseIntAttribute(counter.attr("covered"), 0);
                            int total = covered + missed;

                            logger.trace("[Coverage Debug] Counter type '{}': covered={}, missed={}, total={}, coverage={:.1f}%",
                                type, covered, missed, total, total > 0 ? (covered * 100.0 / total) : 0.0);

                            switch (type) {
                                case "INSTRUCTION":
                                    coverageInfo.setInstructionInfo(covered, total);
                                    break;
                                case "BRANCH":
                                    coverageInfo.setBranchInfo(covered, total);
                                    break;
                                case "LINE":
                                    coverageInfo.setLineInfo(covered, total);
                                    break;
                                case "METHOD":
                                    coverageInfo.setMethodInfo(covered, total);
                                    break;
                                default:
                                    logger.trace("[Coverage Debug] Unknown counter type: '{}'", type);
                            }
                        }

                        coverageInfos.add(coverageInfo);
                        logger.debug("[Coverage Debug] XML coverage entry extracted: {}.{} - Branch: {:.1f}%, Instruction: {:.1f}%",
                                className, displayMethodName, coverageInfo.getBranchCoverage(), coverageInfo.getInstructionCoverage());
                    }
                }
            }

            logger.info("[Coverage Debug] XML parsing summary: {} packages, {} classes, {} methods, {} coverage entries",
                packages.size(), totalClasses, totalMethods, coverageInfos.size());

        } catch (Exception e) {
            logger.error("[Coverage Debug] XML coverage report parsing failed: {}", xmlFile);
            logger.error("[Coverage Debug] Error type: {}, Message: {}", e.getClass().getSimpleName(), e.getMessage());
            if (e.getCause() != null) {
                logger.error("[Coverage Debug] Root cause: {}", e.getCause().getMessage());
            }
            logger.debug("[Coverage Debug] Full error details for XML parsing", e);

            // Provide specific guidance based on error type
            if (e instanceof java.nio.charset.MalformedInputException) {
                logger.error("[Coverage Debug] File encoding issue - try different character encoding");
            } else if (e.getMessage().contains("XML")) {
                logger.error("[Coverage Debug] XML structure issue - verify file is valid JaCoCo XML report");
            } else if (e instanceof java.nio.file.NoSuchFileException) {
                logger.error("[Coverage Debug] File not found - check file path and permissions");
            }

            throw new IOException("Failed to parse XML coverage report", e);
        }

        logger.debug("[Coverage Debug] XML coverage report analysis completed: {} entries extracted", coverageInfos.size());
        return coverageInfos;
    }

    /**
     * JaCoCo HTMLレポートを解析
     * 注：HTMLレポートはXMLレポートより精度が低いため、可能な限りXMLレポートを使用することを推奨
     */
    private List<CoverageInfo> parseHtmlCoverageReport(Path htmlFile) throws IOException {
        logger.debug("[Coverage Debug] HTML coverage report analysis requested: {}", htmlFile);

        List<CoverageInfo> coverageInfos = new ArrayList<>();

        // HTMLレポートの処理は複雑で不正確なため、スキップすることを推奨
        logger.warn("[Coverage Debug] HTML report parsing is disabled: {}", htmlFile);
        logger.warn("[Coverage Debug] Reasons for disabling HTML parsing:");
        logger.warn("[Coverage Debug] 1. HTML parsing is unreliable and inaccurate");
        logger.warn("[Coverage Debug] 2. XML reports provide complete and structured data");
        logger.warn("[Coverage Debug] 3. HTML structure can vary between JaCoCo versions");
        logger.warn("[Coverage Debug] 4. Method-level coverage details are not easily extractable from HTML");

        // Check if corresponding XML file exists
        String htmlFileName = htmlFile.getFileName().toString();
        Path parentDir = htmlFile.getParent();

        if (parentDir != null) {
            Path possibleXmlFile = parentDir.resolve("jacoco.xml");
            logger.debug("[Coverage Debug] Checking for XML alternative: {}", possibleXmlFile);

            if (Files.exists(possibleXmlFile)) {
                logger.warn("[Coverage Debug] XML report found: {} - Use this instead of HTML", possibleXmlFile);
                logger.warn("[Coverage Debug] XML file size: {} bytes", Files.size(possibleXmlFile));
            } else {
                logger.warn("[Coverage Debug] No XML report found in same directory: {}", parentDir);
                logger.warn("[Coverage Debug] Generate XML report with: mvn test jacoco:report");
            }
        }

        // Provide file information for debugging
        try {
            long fileSize = Files.size(htmlFile);
            logger.debug("[Coverage Debug] HTML file size: {} bytes", fileSize);

            if (fileSize > 0) {
                logger.debug("[Coverage Debug] HTML file exists and has content - but parsing is intentionally disabled");
                logger.debug("[Coverage Debug] Alternative solutions:");
                logger.debug("[Coverage Debug] - Run 'mvn test jacoco:report' to generate XML reports");
                logger.debug("[Coverage Debug] - Ensure jacoco.xml is available in target/site/jacoco/");
                logger.debug("[Coverage Debug] - Copy jacoco.xml to coverage-reports/ directory if using source-dir filtering");
            } else {
                logger.warn("[Coverage Debug] HTML file is empty: {}", htmlFile);
            }
        } catch (IOException e) {
            logger.warn("[Coverage Debug] Cannot read HTML file: {} - {}", htmlFile, e.getMessage());
        }

        logger.info("[Coverage Debug] HTML parsing completed (0 entries) - XML reports required for coverage data");
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
        logger.debug("[Coverage Debug] Coverage merge started: {} test cases, {} coverage entries", testCases.size(), coverageData.size());

        if (testCases.isEmpty()) {
            logger.warn("[Coverage Debug] No test cases to merge coverage data with");
            return;
        }

        if (coverageData.isEmpty()) {
            logger.warn("[Coverage Debug] No coverage data available for merging");
            logger.warn("[Coverage Debug] All test cases will have 0% coverage");
            return;
        }

        // カバレッジデータをマップ化（高速検索用）
        logger.debug("[Coverage Debug] Building coverage lookup maps");
        Map<String, List<CoverageInfo>> coverageByMethod = new HashMap<>();
        Map<String, Set<String>> coverageClassesByMethod = new HashMap<>();

        for (CoverageInfo coverage : coverageData) {
            String methodKey = coverage.getMethodName();
            coverageByMethod.computeIfAbsent(methodKey, k -> new ArrayList<>()).add(coverage);
            coverageClassesByMethod.computeIfAbsent(methodKey, k -> new HashSet<>()).add(coverage.getClassName());

            // クラス名もキーとして保存（完全一致用）
            String fullKey = coverage.getClassName() + "." + coverage.getMethodName();
            coverageByMethod.computeIfAbsent(fullKey, k -> new ArrayList<>()).add(coverage);

            logger.trace("[Coverage Debug] Added to lookup: method='{}', fullKey='{}', class='{}'",
                methodKey, fullKey, coverage.getClassName());
        }

        logger.debug("[Coverage Debug] Coverage lookup built: {} unique method keys, {} unique full keys",
            coverageByMethod.size(), coverageByMethod.keySet().stream().mapToInt(key -> key.contains(".") ? 1 : 0).sum());

        // 各テストケースに対応するカバレッジ情報を検索
        int successfulMatches = 0;
        int failedMatches = 0;

        for (int i = 0; i < testCases.size(); i++) {
            TestCaseInfo testCase = testCases.get(i);
            logger.debug("[Coverage Debug] Processing test case {}/{}: {}.{}",
                i + 1, testCases.size(), testCase.getClassName(), testCase.getMethodName());

            // テストクラス名から実装クラス名を推定（パッケージを保持してTestのみ除去）
            String implClassName = testCase.getClassName();
            String testMethodName = testCase.getMethodName();

            // 複数パターンでの実装クラス名推定
            String[] implCandidates = new String[4];
            implCandidates[0] = implClassName; // そのまま
            implCandidates[1] = implClassName.replace("Test", ""); // Test除去
            if (implClassName.endsWith("Test")) {
                implCandidates[2] = implClassName.substring(0, implClassName.length() - 4); // 末尾Test除去
            } else {
                implCandidates[2] = implClassName;
            }
            // テストパッケージをメインパッケージに変換
            implCandidates[3] = implClassName.replace(".test.", ".").replace("Test", "");

            logger.trace("[Coverage Debug] Implementation class candidates: {} from test class: '{}'",
                java.util.Arrays.toString(implCandidates), testCase.getClassName());

            // テストメソッド名から実際のメソッド名を推定（複数のパターンを生成）
            String[] targetMethodCandidates = new String[6];
            targetMethodCandidates[0] = testMethodName; // そのまま

            if (testMethodName.startsWith("test")) {
                String stripped = testMethodName.substring(4);
                if (stripped.length() > 0) {
                    String lowercased = Character.toLowerCase(stripped.charAt(0)) +
                                       (stripped.length() > 1 ? stripped.substring(1) : "");
                    targetMethodCandidates[1] = lowercased; // testXxx -> xxx

                    // CamelCase分割パターン
                    for (int j = 1; j < lowercased.length(); j++) {
                        if (Character.isUpperCase(lowercased.charAt(j))) {
                            targetMethodCandidates[2] = lowercased.substring(0, j); // 最初の大文字まで
                            break;
                        }
                    }
                    // アンダースコア分割パターン
                    if (lowercased.contains("_")) {
                        targetMethodCandidates[3] = lowercased.substring(0, lowercased.indexOf("_"));
                    }
                    // 共通パターン（Valid, Invalid, Test, Case等を除去）
                    String cleaned = lowercased
                        .replaceFirst("Valid$", "")
                        .replaceFirst("Invalid$", "")
                        .replaceFirst("Test$", "")
                        .replaceFirst("Case$", "");
                    targetMethodCandidates[4] = cleaned;
                }
            }
            // ケースインセンシティブな検索用
            targetMethodCandidates[5] = testMethodName.toLowerCase();

            logger.trace("[Coverage Debug] Method name candidates: {} from test method: '{}'",
                java.util.Arrays.toString(targetMethodCandidates), testMethodName);

            logger.debug("[Coverage Debug] Target method candidates generated: {} for test method: '{}'",
                java.util.Arrays.toString(targetMethodCandidates), testMethodName);

            // 複数の候補パターンで検索
            CoverageInfo coverage = null;
            String matchStrategy = "none";
            String finalImplClassName = null;
            String finalMethodName = null;

            // 複数の実装クラス候補とメソッド名候補を組み合わせて検索
            outerLoop: for (String classCandidate : implCandidates) {
                if (classCandidate == null || classCandidate.isEmpty()) continue;

                // 正規化：パッケージ区切りを統一
                String normalizedClass = classCandidate.replace("/", ".");

                for (String methodCandidate : targetMethodCandidates) {
                    if (methodCandidate == null || methodCandidate.isEmpty()) continue;

                    // 1. フルキー検索（クラス名.メソッド名）
                    String fullKey = normalizedClass + "." + methodCandidate;
                    List<CoverageInfo> candidates = coverageByMethod.get(fullKey);
                    logger.trace("[Coverage Debug] Full key lookup: '{}' -> {} candidates",
                        fullKey, candidates != null ? candidates.size() : 0);

                    if (candidates != null && !candidates.isEmpty()) {
                        coverage = candidates.get(0);
                        matchStrategy = "full-key";
                        finalImplClassName = normalizedClass;
                        finalMethodName = methodCandidate;
                        logger.debug("[Coverage Debug] Coverage match (full key): {} -> {} (coverage: {:.1f}%)",
                            testCase.getMethodName(), fullKey, coverage.getBranchCoverage());
                        break outerLoop;
                    }

                    // 2. クラス名短縮 + メソッド名検索
                    String shortClassName = normalizedClass;
                    if (shortClassName.contains(".")) {
                        shortClassName = shortClassName.substring(shortClassName.lastIndexOf(".") + 1);
                    }
                    String shortKey = shortClassName + "." + methodCandidate;
                    candidates = coverageByMethod.get(shortKey);
                    logger.trace("[Coverage Debug] Short key lookup: '{}' -> {} candidates",
                        shortKey, candidates != null ? candidates.size() : 0);

                    if (candidates != null && !candidates.isEmpty()) {
                        coverage = candidates.get(0);
                        matchStrategy = "short-key";
                        finalImplClassName = normalizedClass;
                        finalMethodName = methodCandidate;
                        logger.debug("[Coverage Debug] Coverage match (short key): {} -> {} (coverage: {:.1f}%)",
                            testCase.getMethodName(), shortKey, coverage.getBranchCoverage());
                        break outerLoop;
                    }
                }
            }

            // 3. メソッド名のみで検索（最後の手段）
            if (coverage == null) {
                for (String methodCandidate : targetMethodCandidates) {
                    if (methodCandidate == null || methodCandidate.isEmpty()) continue;

                    List<CoverageInfo> methodCandidates = coverageByMethod.get(methodCandidate);
                    logger.trace("[Coverage Debug] Method only lookup: '{}' -> {} candidates",
                        methodCandidate, methodCandidates != null ? methodCandidates.size() : 0);

                    if (methodCandidates != null && !methodCandidates.isEmpty()) {
                        // 最初の候補を使用（パッケージ問わず）
                        coverage = methodCandidates.get(0);
                        matchStrategy = "method-only";
                        finalImplClassName = coverage.getClassName();
                        finalMethodName = methodCandidate;
                        logger.debug("[Coverage Debug] Coverage match (method only): {} -> {}.{} (coverage: {:.1f}%)",
                            testCase.getMethodName(), coverage.getClassName(), methodCandidate, coverage.getBranchCoverage());
                        break;
                    }
                }
            }

            if (coverage != null) {
                // カバレッジ情報をテストケースに設定
                testCase.setCoveragePercent(coverage.getBranchCoverage());
                testCase.setBranchesCovered(coverage.getBranchesCovered());
                testCase.setBranchesTotal(coverage.getBranchesTotal());
                successfulMatches++;

                logger.debug("[Coverage Debug] Coverage merge successful: {} -> {:.1f}% (strategy: {}, branch: {}/{}, instruction: {:.1f}%)",
                    testCase.getMethodName(), testCase.getCoveragePercent(), matchStrategy,
                    coverage.getBranchesCovered(), coverage.getBranchesTotal(), coverage.getInstructionCoverage());
            } else {
                failedMatches++;
                logger.debug("[Coverage Debug] Coverage match failed: {} (class candidates: {}, method candidates: '{}')",
                    testCase.getMethodName(), java.util.Arrays.toString(implCandidates),
                    java.util.Arrays.toString(targetMethodCandidates));
                logger.trace("[Coverage Debug] Available coverage methods: {}",
                    coverageByMethod.keySet().stream().filter(key -> !key.contains(".")).limit(10).toList());
                logger.trace("[Coverage Debug] Available coverage classes: {}",
                    coverageByMethod.values().stream().flatMap(List::stream)
                        .map(CoverageInfo::getClassName).distinct().limit(10).toList());
            }
        }

        logger.info("[Coverage Debug] Coverage merge completed: {} successful matches, {} failed matches out of {} test cases",
            successfulMatches, failedMatches, testCases.size());

        if (failedMatches > 0) {
            logger.warn("[Coverage Debug] {} test cases have no coverage data", failedMatches);
            logger.warn("[Coverage Debug] Possible reasons for failed matches:");
            logger.warn("[Coverage Debug] 1. Test method names don't match implementation method names");
            logger.warn("[Coverage Debug] 2. Implementation classes are not covered by any tests");
            logger.warn("[Coverage Debug] 3. Package structure differs between test and implementation");
            logger.warn("[Coverage Debug] 4. JaCoCo report doesn't include all executed methods");
            logger.warn("[Coverage Debug] 5. Class name patterns don't match (e.g., UserServiceTest vs UserService)");

            if (logger.isDebugEnabled()) {
                logger.debug("[Coverage Debug] Sample coverage methods available:");
                coverageByMethod.keySet().stream()
                    .filter(key -> !key.contains("."))
                    .limit(5)
                    .forEach(method -> logger.debug("[Coverage Debug] - {}", method));
            }
        }
    }

    /**
     * クラスパスからクラス名を抽出
     */
    private String extractClassNameFromPath(String classPath) {
        logger.debug("[Coverage Debug] extractClassNameFromPath input: '{}'", classPath);

        if (classPath == null || classPath.isEmpty()) {
            logger.debug("[Coverage Debug] classPath is null/empty, returning 'UnknownClass'");
            return "UnknownClass";
        }

        // パッケージパス区切りの最後の要素を取得
        String[] parts = classPath.split("/");
        logger.debug("[Coverage Debug] classPath split result: {} parts", parts.length);

        if (parts.length == 0) {
            logger.debug("[Coverage Debug] No parts after split, returning 'UnknownClass'");
            return "UnknownClass";
        }

        String className = parts[parts.length - 1];
        logger.debug("[Coverage Debug] Extracted className: '{}'", className);

        // 空文字の場合のsafety check
        if (className == null || className.isEmpty()) {
            logger.debug("[Coverage Debug] Extracted className is null/empty, returning 'UnknownClass'");
            return "UnknownClass";
        }

        // 内部クラスの場合の処理
        // 注：匿名内部クラスは元のまま残す（FolderScanner$1など）
        // ただし、通常の内部クラスは親クラス名を返す

        logger.debug("[Coverage Debug] Final className result: '{}'", className);
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

        logger.info("[Coverage Debug] ========== Coverage Analysis Summary ==========");
        logger.info("[Coverage Debug] Total entries: {}", stats.get("totalEntries"));
        logger.info("[Coverage Debug] XML reports: {}, HTML reports: {}", stats.get("xmlReports"), stats.get("htmlReports"));
        logger.info("[Coverage Debug] Average branch coverage: {:.1f}%", stats.get("averageBranchCoverage"));
        logger.info("[Coverage Debug] High coverage (80%+): {} entries", stats.get("highCoverageCount"));

        if (coverageData.isEmpty()) {
            logger.warn("[Coverage Debug] No coverage data available!");
            logger.warn("[Coverage Debug] This indicates one of the following issues:");
            logger.warn("[Coverage Debug] 1. No JaCoCo XML reports were found");
            logger.warn("[Coverage Debug] 2. XML reports were found but contain no coverage data");
            logger.warn("[Coverage Debug] 3. All coverage entries were filtered out");
            logger.warn("[Coverage Debug] 4. Tests were not executed before generating reports");
            logger.warn("[Coverage Debug] Solution: Run 'mvn clean compile test jacoco:report' to generate complete coverage data");
        } else {
            // Additional detailed statistics
            Map<String, Long> packageDistribution = coverageData.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                    CoverageInfo::getPackageName,
                    java.util.stream.Collectors.counting()));

            logger.debug("[Coverage Debug] Package distribution:");
            packageDistribution.forEach((pkg, count) ->
                logger.debug("[Coverage Debug] - {}: {} entries", pkg != null ? pkg : "null", count));

            // Coverage quality distribution
            long excellent = coverageData.stream().mapToLong(c -> c.getBranchCoverage() >= 95.0 ? 1 : 0).sum();
            long good = coverageData.stream().mapToLong(c -> c.getBranchCoverage() >= 80.0 && c.getBranchCoverage() < 95.0 ? 1 : 0).sum();
            long fair = coverageData.stream().mapToLong(c -> c.getBranchCoverage() >= 60.0 && c.getBranchCoverage() < 80.0 ? 1 : 0).sum();
            long poor = coverageData.stream().mapToLong(c -> c.getBranchCoverage() < 60.0 ? 1 : 0).sum();

            logger.info("[Coverage Debug] Coverage quality distribution:");
            logger.info("[Coverage Debug] - Excellent (95%+): {} entries", excellent);
            logger.info("[Coverage Debug] - Good (80-95%): {} entries", good);
            logger.info("[Coverage Debug] - Fair (60-80%): {} entries", fair);
            logger.info("[Coverage Debug] - Poor (<60%): {} entries", poor);

            // Method name patterns analysis
            Map<String, Long> methodPatterns = coverageData.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                    c -> c.getMethodName().startsWith("<") ? "special" :
                         c.getMethodName().startsWith("get") || c.getMethodName().startsWith("set") ? "accessor" :
                         c.getMethodName().startsWith("is") || c.getMethodName().startsWith("has") ? "boolean" : "regular",
                    java.util.stream.Collectors.counting()));

            logger.debug("[Coverage Debug] Method type distribution: {}", methodPatterns);
        }

        logger.info("[Coverage Debug] ============================================");
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