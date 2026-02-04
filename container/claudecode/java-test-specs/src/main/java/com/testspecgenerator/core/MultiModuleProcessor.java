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
                    .coverageData(new ArrayList<>())  // SIMPLIFIED: Changed from HashMap to ArrayList
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
                    LOGGER.info(String.format("[Detail Log] Module %s - File processing completed: %s (%d test cases)",
                               module.getModuleName(), testFile.getFileName(), fileTestCases.size()));
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Failed to parse test file: " + testFile, e);
                }
            }

            LOGGER.info(String.format("[Detail Log] Module %s - Annotation analysis completed: %d Test cases extracted", module.getModuleName(), testCases.size()));

            // Step 3: Parse coverage reports (SIMPLIFIED - No Map conversion)
            LOGGER.info(String.format("[Detail Log] Module %s - Coverage report analysis started", module.getModuleName()));
            CoverageReportParser coverageParser = new CoverageReportParser();
            List<CoverageInfo> coverageData = new ArrayList<>();

            try {
                // Look for coverage reports in the module
                List<Path> coverageFiles = scanner.scanForCoverageReports(module.getModuleRoot());
                if (!coverageFiles.isEmpty()) {
                    LOGGER.info("[SIMPLIFIED] Calling processCoverageReports() directly - NO Map conversion!");
                    coverageData = coverageParser.processCoverageReports(coverageFiles, testFiles);
                    LOGGER.info(String.format("[SIMPLIFIED] Coverage data retrieved: %d entries (direct List<CoverageInfo>)",
                               coverageData != null ? coverageData.size() : 0));

                    // Log sample data to verify
                    if (coverageData != null && !coverageData.isEmpty()) {
                        int sampleSize = Math.min(3, coverageData.size());
                        for (int i = 0; i < sampleSize; i++) {
                            CoverageInfo sample = coverageData.get(i);
                            LOGGER.info(String.format("[SIMPLIFIED] Sample %d: %s.%s - Branch: %.1f%%, Line: %.1f%%, Instruction: %.1f%%",
                                       i + 1, sample.getClassName(), sample.getMethodName(),
                                       sample.getBranchCoverage(), sample.getLineCoverage(),
                                       sample.getInstructionCoverage()));
                        }
                    }
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

        // Combine all test cases and coverage data (SIMPLIFIED)
        List<TestCaseInfo> allTestCases = new ArrayList<>();
        List<CoverageInfo> allCoverageData = new ArrayList<>();  // SIMPLIFIED: Changed from Map to List

        for (ModuleResult result : successfulResults) {
            // Add test cases
            if (result.hasTestCases()) {
                allTestCases.addAll(result.getTestCases());
                LOGGER.info(String.format("[SIMPLIFIED] Added %d test cases from module: %s",
                           result.getTestCases().size(), result.getModuleInfo().getModuleName()));
            }

            // Add coverage data (SIMPLIFIED: Just combine lists, no Map conversion)
            if (result.hasCoverageData()) {
                List<CoverageInfo> moduleCoverage = result.getCoverageData();
                allCoverageData.addAll(moduleCoverage);
                LOGGER.info(String.format("[SIMPLIFIED] Added %d coverage entries from module: %s",
                           moduleCoverage.size(), result.getModuleInfo().getModuleName()));
            }
        }

        LOGGER.info(String.format("[SIMPLIFIED] Combined totals: %d test cases, %d coverage entries",
                   allTestCases.size(), allCoverageData.size()));

        // Generate Excel report (SIMPLIFIED: Pass List instead of Map)
        Path excelOutput = outputDir.resolve("combined-report.xlsx");
        ExcelSheetBuilder excelBuilder = new ExcelSheetBuilder();

        // SIMPLIFIED: generateTestSpecificationReport works with List<CoverageInfo>
        boolean success = excelBuilder.generateTestSpecificationReport(excelOutput.toString(), allTestCases, allCoverageData);
        if (!success) {
            throw new IOException("Failed to generate combined Excel report");
        }

        LOGGER.info("Combined Excel report generated: " + excelOutput);

        // Generate CSV files if requested (SIMPLIFIED: Use standard methods)
        if (csvOutput) {
            CsvSheetBuilder csvBuilder = new CsvSheetBuilder();

            // SIMPLIFIED: Use existing methods that work with List<CoverageInfo>
            // Note: generateTestDetailsCsv/generateCoverageSheetCsv expect path WITH .xlsx extension
            String excelPathStr = excelOutput.toString();
            boolean testDetailsCsvSuccess = csvBuilder.generateTestDetailsCsv(excelPathStr, allTestCases);
            boolean coverageCsvSuccess = csvBuilder.generateCoverageSheetCsv(excelPathStr, allTestCases, allCoverageData);

            if (testDetailsCsvSuccess && coverageCsvSuccess) {
                LOGGER.info("Combined CSV reports generated successfully");
            } else {
                LOGGER.warning("Some CSV reports failed to generate");
            }
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

        // SIMPLIFIED: No conversion needed - coverageData is already List<CoverageInfo>
        List<CoverageInfo> coverageData = result.getCoverageData();
        LOGGER.info(String.format("[SIMPLIFIED] Generating Excel for module %s with %d coverage entries (direct List)",
                   moduleName, coverageData != null ? coverageData.size() : 0));
        excelBuilder.generateTestSpecificationReport(excelOutput.toString(), result.getTestCases(), coverageData);

        LOGGER.info("Module Excel report generated: " + excelOutput);

        // Generate CSV files if requested
        if (csvOutput && result.hasTestCases()) {
            CsvSheetBuilder csvBuilder = new CsvSheetBuilder();

            Path csvTestDetails = moduleOutputDir.resolve("report_test_details.csv");
            Path csvCoverage = moduleOutputDir.resolve("report_coverage.csv");

            // SIMPLIFIED: No conversion needed
            csvBuilder.generateCsvFiles(result.getTestCases(), coverageData, csvTestDetails, csvCoverage);

            LOGGER.info("Module CSV reports generated: " + csvTestDetails + ", " + csvCoverage);
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
            LOGGER.warning("[MultiModule Debug] Coverage data is NULL - returning empty list");
            return coverageInfoList;
        }

        if (coverageData.isEmpty()) {
            LOGGER.warning("[MultiModule Debug] Coverage data is EMPTY - returning empty list");
            return coverageInfoList;
        }

        LOGGER.info("[MultiModule Debug] Conversion target: " + coverageData.size() + " entries");

        // Convert coverage data back to CoverageInfo objects
        int successCount = 0;
        int failureCount = 0;

        for (Map.Entry<String, Object> entry : coverageData.entrySet()) {
            String entryKey = entry.getKey();
            Object entryValue = entry.getValue();

            LOGGER.info("[MultiModule Debug] Processing entry: key='" + entryKey + "', value type=" +
                       (entryValue != null ? entryValue.getClass().getSimpleName() : "null"));

            try {
                if (entryValue instanceof Map) {
                    Map<String, Object> coverageMap = (Map<String, Object>) entryValue;
                    LOGGER.fine("[MultiModule Debug] Map entry processing: " + coverageMap.size() + " fields");

                    // Extract required fields with detailed logging
                    String className = (String) coverageMap.get("className");
                    String methodName = (String) coverageMap.get("methodName");
                    String packageName = (String) coverageMap.get("packageName");

                    LOGGER.fine("[MultiModule Debug] Basic info extracted: class='" + className + "', method='" + methodName + "', package='" + packageName + "'");

                    if (className != null && methodName != null) {
                        CoverageInfo info = new CoverageInfo(className, methodName);

                        // Set package name
                        if (packageName != null) {
                            info.setPackageName(packageName);
                            LOGGER.fine("[MultiModule Debug] Package name set: " + packageName);
                        }

                        // Set coverage metrics with safe type conversion and detailed logging
                        LOGGER.info("[MultiModule Debug] Branch coverage conversion started for: " + className + "." + methodName);
                        Object branchesCoveredObj = coverageMap.get("branchesCovered");
                        Object branchesTotalObj = coverageMap.get("branchesTotal");

                        LOGGER.info("[MultiModule Debug] Retrieved from Map: branchesCovered=" + branchesCoveredObj + " (" +
                                   (branchesCoveredObj != null ? branchesCoveredObj.getClass().getSimpleName() : "null") +
                                   "), branchesTotal=" + branchesTotalObj + " (" +
                                   (branchesTotalObj != null ? branchesTotalObj.getClass().getSimpleName() : "null") + ")");

                        if (branchesCoveredObj != null && branchesTotalObj != null) {
                            int branchesCovered = safeConvertToInt(branchesCoveredObj);
                            int branchesTotal = safeConvertToInt(branchesTotalObj);
                            info.setBranchInfo(branchesCovered, branchesTotal);

                            double calculatedPercentage = branchesTotal > 0 ? (branchesCovered * 100.0 / branchesTotal) : 0.0;
                            LOGGER.info("[MultiModule Debug] Branch coverage set: " + branchesCovered + "/" + branchesTotal +
                                       " = " + calculatedPercentage + "%, After setBranchInfo: getBranchCoverage()=" + info.getBranchCoverage() + "%");
                        } else {
                            LOGGER.warning("[MultiModule Debug] Branch coverage data incomplete: branchesCovered=" + branchesCoveredObj +
                                         ", branchesTotal=" + branchesTotalObj);
                        }

                        // Line coverage
                        LOGGER.fine("[MultiModule Debug] Line coverage conversion started");
                        Object linesCoveredObj = coverageMap.get("linesCovered");
                        Object linesTotalObj = coverageMap.get("linesTotal");

                        if (linesCoveredObj != null && linesTotalObj != null) {
                            int linesCovered = safeConvertToInt(linesCoveredObj);
                            int linesTotal = safeConvertToInt(linesTotalObj);
                            info.setLineInfo(linesCovered, linesTotal);

                            LOGGER.fine("[MultiModule Debug] Line coverage set: " + linesCovered + "/" + linesTotal +
                                       " = " + (linesTotal > 0 ? (linesCovered * 100.0 / linesTotal) : 0.0) + "%");
                        } else {
                            LOGGER.fine("[MultiModule Debug] No line coverage data");
                        }

                        // Set instruction coverage data
                        LOGGER.fine("[MultiModule Debug] Instruction coverage conversion started");
                        Object instructionsCoveredObj = coverageMap.get("instructionsCovered");
                        Object instructionsTotalObj = coverageMap.get("instructionsTotal");

                        if (instructionsCoveredObj != null && instructionsTotalObj != null) {
                            int instructionsCovered = safeConvertToInt(instructionsCoveredObj);
                            int instructionsTotal = safeConvertToInt(instructionsTotalObj);
                            info.setInstructionInfo(instructionsCovered, instructionsTotal);

                            LOGGER.fine("[MultiModule Debug] Instruction coverage set: " + instructionsCovered + "/" + instructionsTotal +
                                       " = " + (instructionsTotal > 0 ? (instructionsCovered * 100.0 / instructionsTotal) : 0.0) + "%");
                        } else {
                            LOGGER.fine("[MultiModule Debug] No instruction coverage data");
                        }

                        // Set method coverage data
                        Object methodsCoveredObj = coverageMap.get("methodsCovered");
                        Object methodsTotalObj = coverageMap.get("methodsTotal");

                        if (methodsCoveredObj != null && methodsTotalObj != null) {
                            int methodsCovered = safeConvertToInt(methodsCoveredObj);
                            int methodsTotal = safeConvertToInt(methodsTotalObj);
                            info.setMethodInfo(methodsCovered, methodsTotal);

                            LOGGER.fine("[MultiModule Debug] Method coverage set: " + methodsCovered + "/" + methodsTotal +
                                       " = " + (methodsTotal > 0 ? (methodsCovered * 100.0 / methodsTotal) : 0.0) + "%");
                        }

                        // Set additional metadata
                        String sourceFile = (String) coverageMap.get("sourceFile");
                        String reportType = (String) coverageMap.get("reportType");

                        if (sourceFile != null) {
                            info.setSourceFile(sourceFile);
                            LOGGER.fine("[MultiModule Debug] Source file set: " + sourceFile);
                        }
                        if (reportType != null) {
                            info.setReportType(reportType);
                            LOGGER.fine("[MultiModule Debug] Report type set: " + reportType);
                        }

                        coverageInfoList.add(info);
                        successCount++;

                        LOGGER.info("[MultiModule Debug] Conversion SUCCESS (" + successCount + "/" + coverageData.size() + "): " +
                                   className + "." + methodName + " - Branch: " + info.getBranchCoverage() + "%, Line: " + info.getLineCoverage() +
                                   "%, Instruction: " + info.getInstructionCoverage() + "%");
                    } else {
                        failureCount++;
                        LOGGER.warning("[MultiModule Debug] SKIP - Missing required fields (" + failureCount + "): className=" +
                                     className + ", methodName=" + methodName);
                    }
                } else {
                    failureCount++;
                    LOGGER.warning("[MultiModule Debug] SKIP - Non-Map entry (" + failureCount + "): " + entryKey +
                                 " -> " + (entryValue != null ? entryValue.getClass().getSimpleName() : "null"));
                }
            } catch (Exception e) {
                failureCount++;
                LOGGER.log(Level.WARNING, "[MultiModule Debug] Conversion ERROR (" + failureCount + "): " + entryKey, e);
            }
        }

        LOGGER.info("[MultiModule Debug] Map -> CoverageInfo conversion COMPLETED: Success=" + successCount + ", Failed=" + failureCount +
                   ", Total=" + coverageData.size() + " -> Result=" + coverageInfoList.size() + " entries");

        if (coverageInfoList.isEmpty() && !coverageData.isEmpty()) {
            LOGGER.severe("[MultiModule Debug] CRITICAL: Source data exists but conversion result is EMPTY!");
            LOGGER.severe("[MultiModule Debug] Sample source data keys: " + coverageData.keySet().stream().limit(5).toArray());

            // Display sample data details
            if (!coverageData.isEmpty()) {
                Map.Entry<String, Object> sample = coverageData.entrySet().iterator().next();
                LOGGER.severe("[MultiModule Debug] Sample entry details: key=" + sample.getKey() +
                             ", value=" + sample.getValue());
                if (sample.getValue() instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> sampleMap = (Map<String, Object>) sample.getValue();
                    LOGGER.severe("[MultiModule Debug] Sample Map contents: " + sampleMap);
                }
            }
        }

        return coverageInfoList;
    }

    /**
     * Safely converts an Object to int, handling various numeric types.
     */
    private int safeConvertToInt(Object value) {
        LOGGER.info("[Type Conversion Debug] Type conversion started: " + (value != null ? value.getClass().getSimpleName() : "null") + " -> int, value: " + value);

        if (value == null) {
            LOGGER.warning("[Type Conversion Debug] NULL value - returning 0");
            return 0;
        }

        if (value instanceof Integer) {
            Integer intValue = (Integer) value;
            LOGGER.info("[Type Conversion Debug] Integer type: " + intValue);
            return intValue;
        } else if (value instanceof Long) {
            Long longValue = (Long) value;
            int intValue = longValue.intValue();
            LOGGER.info("[Type Conversion Debug] Long type conversion: " + longValue + " -> " + intValue);

            if (longValue > Integer.MAX_VALUE) {
                LOGGER.warning("[Type Conversion Debug] Long value exceeds Integer range: " + longValue + " -> " + intValue);
            }
            return intValue;
        } else if (value instanceof Double) {
            Double doubleValue = (Double) value;
            int intValue = doubleValue.intValue();
            LOGGER.info("[Type Conversion Debug] Double type conversion: " + doubleValue + " -> " + intValue);

            if (doubleValue != intValue) {
                LOGGER.warning("[Type Conversion Debug] Double decimal truncated: " + doubleValue + " -> " + intValue);
            }
            return intValue;
        } else if (value instanceof Float) {
            Float floatValue = (Float) value;
            int intValue = floatValue.intValue();
            LOGGER.info("[Type Conversion Debug] Float type conversion: " + floatValue + " -> " + intValue);

            if (floatValue != intValue) {
                LOGGER.warning("[Type Conversion Debug] Float decimal truncated: " + floatValue + " -> " + intValue);
            }
            return intValue;
        } else if (value instanceof String) {
            String stringValue = (String) value;
            LOGGER.info("[Type Conversion Debug] String type parsing attempt: '" + stringValue + "'");

            if (stringValue.isEmpty()) {
                LOGGER.warning("[Type Conversion Debug] Empty string - returning 0");
                return 0;
            }

            try {
                int intValue = Integer.parseInt(stringValue);
                LOGGER.info("[Type Conversion Debug] String parsing success: '" + stringValue + "' -> " + intValue);
                return intValue;
            } catch (NumberFormatException e) {
                LOGGER.warning("[Type Conversion Debug] String parsing failed: '" + stringValue + "' -> 0 (error: " + e.getMessage() + ")");
                return 0;
            }
        } else if (value instanceof Number) {
            // Other Number types (BigInteger, BigDecimal, etc.)
            Number numberValue = (Number) value;
            int intValue = numberValue.intValue();
            LOGGER.info("[Type Conversion Debug] Other Number type conversion: " + numberValue + " (" + numberValue.getClass().getSimpleName() + ") -> " + intValue);
            return intValue;
        }

        // Unexpected type
        LOGGER.warning("[Type Conversion Debug] Unexpected type - returning 0: " + value.getClass().getSimpleName() + " value: " + value);
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