package com.testspecgenerator;

import com.testspecgenerator.core.*;
import com.testspecgenerator.model.*;
import org.apache.commons.cli.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Scanner;

/**
 * Java Test Specification Generator メインクラス
 *
 * Javaテストファイルからカスタムアノテーションを抽出し、
 * JaCoCoカバレッジレポートと統合してExcelテスト仕様書を自動生成します。
 */
public class TestSpecificationGeneratorMain {

    private static final Logger logger = LoggerFactory.getLogger(TestSpecificationGeneratorMain.class);
    private static final String VERSION = "1.0.0";

    private final FolderScanner folderScanner;
    private final JavaAnnotationParser annotationParser;
    private final CoverageReportParser coverageParser;
    private final SurefireReportParser surefireParser;
    private final ExcelSheetBuilder excelBuilder;
    private final CsvSheetBuilder csvBuilder;
    private final EnhancedJavaDocBuilder javaDocBuilder;

    private LocalDateTime processingStartTime;

    public TestSpecificationGeneratorMain() {
        this.folderScanner = new FolderScanner();
        this.annotationParser = new JavaAnnotationParser();
        this.coverageParser = new CoverageReportParser();
        this.surefireParser = new SurefireReportParser();
        this.excelBuilder = new ExcelSheetBuilder();
        this.csvBuilder = new CsvSheetBuilder();
        this.javaDocBuilder = new EnhancedJavaDocBuilder();
    }

    public static void main(String[] args) {
        TestSpecificationGeneratorMain app = new TestSpecificationGeneratorMain();

        try {
            app.run(args);
        } catch (Exception e) {
            logger.error("アプリケーション実行エラー", e);
            System.exit(1);
        }
    }

    public void run(String[] args) throws Exception {
        Options options = createCommandLineOptions();
        CommandLineParser parser = new DefaultParser();

        try {
            CommandLine cmd = parser.parse(options, args);

            if (cmd.hasOption("help")) {
                printHelp(options);
                return;
            }

            if (cmd.hasOption("version")) {
                printVersion();
                return;
            }

            if (cmd.hasOption("interactive")) {
                runInteractiveMode();
                return;
            }

            // コマンドライン引数から設定を取得
            String sourceDir = cmd.getOptionValue("source-dir");
            String outputFile = cmd.getOptionValue("output");
            String coverageDir = cmd.getOptionValue("coverage-dir");
            boolean includeCoverage = !cmd.hasOption("no-coverage");
            boolean csvOutput = cmd.hasOption("csv-output");
            String logLevel = cmd.getOptionValue("log-level", "INFO");

            if (sourceDir == null || outputFile == null) {
                System.err.println("エラー: --source-dir と --output は必須パラメータです");
                printHelp(options);
                System.exit(1);
            }

            // ログレベル設定
            setLogLevel(logLevel);

            // 処理実行
            boolean success = generateTestSpecification(sourceDir, outputFile, coverageDir, includeCoverage, csvOutput, false);

            if (!success) {
                System.exit(1);
            }

        } catch (ParseException e) {
            System.err.println("コマンドライン引数解析エラー: " + e.getMessage());
            printHelp(options);
            System.exit(1);
        }
    }

    private Options createCommandLineOptions() {
        Options options = new Options();

        options.addOption(Option.builder("s")
                .longOpt("source-dir")
                .hasArg()
                .argName("directory")
                .desc("Javaテストファイルのソースディレクトリ")
                .build());

        options.addOption(Option.builder("o")
                .longOpt("output")
                .hasArg()
                .argName("file")
                .desc("出力Excelファイルのパス")
                .build());

        options.addOption(Option.builder("c")
                .longOpt("coverage-dir")
                .hasArg()
                .argName("directory")
                .desc("カバレッジレポートのディレクトリ（省略時はソースディレクトリから自動検索）")
                .build());

        options.addOption(Option.builder()
                .longOpt("no-coverage")
                .desc("カバレッジレポート処理をスキップ")
                .build());

        options.addOption(Option.builder()
                .longOpt("csv-output")
                .desc("CSV形式でのテスト仕様書も生成（Excel出力に追加）")
                .build());

        options.addOption(Option.builder("i")
                .longOpt("interactive")
                .desc("対話モードで実行")
                .build());

        options.addOption(Option.builder()
                .longOpt("log-level")
                .hasArg()
                .argName("level")
                .desc("ログレベル (DEBUG/INFO/WARNING/ERROR)")
                .build());

        options.addOption(Option.builder("h")
                .longOpt("help")
                .desc("このヘルプメッセージを表示")
                .build());

        options.addOption(Option.builder("v")
                .longOpt("version")
                .desc("バージョン情報を表示")
                .build());

        return options;
    }

    private void printHelp(Options options) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.printHelp("java -jar java-test-specification-generator-1.0.0.jar",
                "Java Test Specification Generator - Javaテストファイルから仕様書を生成",
                options,
                "\n使用例:\n" +
                "  # 基本的な使用方法（完全なデータ取得）\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --output test_specification.xlsx\n\n" +
                "  # カバレッジレポートのディレクトリを明示的に指定\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --coverage-dir ./target/site/jacoco \\\n" +
                "    --output report.xlsx\n\n" +
                "  # ExcelとCSVの両方を生成\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --output report.xlsx \\\n" +
                "    --csv-output\n\n" +
                "  # 対話モード\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar --interactive\n\n" +
                "  # デバッグモード\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --output report.xlsx \\\n" +
                "    --log-level DEBUG\n");
    }

    private void printVersion() {
        System.out.println("Java Test Specification Generator " + VERSION);
    }

    private void runInteractiveMode() {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== Java Test Specification Generator 対話モード ===");
        System.out.println("バージョン: " + VERSION);
        System.out.println();

        // ソースディレクトリ入力
        System.out.print("ソースディレクトリのパスを入力してください: ");
        String sourceDir = scanner.nextLine().trim();

        // 出力ファイル入力
        System.out.print("出力Excelファイルのパスを入力してください: ");
        String outputFile = scanner.nextLine().trim();

        // カバレッジ処理確認
        System.out.print("カバレッジレポートを処理しますか？ (y/n) [y]: ");
        String coverageInput = scanner.nextLine().trim();
        boolean includeCoverage = coverageInput.isEmpty() || coverageInput.toLowerCase().startsWith("y");

        scanner.close();

        try {
            boolean success = generateTestSpecification(sourceDir, outputFile, null, includeCoverage, false, true);
            if (!success) {
                System.exit(1);
            }
        } catch (Exception e) {
            logger.error("処理中にエラーが発生しました", e);
            System.exit(1);
        }
    }

    public boolean generateTestSpecification(String sourceDirectory, String outputFile,
                                           String coverageDirectory, boolean includeCoverage, boolean csvOutput, boolean interactive) {
        try {
            this.processingStartTime = LocalDateTime.now();

            logger.info("📊 Java Test Specification Generator 開始");
            logger.info("   バージョン: {}", VERSION);
            logger.info("   ソース: {}", sourceDirectory);
            logger.info("   出力: {}", outputFile);

            // Step 1: Javaファイルスキャン
            logger.info("🔍 Step 1: Javaファイルスキャン開始...");
            List<Path> javaFiles = folderScanner.scanForJavaFiles(Paths.get(sourceDirectory));
            logger.info("✅ Javaファイル発見: {}個", javaFiles.size());

            if (javaFiles.isEmpty()) {
                logger.error("❌ Javaファイルが見つかりません");
                return false;
            }

            // Step 2: アノテーション解析
            logger.info("📝 Step 2: アノテーション解析開始...");
            List<TestCaseInfo> testCases = annotationParser.processJavaFiles(javaFiles);
            logger.info("✅ テストケース抽出: {}個", testCases.size());

            // Step 3: カバレッジレポート処理
            List<CoverageInfo> coverageData = null;
            if (includeCoverage) {
                logger.info("📈 Step 3: カバレッジレポート処理開始...");

                // カバレッジディレクトリの決定
                String coverageScanDir = (coverageDirectory != null) ? coverageDirectory : sourceDirectory;
                if (coverageDirectory != null) {
                    logger.info("   カバレッジディレクトリ: {}", coverageDirectory);
                }

                List<Path> coverageFiles = folderScanner.scanForCoverageReports(Paths.get(coverageScanDir));
                coverageData = coverageParser.processCoverageReports(coverageFiles);
                logger.info("✅ カバレッジデータ取得: {}個", coverageData.size());

                // カバレッジデータをテストケースにマージ
                coverageParser.mergeCoverageWithTestCases(testCases, coverageData);
            } else {
                logger.info("⏭️ Step 3: カバレッジレポート処理をスキップ");
            }

            // Step 3.5: Surefireテストレポート処理
            logger.info("📊 Step 3.5: テスト実行結果処理開始...");
            List<Path> surefireReports = folderScanner.scanForSurefireReports(Paths.get(sourceDirectory));
            if (!surefireReports.isEmpty()) {
                List<TestExecutionInfo> executionResults = surefireParser.parseSurefireReports(surefireReports);
                surefireParser.mergeExecutionResults(testCases, executionResults);
                logger.info("✅ テスト実行結果取得: {}個のテストスイート", executionResults.size());
            } else {
                logger.info("⚠️ Surefireテストレポートが見つかりません - テスト実行結果は0/0と表示されます");
            }

            // Step 4: Excelレポート生成
            logger.info("📊 Step 4: Excelレポート生成開始...");
            boolean excelSuccess = excelBuilder.generateTestSpecificationReport(outputFile, testCases, coverageData);

            if (!excelSuccess) {
                logger.error("❌ Excelレポート生成に失敗しました");
                return false;
            }
            logger.info("✅ Excelレポート生成完了");

            // Step 4.5: CSV出力（オプション）
            boolean csvSuccess = true;
            if (csvOutput) {
                logger.info("📄 Step 4.5: CSVレポート生成開始...");
                boolean testDetailsCsvSuccess = csvBuilder.generateTestDetailsCsv(outputFile, testCases);
                boolean coverageCsvSuccess = csvBuilder.generateCoverageSheetCsv(outputFile, testCases, coverageData);

                csvSuccess = testDetailsCsvSuccess && coverageCsvSuccess;

                if (csvSuccess) {
                    logger.info("✅ CSVレポート生成完了");
                } else {
                    logger.warn("⚠️ CSVレポート生成に一部失敗しましたが、処理を継続します");
                }
            }

            // Step 5: 拡張JavaDocレポート生成
            logger.info("🌐 Step 5: 拡張JavaDocレポート生成開始...");
            boolean javaDocSuccess = javaDocBuilder.generateEnhancedJavaDoc(testCases, coverageData);

            if (javaDocSuccess) {
                logger.info("✅ 拡張JavaDocレポート生成完了");
            } else {
                logger.warn("⚠️ 拡張JavaDocレポート生成に失敗しましたが、処理を継続します");
            }

            printSummary(javaFiles.size(), testCases.size(),
                       coverageData != null ? coverageData.size() : 0, outputFile, csvOutput);
            return true;

        } catch (Exception e) {
            logger.error("処理中にエラーが発生しました", e);
            return false;
        }
    }

    private void printSummary(int javaFiles, int testCases, int coverageEntries, String outputFile, boolean csvOutput) {
        LocalDateTime endTime = LocalDateTime.now();
        java.time.Duration duration = java.time.Duration.between(processingStartTime, endTime);

        System.out.println();
        System.out.println("============================================================");
        System.out.println("🎉 処理完了サマリー");
        System.out.println("============================================================");
        System.out.println("📁 Javaファイル処理: " + javaFiles + "個");
        System.out.println("🧪 テストケース抽出: " + testCases + "個");
        System.out.println("📈 カバレッジエントリ: " + coverageEntries + "個");
        System.out.println("⏱️ 処理時間: " + formatDuration(duration));
        System.out.println("📊 出力ファイル: " + outputFile);

        // CSV出力ファイル情報も表示
        if (csvOutput) {
            String baseName = outputFile.substring(0, outputFile.lastIndexOf('.'));
            System.out.println("📄 CSV出力ファイル: " + baseName + "_test_details.csv");
            System.out.println("📄 CSV出力ファイル: " + baseName + "_coverage.csv");
        }

        // ファイルサイズ表示
        try {
            Path outputPath = Paths.get(outputFile);
            if (java.nio.file.Files.exists(outputPath)) {
                long fileSize = java.nio.file.Files.size(outputPath);
                System.out.println("📏 Excelファイルサイズ: " + String.format("%,d", fileSize) + "バイト");
            }

            // CSVファイルサイズも表示
            if (csvOutput) {
                String baseName = outputFile.substring(0, outputFile.lastIndexOf('.'));
                displayCsvFileSize(baseName + "_test_details.csv");
                displayCsvFileSize(baseName + "_coverage.csv");
            }
        } catch (Exception e) {
            // ファイルサイズ取得エラーは無視
        }

        System.out.println("============================================================");
        if (csvOutput) {
            System.out.println("✅ テスト仕様書（ExcelとCSV）が正常に生成されました");
        } else {
            System.out.println("✅ テスト仕様書が正常に生成されました: " + outputFile);
        }
    }

    private void displayCsvFileSize(String csvFilePath) {
        try {
            Path csvPath = Paths.get(csvFilePath);
            if (java.nio.file.Files.exists(csvPath)) {
                long fileSize = java.nio.file.Files.size(csvPath);
                System.out.println("📏 CSVファイルサイズ (" + csvPath.getFileName() + "): " + String.format("%,d", fileSize) + "バイト");
            }
        } catch (Exception e) {
            // CSVファイルサイズ取得エラーは無視
        }
    }

    private String formatDuration(java.time.Duration duration) {
        long seconds = duration.getSeconds();
        long millis = duration.toMillis() % 1000;

        if (seconds > 0) {
            return String.format("%d.%03d秒", seconds, millis);
        } else {
            return String.format("0.%03d秒", millis);
        }
    }

    private void setLogLevel(String logLevel) {
        // ログレベルの設定はlogback.xmlで管理
        // ここでは設定確認のみ
        logger.debug("ログレベル設定: {}", logLevel);
    }
}