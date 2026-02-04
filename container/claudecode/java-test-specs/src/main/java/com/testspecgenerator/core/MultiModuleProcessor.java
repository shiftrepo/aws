package com.testspecgenerator.core;

import com.testspecgenerator.model.ModuleInfo;
import com.testspecgenerator.model.ModuleResult;
import com.testspecgenerator.model.TestCaseInfo;
import com.testspecgenerator.model.CoverageInfo;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

/**
 * Handles the processing of Maven multi-module projects including parallel
 * processing of modules, combined report generation, and individual module reports.
 */
public class MultiModuleProcessor {
    private static final Logger LOGGER = Logger.getLogger(MultiModuleProcessor.class.getName());
    private final ExecutorService executorService;
    private final int maxConcurrency;

    public MultiModuleProcessor() {
        this.maxConcurrency = Math.max(2, Runtime.getRuntime().availableProcessors());
        this.executorService = Executors.newFixedThreadPool(maxConcurrency);
        LOGGER.info("MultiModuleProcessor initialized with " + maxConcurrency + " threads");
    }

    /**
     * Processes all modules in a multi-module project and generates reports.
     *
     * @param modules list of modules to process
     * @param outputDir directory for output files
     * @param csvOutput whether to generate CSV files
     * @return list of processing results for each module
     */
    public List<ModuleResult> processAllModules(List<ModuleInfo> modules, Path outputDir, boolean csvOutput) {
        LOGGER.info("Processing " + modules.size() + " modules with output directory: " + outputDir);

        try {
            Files.createDirectories(outputDir);
        } catch (IOException e) {
            throw new RuntimeException("Failed to create output directory: " + outputDir, e);
        }

        // Filter valid modules
        List<ModuleInfo> validModules = modules.stream()
            .filter(ModuleInfo::isValid)
            .collect(Collectors.toList());

        List<ModuleInfo> invalidModules = modules.stream()
            .filter(m -> !m.isValid())
            .collect(Collectors.toList());

        if (!invalidModules.isEmpty()) {
            LOGGER.warning("Skipping " + invalidModules.size() + " invalid modules:");
            invalidModules.forEach(m -> LOGGER.warning("  - " + m.getModuleName() + ": " + m.getValidationError()));
        }

        if (validModules.isEmpty()) {
            LOGGER.warning("No valid modules to process");
            return new ArrayList<>();
        }

        // Process modules in parallel
        List<ModuleResult> results = processModulesInParallel(validModules);

        // Add skipped modules to results
        for (ModuleInfo invalidModule : invalidModules) {
            ModuleResult skippedResult = ModuleResult.builder()
                .moduleInfo(invalidModule)
                .processingStatus(ModuleResult.ProcessingStatus.SKIPPED)
                .errorMessage(invalidModule.getValidationError())
                .build();
            results.add(skippedResult);
        }

        // Generate combined report
        try {
            generateCombinedReport(results, outputDir, csvOutput);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to generate combined report", e);
        }

        // Generate individual module reports
        for (ModuleResult result : results) {
            if (result.isSuccessful()) {
                try {
                    generateModuleReport(result, outputDir, csvOutput);
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Failed to generate report for module: " +
                              result.getModuleInfo().getModuleName(), e);
                }
            }
        }

        // Generate summary report
        try {
            generateSummaryReport(results, outputDir);
        } catch (Exception e) {
            LOGGER.log(Level.WARNING, "Failed to generate summary report", e);
        }

        return results;
    }

    /**
     * Processes modules in parallel using a thread pool.
     */
    private List<ModuleResult> processModulesInParallel(List<ModuleInfo> modules) {
        LOGGER.info("Processing " + modules.size() + " modules in parallel");

        List<Future<ModuleResult>> futures = new ArrayList<>();

        for (ModuleInfo module : modules) {
            Future<ModuleResult> future = executorService.submit(() -> processSingleModule(module));
            futures.add(future);
        }

        List<ModuleResult> results = new ArrayList<>();
        for (int i = 0; i < futures.size(); i++) {
            try {
                ModuleResult result = futures.get(i).get(30, TimeUnit.MINUTES); // 30 minute timeout per module
                results.add(result);

                String status = result.isSuccessful() ? "OK" : "ERROR";
                LOGGER.info(String.format("%s Module processed: %s (%d test cases, %.0fms)",
                    status, result.getModuleInfo().getModuleName(),
                    result.hasTestCases() ? result.getTestCases().size() : 0,
                    (double) result.getProcessingTimeMs()));

            } catch (TimeoutException e) {
                ModuleInfo module = modules.get(i);
                LOGGER.severe("Module processing timeout: " + module.getModuleName());
                ModuleResult timeoutResult = ModuleResult.builder()
                    .moduleInfo(module)
                    .failed("Processing timeout (30 minutes)")
                    .build();
                results.add(timeoutResult);
            } catch (Exception e) {
                ModuleInfo module = modules.get(i);
                LOGGER.log(Level.SEVERE, "Module processing error: " + module.getModuleName(), e);
                ModuleResult errorResult = ModuleResult.builder()
                    .moduleInfo(module)
                    .failed("Processing error: " + e.getMessage())
                    .build();
                results.add(errorResult);
            }
        }

        return results;
    }

    /**
     * Processes a single module using the existing 4-step pipeline.
     */
    private ModuleResult processSingleModule(ModuleInfo module) {
        long startTime = System.currentTimeMillis();
        LOGGER.fine("Processing module: " + module.getModuleName());

        try {
            ModuleResult.Builder resultBuilder = ModuleResult.builder()
                .moduleInfo(module);

            // Step 1: Scan for test files
            FolderScanner scanner = new FolderScanner();
            List<Path> testFiles = scanner.scanForJavaFiles(module.getTestDir());

            if (testFiles.isEmpty()) {
                LOGGER.info("No test files found in module: " + module.getModuleName());
                return resultBuilder
                    .testCases(new ArrayList<>())
                    .coverageData(new HashMap<>())
                    .processingTimeMs(System.currentTimeMillis() - startTime)
                    .build();
            }

            // Step 2: Parse annotations
            LOGGER.info(String.format("[Detail Log] Module %s - Annotation analysis started: %d test files", module.getModuleName(), testFiles.size()));
            JavaAnnotationParser annotationParser = new JavaAnnotationParser();
            List<TestCaseInfo> testCases = new ArrayList<>();

            for (Path testFile : testFiles) {
                try {
                    List<TestCaseInfo> fileTestCases = annotationParser.processJavaFile(testFile);
                    testCases.addAll(fileTestCases);
                    LOGGER.info(String.format("[詳細ログ] モジュール %s - ファイル処理完了: %s (%d テストケース)",
                               module.getModuleName(), testFile.getFileName(), fileTestCases.size()));
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Failed to parse test file: " + testFile, e);
                }
            }

            LOGGER.info(String.format("[詳細ログ] モジュール %s - アノテーション解析完了: %d テストケース抽出", module.getModuleName(), testCases.size()));

            // Step 3: Parse coverage reports
            LOGGER.info(String.format("[詳細ログ] モジュール %s - カバレッジレポート解析開始", module.getModuleName()));
            CoverageReportParser coverageParser = new CoverageReportParser();
            Map<String, Object> coverageData = new HashMap<>();

            try {
                // Look for coverage reports in the module
                List<Path> coverageFiles = scanner.scanForCoverageReports(module.getModuleRoot());
                if (!coverageFiles.isEmpty()) {
                    coverageData = coverageParser.parseCoverageReports(coverageFiles, testFiles);
                } else {
                    LOGGER.info("No coverage reports found for module: " + module.getModuleName());
                }
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Failed to parse coverage for module: " + module.getModuleName(), e);
                // Continue without coverage data
            }

            return resultBuilder
                .testCases(testCases)
                .coverageData(coverageData)
                .processingTimeMs(System.currentTimeMillis() - startTime)
                .build();

        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to process module: " + module.getModuleName(), e);
            return ModuleResult.builder()
                .moduleInfo(module)
                .failed("Processing failed: " + e.getMessage())
                .processingTimeMs(System.currentTimeMillis() - startTime)
                .build();
        }
    }

    /**
     * Generates a combined report containing data from all modules.
     */
    public void generateCombinedReport(List<ModuleResult> results, Path outputDir, boolean csvOutput) throws IOException {
        LOGGER.info("Generating combined report");

        List<ModuleResult> successfulResults = results.stream()
            .filter(ModuleResult::isSuccessful)
            .collect(Collectors.toList());

        if (successfulResults.isEmpty()) {
            LOGGER.warning("No successful modules to generate combined report");
            return;
        }

        // Combine all test cases
        List<TestCaseInfo> allTestCases = new ArrayList<>();
        Map<String, Object> allCoverageData = new HashMap<>();

        for (ModuleResult result : successfulResults) {
            // Add module name to each test case
            if (result.hasTestCases()) {
                for (TestCaseInfo testCase : result.getTestCases()) {
                    // Create a copy with module information (we'll need to modify TestCaseInfo to support this)
                    allTestCases.add(testCase);
                }
            }

            if (result.hasCoverageData()) {
                // Prefix coverage data keys with module name to avoid conflicts
                String modulePrefix = result.getModuleInfo().getModuleName() + ".";
                for (Map.Entry<String, Object> entry : result.getCoverageData().entrySet()) {
                    allCoverageData.put(modulePrefix + entry.getKey(), entry.getValue());
                }
            }
        }

        // Generate Excel report
        Path excelOutput = outputDir.resolve("combined-report.xlsx");
        ExcelSheetBuilder excelBuilder = new ExcelSheetBuilder();

        // We need to extend ExcelSheetBuilder to support module information
        excelBuilder.generateCombinedReport(allTestCases, allCoverageData, excelOutput.toString(), results);

        LOGGER.info("Combined Excel report generated: " + excelOutput);

        // Generate CSV files if requested
        if (csvOutput) {
            CsvSheetBuilder csvBuilder = new CsvSheetBuilder();

            Path csvTestDetails = outputDir.resolve("combined-report_test_details.csv");
            Path csvCoverage = outputDir.resolve("combined-report_coverage.csv");

            csvBuilder.generateCombinedCsvFiles(allTestCases, allCoverageData, csvTestDetails, csvCoverage, results);

            LOGGER.info("Combined CSV reports generated: " + csvTestDetails + ", " + csvCoverage);
        }
    }

    /**
     * Generates an individual report for a single module.
     */
    private void generateModuleReport(ModuleResult result, Path outputDir, boolean csvOutput) throws IOException {
        String moduleName = result.getModuleInfo().getModuleName();
        Path moduleOutputDir = outputDir.resolve(moduleName);
        Files.createDirectories(moduleOutputDir);

        // Generate Excel report
        Path excelOutput = moduleOutputDir.resolve("report.xlsx");
        ExcelSheetBuilder excelBuilder = new ExcelSheetBuilder();

        // Convert to the format expected by ExcelSheetBuilder
        List<CoverageInfo> coverageInfoList = convertToCoverageInfoList(result.getCoverageData());
        excelBuilder.generateTestSpecificationReport(excelOutput.toString(), result.getTestCases(), coverageInfoList);

        LOGGER.fine("Module Excel report generated: " + excelOutput);

        // Generate CSV files if requested
        if (csvOutput && result.hasTestCases()) {
            CsvSheetBuilder csvBuilder = new CsvSheetBuilder();

            Path csvTestDetails = moduleOutputDir.resolve("report_test_details.csv");
            Path csvCoverage = moduleOutputDir.resolve("report_coverage.csv");

            csvBuilder.generateCsvFiles(result.getTestCases(), result.getCoverageData(), csvTestDetails, csvCoverage);

            LOGGER.fine("Module CSV reports generated: " + csvTestDetails + ", " + csvCoverage);
        }
    }

    /**
     * Generates a JSON summary report with processing statistics.
     */
    private void generateSummaryReport(List<ModuleResult> results, Path outputDir) throws IOException {
        Path summaryFile = outputDir.resolve("modules-summary.json");

        Map<String, Object> summary = new HashMap<>();
        summary.put("timestamp", new Date().toString());
        summary.put("totalModules", results.size());

        long successful = results.stream().mapToLong(r -> r.isSuccessful() ? 1 : 0).sum();
        summary.put("successfulModules", successful);
        summary.put("failedModules", results.size() - successful);

        long totalTestCases = results.stream()
            .filter(ModuleResult::isSuccessful)
            .mapToLong(r -> r.hasTestCases() ? r.getTestCases().size() : 0)
            .sum();
        summary.put("totalTestCases", totalTestCases);

        List<Map<String, Object>> moduleDetails = new ArrayList<>();
        for (ModuleResult result : results) {
            Map<String, Object> moduleDetail = new HashMap<>();
            moduleDetail.put("name", result.getModuleInfo().getModuleName());
            moduleDetail.put("status", result.getProcessingStatus().toString());
            moduleDetail.put("testCases", result.hasTestCases() ? result.getTestCases().size() : 0);
            moduleDetail.put("processingTimeMs", result.getProcessingTimeMs());

            if (result.getErrorMessage() != null) {
                moduleDetail.put("error", result.getErrorMessage());
            }

            moduleDetails.add(moduleDetail);
        }
        summary.put("modules", moduleDetails);

        // Simple JSON generation (could use Jackson if needed)
        String jsonContent = generateSimpleJson(summary);
        Files.writeString(summaryFile, jsonContent);

        LOGGER.info("Summary report generated: " + summaryFile);
    }

    /**
     * Converts coverage data from Map format to CoverageInfo list.
     */
    @SuppressWarnings("unchecked")
    private List<CoverageInfo> convertToCoverageInfoList(Map<String, Object> coverageData) {
        LOGGER.info("[MultiModule Debug] Map -> CoverageInfo conversion started: " + (coverageData != null ? coverageData.size() : 0) + " entries");
        List<CoverageInfo> coverageInfoList = new ArrayList<>();

        if (coverageData == null) {
            LOGGER.warning("[MultiModule Debug] カバレッジデータがnullです - 空のリストを返します");
            return coverageInfoList;
        }

        if (coverageData.isEmpty()) {
            LOGGER.warning("[MultiModule Debug] カバレッジデータが空です - 空のリストを返します");
            return coverageInfoList;
        }

        LOGGER.info("[MultiModule Debug] 変換対象: " + coverageData.size() + " エントリ");

        // Convert coverage data back to CoverageInfo objects
        int successCount = 0;
        int failureCount = 0;

        for (Map.Entry<String, Object> entry : coverageData.entrySet()) {
            String entryKey = entry.getKey();
            Object entryValue = entry.getValue();

            LOGGER.fine("[MultiModule Debug] 処理中: キー='" + entryKey + "', 値タイプ=" +
                       (entryValue != null ? entryValue.getClass().getSimpleName() : "null"));

            try {
                if (entryValue instanceof Map) {
                    Map<String, Object> coverageMap = (Map<String, Object>) entryValue;
                    LOGGER.fine("[MultiModule Debug] Mapエントリ処理: " + coverageMap.size() + " フィールド");

                    // Extract required fields with detailed logging
                    String className = (String) coverageMap.get("className");
                    String methodName = (String) coverageMap.get("methodName");
                    String packageName = (String) coverageMap.get("packageName");

                    LOGGER.fine("[MultiModule Debug] 基本情報抽出: class='" + className + "', method='" + methodName + "', package='" + packageName + "'");

                    if (className != null && methodName != null) {
                        CoverageInfo info = new CoverageInfo(className, methodName);

                        // Set package name
                        if (packageName != null) {
                            info.setPackageName(packageName);
                            LOGGER.fine("[MultiModule Debug] パッケージ名設定: " + packageName);
                        }

                        // Set coverage metrics with safe type conversion and detailed logging
                        LOGGER.fine("[MultiModule Debug] ブランチカバレッジ変換開始");
                        Object branchesCoveredObj = coverageMap.get("branchesCovered");
                        Object branchesTotalObj = coverageMap.get("branchesTotal");

                        if (branchesCoveredObj != null && branchesTotalObj != null) {
                            int branchesCovered = safeConvertToInt(branchesCoveredObj);
                            int branchesTotal = safeConvertToInt(branchesTotalObj);
                            info.setBranchInfo(branchesCovered, branchesTotal);

                            LOGGER.fine("[MultiModule Debug] ブランチカバレッジ設定: " + branchesCovered + "/" + branchesTotal +
                                       " = " + (branchesTotal > 0 ? (branchesCovered * 100.0 / branchesTotal) : 0.0) + "%");
                            LOGGER.fine("[MultiModule Debug] 元の値: branchesCovered=" + branchesCoveredObj + " (" +
                                       (branchesCoveredObj != null ? branchesCoveredObj.getClass().getSimpleName() : "null") +
                                       "), branchesTotal=" + branchesTotalObj + " (" +
                                       (branchesTotalObj != null ? branchesTotalObj.getClass().getSimpleName() : "null") + ")");
                        } else {
                            LOGGER.warning("[MultiModule Debug] ブランチカバレッジデータが不完全: branchesCovered=" + branchesCoveredObj +
                                         ", branchesTotal=" + branchesTotalObj);
                        }

                        // Line coverage
                        LOGGER.fine("[MultiModule Debug] ラインカバレッジ変換開始");
                        Object linesCoveredObj = coverageMap.get("linesCovered");
                        Object linesTotalObj = coverageMap.get("linesTotal");

                        if (linesCoveredObj != null && linesTotalObj != null) {
                            int linesCovered = safeConvertToInt(linesCoveredObj);
                            int linesTotal = safeConvertToInt(linesTotalObj);
                            info.setLineInfo(linesCovered, linesTotal);

                            LOGGER.fine("[MultiModule Debug] ラインカバレッジ設定: " + linesCovered + "/" + linesTotal +
                                       " = " + (linesTotal > 0 ? (linesCovered * 100.0 / linesTotal) : 0.0) + "%");
                        } else {
                            LOGGER.fine("[MultiModule Debug] ラインカバレッジデータなし");
                        }

                        // Set instruction coverage data
                        LOGGER.fine("[MultiModule Debug] 命令カバレッジ変換開始");
                        Object instructionsCoveredObj = coverageMap.get("instructionsCovered");
                        Object instructionsTotalObj = coverageMap.get("instructionsTotal");

                        if (instructionsCoveredObj != null && instructionsTotalObj != null) {
                            int instructionsCovered = safeConvertToInt(instructionsCoveredObj);
                            int instructionsTotal = safeConvertToInt(instructionsTotalObj);
                            info.setInstructionInfo(instructionsCovered, instructionsTotal);

                            LOGGER.fine("[MultiModule Debug] 命令カバレッジ設定: " + instructionsCovered + "/" + instructionsTotal +
                                       " = " + (instructionsTotal > 0 ? (instructionsCovered * 100.0 / instructionsTotal) : 0.0) + "%");
                        } else {
                            LOGGER.fine("[MultiModule Debug] 命令カバレッジデータなし");
                        }

                        // Set method coverage data
                        Object methodsCoveredObj = coverageMap.get("methodsCovered");
                        Object methodsTotalObj = coverageMap.get("methodsTotal");

                        if (methodsCoveredObj != null && methodsTotalObj != null) {
                            int methodsCovered = safeConvertToInt(methodsCoveredObj);
                            int methodsTotal = safeConvertToInt(methodsTotalObj);
                            info.setMethodInfo(methodsCovered, methodsTotal);

                            LOGGER.fine("[MultiModule Debug] メソッドカバレッジ設定: " + methodsCovered + "/" + methodsTotal +
                                       " = " + (methodsTotal > 0 ? (methodsCovered * 100.0 / methodsTotal) : 0.0) + "%");
                        }

                        // Set additional metadata
                        String sourceFile = (String) coverageMap.get("sourceFile");
                        String reportType = (String) coverageMap.get("reportType");

                        if (sourceFile != null) {
                            info.setSourceFile(sourceFile);
                            LOGGER.fine("[MultiModule Debug] ソースファイル設定: " + sourceFile);
                        }
                        if (reportType != null) {
                            info.setReportType(reportType);
                            LOGGER.fine("[MultiModule Debug] レポートタイプ設定: " + reportType);
                        }

                        coverageInfoList.add(info);
                        successCount++;

                        LOGGER.info("[MultiModule Debug] 変換成功 (" + successCount + "/" + coverageData.size() + "): " +
                                   className + "." + methodName + " - ブランチ: " + info.getBranchCoverage() + "%");
                    } else {
                        failureCount++;
                        LOGGER.warning("[MultiModule Debug] 必要フィールド不足でスキップ (" + failureCount + "): className=" +
                                     className + ", methodName=" + methodName);
                    }
                } else {
                    failureCount++;
                    LOGGER.warning("[MultiModule Debug] 非Mapエントリをスキップ (" + failureCount + "): " + entryKey +
                                 " -> " + (entryValue != null ? entryValue.getClass().getSimpleName() : "null"));
                }
            } catch (Exception e) {
                failureCount++;
                LOGGER.log(Level.WARNING, "[MultiModule Debug] 変換エラー (" + failureCount + "): " + entryKey, e);
            }
        }

        LOGGER.info("[MultiModule Debug] Map → CoverageInfo変換完了: 成功=" + successCount + ", 失敗=" + failureCount +
                   ", 総数=" + coverageData.size() + " → 結果=" + coverageInfoList.size() + " エントリ");

        if (coverageInfoList.isEmpty() && !coverageData.isEmpty()) {
            LOGGER.severe("[MultiModule Debug] 重大: 元データは存在するが変換結果が空です!");
            LOGGER.severe("[MultiModule Debug] 元データのキー例: " + coverageData.keySet().stream().limit(5).toArray());

            // サンプルデータの詳細表示
            if (!coverageData.isEmpty()) {
                Map.Entry<String, Object> sample = coverageData.entrySet().iterator().next();
                LOGGER.severe("[MultiModule Debug] サンプルエントリ詳細: key=" + sample.getKey() +
                             ", value=" + sample.getValue());
                if (sample.getValue() instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> sampleMap = (Map<String, Object>) sample.getValue();
                    LOGGER.severe("[MultiModule Debug] サンプルMapの内容: " + sampleMap);
                }
            }
        }

        return coverageInfoList;
    }

    /**
     * Safely converts an Object to int, handling various numeric types.
     */
    private int safeConvertToInt(Object value) {
        LOGGER.finest("[Type Conversion Debug] 型変換開始: " + (value != null ? value.getClass().getSimpleName() : "null") + " -> int");
        LOGGER.finest("[Type Conversion Debug] 元の値: " + value);

        if (value == null) {
            LOGGER.fine("[Type Conversion Debug] null値のため0を返します");
            return 0;
        }

        if (value instanceof Integer) {
            Integer intValue = (Integer) value;
            LOGGER.finest("[Type Conversion Debug] Integer型: " + intValue);
            return intValue;
        } else if (value instanceof Long) {
            Long longValue = (Long) value;
            int intValue = longValue.intValue();
            LOGGER.finest("[Type Conversion Debug] Long型変換: " + longValue + " -> " + intValue);

            if (longValue > Integer.MAX_VALUE) {
                LOGGER.warning("[Type Conversion Debug] Long値がInteger範囲を超えています: " + longValue + " -> " + intValue);
            }
            return intValue;
        } else if (value instanceof Double) {
            Double doubleValue = (Double) value;
            int intValue = doubleValue.intValue();
            LOGGER.finest("[Type Conversion Debug] Double型変換: " + doubleValue + " -> " + intValue);

            if (doubleValue != intValue) {
                LOGGER.fine("[Type Conversion Debug] Double値の小数部が切り捨てられました: " + doubleValue + " -> " + intValue);
            }
            return intValue;
        } else if (value instanceof Float) {
            Float floatValue = (Float) value;
            int intValue = floatValue.intValue();
            LOGGER.finest("[Type Conversion Debug] Float型変換: " + floatValue + " -> " + intValue);

            if (floatValue != intValue) {
                LOGGER.fine("[Type Conversion Debug] Float値の小数部が切り捨てられました: " + floatValue + " -> " + intValue);
            }
            return intValue;
        } else if (value instanceof String) {
            String stringValue = (String) value;
            LOGGER.finest("[Type Conversion Debug] String型解析試行: '" + stringValue + "'");

            if (stringValue.isEmpty()) {
                LOGGER.fine("[Type Conversion Debug] 空文字列のため0を返します");
                return 0;
            }

            try {
                int intValue = Integer.parseInt(stringValue);
                LOGGER.finest("[Type Conversion Debug] String解析成功: '" + stringValue + "' -> " + intValue);
                return intValue;
            } catch (NumberFormatException e) {
                LOGGER.warning("[Type Conversion Debug] String解析失敗: '" + stringValue + "' -> 0 (エラー: " + e.getMessage() + ")");
                return 0;
            }
        } else if (value instanceof Number) {
            // その他のNumber型（BigInteger、BigDecimalなど）
            Number numberValue = (Number) value;
            int intValue = numberValue.intValue();
            LOGGER.finest("[Type Conversion Debug] その他Number型変換: " + numberValue + " (" + numberValue.getClass().getSimpleName() + ") -> " + intValue);
            return intValue;
        }

        // 予期しない型
        LOGGER.warning("[Type Conversion Debug] 予期しない型です - 0を返します: " + value.getClass().getSimpleName() + " 値: " + value);
        return 0; // Default fallback
    }

    /**
     * Simple JSON generation method (basic implementation).
     */
    private String generateSimpleJson(Map<String, Object> data) {
        StringBuilder json = new StringBuilder();
        json.append("{\n");

        boolean first = true;
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            if (!first) json.append(",\n");
            first = false;

            json.append("  \"").append(entry.getKey()).append("\": ");
            Object value = entry.getValue();

            if (value instanceof String) {
                json.append("\"").append(value).append("\"");
            } else if (value instanceof Number) {
                json.append(value);
            } else if (value instanceof List) {
                json.append("[\n");
                @SuppressWarnings("unchecked")
                List<Object> list = (List<Object>) value;
                for (int i = 0; i < list.size(); i++) {
                    if (i > 0) json.append(",\n");
                    json.append("    ").append(generateSimpleJson((Map<String, Object>) list.get(i)).replace("\n", "\n    "));
                }
                json.append("\n  ]");
            }
        }

        json.append("\n}");
        return json.toString();
    }

    /**
     * Shuts down the executor service.
     */
    public void shutdown() {
        if (executorService != null && !executorService.isShutdown()) {
            executorService.shutdown();
            try {
                if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                    executorService.shutdownNow();
                }
            } catch (InterruptedException e) {
                executorService.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
}