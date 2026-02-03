package com.testspecgenerator.core;

import com.testspecgenerator.model.CoverageInfo;
import com.testspecgenerator.model.ModuleResult;
import com.testspecgenerator.model.TestCaseInfo;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/**
 * Class for generating Excel test specification documents
 */
public class ExcelSheetBuilder {

    private static final Logger logger = LoggerFactory.getLogger(ExcelSheetBuilder.class);

    // Sheet name constants
    private static final String TEST_DETAILS_SHEET = "Test Details";
    private static final String SUMMARY_SHEET = "Summary";
    private static final String COVERAGE_SHEET = "Coverage";
    private static final String CONFIGURATION_SHEET = "Configuration";

    // Color constants
    private static final short COLOR_LIGHT_BLUE = IndexedColors.LIGHT_BLUE.getIndex();
    private static final short COLOR_LIGHT_YELLOW = IndexedColors.LIGHT_YELLOW.getIndex();
    private static final short COLOR_LIGHT_GREEN = IndexedColors.LIGHT_GREEN.getIndex();
    private static final short COLOR_WHITE = IndexedColors.WHITE.getIndex();

    /**
     * Generate test specification Excel report
     */
    public boolean generateTestSpecificationReport(String outputFile, List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        logger.info("Excel report generation started: {}", outputFile);
        logger.info("[詳細ログ] 結果出力開始 - テストケース数: {}, カバレッジエントリ数: {}", testCases.size(), coverageData.size());

        try (XSSFWorkbook workbook = new XSSFWorkbook()) {
            // Create each sheet
            logger.debug("[詳細ログ] Test Detailsシート作成開始...");
            createTestDetailsSheet(workbook, testCases);

            logger.debug("[詳細ログ] Summaryシート作成開始...");
            createSummarySheet(workbook, testCases, coverageData);

            logger.debug("[詳細ログ] Coverageシート作成開始...");
            createCoverageSheet(workbook, testCases, coverageData);
            createConfigurationSheet(workbook, testCases, coverageData);

            // Save to file
            try (FileOutputStream outputStream = new FileOutputStream(outputFile)) {
                workbook.write(outputStream);
            }

            // Get file size
            long fileSize = Files.size(Paths.get(outputFile));
            logger.info("Excel report generation completed: {} ({:,} bytes)", outputFile, fileSize);

            return true;

        } catch (Exception e) {
            logger.error("Excel report generation error", e);
            return false;
        }
    }

    /**
     * Multi-module combined report generation
     */
    public boolean generateCombinedReport(List<TestCaseInfo> allTestCases, Map<String, Object> allCoverageData,
                                        String outputFile, List<ModuleResult> results) {
        logger.info("Multi-module combined Excel report generation started: {}", outputFile);

        try (XSSFWorkbook workbook = new XSSFWorkbook()) {
            // Create enhanced sheets for multi-module support
            createTestDetailsSheetWithModules(workbook, allTestCases, results);
            createSummarySheetWithModules(workbook, allTestCases, allCoverageData, results);
            createCoverageSheetWithModules(workbook, allTestCases, allCoverageData, results);
            createModulesSheet(workbook, results);
            createConfigurationSheetWithModules(workbook, allTestCases, allCoverageData, results);

            // Save to file
            try (FileOutputStream outputStream = new FileOutputStream(outputFile)) {
                workbook.write(outputStream);
            }

            // Get file size
            long fileSize = Files.size(Paths.get(outputFile));
            logger.info("Multi-module combined Excel report generation completed: {} ({:,} bytes)", outputFile, fileSize);

            return true;

        } catch (Exception e) {
            logger.error("Multi-module combined Excel report generation error", e);
            return false;
        }
    }

    /**
     * Create Test Details sheet
     */
    private void createTestDetailsSheet(XSSFWorkbook workbook, List<TestCaseInfo> testCases) {
        Sheet sheet = workbook.createSheet(TEST_DETAILS_SHEET);

        // Create styles
        CellStyle headerStyle = createHeaderStyle(workbook);
        CellStyle dataStyle = createDataStyle(workbook);

        // ヘッダー行を作成（日本語項目）
        Row headerRow = sheet.createRow(0);
        String[] headers = {
                "No.", "FQCN (完全修飾クラス名)", "ソフトウェア・サービス", "項目名", "試験内容", "確認項目",
                "テスト対象モジュール名", "テスト実施ベースラインバージョン",
                "テストケース作成者", "テストケース作成日", "テストケース修正者", "テストケース修正日"
        };

        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        // データ行を作成
        for (int i = 0; i < testCases.size(); i++) {
            TestCaseInfo testCase = testCases.get(i);
            Row dataRow = sheet.createRow(i + 1);

            // データセルを設定（日本語項目）
            setCellValue(dataRow, 0, i + 1, dataStyle);
            setCellValue(dataRow, 1, testCase.getFullyQualifiedName(), dataStyle);
            setCellValue(dataRow, 2, testCase.getSoftwareService(), dataStyle);
            setCellValue(dataRow, 3, testCase.getTestItemName(), dataStyle);
            setCellValue(dataRow, 4, testCase.getTestContent(), dataStyle);
            setCellValue(dataRow, 5, testCase.getConfirmationItem(), dataStyle);
            setCellValue(dataRow, 6, testCase.getTestModule(), dataStyle);
            setCellValue(dataRow, 7, testCase.getBaselineVersion(), dataStyle);
            setCellValue(dataRow, 8, testCase.getCreator(), dataStyle);
            setCellValue(dataRow, 9, testCase.getCreatedDate(), dataStyle);
            setCellValue(dataRow, 10, testCase.getModifier(), dataStyle);
            setCellValue(dataRow, 11, testCase.getModifiedDate(), dataStyle);
        }

        // 列幅を自動調整
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
            // FQCN列は長いパッケージ名に対応
            if (i == 1) {
                if (sheet.getColumnWidth(i) < 10000) {
                    sheet.setColumnWidth(i, 10000);
                }
            }
            // 最大幅を制限
            if (sheet.getColumnWidth(i) > 15000) {
                sheet.setColumnWidth(i, 15000);
            }
        }

        // フリーズペイン（ヘッダー行を固定）
        sheet.createFreezePane(0, 1);
    }

    /**
     * Summaryシートを作成
     */
    private void createSummarySheet(XSSFWorkbook workbook, List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        Sheet sheet = workbook.createSheet(SUMMARY_SHEET);

        CellStyle titleStyle = createTitleStyle(workbook);
        CellStyle labelStyle = createLabelStyle(workbook);
        CellStyle valueStyle = createValueStyle(workbook);

        int rowNum = 0;

        // タイトル
        Row titleRow = sheet.createRow(rowNum++);
        Cell titleCell = titleRow.createCell(0);
        titleCell.setCellValue("テスト仕様書生成サマリー");
        titleCell.setCellStyle(titleStyle);
        sheet.addMergedRegion(new CellRangeAddress(rowNum - 1, rowNum - 1, 0, 3));

        rowNum++; // 空行

        // 処理統計
        createSummarySection(sheet, rowNum, "処理統計", labelStyle, valueStyle);
        rowNum += 2;

        rowNum = addSummaryRow(sheet, rowNum, "処理日時:", getCurrentDateTime(), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "Javaファイル処理数:", String.valueOf(getUniqueClassCount(testCases)), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "テストケース抽出数:", String.valueOf(testCases.size()), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "カバレッジエントリ数:", String.valueOf(coverageData != null ? coverageData.size() : 0), labelStyle, valueStyle);

        rowNum++; // 空行

        // カバレッジ統計
        if (coverageData != null && !coverageData.isEmpty()) {
            createSummarySection(sheet, rowNum, "カバレッジ統計", labelStyle, valueStyle);
            rowNum += 2;

            double avgCoverage = calculateAverageCoverage(testCases);
            int[] branchStats = calculateBranchStats(testCases);

            rowNum = addSummaryRow(sheet, rowNum, "全体ブランチカバレッジ:", String.format("%.1f%%", avgCoverage), labelStyle, valueStyle);
            rowNum = addSummaryRow(sheet, rowNum, "カバー済みブランチ:", String.format("%d/%d", branchStats[0], branchStats[1]), labelStyle, valueStyle);
            rowNum = addSummaryRow(sheet, rowNum, "高カバレッジケース（80%以上）:", String.valueOf(countHighCoverageCases(testCases)), labelStyle, valueStyle);
        }

        rowNum++; // 空行

        // テスト実行結果統計
        createSummarySection(sheet, rowNum, "テスト実行結果", labelStyle, valueStyle);
        rowNum += 2;

        int[] testExecutionStats = calculateTestExecutionStats(testCases);
        double testSuccessRate = calculateTestSuccessRate(testCases);

        rowNum = addSummaryRow(sheet, rowNum, "総テスト数:", String.valueOf(testExecutionStats[1]), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "成功テスト数:", String.valueOf(testExecutionStats[0]), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "テスト成功率:", String.format("%.1f%%", testSuccessRate), labelStyle, valueStyle);

        rowNum++; // 空行

        // 品質指標
        createSummarySection(sheet, rowNum, "品質指標", labelStyle, valueStyle);
        rowNum += 2;

        rowNum = addSummaryRow(sheet, rowNum, "アノテーション完成度:", String.format("%.1f%%", calculateAnnotationCompleteness(testCases)), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "ドキュメント化済みケース:", String.valueOf(countDocumentedCases(testCases)), labelStyle, valueStyle);

        // 列幅設定
        sheet.setColumnWidth(0, 6000);
        sheet.setColumnWidth(1, 4000);
        sheet.setColumnWidth(2, 3000);
        sheet.setColumnWidth(3, 3000);
    }

    /**
     * Coverageシートを作成
     */
    private void createCoverageSheet(XSSFWorkbook workbook, List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        Sheet sheet = workbook.createSheet(COVERAGE_SHEET);

        CellStyle headerStyle = createHeaderStyle(workbook);
        CellStyle dataStyle = createDataStyle(workbook);

        // テスト対象クラス名からテストクラスへのマッピングを作成（クラスレベル）
        java.util.Map<String, java.util.Set<String>> classToTestClassMap = new java.util.HashMap<>();
        if (testCases != null) {
            for (TestCaseInfo testCase : testCases) {
                String testClassName = testCase.getClassName();
                String packageName = testCase.getPackageName();

                // テストクラスのFQCN（パッケージ名.クラス名）
                String testClassFQCN;
                if (packageName != null && !packageName.isEmpty() && !"未指定".equals(packageName)) {
                    testClassFQCN = packageName + "." + testClassName;
                } else {
                    testClassFQCN = testClassName;
                }

                // テストクラス名から "Test" サフィックスを除去してテスト対象クラス名を推測
                String targetClassName = testClassName;
                if (targetClassName.endsWith("Test")) {
                    targetClassName = targetClassName.substring(0, targetClassName.length() - 4);
                }

                classToTestClassMap.computeIfAbsent(targetClassName, k -> new java.util.HashSet<>()).add(testClassFQCN);
            }
        }

        // ヘッダー行
        Row headerRow = sheet.createRow(0);
        String[] headers = {
                "No.", "Package", "Class Name", "Method Name", "Source File",
                "Test Class (テストクラス)",
                "Branch Coverage %", "Branch (Covered/Total)", "Instruction Coverage %", "Instruction (Covered/Total)",
                "Line Coverage %", "Line (Covered/Total)", "Method Coverage %", "Method (Covered/Total)",
                "Status", "Report Type", "Primary Coverage (C1)"
        };

        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        // データ行
        if (coverageData != null) {
            for (int i = 0; i < coverageData.size(); i++) {
                CoverageInfo coverage = coverageData.get(i);
                Row dataRow = sheet.createRow(i + 1);

                int colIndex = 0;
                setCellValue(dataRow, colIndex++, i + 1, dataStyle); // No.
                setCellValue(dataRow, colIndex++, coverage.getPackageName(), dataStyle); // Package
                setCellValue(dataRow, colIndex++, coverage.getClassName(), dataStyle); // Class Name
                setCellValue(dataRow, colIndex++, coverage.getMethodName(), dataStyle); // Method Name
                setCellValue(dataRow, colIndex++, coverage.getSourceFile(), dataStyle); // Source File

                // テストクラスを検索（クラスレベルのマッピング）
                String className = coverage.getClassName();
                if (className == null) {
                    className = "Unknown"; // null safety
                } else {
                    // 内部クラスの場合は親クラス名を使用（例: DataStructures$MinHeap → DataStructures）
                    if (className.contains("$")) {
                        className = className.split("\\$")[0];
                    }
                }

                java.util.Set<String> testClasses = classToTestClassMap.get(className);
                String testClassDisplay;
                if (testClasses != null && !testClasses.isEmpty()) {
                    // 複数のテストクラスがある場合はカンマ区切りで表示
                    // （通常は1つのクラスに対して1つのテストクラスだが、複数の可能性もある）
                    testClassDisplay = String.join(", ", testClasses);
                } else {
                    testClassDisplay = "N/A";
                }
                setCellValue(dataRow, colIndex++, testClassDisplay, dataStyle); // Test Class

                // Branch Coverage
                setCellValue(dataRow, colIndex++, String.format("%.1f%%", coverage.getBranchCoverage()), dataStyle);
                setCellValue(dataRow, colIndex++, String.format("%d/%d", coverage.getBranchesCovered(), coverage.getBranchesTotal()), dataStyle);

                // Instruction Coverage
                setCellValue(dataRow, colIndex++, String.format("%.1f%%", coverage.getInstructionCoverage()), dataStyle);
                setCellValue(dataRow, colIndex++, String.format("%d/%d", coverage.getInstructionsCovered(), coverage.getInstructionsTotal()), dataStyle);

                // Line Coverage
                setCellValue(dataRow, colIndex++, String.format("%.1f%%", coverage.getLineCoverage()), dataStyle);
                setCellValue(dataRow, colIndex++, String.format("%d/%d", coverage.getLinesCovered(), coverage.getLinesTotal()), dataStyle);

                // Method Coverage
                setCellValue(dataRow, colIndex++, String.format("%.1f%%", coverage.getMethodCoverage()), dataStyle);
                setCellValue(dataRow, colIndex++, String.format("%d/%d", coverage.getMethodsCovered(), coverage.getMethodsTotal()), dataStyle);

                setCellValue(dataRow, colIndex++, coverage.getCoverageStatus(), dataStyle); // Status
                setCellValue(dataRow, colIndex++, coverage.getReportType(), dataStyle); // Report Type
                setCellValue(dataRow, colIndex++, String.format("%.1f%%", coverage.getPrimaryCoverage()), dataStyle); // Primary Coverage (C1)
            }
        }

        // 列幅調整
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
            // Test Class列は長いパッケージ名のため、最小幅を設定
            if (i == 5) {
                if (sheet.getColumnWidth(i) < 10000) {
                    sheet.setColumnWidth(i, 10000);
                }
            }
        }

        sheet.createFreezePane(0, 1);
    }

    /**
     * Configurationシートを作成
     */
    private void createConfigurationSheet(XSSFWorkbook workbook, List<TestCaseInfo> testCases, List<CoverageInfo> coverageData) {
        Sheet sheet = workbook.createSheet(CONFIGURATION_SHEET);

        CellStyle titleStyle = createTitleStyle(workbook);
        CellStyle labelStyle = createLabelStyle(workbook);
        CellStyle valueStyle = createValueStyle(workbook);

        int rowNum = 0;

        // タイトル
        Row titleRow = sheet.createRow(rowNum++);
        Cell titleCell = titleRow.createCell(0);
        titleCell.setCellValue("処理設定・システム情報");
        titleCell.setCellStyle(titleStyle);
        sheet.addMergedRegion(new CellRangeAddress(rowNum - 1, rowNum - 1, 0, 3));

        rowNum++; // 空行

        // システム情報
        createSummarySection(sheet, rowNum, "システム情報", labelStyle, valueStyle);
        rowNum += 2;

        rowNum = addSummaryRow(sheet, rowNum, "ツール名:", "Java Test Specification Generator", labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "バージョン:", "1.0.0", labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "実行環境:", System.getProperty("java.runtime.name"), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "Java バージョン:", System.getProperty("java.version"), labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "OS:", System.getProperty("os.name") + " " + System.getProperty("os.version"), labelStyle, valueStyle);

        rowNum++; // 空行

        // 処理設定
        createSummarySection(sheet, rowNum, "処理設定", labelStyle, valueStyle);
        rowNum += 2;

        rowNum = addSummaryRow(sheet, rowNum, "カバレッジ処理:", coverageData != null ? "有効" : "無効", labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "アノテーション解析:", "有効", labelStyle, valueStyle);
        rowNum = addSummaryRow(sheet, rowNum, "Excel形式:", "XLSX (Office 2007以降)", labelStyle, valueStyle);

        sheet.setColumnWidth(0, 4000);
        sheet.setColumnWidth(1, 8000);
    }

    // スタイル作成メソッド群

    private CellStyle createHeaderStyle(Workbook workbook) {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setBold(true);
        font.setColor(IndexedColors.WHITE.getIndex());
        style.setFont(font);
        style.setFillForegroundColor(COLOR_LIGHT_BLUE);
        style.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        style.setBorderBottom(BorderStyle.THIN);
        style.setBorderTop(BorderStyle.THIN);
        style.setBorderRight(BorderStyle.THIN);
        style.setBorderLeft(BorderStyle.THIN);
        style.setAlignment(HorizontalAlignment.CENTER);
        style.setVerticalAlignment(VerticalAlignment.CENTER);
        return style;
    }

    private CellStyle createDataStyle(XSSFWorkbook workbook) {
        CellStyle style = workbook.createCellStyle();
        style.setBorderBottom(BorderStyle.THIN);
        style.setBorderTop(BorderStyle.THIN);
        style.setBorderRight(BorderStyle.THIN);
        style.setBorderLeft(BorderStyle.THIN);
        style.setVerticalAlignment(VerticalAlignment.TOP);
        style.setWrapText(true);
        return style;
    }

    private CellStyle createTitleStyle(XSSFWorkbook workbook) {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setBold(true);
        font.setFontHeightInPoints((short) 16);
        style.setFont(font);
        style.setAlignment(HorizontalAlignment.CENTER);
        return style;
    }

    private CellStyle createLabelStyle(XSSFWorkbook workbook) {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setBold(true);
        style.setFont(font);
        style.setFillForegroundColor(COLOR_LIGHT_YELLOW);
        style.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        return style;
    }

    private CellStyle createValueStyle(XSSFWorkbook workbook) {
        CellStyle style = workbook.createCellStyle();
        style.setFillForegroundColor(COLOR_WHITE);
        style.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        return style;
    }

    // ヘルパーメソッド群

    private void setCellValue(Row row, int column, Object value, CellStyle style) {
        Cell cell = row.createCell(column);
        if (value instanceof Number) {
            cell.setCellValue(((Number) value).doubleValue());
        } else {
            cell.setCellValue(value != null ? value.toString() : "");
        }
        cell.setCellStyle(style);
    }

    private void createSummarySection(Sheet sheet, int rowNum, String title, CellStyle labelStyle, CellStyle valueStyle) {
        Row sectionRow = sheet.createRow(rowNum);
        Cell sectionCell = sectionRow.createCell(0);
        sectionCell.setCellValue(title);
        sectionCell.setCellStyle(labelStyle);
        sheet.addMergedRegion(new CellRangeAddress(rowNum, rowNum, 0, 3));
    }

    private int addSummaryRow(Sheet sheet, int rowNum, String label, String value, CellStyle labelStyle, CellStyle valueStyle) {
        Row row = sheet.createRow(rowNum);

        Cell labelCell = row.createCell(0);
        labelCell.setCellValue(label);
        labelCell.setCellStyle(labelStyle);

        Cell valueCell = row.createCell(1);
        valueCell.setCellValue(value);
        valueCell.setCellStyle(valueStyle);

        return rowNum + 1;
    }

    private String getCurrentDateTime() {
        return LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }

    private int getUniqueClassCount(List<TestCaseInfo> testCases) {
        return (int) testCases.stream().map(TestCaseInfo::getClassName).distinct().count();
    }

    private double calculateAverageCoverage(List<TestCaseInfo> testCases) {
        return testCases.stream().mapToDouble(TestCaseInfo::getCoveragePercent).average().orElse(0.0);
    }

    private int[] calculateBranchStats(List<TestCaseInfo> testCases) {
        int totalCovered = testCases.stream().mapToInt(TestCaseInfo::getBranchesCovered).sum();
        int totalBranches = testCases.stream().mapToInt(TestCaseInfo::getBranchesTotal).sum();
        return new int[]{totalCovered, totalBranches};
    }

    private int countHighCoverageCases(List<TestCaseInfo> testCases) {
        return (int) testCases.stream().filter(tc -> tc.getCoveragePercent() >= 80.0).count();
    }

    private double calculateAnnotationCompleteness(List<TestCaseInfo> testCases) {
        if (testCases.isEmpty()) return 0.0;

        long annotatedCount = testCases.stream()
                .filter(tc -> !"Not Specified".equals(tc.getTestModule()))
                .count();

        return (double) annotatedCount / testCases.size() * 100.0;
    }

    private int countDocumentedCases(List<TestCaseInfo> testCases) {
        return (int) testCases.stream()
                .filter(tc -> !"Not Specified".equals(tc.getTestModule()) ||
                             !"Not Specified".equals(tc.getTestCase()))
                .count();
    }

    private int[] calculateTestExecutionStats(List<TestCaseInfo> testCases) {
        int totalPassed = testCases.stream().mapToInt(TestCaseInfo::getTestsPassed).sum();
        int totalTests = testCases.stream().mapToInt(TestCaseInfo::getTestsTotal).sum();
        return new int[]{totalPassed, totalTests};
    }

    private double calculateTestSuccessRate(List<TestCaseInfo> testCases) {
        int totalPassed = testCases.stream().mapToInt(TestCaseInfo::getTestsPassed).sum();
        int totalTests = testCases.stream().mapToInt(TestCaseInfo::getTestsTotal).sum();
        if (totalTests == 0) {
            return 0.0;
        }
        return (double) totalPassed / totalTests * 100.0;
    }

    // Multi-module specific sheet creation methods

    /**
     * Creates Test Details sheet with module information for multi-module projects
     */
    private void createTestDetailsSheetWithModules(Workbook workbook, List<TestCaseInfo> testCases, List<ModuleResult> results) {
        Sheet sheet = workbook.createSheet(TEST_DETAILS_SHEET);

        // Create header style
        CellStyle headerStyle = createHeaderStyle(workbook);

        // Header row with module column
        Row headerRow = sheet.createRow(0);
        String[] headers = {
            "No.", "FQCN (完全修飾クラス名)", "Module Name", "ソフトウェア・サービス", "項目名", "試験内容",
            "確認項目", "テスト対象モジュール名", "テスト実施ベースラインバージョン",
            "テストケース作成者", "テストケース作成日", "テストケース修正者", "テストケース修正日"
        };

        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        // Data rows
        int rowIndex = 1;
        for (ModuleResult result : results) {
            if (!result.isSuccessful() || !result.hasTestCases()) continue;

            String moduleName = result.getModuleInfo().getModuleName();
            for (TestCaseInfo testCase : result.getTestCases()) {
                Row row = sheet.createRow(rowIndex);

                row.createCell(0).setCellValue(rowIndex);
                row.createCell(1).setCellValue(testCase.getFullyQualifiedName());
                row.createCell(2).setCellValue(moduleName);
                row.createCell(3).setCellValue(testCase.getSoftwareService());
                row.createCell(4).setCellValue(testCase.getTestItemName());
                row.createCell(5).setCellValue(testCase.getTestContent());
                row.createCell(6).setCellValue(testCase.getConfirmationItem());
                row.createCell(7).setCellValue(testCase.getTestModule());
                row.createCell(8).setCellValue(testCase.getBaselineVersion());
                row.createCell(9).setCellValue(testCase.getCreator());
                row.createCell(10).setCellValue(testCase.getCreatedDate());
                row.createCell(11).setCellValue(testCase.getModifier());
                row.createCell(12).setCellValue(testCase.getModifiedDate());

                rowIndex++;
            }
        }

        // Auto-size columns
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
    }

    /**
     * Creates Summary sheet with multi-module statistics
     */
    private void createSummarySheetWithModules(Workbook workbook, List<TestCaseInfo> allTestCases,
                                             Map<String, Object> allCoverageData, List<ModuleResult> results) {
        Sheet sheet = workbook.createSheet(SUMMARY_SHEET);

        CellStyle headerStyle = createHeaderStyle(workbook);
        int rowIndex = 0;

        // Overall summary
        Row titleRow = sheet.createRow(rowIndex++);
        Cell titleCell = titleRow.createCell(0);
        titleCell.setCellValue("マルチモジュールプロジェクト統合サマリー");
        titleCell.setCellStyle(headerStyle);

        rowIndex++; // Empty row

        // Project statistics
        sheet.createRow(rowIndex++).createCell(0).setCellValue("総モジュール数: " + results.size());
        long successful = results.stream().mapToLong(r -> r.isSuccessful() ? 1 : 0).sum();
        sheet.createRow(rowIndex++).createCell(0).setCellValue("成功したモジュール: " + successful);
        sheet.createRow(rowIndex++).createCell(0).setCellValue("失敗したモジュール: " + (results.size() - successful));
        sheet.createRow(rowIndex++).createCell(0).setCellValue("総テストケース: " + allTestCases.size());

        rowIndex++; // Empty row

        // Module-by-module breakdown
        Row moduleHeaderRow = sheet.createRow(rowIndex++);
        String[] moduleHeaders = {"Module Name", "Status", "Test Cases", "Processing Time (ms)"};
        for (int i = 0; i < moduleHeaders.length; i++) {
            Cell cell = moduleHeaderRow.createCell(i);
            cell.setCellValue(moduleHeaders[i]);
            cell.setCellStyle(headerStyle);
        }

        for (ModuleResult result : results) {
            Row row = sheet.createRow(rowIndex++);
            row.createCell(0).setCellValue(result.getModuleInfo().getModuleName());
            row.createCell(1).setCellValue(result.getProcessingStatus().toString());
            row.createCell(2).setCellValue(result.hasTestCases() ? result.getTestCases().size() : 0);
            row.createCell(3).setCellValue(result.getProcessingTimeMs());
        }

        // Auto-size columns
        for (int i = 0; i < 4; i++) {
            sheet.autoSizeColumn(i);
        }
    }

    /**
     * Creates Coverage sheet with module information
     */
    private void createCoverageSheetWithModules(Workbook workbook, List<TestCaseInfo> allTestCases,
                                              Map<String, Object> allCoverageData, List<ModuleResult> results) {
        // For now, create a simplified coverage sheet
        // In a full implementation, this would need to aggregate coverage data from all modules
        Sheet sheet = workbook.createSheet(COVERAGE_SHEET);

        CellStyle headerStyle = createHeaderStyle(workbook);

        Row headerRow = sheet.createRow(0);
        String[] headers = {"Module Name", "Test Cases", "Coverage Status"};

        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        int rowIndex = 1;
        for (ModuleResult result : results) {
            if (!result.isSuccessful()) continue;

            Row row = sheet.createRow(rowIndex++);
            row.createCell(0).setCellValue(result.getModuleInfo().getModuleName());
            row.createCell(1).setCellValue(result.hasTestCases() ? result.getTestCases().size() : 0);
            row.createCell(2).setCellValue(result.hasCoverageData() ? "Available" : "No Coverage Data");
        }

        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
    }

    /**
     * Creates a new Modules sheet with module processing details
     */
    private void createModulesSheet(Workbook workbook, List<ModuleResult> results) {
        Sheet sheet = workbook.createSheet("Modules");

        CellStyle headerStyle = createHeaderStyle(workbook);

        Row headerRow = sheet.createRow(0);
        String[] headers = {
            "Module Name", "Status", "Test Cases", "Has Coverage", "Processing Time (ms)", "Error Message"
        };

        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
            cell.setCellStyle(headerStyle);
        }

        int rowIndex = 1;
        for (ModuleResult result : results) {
            Row row = sheet.createRow(rowIndex++);
            row.createCell(0).setCellValue(result.getModuleInfo().getModuleName());
            row.createCell(1).setCellValue(result.getProcessingStatus().toString());
            row.createCell(2).setCellValue(result.hasTestCases() ? result.getTestCases().size() : 0);
            row.createCell(3).setCellValue(result.hasCoverageData() ? "Yes" : "No");
            row.createCell(4).setCellValue(result.getProcessingTimeMs());
            row.createCell(5).setCellValue(result.getErrorMessage() != null ? result.getErrorMessage() : "");
        }

        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }
    }

    /**
     * Creates Configuration sheet with multi-module information
     */
    private void createConfigurationSheetWithModules(Workbook workbook, List<TestCaseInfo> allTestCases,
                                                    Map<String, Object> allCoverageData, List<ModuleResult> results) {
        Sheet sheet = workbook.createSheet(CONFIGURATION_SHEET);

        int rowIndex = 0;

        // Processing information
        sheet.createRow(rowIndex++).createCell(0).setCellValue("処理モード: マルチモジュール");
        sheet.createRow(rowIndex++).createCell(0).setCellValue("処理日時: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        sheet.createRow(rowIndex++).createCell(0).setCellValue("総モジュール数: " + results.size());

        long successful = results.stream().mapToLong(r -> r.isSuccessful() ? 1 : 0).sum();
        sheet.createRow(rowIndex++).createCell(0).setCellValue("成功モジュール数: " + successful);
        sheet.createRow(rowIndex++).createCell(0).setCellValue("総テストケース数: " + allTestCases.size());

        rowIndex++; // Empty row

        // Module list
        sheet.createRow(rowIndex++).createCell(0).setCellValue("処理されたモジュール:");
        for (ModuleResult result : results) {
            String status = result.isSuccessful() ? "✓" : "✗";
            sheet.createRow(rowIndex++).createCell(0)
                 .setCellValue(status + " " + result.getModuleInfo().getModuleName());
        }

        sheet.autoSizeColumn(0);
    }
}