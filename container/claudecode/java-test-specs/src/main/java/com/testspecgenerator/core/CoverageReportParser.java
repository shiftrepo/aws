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
        logger.debug("[Map Conversion Debug] Coverage report processing started: {} files", coverageFiles.size());

        List<CoverageInfo> coverageInfos = processCoverageReports(coverageFiles, testFiles);
        logger.debug("[Map Conversion Debug] CoverageInfo processing completed: {} entries extracted", coverageInfos.size());

        // Convert to Map format for compatibility
        Map<String, Object> coverageData = new java.util.HashMap<>();
        logger.debug("[Map Conversion Debug] Map conversion started: converting {} entries to Map", coverageInfos.size());

        if (coverageInfos.isEmpty()) {
            logger.warn("[Map Conversion Debug] Coverage data is empty - returning empty Map");
            logger.warn("[Map Conversion Debug] Possible causes:");
            logger.warn("[Map Conversion Debug] 1. Coverage files not found");
            logger.warn("[Map Conversion Debug] 2. XML file parsing failed");
            logger.warn("[Map Conversion Debug] 3. All entries excluded by package filtering");
            logger.warn("[Map Conversion Debug] 4. JaCoCo report not generated");
            return coverageData;
        }

        for (int i = 0; i < coverageInfos.size(); i++) {
            CoverageInfo coverage = coverageInfos.get(i);
            String mapKey = "coverage_" + i;

            logger.trace("[Map Conversion Debug] エントリ{}/{}: キー='{}', クラス='{}'",
                        i + 1, coverageInfos.size(), mapKey, coverage.getClassName());

            Map<String, Object> coverageMap = convertCoverageInfoToMap(coverage);
            coverageData.put(mapKey, coverageMap);

            // 詳細ログ: 変換前後の数値確認
            logger.debug("[Map Conversion Debug] Conversion completed {}/{}: {}.{}", i + 1, coverageInfos.size(),
                        coverage.getClassName(), coverage.getMethodName());
            logger.debug("[Map Conversion Debug] - Branch: {}% ({}/{})",
                        coverage.getBranchCoverage(), coverage.getBranchesCovered(), coverage.getBranchesTotal());
            logger.debug("[Map Conversion Debug] - Instruction: {}% ({}/{})",
                        coverage.getInstructionCoverage(), coverage.getInstructionsCovered(), coverage.getInstructionsTotal());
            logger.debug("[Map Conversion Debug] - Line: {}% ({}/{})",
                        coverage.getLineCoverage(), coverage.getLinesCovered(), coverage.getLinesTotal());

            // Verify values after Map conversion
            logger.trace("[Map Conversion Debug] Verification after Map conversion:");
            logger.trace("[Map Conversion Debug] - branchesCovered: {}", coverageMap.get("branchesCovered"));
            logger.trace("[Map Conversion Debug] - branchesTotal: {}", coverageMap.get("branchesTotal"));
            logger.trace("[Map Conversion Debug] - branchCoverage: {}", coverageMap.get("branchCoverage"));
            logger.trace("[Map Conversion Debug] - instructionsCovered: {}", coverageMap.get("instructionsCovered"));
            logger.trace("[Map Conversion Debug] - instructionsTotal: {}", coverageMap.get("instructionsTotal"));
            logger.trace("[Map Conversion Debug] - instructionCoverage: {}", coverageMap.get("instructionCoverage"));
        }

        logger.info("[Map Conversion Debug] Coverage data Map conversion completed: {} entries -> {} Map entries",
                   coverageInfos.size(), coverageData.size());

        // Map overall statistics
        if (!coverageData.isEmpty()) {
            int totalWithBranchData = 0;
            double totalBranchCoverage = 0.0;

            for (Map.Entry<String, Object> entry : coverageData.entrySet()) {
                if (entry.getValue() instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> itemMap = (Map<String, Object>) entry.getValue();

                    Object branchCoverageObj = itemMap.get("branchCoverage");
                    if (branchCoverageObj instanceof Number) {
                        double branchCoverage = ((Number) branchCoverageObj).doubleValue();
                        if (branchCoverage > 0) {
                            totalWithBranchData++;
                            totalBranchCoverage += branchCoverage;
                        }
                    }
                }
            }

            logger.debug("[Map Conversion Debug] Map statistics: {} entries total, {} entries with branch data, average: {}%",
                        coverageData.size(), totalWithBranchData,
                        totalWithBranchData > 0 ? totalBranchCoverage / totalWithBranchData : 0.0);
        }

        return coverageData;
    }

    /**
     * 複数のカバレッジレポートファイルを処理し、動的パッケージフィルタリングを適用して結合された結果を返します
     */
    public List<CoverageInfo> processCoverageReports(List<Path> coverageFiles, List<Path> testFiles) {
        logger.info("[Coverage Debug LINE-BY-LINE] ========== COVERAGE PROCESSING STARTED ==========");
        logger.info("[Coverage Debug LINE-BY-LINE] Input: {} coverage files", coverageFiles.size());
        logger.debug("[Coverage Debug LINE-BY-LINE] Coverage file list:");
        for (int idx = 0; idx < coverageFiles.size(); idx++) {
            logger.debug("[Coverage Debug LINE-BY-LINE]   File {}: {}", idx + 1, coverageFiles.get(idx));
        }

        List<CoverageInfo> coverageData = new ArrayList<>();
        logger.debug("[Coverage Debug LINE-BY-LINE] Created empty coverageData list (size={})", coverageData.size());

        // Validate input files first
        if (coverageFiles.isEmpty()) {
            logger.warn("[Coverage Debug LINE-BY-LINE] No coverage files provided - returning empty list");
            return coverageData;
        }

        logger.debug("[Coverage Debug LINE-BY-LINE] Starting file-by-file processing loop");
        for (int i = 0; i < coverageFiles.size(); i++) {
            Path coverageFile = coverageFiles.get(i);
            logger.info("[Coverage Debug LINE-BY-LINE] ========== Processing file {}/{} ==========", i + 1, coverageFiles.size());
            logger.info("[Coverage Debug LINE-BY-LINE] File name: {}", coverageFile.getFileName());
            logger.info("[Coverage Debug LINE-BY-LINE] File path: {}", coverageFile.toAbsolutePath());

            try {
                // Check file exists and size
                boolean fileExists = Files.exists(coverageFile);
                logger.debug("[Coverage Debug LINE-BY-LINE] File exists check: {}", fileExists);

                if (!fileExists) {
                    logger.error("[Coverage Debug LINE-BY-LINE] File does not exist - skipping: {}", coverageFile);
                    continue;
                }

                long fileSize = Files.size(coverageFile);
                logger.info("[Coverage Debug LINE-BY-LINE] File size: {} bytes", fileSize);

                if (fileSize == 0) {
                    logger.warn("[Coverage Debug LINE-BY-LINE] File is empty - skipping: {}", coverageFile);
                    continue;
                }

                logger.debug("[Coverage Debug LINE-BY-LINE] Calling processCoverageFile() for: {}", coverageFile.getFileName());
                int beforeSize = coverageData.size();
                logger.debug("[Coverage Debug LINE-BY-LINE] coverageData size BEFORE processing: {}", beforeSize);

                List<CoverageInfo> fileCoverage = processCoverageFile(coverageFile);
                logger.info("[Coverage Debug LINE-BY-LINE] processCoverageFile() returned {} entries", fileCoverage.size());

                if (fileCoverage.isEmpty()) {
                    logger.warn("[Coverage Debug LINE-BY-LINE] No coverage entries extracted from file: {}", coverageFile.getFileName());
                } else {
                    logger.debug("[Coverage Debug LINE-BY-LINE] Sample entries from file:");
                    int sampleCount = Math.min(3, fileCoverage.size());
                    for (int j = 0; j < sampleCount; j++) {
                        CoverageInfo sample = fileCoverage.get(j);
                        logger.debug("[Coverage Debug LINE-BY-LINE]   Entry {}: {}.{} (package: {}, branch: {}%)",
                            j + 1, sample.getClassName(), sample.getMethodName(), sample.getPackageName(), sample.getBranchCoverage());
                    }
                }

                logger.debug("[Coverage Debug LINE-BY-LINE] Adding {} entries to coverageData", fileCoverage.size());
                coverageData.addAll(fileCoverage);
                int afterSize = coverageData.size();
                logger.info("[Coverage Debug LINE-BY-LINE] coverageData size AFTER adding: {} (added: {})", afterSize, afterSize - beforeSize);

            } catch (Exception e) {
                logger.error("[Coverage Debug LINE-BY-LINE] ========== EXCEPTION OCCURRED ==========");
                logger.error("[Coverage Debug LINE-BY-LINE] File: {}", coverageFile);
                logger.error("[Coverage Debug LINE-BY-LINE] Exception type: {}", e.getClass().getName());
                logger.error("[Coverage Debug LINE-BY-LINE] Exception message: {}", e.getMessage());
                if (e.getCause() != null) {
                    logger.error("[Coverage Debug LINE-BY-LINE] Root cause: {}", e.getCause().getMessage());
                }
                logger.error("[Coverage Debug LINE-BY-LINE] Full stack trace:", e);
            }
        }

        logger.info("[Coverage Debug LINE-BY-LINE] ========== FILE PROCESSING LOOP COMPLETED ==========");
        logger.info("[Coverage Debug LINE-BY-LINE] FINAL coverageData size: {}", coverageData.size());
        logger.info("[Coverage Debug LINE-BY-LINE] Total entries extracted from {} files: {}", coverageFiles.size(), coverageData.size());

        // Log statistics about extracted data
        if (!coverageData.isEmpty()) {
            logger.debug("[Coverage Debug LINE-BY-LINE] Calculating statistics for {} entries", coverageData.size());

            Map<String, Long> typeStats = coverageData.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                    CoverageInfo::getReportType,
                    java.util.stream.Collectors.counting()));
            logger.info("[Coverage Debug LINE-BY-LINE] Report type statistics: {}", typeStats);

            Map<String, Long> packageStats = coverageData.stream()
                .collect(java.util.stream.Collectors.groupingBy(
                    CoverageInfo::getPackageName,
                    java.util.stream.Collectors.counting()));
            logger.info("[Coverage Debug LINE-BY-LINE] Package distribution: {}", packageStats);

            logger.debug("[Coverage Debug LINE-BY-LINE] Listing all package names:");
            packageStats.keySet().forEach(pkg -> logger.debug("[Coverage Debug LINE-BY-LINE]   - {}", pkg));
        } else {
            logger.warn("[Coverage Debug LINE-BY-LINE] ========== NO COVERAGE DATA EXTRACTED ==========");
            logger.warn("[Coverage Debug LINE-BY-LINE] Possible reasons:");
            logger.warn("[Coverage Debug LINE-BY-LINE] 1. XML files do not contain JaCoCo coverage data");
            logger.warn("[Coverage Debug LINE-BY-LINE] 2. Files are in unsupported format (HTML-only without XML)");
            logger.warn("[Coverage Debug LINE-BY-LINE] 3. Package filtering excluded all entries");
            logger.warn("[Coverage Debug LINE-BY-LINE] 4. XML structure does not match expected JaCoCo format");
            logger.warn("[Coverage Debug LINE-BY-LINE] 5. All coverage entries were filtered out");
            logger.warn("[Coverage Debug LINE-BY-LINE] Recommendation: Run 'mvn test jacoco:report' to generate proper XML reports");
        }

        logger.info("[Coverage Debug LINE-BY-LINE] ========== RETURNING {} ENTRIES ==========", coverageData.size());
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

        logger.info("[Coverage Debug LINE-BY-LINE] ========== PACKAGE FILTERING STARTED ==========");
        logger.info("[Coverage Debug LINE-BY-LINE] Raw entries BEFORE filtering: {}", coverageInfos.size());
        logger.info("[Coverage Debug LINE-BY-LINE] allowedPackages parameter: {}", allowedPackages);

        if (coverageInfos.isEmpty()) {
            logger.warn("[Coverage Debug LINE-BY-LINE] No coverage entries found in file: {}", coverageFile);
            logger.warn("[Coverage Debug LINE-BY-LINE] Possible reasons:");
            logger.warn("[Coverage Debug LINE-BY-LINE] 1. File is not a valid JaCoCo report");
            logger.warn("[Coverage Debug LINE-BY-LINE] 2. File structure does not match expected XML format");
            logger.warn("[Coverage Debug LINE-BY-LINE] 3. File contains no coverage data");
            return coverageInfos;
        }

        // Log all raw entries before filtering
        logger.debug("[Coverage Debug LINE-BY-LINE] Listing ALL {} raw entries:", coverageInfos.size());
        for (int i = 0; i < coverageInfos.size(); i++) {
            CoverageInfo info = coverageInfos.get(i);
            logger.debug("[Coverage Debug LINE-BY-LINE]   Raw entry {}: {}.{} (package: {}, branch: {}%)",
                i + 1, info.getClassName(), info.getMethodName(), info.getPackageName(), info.getBranchCoverage());
        }

        // Package filtering: Only exclude tool's own packages - include ALL user packages
        List<CoverageInfo> filteredCoverage = new ArrayList<>();
        int excludedToolPackages = 0;
        int excludedByPackageFilter = 0;

        logger.info("[Coverage Debug LINE-BY-LINE] Starting filtering loop (entry-by-entry)");
        for (int i = 0; i < coverageInfos.size(); i++) {
            CoverageInfo coverage = coverageInfos.get(i);
            String packageName = coverage.getPackageName();
            String className = coverage.getClassName();
            String methodName = coverage.getMethodName();

            logger.debug("[Coverage Debug LINE-BY-LINE] ===== Entry {}/{} =====", i + 1, coverageInfos.size());
            logger.debug("[Coverage Debug LINE-BY-LINE] Class: {}", className);
            logger.debug("[Coverage Debug LINE-BY-LINE] Method: {}", methodName);
            logger.debug("[Coverage Debug LINE-BY-LINE] Package: {}", packageName);
            logger.debug("[Coverage Debug LINE-BY-LINE] Branch coverage: {}% ({}/{})",
                coverage.getBranchCoverage(), coverage.getBranchesCovered(), coverage.getBranchesTotal());

            if (packageName != null) {
                logger.debug("[Coverage Debug LINE-BY-LINE] Package is not null - proceeding with filter check");

                // NOTE: Package exclusion removed to support any package names
                // Previously excluded com.testspecgenerator packages causing mapping failures

                // If allowedPackages is provided, use dynamic filtering
                if (allowedPackages != null && !allowedPackages.isEmpty()) {
                    logger.debug("[Coverage Debug LINE-BY-LINE] allowedPackages filter IS PROVIDED: {}", allowedPackages);

                    boolean isAllowed = false;
                    String normalizedPackage = packageName.replace('/', '.');
                    logger.debug("[Coverage Debug LINE-BY-LINE] Normalized package name: '{}' (original: '{}')", normalizedPackage, packageName);

                    logger.debug("[Coverage Debug LINE-BY-LINE] Checking against {} allowed packages:", allowedPackages.size());
                    for (String allowedPackage : allowedPackages) {
                        logger.debug("[Coverage Debug LINE-BY-LINE]   Checking if '{}' starts with '{}'", normalizedPackage, allowedPackage);
                        if (normalizedPackage.startsWith(allowedPackage)) {
                            isAllowed = true;
                            logger.info("[Coverage Debug LINE-BY-LINE]   MATCH FOUND: '{}' matches '{}'", normalizedPackage, allowedPackage);
                            break;
                        } else {
                            logger.debug("[Coverage Debug LINE-BY-LINE]   No match: '{}' does not start with '{}'", normalizedPackage, allowedPackage);
                        }
                    }

                    if (isAllowed) {
                        logger.info("[Coverage Debug LINE-BY-LINE] ADDING entry (passed filter): {}.{}", className, methodName);
                        filteredCoverage.add(coverage);
                        logger.debug("[Coverage Debug LINE-BY-LINE] filteredCoverage size now: {}", filteredCoverage.size());
                    } else {
                        excludedByPackageFilter++;
                        logger.warn("[Coverage Debug LINE-BY-LINE] EXCLUDING entry (failed filter): {}.{} (package: {})",
                            className, methodName, normalizedPackage);
                        logger.debug("[Coverage Debug LINE-BY-LINE] excludedByPackageFilter count now: {}", excludedByPackageFilter);
                    }
                } else {
                    // No package filtering - include ALL packages
                    logger.info("[Coverage Debug LINE-BY-LINE] NO package filter - ADDING entry: {}.{} (package: {})",
                        className, methodName, packageName);
                    filteredCoverage.add(coverage);
                    logger.debug("[Coverage Debug LINE-BY-LINE] filteredCoverage size now: {}", filteredCoverage.size());
                }
            } else {
                logger.warn("[Coverage Debug LINE-BY-LINE] SKIPPING entry with NULL package: {}.{}", className, methodName);
            }
        }

        String filterDescription = (allowedPackages != null && !allowedPackages.isEmpty())
            ? allowedPackages.toString()
            : "ALL PACKAGES (no filtering)";
        logger.info("[Coverage Debug LINE-BY-LINE] ========== FILTERING COMPLETED ==========");
        logger.info("[Coverage Debug LINE-BY-LINE] Total entries BEFORE filtering: {}", coverageInfos.size());
        logger.info("[Coverage Debug LINE-BY-LINE] Total entries AFTER filtering: {}", filteredCoverage.size());
        logger.info("[Coverage Debug LINE-BY-LINE] Filter description: {}", filterDescription);
        logger.info("[Coverage Debug LINE-BY-LINE] Excluded by tool package filter: {}", excludedToolPackages);
        logger.info("[Coverage Debug LINE-BY-LINE] Excluded by allowedPackages filter: {}", excludedByPackageFilter);

        if (filteredCoverage.isEmpty() && !coverageInfos.isEmpty()) {
            logger.error("[Coverage Debug LINE-BY-LINE] ========== ALL ENTRIES WERE FILTERED OUT ==========");
            logger.error("[Coverage Debug LINE-BY-LINE] This is the root cause of 0% coverage!");

            Set<String> originalPackages = coverageInfos.stream()
                .map(CoverageInfo::getPackageName)
                .filter(Objects::nonNull)
                .collect(java.util.stream.Collectors.toSet());

            logger.error("[Coverage Debug LINE-BY-LINE] Original packages found ({}): ", originalPackages.size());
            originalPackages.forEach(pkg -> logger.error("[Coverage Debug LINE-BY-LINE]   - {}", pkg));

            logger.error("[Coverage Debug LINE-BY-LINE] Applied filter: {}", filterDescription);
            if (allowedPackages != null && !allowedPackages.isEmpty()) {
                logger.error("[Coverage Debug LINE-BY-LINE] Allowed packages ({}): ", allowedPackages.size());
                allowedPackages.forEach(pkg -> logger.error("[Coverage Debug LINE-BY-LINE]   - {}", pkg));
                logger.error("[Coverage Debug LINE-BY-LINE] PROBLEM: None of the original packages matched any allowed packages!");
            } else {
                logger.error("[Coverage Debug LINE-BY-LINE] PROBLEM: No filtering should be applied but all entries were still excluded!");
            }
        }

        logger.info("[Coverage Debug LINE-BY-LINE] ========== RETURNING {} FILTERED ENTRIES ==========", filteredCoverage.size());
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
                logger.info("[Coverage Debug LINE-BY-LINE] ========== Processing package {}/{} ==========", pkgIndex + 1, packages.size());
                logger.info("[Coverage Debug LINE-BY-LINE] Package name RAW: '{}'", packageName);
                logger.debug("[Coverage Debug LINE-BY-LINE] Package element tag: {}", packageElement.tagName());
                logger.debug("[Coverage Debug LINE-BY-LINE] Package element has 'name' attribute: {}", packageElement.hasAttr("name"));

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

                    logger.info("[Coverage Debug LINE-BY-LINE] --- Processing class {}/{} in package '{}' ---", classIndex + 1, classes.size(), packageName);
                    logger.info("[Coverage Debug LINE-BY-LINE] RAW classPath attribute: '{}'", classPath);
                    logger.info("[Coverage Debug LINE-BY-LINE] Extracted className: '{}'", className);
                    logger.info("[Coverage Debug LINE-BY-LINE] Source file name: '{}'", sourceFileName);
                    logger.debug("[Coverage Debug LINE-BY-LINE] Class element tag: {}", classElement.tagName());
                    logger.debug("[Coverage Debug LINE-BY-LINE] Class element has 'name' attribute: {}", classElement.hasAttr("name"));

                    // メソッド要素を検索
                    Elements methods = classElement.select("method");
                    totalMethods += methods.size();
                    logger.trace("[Coverage Debug] Class '{}' contains {} methods", className, methods.size());

                    for (int methodIndex = 0; methodIndex < methods.size(); methodIndex++) {
                        Element methodElement = methods.get(methodIndex);
                        String methodName = methodElement.attr("name");
                        int line = parseIntAttribute(methodElement.attr("line"), 0);

                        logger.info("[Coverage Debug LINE-BY-LINE] +++ Processing method {}/{} +++", methodIndex + 1, methods.size());
                        logger.info("[Coverage Debug LINE-BY-LINE] RAW method name: '{}'", methodName);
                        logger.info("[Coverage Debug LINE-BY-LINE] Method line number: {}", line);

                        // メソッド名の特殊文字をデコード
                        String displayMethodName = decodeMethodName(methodName);
                        if (!methodName.equals(displayMethodName)) {
                            logger.debug("[Coverage Debug LINE-BY-LINE] Method name DECODED: '{}' -> '{}'", methodName, displayMethodName);
                        } else {
                            logger.debug("[Coverage Debug LINE-BY-LINE] Method name (no decoding needed): '{}'", displayMethodName);
                        }

                        // Null safety checks
                        logger.debug("[Coverage Debug LINE-BY-LINE] Performing null safety checks");
                        logger.debug("[Coverage Debug LINE-BY-LINE]   className: '{}' (isNull: {})", className, className == null);
                        logger.debug("[Coverage Debug LINE-BY-LINE]   displayMethodName: '{}' (isNull: {})", displayMethodName, displayMethodName == null);

                        String safeClassName = (className != null && !className.isEmpty()) ? className : "UnknownClass";
                        String safeMethodName = (displayMethodName != null && !displayMethodName.isEmpty()) ? displayMethodName : "unknownMethod";

                        logger.info("[Coverage Debug LINE-BY-LINE] Creating CoverageInfo object:");
                        logger.info("[Coverage Debug LINE-BY-LINE]   - className: '{}'", safeClassName);
                        logger.info("[Coverage Debug LINE-BY-LINE]   - methodName: '{}'", safeMethodName);
                        logger.info("[Coverage Debug LINE-BY-LINE]   - packageName: '{}'", packageName);

                        CoverageInfo coverageInfo = new CoverageInfo(safeClassName, safeMethodName);
                        coverageInfo.setPackageName(packageName);
                        coverageInfo.setReportType("XML");
                        logger.debug("[Coverage Debug LINE-BY-LINE] CoverageInfo object created, packageName set to: '{}'", coverageInfo.getPackageName());

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

                            logger.trace("[Coverage Debug] Counter type '{}': covered={}, missed={}, total={}, coverage={}%",
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

                        int beforeAdd = coverageInfos.size();
                        logger.debug("[Coverage Debug LINE-BY-LINE] coverageInfos list size BEFORE add: {}", beforeAdd);

                        coverageInfos.add(coverageInfo);

                        int afterAdd = coverageInfos.size();
                        logger.info("[Coverage Debug LINE-BY-LINE] CoverageInfo ADDED to list (size: {} -> {})", beforeAdd, afterAdd);
                        logger.info("[Coverage Debug LINE-BY-LINE] Added entry: {}.{} (package: {}, branch: {}%, instruction: {}%)",
                                safeClassName, safeMethodName, packageName,
                                coverageInfo.getBranchCoverage(), coverageInfo.getInstructionCoverage());
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
                        logger.debug("[Coverage Debug] Coverage match (full key): {} -> {} (coverage: {}%)",
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
                        logger.debug("[Coverage Debug] Coverage match (short key): {} -> {} (coverage: {}%)",
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
                        logger.debug("[Coverage Debug] Coverage match (method only): {} -> {}.{} (coverage: {}%)",
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

                logger.debug("[Coverage Debug] Coverage merge successful: {} -> {}% (strategy: {}, branch: {}/{}, instruction: {}%)",
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
        logger.debug("[Statistics Debug] Statistics calculation started: {} entries", coverageData.size());
        Map<String, Object> stats = new HashMap<>();

        // 基本統計
        int totalEntries = coverageData.size();
        stats.put("totalEntries", totalEntries);
        logger.debug("[Statistics Debug] 基本統計 - 総エントリ数: {}", totalEntries);

        if (totalEntries == 0) {
            logger.warn("[Statistics Debug] Coverage data is empty - all statistics will be 0");
            stats.put("xmlReports", 0L);
            stats.put("htmlReports", 0L);
            stats.put("averageBranchCoverage", 0.0);
            stats.put("highCoverageCount", 0L);
            return stats;
        }

        // レポートタイプ別統計（1行ずつデバッグ）
        logger.debug("[Statistics Debug] レポートタイプ別統計計算開始");
        long xmlReports = 0;
        long htmlReports = 0;

        for (int i = 0; i < coverageData.size(); i++) {
            CoverageInfo coverage = coverageData.get(i);
            String reportType = coverage.getReportType();
            logger.trace("[Statistics Debug] エントリ{}/{}: クラス={}, メソッド={}, レポートタイプ='{}'",
                        i + 1, totalEntries, coverage.getClassName(), coverage.getMethodName(), reportType);

            if ("XML".equals(reportType)) {
                xmlReports++;
                logger.trace("[Statistics Debug] XMLレポート数: {} (+1)", xmlReports);
            } else {
                htmlReports++;
                logger.trace("[Statistics Debug] HTMLレポート数: {} (+1)", htmlReports);
            }
        }

        stats.put("xmlReports", xmlReports);
        stats.put("htmlReports", htmlReports);
        logger.debug("[Statistics Debug] レポートタイプ統計完了 - XML: {}, HTML: {}", xmlReports, htmlReports);

        // カバレッジ統計（1行ずつデバッグ）
        logger.debug("[Statistics Debug] ブランチカバレッジ統計計算開始");
        double totalBranchCoverage = 0.0;
        int validCoverageEntries = 0;
        double minCoverage = Double.MAX_VALUE;
        double maxCoverage = Double.MIN_VALUE;

        for (int i = 0; i < coverageData.size(); i++) {
            CoverageInfo coverage = coverageData.get(i);
            double branchCoverage = coverage.getBranchCoverage();

            logger.trace("[Statistics Debug] Coverage calculation {}/{}: {}.{} = {}% (branch: {}/{}, instruction: {}%)",
                        i + 1, totalEntries, coverage.getClassName(), coverage.getMethodName(),
                        branchCoverage, coverage.getBranchesCovered(), coverage.getBranchesTotal(),
                        coverage.getInstructionCoverage());

            if (!Double.isNaN(branchCoverage) && branchCoverage >= 0.0) {
                totalBranchCoverage += branchCoverage;
                validCoverageEntries++;
                minCoverage = Math.min(minCoverage, branchCoverage);
                maxCoverage = Math.max(maxCoverage, branchCoverage);
                logger.trace("[Statistics Debug] 累積カバレッジ: {:.2f}%, 有効エントリ数: {}", totalBranchCoverage, validCoverageEntries);
            } else {
                logger.trace("[Statistics Debug] 無効なカバレッジ値をスキップ: {}", branchCoverage);
            }
        }

        double averageBranchCoverage = validCoverageEntries > 0 ? totalBranchCoverage / validCoverageEntries : 0.0;
        stats.put("averageBranchCoverage", averageBranchCoverage);

        logger.debug("[Statistics Debug] Branch coverage statistics completed:");
        logger.debug("[Statistics Debug] - Average: {}% (valid entries: {}/{})", averageBranchCoverage, validCoverageEntries, totalEntries);
        logger.debug("[Statistics Debug] - Range: {}% - {}%",
                    minCoverage != Double.MAX_VALUE ? minCoverage : 0.0,
                    maxCoverage != Double.MIN_VALUE ? maxCoverage : 0.0);

        // High coverage cases (80% or higher)
        logger.debug("[Statistics Debug] High coverage case calculation started (80% or higher)");
        long highCoverageCount = 0;

        for (int i = 0; i < coverageData.size(); i++) {
            CoverageInfo coverage = coverageData.get(i);
            double branchCoverage = coverage.getBranchCoverage();

            if (branchCoverage >= 80.0) {
                highCoverageCount++;
                logger.trace("[Statistics Debug] High coverage {}: {}.{} = {}%",
                           highCoverageCount, coverage.getClassName(), coverage.getMethodName(), branchCoverage);
            }
        }

        stats.put("highCoverageCount", highCoverageCount);
        logger.debug("[Statistics Debug] High coverage case calculation completed: {} entries ({}%)",
                    highCoverageCount, totalEntries > 0 ? (highCoverageCount * 100 / totalEntries) : 0);

        logger.info("[Statistics Debug] Statistics calculation completed - Total entries: {}, XML: {}, Average coverage: {}%, High coverage: {}",
                   totalEntries, xmlReports, averageBranchCoverage, highCoverageCount);

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
        logger.info("[Coverage Debug] Average branch coverage: {}%", stats.get("averageBranchCoverage"));
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
                .limit(200) // Only check first 200 lines for package declaration
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
        logger.trace("[Convert Debug] Map変換開始: {}.{}", coverage.getClassName(), coverage.getMethodName());

        Map<String, Object> map = new java.util.HashMap<>();

        // 基本情報
        String className = coverage.getClassName();
        String methodName = coverage.getMethodName();
        String packageName = coverage.getPackageName();

        map.put("className", className);
        map.put("methodName", methodName);
        map.put("packageName", packageName);

        logger.trace("[Convert Debug] 基本情報設定: class='{}', method='{}', package='{}'",
                    className, methodName, packageName);

        // Coverage percentages - 元の値をログ出力
        double branchCoverage = coverage.getBranchCoverage();
        double lineCoverage = coverage.getLineCoverage();
        double instructionCoverage = coverage.getInstructionCoverage();
        double methodCoverage = coverage.getMethodCoverage();

        map.put("branchCoverage", branchCoverage);
        map.put("lineCoverage", lineCoverage);
        map.put("instructionCoverage", instructionCoverage);
        map.put("methodCoverage", methodCoverage);

        logger.trace("[Convert Debug] Coverage rates set: branch={}%, line={}%, instruction={}%, method={}%",
                    branchCoverage, lineCoverage, instructionCoverage, methodCoverage);

        // Coverage counts - Most important data (if lost, will display 0%)
        int branchesCovered = coverage.getBranchesCovered();
        int branchesTotal = coverage.getBranchesTotal();
        int linesCovered = coverage.getLinesCovered();
        int linesTotal = coverage.getLinesTotal();
        int instructionsCovered = coverage.getInstructionsCovered();
        int instructionsTotal = coverage.getInstructionsTotal();
        int methodsCovered = coverage.getMethodsCovered();
        int methodsTotal = coverage.getMethodsTotal();

        map.put("branchesCovered", branchesCovered);
        map.put("branchesTotal", branchesTotal);
        map.put("linesCovered", linesCovered);
        map.put("linesTotal", linesTotal);
        map.put("instructionsCovered", instructionsCovered);
        map.put("instructionsTotal", instructionsTotal);
        map.put("methodsCovered", methodsCovered);
        map.put("methodsTotal", methodsTotal);

        logger.info("[Convert Debug] Coverage counts set for {}.{}: Branch={}/{} ({}%), Line={}/{}, Instruction={}/{}, Method={}/{}",
                    className, methodName,
                    branchesCovered, branchesTotal, branchesTotal > 0 ? (branchesCovered * 100.0 / branchesTotal) : 0.0,
                    linesCovered, linesTotal,
                    instructionsCovered, instructionsTotal,
                    methodsCovered, methodsTotal);
        logger.info("[Convert Debug] Map entry types after put: branchesCovered={} ({}), branchesTotal={} ({})",
                    map.get("branchesCovered"),
                    map.get("branchesCovered") != null ? map.get("branchesCovered").getClass().getSimpleName() : "null",
                    map.get("branchesTotal"),
                    map.get("branchesTotal") != null ? map.get("branchesTotal").getClass().getSimpleName() : "null");

        // Data validation: Check if important values are lost
        if (branchesTotal == 0 && instructionsTotal == 0 && linesTotal == 0) {
            logger.warn("[Convert Debug] WARNING: {}.{} - All coverage totals are 0. Data may not be extracted correctly",
                       className, methodName);
        } else if (branchesCovered == 0 && instructionsCovered == 0 && linesCovered == 0) {
            logger.warn("[Convert Debug] 警告: {}.{} - 全てのカバレッジ実行数が0です。テストが実行されていない可能性があります",
                       className, methodName);
        }

        // Additional metadata
        String sourceFile = coverage.getSourceFile();
        String reportType = coverage.getReportType();

        map.put("sourceFile", sourceFile);
        map.put("reportType", reportType);

        logger.trace("[Convert Debug] メタデータ設定: sourceFile='{}', reportType='{}'", sourceFile, reportType);

        // 最終的なMap内容の検証
        logger.trace("[Convert Debug] Map変換完了: {} フィールド設定, キー: {}",
                    map.size(), map.keySet());

        // クリティカルなフィールドの存在確認
        boolean hasCriticalData = map.containsKey("branchesCovered") && map.containsKey("branchesTotal") &&
                                 map.get("branchesCovered") != null && map.get("branchesTotal") != null;

        if (!hasCriticalData) {
            logger.error("[Convert Debug] エラー: 重要なカバレッジデータがMapに設定されていません: {}.{}",
                        className, methodName);
        }

        return map;
    }
}