package com.testspecgenerator.core;

import com.testspecgenerator.model.CoverageInfo;
import com.testspecgenerator.model.ModuleResult;
import com.testspecgenerator.model.TestCaseInfo;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

/**
 * Class responsible for generating test specifications in CSV format
 * Generates CSV files for Test Details and Coverage sheets
 */
public class CsvSheetBuilder {

    private static final Logger logger = LoggerFactory.getLogger(CsvSheetBuilder.class);

    /**
     * Generate Test Details CSV file
     *
     * @param outputPath Output file path (Excel) to generate CSV path from
     * @param testCases Test case information list
     * @return true on successful generation, false on failure
     */
    public boolean generateTestDetailsCsv(String outputPath, List<TestCaseInfo> testCases) {
        String csvPath = generateCsvPath(outputPath, "_test_details");

        logger.info("Test Details CSV generation started: {}", csvPath);
        logger.info("[Detail Log] CSV output started - Test Detailsシート: {} テストケース", testCases.size());

        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(csvPath), StandardCharsets.UTF_8);
             CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.builder()
                     .setHeader(getTestDetailsHeaders())
                     .build())) {

            int rowNumber = 1;
            for (TestCaseInfo testCase : testCases) {
                logger.debug("[Detail Log] CSV行出力: {} - FQCN: {}, テスト名: {}",
                           rowNumber, testCase.getFullyQualifiedName(), testCase.getTestItemName());
                csvPrinter.printRecord(
                    rowNumber++,
                    testCase.getFullyQualifiedName(),
                    testCase.getSoftwareService(),
                    testCase.getTestItemName(),
                    testCase.getTestContent(),
                    testCase.getConfirmationItem(),
                    testCase.getTestModule(),
                    testCase.getBaselineVersion(),
                    testCase.getCreator(),
                    testCase.getCreatedDate(),
                    testCase.getModifier(),
                    testCase.getModifiedDate()
                );
            }

            logger.info("Test Details CSV generation completed: {} ({} rows)", csvPath, testCases.size());
            return true;

        } catch (IOException e) {
            logger.error("Test Details CSV generation error: {}", csvPath, e);
            return false;
        }
    }

    /**
     * Generate Coverage CSV file
     *
     * @param outputPath 出力ファイルパス（Excel）からCSVパスを生成
     * @param testCases テストケース情報リスト（Test Classマッピング用）
     * @param coverageData カバレッジ情報リスト
     * @return 生成成功時true、失敗時false
     */
    public boolean generateCoverageSheetCsv(String outputPath, List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        String csvPath = generateCsvPath(outputPath, "_coverage");

        logger.info("Coverage CSV生成開始: {}", csvPath);

        if (coverageData == null || coverageData.isEmpty()) {
            logger.warn("⚠️ Skipping Coverage CSV generation because coverage data is empty");
            return true;
        }

        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(csvPath), StandardCharsets.UTF_8);
             CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.builder()
                     .setHeader(getCoverageHeaders())
                     .build())) {

            int rowNumber = 1;
            for (CoverageInfo coverage : coverageData) {
                // Test Classマッピングを検索
                String testClass = findTestClassForCoverage(coverage, testCases);

                csvPrinter.printRecord(
                    rowNumber++,
                    coverage.getPackageName(),
                    coverage.getClassName(),
                    coverage.getMethodName(),
                    coverage.getSourceFile(),
                    testClass,
                    formatPercentage(coverage.getBranchCoverage()),
                    formatCoverage(coverage.getBranchesCovered(), coverage.getBranchesTotal()),
                    formatPercentage(coverage.getInstructionCoverage()),
                    formatCoverage(coverage.getInstructionsCovered(), coverage.getInstructionsTotal()),
                    formatPercentage(coverage.getLineCoverage()),
                    formatCoverage(coverage.getLinesCovered(), coverage.getLinesTotal()),
                    formatPercentage(coverage.getMethodCoverage()),
                    formatCoverage(coverage.getMethodsCovered(), coverage.getMethodsTotal()),
                    coverage.getCoverageStatus(),
                    coverage.getReportType(),
                    formatPercentage(coverage.getBranchCoverage()) // Primary Coverage (C1)
                );
            }

            logger.info("✅ Coverage CSV生成完了: {} ({}行)", csvPath, coverageData.size());
            return true;

        } catch (IOException e) {
            logger.error("❌ Coverage CSV生成エラー: {}", csvPath, e);
            return false;
        }
    }

    /**
     * Test Detailsシートのヘッダー配列を取得
     */
    private String[] getTestDetailsHeaders() {
        return new String[]{
            "No.",
            "FQCN (完全修飾クラス名)",
            "ソフトウェア・サービス",
            "項目名",
            "試験内容",
            "確認項目",
            "テスト対象モジュール名",
            "テスト実施ベースラインバージョン",
            "テストケース作成者",
            "テストケース作成日",
            "テストケース修正者",
            "テストケース修正日"
        };
    }

    /**
     * Coverageシートのヘッダー配列を取得
     */
    private String[] getCoverageHeaders() {
        return new String[]{
            "No.",
            "Package",
            "Class Name",
            "Method Name",
            "Source File",
            "Test Class (テストクラス)",
            "Branch Coverage %",
            "Branch (Covered/Total)",
            "Instruction Coverage %",
            "Instruction (Covered/Total)",
            "Line Coverage %",
            "Line (Covered/Total)",
            "Method Coverage %",
            "Method (Covered/Total)",
            "Status",
            "Report Type",
            "Primary Coverage (C1)"
        };
    }

    /**
     * Excelパスに基づいてCSVファイルパスを生成
     */
    private String generateCsvPath(String excelPath, String suffix) {
        Path path = Paths.get(excelPath);
        String filename = path.getFileName().toString();
        String nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
        String directory = path.getParent() != null ? path.getParent().toString() : "";

        return directory.isEmpty() ?
            nameWithoutExt + suffix + ".csv" :
            directory + "/" + nameWithoutExt + suffix + ".csv";
    }

    /**
     * カバレッジ情報に対応するテストクラスを検索
     */
    private String findTestClassForCoverage(CoverageInfo coverage, List<TestCaseInfo> testCases) {
        if (testCases == null || coverage == null) {
            return "";
        }

        String targetClassName = coverage.getClassName();
        if (targetClassName == null || targetClassName.isEmpty()) {
            return "";
        }

        // テストケースから対象クラス名に対応するテストクラスを検索
        for (TestCaseInfo testCase : testCases) {
            if (testCase.getTestModule() != null &&
                testCase.getTestModule().contains(targetClassName)) {
                return testCase.getClassName();
            }
        }

        // 命名規則による推測（例: BasicCalculator -> BasicCalculatorTest）
        for (TestCaseInfo testCase : testCases) {
            String testClassName = testCase.getClassName();
            if (testClassName != null && testClassName.startsWith(targetClassName)) {
                return testClassName;
            }
        }

        return "";
    }

    /**
     * パーセンテージのフォーマット
     */
    private String formatPercentage(double percentage) {
        if (Double.isNaN(percentage)) {
            return "0.0%";
        }
        return String.format("%.1f%%", percentage);
    }

    /**
     * カバレッジ数値のフォーマット（Covered/Total形式）
     */
    private String formatCoverage(int covered, int total) {
        return covered + "/" + total;
    }

    // Multi-module support methods

    /**
     * Generates combined CSV files for multi-module projects
     */
    public boolean generateCombinedCsvFiles(List<TestCaseInfo> allTestCases, Map<String, Object> allCoverageData,
                                          Path testDetailsPath, Path coveragePath, List<ModuleResult> results) {
        logger.info("Multi-module integrated CSV generation started");

        boolean success = true;

        // Generate test details CSV with module information
        success &= generateCombinedTestDetailsCsv(testDetailsPath, allTestCases, results);

        // Generate coverage CSV with module information
        success &= generateCombinedCoverageCsv(coveragePath, allTestCases, allCoverageData, results);

        if (success) {
            logger.info("Multi-module integrated CSV generation completed");
        } else {
            logger.warn("マルチモジュール統合CSV生成に一部失敗しました");
        }

        return success;
    }

    /**
     * Generates individual CSV files for a single module
     */
    // SIMPLIFIED: Changed parameter type from Map to List<CoverageInfo>
    public boolean generateCsvFiles(List<TestCaseInfo> testCases, List<CoverageInfo> coverageData,
                                   Path testDetailsPath, Path coveragePath) {
        logger.info("[SIMPLIFIED] Individual module CSV generation started: {}", testDetailsPath.getParent());
        logger.info("[SIMPLIFIED] Coverage data: {} entries (direct List<CoverageInfo>)",
                   coverageData != null ? coverageData.size() : 0);

        boolean success = true;

        // Use existing methods for individual modules
        success &= generateTestDetailsCsv(testDetailsPath.toString(), testCases);

        // SIMPLIFIED: No conversion needed - coverageData is already List<CoverageInfo>
        success &= generateCoverageSheetCsv(coveragePath.toString(), testCases, coverageData);

        return success;
    }

    /**
     * Generates combined test details CSV with module information
     */
    private boolean generateCombinedTestDetailsCsv(Path csvPath, List<TestCaseInfo> allTestCases, List<ModuleResult> results) {
        logger.info("Integrated Test Details CSV generation started: {}", csvPath);

        try (BufferedWriter writer = Files.newBufferedWriter(csvPath, StandardCharsets.UTF_8);
             CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.builder()
                     .setHeader(getCombinedTestDetailsHeaders())
                     .build())) {

            int rowNumber = 1;
            for (ModuleResult result : results) {
                if (!result.isSuccessful() || !result.hasTestCases()) continue;

                String moduleName = result.getModuleInfo().getModuleName();
                for (TestCaseInfo testCase : result.getTestCases()) {
                    csvPrinter.printRecord(
                        rowNumber++,
                        testCase.getFullyQualifiedName(),
                        moduleName,
                        testCase.getSoftwareService(),
                        testCase.getTestItemName(),
                        testCase.getTestContent(),
                        testCase.getConfirmationItem(),
                        testCase.getTestModule(),
                        testCase.getBaselineVersion(),
                        testCase.getCreator(),
                        testCase.getCreatedDate(),
                        testCase.getModifier(),
                        testCase.getModifiedDate()
                    );
                }
            }

            logger.info("Integrated Test Details CSV generation completed: {} ({} rows)", csvPath, rowNumber - 1);
            return true;

        } catch (IOException e) {
            logger.error("統合Test Details CSV生成エラー", e);
            return false;
        }
    }

    /**
     * Generates combined coverage CSV with module information
     */
    private boolean generateCombinedCoverageCsv(Path csvPath, List<TestCaseInfo> allTestCases,
                                              Map<String, Object> allCoverageData, List<ModuleResult> results) {
        logger.info("Integrated Coverage CSV generation started: {}", csvPath);

        try (BufferedWriter writer = Files.newBufferedWriter(csvPath, StandardCharsets.UTF_8);
             CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT.builder()
                     .setHeader(getCombinedCoverageHeaders())
                     .build())) {

            int rowNumber = 1;
            for (ModuleResult result : results) {
                if (!result.isSuccessful()) continue;

                String moduleName = result.getModuleInfo().getModuleName();

                if (result.hasTestCases()) {
                    for (TestCaseInfo testCase : result.getTestCases()) {
                        csvPrinter.printRecord(
                            rowNumber++,
                            moduleName,
                            testCase.getClassName(),
                            testCase.getMethodName(),
                            testCase.getPackageName(),
                            formatCoverage(testCase.getBranchesCovered(), testCase.getBranchesTotal()),
                            formatPercentage(testCase.getCoveragePercent()),
                            testCase.getCoverageStatus(),
                            formatCoverage(testCase.getTestsPassed(), testCase.getTestsTotal()),
                            formatPercentage(testCase.getTestSuccessRate())
                        );
                    }
                } else {
                    // Add row for module without test cases
                    csvPrinter.printRecord(
                        rowNumber++,
                        moduleName,
                        "No Tests",
                        "",
                        "",
                        "0/0",
                        "0.0%",
                        "No Coverage",
                        "0/0",
                        "0.0%"
                    );
                }
            }

            logger.info("Integrated Coverage CSV generation completed: {} ({} rows)", csvPath, rowNumber - 1);
            return true;

        } catch (IOException e) {
            logger.error("統合Coverage CSV生成エラー", e);
            return false;
        }
    }

    /**
     * Headers for combined test details CSV (with module column)
     */
    private String[] getCombinedTestDetailsHeaders() {
        return new String[] {
            "No.", "FQCN (完全修飾クラス名)", "Module Name", "ソフトウェア・サービス", "項目名", "試験内容",
            "確認項目", "テスト対象モジュール名", "テスト実施ベースラインバージョン",
            "テストケース作成者", "テストケース作成日", "テストケース修正者", "テストケース修正日"
        };
    }

    /**
     * Headers for combined coverage CSV (with module column)
     */
    private String[] getCombinedCoverageHeaders() {
        return new String[] {
            "No.", "Module Name", "Class Name", "Method Name", "Package Name",
            "Branch Coverage", "Coverage %", "Coverage Status",
            "Test Results", "Success Rate"
        };
    }

    /**
     * Converts coverage data from Map format to CoverageInfo list (simplified)
     */
    @SuppressWarnings("unchecked")
    private List<CoverageInfo> convertToCoverageInfoList(Map<String, Object> coverageData) {
        List<CoverageInfo> coverageInfoList = new java.util.ArrayList<>();

        if (coverageData == null) {
            return coverageInfoList;
        }

        // Simplified conversion - in practice this would need more sophisticated handling
        for (Map.Entry<String, Object> entry : coverageData.entrySet()) {
            try {
                if (entry.getValue() instanceof Map) {
                    CoverageInfo info = new CoverageInfo();
                    // Basic coverage info setup would go here
                    coverageInfoList.add(info);
                }
            } catch (Exception e) {
                logger.debug("Failed to convert coverage entry: " + entry.getKey(), e);
            }
        }

        return coverageInfoList;
    }
}