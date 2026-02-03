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
 * Java Test Specification Generator Main Class
 *
 * Extracts custom annotations from Java test files and
 * automatically generates Excel test specification documents integrated with JaCoCo coverage reports.
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
            logger.error("Application execution error", e);
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

            // Get configuration from command line arguments
            String sourceDir = cmd.getOptionValue("source-dir");
            String outputFile = cmd.getOptionValue("output");
            String projectRoot = cmd.getOptionValue("project-root");
            String outputDir = cmd.getOptionValue("output-dir");
            String coverageDir = cmd.getOptionValue("coverage-dir");
            boolean includeCoverage = !cmd.hasOption("no-coverage");
            boolean csvOutput = cmd.hasOption("csv-output");
            String logLevel = cmd.getOptionValue("log-level", "INFO");

            // Set log level
            setLogLevel(logLevel);

            // Multi-module mode check
            boolean isMultiModuleMode = projectRoot != null && outputDir != null;

            if (isMultiModuleMode) {
                // Multi-module processing
                logger.info("Running in multi-module mode");
                boolean success = generateMultiModuleSpecification(projectRoot, outputDir, csvOutput);
                if (!success) {
                    System.exit(1);
                }
            } else {
                // Single module mode (backward compatibility)
                if (sourceDir == null || outputFile == null) {
                    System.err.println("Error: --source-dir and --output are required parameters for single-module mode");
                    System.err.println("To use multi-module mode, specify --project-root and --output-dir");
                    printHelp(options);
                    System.exit(1);
                }

                // Execute processing
                boolean success = generateTestSpecification(sourceDir, outputFile, coverageDir, includeCoverage, csvOutput, false);
                if (!success) {
                    System.exit(1);
                }
            }

        } catch (ParseException e) {
            System.err.println("Command line argument parsing error: " + e.getMessage());
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
                .desc("Source directory of Java test files")
                .build());

        options.addOption(Option.builder("o")
                .longOpt("output")
                .hasArg()
                .argName("file")
                .desc("Path of output Excel file")
                .build());

        options.addOption(Option.builder("c")
                .longOpt("coverage-dir")
                .hasArg()
                .argName("directory")
                .desc("Coverage report directory (auto-search from source directory if omitted)")
                .build());

        options.addOption(Option.builder()
                .longOpt("no-coverage")
                .desc("Skip coverage report processing")
                .build());

        options.addOption(Option.builder()
                .longOpt("csv-output")
                .desc("Generate test specification in CSV format as well (additional to Excel output)")
                .build());

        options.addOption(Option.builder("i")
                .longOpt("interactive")
                .desc("Run in interactive mode")
                .build());

        options.addOption(Option.builder()
                .longOpt("log-level")
                .hasArg()
                .argName("level")
                .desc("Log level (DEBUG/INFO/WARNING/ERROR)")
                .build());

        options.addOption(Option.builder("h")
                .longOpt("help")
                .desc("Show this help message")
                .build());

        options.addOption(Option.builder("v")
                .longOpt("version")
                .desc("Show version information")
                .build());

        // Multi-module support options
        options.addOption(Option.builder("pr")
                .longOpt("project-root")
                .hasArg()
                .argName("directory")
                .desc("Root directory of multi-module project (where pom.xml is located)")
                .build());

        options.addOption(Option.builder("od")
                .longOpt("output-dir")
                .hasArg()
                .argName("directory")
                .desc("Output directory (for multi-module: sub-folders are automatically created)")
                .build());

        return options;
    }

    private void printHelp(Options options) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.printHelp("java -jar java-test-specification-generator-1.0.0.jar",
                "Java Test Specification Generator - Generate specification from Java test files",
                options,
                "\nUsage Examples:\n" +
                "  # Basic usage (single module: complete data retrieval)\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --output test_specification.xlsx\n\n" +
                "  # Multi-module project processing\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --project-root /path/to/multimodule-project \\\n" +
                "    --output-dir /path/to/output\n\n" +
                "  # Multi-module + CSV output\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --project-root . \\\n" +
                "    --output-dir ./reports \\\n" +
                "    --csv-output\n\n" +
                "  # Explicitly specify coverage report directory (single module)\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --coverage-dir ./target/site/jacoco \\\n" +
                "    --output report.xlsx\n\n" +
                "  # Generate both Excel and CSV (single module)\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar \\\n" +
                "    --source-dir . \\\n" +
                "    --output report.xlsx \\\n" +
                "    --csv-output\n\n" +
                "  # Interactive mode (single module)\n" +
                "  java -jar java-test-specification-generator-1.0.0.jar --interactive\n\n" +
                "  # Debug mode\n" +
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

        System.out.println("=== Java Test Specification Generator Interactive Mode ===");
        System.out.println("Version: " + VERSION);
        System.out.println();

        // Source directory input
        System.out.print("Please enter the source directory path: ");
        String sourceDir = scanner.nextLine().trim();

        // Output file input
        System.out.print("Please enter the output Excel file path: ");
        String outputFile = scanner.nextLine().trim();

        // Coverage processing confirmation
        System.out.print("Process coverage reports? (y/n) [y]: ");
        String coverageInput = scanner.nextLine().trim();
        boolean includeCoverage = coverageInput.isEmpty() || coverageInput.toLowerCase().startsWith("y");

        scanner.close();

        try {
            boolean success = generateTestSpecification(sourceDir, outputFile, null, includeCoverage, false, true);
            if (!success) {
                System.exit(1);
            }
        } catch (Exception e) {
            logger.error("Error occurred during processing", e);
            System.exit(1);
        }
    }

    public boolean generateTestSpecification(String sourceDirectory, String outputFile,
                                           String coverageDirectory, boolean includeCoverage, boolean csvOutput, boolean interactive) {
        try {
            this.processingStartTime = LocalDateTime.now();

            logger.info("Java Test Specification Generator started");
            logger.info("   Version: {}", VERSION);
            logger.info("   Source: {}", sourceDirectory);
            logger.info("   Output: {}", outputFile);

            // Step 1: Java file scanning
            logger.info("Step 1: Java file scanning started...");
            List<Path> javaFiles = folderScanner.scanForJavaFiles(Paths.get(sourceDirectory));
            logger.info("Java files found: {} files", javaFiles.size());

            if (javaFiles.isEmpty()) {
                logger.error("No Java files found");
                return false;
            }

            // Step 2: Annotation parsing
            logger.info("Step 2: Annotation parsing started...");
            List<TestCaseInfo> testCases = annotationParser.processJavaFiles(javaFiles);
            logger.info("Test cases extracted: {} cases", testCases.size());

            // Step 3: Coverage report processing
            List<CoverageInfo> coverageData = null;
            if (includeCoverage) {
                logger.info("Step 3: Coverage report processing started...");

                // Determine coverage directory
                String coverageScanDir = (coverageDirectory != null) ? coverageDirectory : sourceDirectory;
                if (coverageDirectory != null) {
                    logger.info("   Coverage directory: {}", coverageDirectory);
                }

                List<Path> coverageFiles = folderScanner.scanForCoverageReports(Paths.get(coverageScanDir));
                coverageData = coverageParser.processCoverageReports(coverageFiles);
                logger.info("Coverage data retrieved: {} entries", coverageData.size());

                // Merge coverage data with test cases
                coverageParser.mergeCoverageWithTestCases(testCases, coverageData);
            } else {
                logger.info("Step 3: Skipping coverage report processing");
            }

            // Step 3.5: Surefire test report processing
            logger.info("Step 3.5: Test execution result processing started...");
            List<Path> surefireReports = folderScanner.scanForSurefireReports(Paths.get(sourceDirectory));
            if (!surefireReports.isEmpty()) {
                List<TestExecutionInfo> executionResults = surefireParser.parseSurefireReports(surefireReports);
                surefireParser.mergeExecutionResults(testCases, executionResults);
                logger.info("Test execution results retrieved: {} test suites", executionResults.size());
            } else {
                logger.info("WARNING: Surefire test reports not found - test execution results will be displayed as 0/0");
            }

            // Step 4: Excel report generation
            logger.info("Step 4: Excel report generation started...");
            boolean excelSuccess = excelBuilder.generateTestSpecificationReport(outputFile, testCases, coverageData);

            if (!excelSuccess) {
                logger.error("Excel report generation failed");
                return false;
            }
            logger.info("Excel report generation completed");

            // Step 4.5: CSV output (optional)
            boolean csvSuccess = true;
            if (csvOutput) {
                logger.info("Step 4.5: CSV report generation started...");
                boolean testDetailsCsvSuccess = csvBuilder.generateTestDetailsCsv(outputFile, testCases);
                boolean coverageCsvSuccess = csvBuilder.generateCoverageSheetCsv(outputFile, testCases, coverageData);

                csvSuccess = testDetailsCsvSuccess && coverageCsvSuccess;

                if (csvSuccess) {
                    logger.info("CSV report generation completed");
                } else {
                    logger.warn("CSV report generation partially failed, but processing continues");
                }
            }

            // Step 5: Enhanced JavaDoc report generation
            logger.info("Step 5: Enhanced JavaDoc report generation started...");
            boolean javaDocSuccess = javaDocBuilder.generateEnhancedJavaDoc(testCases, coverageData);

            if (javaDocSuccess) {
                logger.info("Enhanced JavaDoc report generation completed");
            } else {
                logger.warn("Enhanced JavaDoc report generation failed, but processing continues");
            }

            printSummary(javaFiles.size(), testCases.size(),
                       coverageData != null ? coverageData.size() : 0, outputFile, csvOutput);
            return true;

        } catch (Exception e) {
            logger.error("Error occurred during processing", e);
            return false;
        }
    }

    private void printSummary(int javaFiles, int testCases, int coverageEntries, String outputFile, boolean csvOutput) {
        LocalDateTime endTime = LocalDateTime.now();
        java.time.Duration duration = java.time.Duration.between(processingStartTime, endTime);

        System.out.println();
        System.out.println("============================================================");
        System.out.println("Processing Completed Summary");
        System.out.println("============================================================");
        System.out.println("Java files processed: " + javaFiles + " files");
        System.out.println("Test cases extracted: " + testCases + " cases");
        System.out.println("Coverage entries: " + coverageEntries + " entries");
        System.out.println("Processing time: " + formatDuration(duration));
        System.out.println("Output file: " + outputFile);

        // Display CSV output file information as well
        if (csvOutput) {
            String baseName = outputFile.substring(0, outputFile.lastIndexOf('.'));
            System.out.println("CSV output file: " + baseName + "_test_details.csv");
            System.out.println("CSV output file: " + baseName + "_coverage.csv");
        }

        // Display file size
        try {
            Path outputPath = Paths.get(outputFile);
            if (java.nio.file.Files.exists(outputPath)) {
                long fileSize = java.nio.file.Files.size(outputPath);
                System.out.println("Excel file size: " + String.format("%,d", fileSize) + " bytes");
            }

            // Display CSV file sizes as well
            if (csvOutput) {
                String baseName = outputFile.substring(0, outputFile.lastIndexOf('.'));
                displayCsvFileSize(baseName + "_test_details.csv");
                displayCsvFileSize(baseName + "_coverage.csv");
            }
        } catch (Exception e) {
            // Ignore file size retrieval errors
        }

        System.out.println("============================================================");
        if (csvOutput) {
            System.out.println("Test specification (Excel and CSV) has been successfully generated");
        } else {
            System.out.println("Test specification has been successfully generated: " + outputFile);
        }
    }

    private void displayCsvFileSize(String csvFilePath) {
        try {
            Path csvPath = Paths.get(csvFilePath);
            if (java.nio.file.Files.exists(csvPath)) {
                long fileSize = java.nio.file.Files.size(csvPath);
                System.out.println("CSV file size (" + csvPath.getFileName() + "): " + String.format("%,d", fileSize) + " bytes");
            }
        } catch (Exception e) {
            // Ignore CSV file size retrieval errors
        }
    }

    private String formatDuration(java.time.Duration duration) {
        long seconds = duration.getSeconds();
        long millis = duration.toMillis() % 1000;

        if (seconds > 0) {
            return String.format("%d.%03ds", seconds, millis);
        } else {
            return String.format("0.%03ds", millis);
        }
    }

    /**
     * Multi-module specification generation
     */
    public boolean generateMultiModuleSpecification(String projectRootPath, String outputDirPath, boolean csvOutput) {
        try {
            this.processingStartTime = LocalDateTime.now();

            logger.info("Java Test Specification Generator (Multi-Module) started");
            logger.info("   Version: {}", VERSION);
            logger.info("   Project root: {}", projectRootPath);
            logger.info("   Output directory: {}", outputDirPath);

            Path projectRoot = Paths.get(projectRootPath);
            Path outputDir = Paths.get(outputDirPath);

            // Check if it's really a multi-module project
            if (!MavenModuleAnalyzer.isMultiModuleProject(projectRoot)) {
                logger.error("The specified directory is not a Maven multi-module project: {}", projectRoot);
                logger.info("For single module, use --source-dir and --output options");
                return false;
            }

            // Analyze project structure
            logger.info("Step 1: Multi-module project analysis started...");
            MavenModuleAnalyzer analyzer = new MavenModuleAnalyzer();
            List<ModuleInfo> modules = analyzer.analyzeProject(projectRoot);

            if (modules.isEmpty()) {
                logger.error("No modules found");
                return false;
            }

            logger.info("Modules found: {} modules", modules.size());
            for (ModuleInfo module : modules) {
                String status = module.isValid() ? "OK" : "ERROR";
                logger.info("  [{}] {}", status, module.getModuleName());
                if (!module.isValid()) {
                    logger.warn("    Error: {}", module.getValidationError());
                }
            }

            // Process all modules
            logger.info("Step 2: Multi-module processing started...");
            MultiModuleProcessor processor = new MultiModuleProcessor();
            List<ModuleResult> results;

            try {
                results = processor.processAllModules(modules, outputDir, csvOutput);
            } finally {
                processor.shutdown();
            }

            // Summary
            long successful = results.stream().mapToLong(r -> r.isSuccessful() ? 1 : 0).sum();
            long failed = results.size() - successful;
            long totalTestCases = results.stream()
                .filter(ModuleResult::isSuccessful)
                .mapToLong(r -> r.hasTestCases() ? r.getTestCases().size() : 0)
                .sum();

            printMultiModuleSummary(modules.size(), (int) successful, (int) failed,
                                  (int) totalTestCases, outputDirPath, csvOutput, results);

            return successful > 0; // Success if at least one module was processed successfully

        } catch (Exception e) {
            logger.error("Error occurred during multi-module processing", e);
            return false;
        }
    }

    private void printMultiModuleSummary(int totalModules, int successfulModules, int failedModules,
                                       int totalTestCases, String outputDir, boolean csvOutput, List<ModuleResult> results) {
        LocalDateTime endTime = LocalDateTime.now();
        java.time.Duration duration = java.time.Duration.between(processingStartTime, endTime);

        System.out.println();
        System.out.println("============================================================");
        System.out.println("Multi-Module Processing Completed Summary");
        System.out.println("============================================================");
        System.out.println("Total modules: " + totalModules + " modules");
        System.out.println("Successful modules: " + successfulModules + " modules");
        if (failedModules > 0) {
            System.out.println("Failed modules: " + failedModules + " modules");
        }
        System.out.println("Total test cases: " + totalTestCases + " cases");
        System.out.println("Processing time: " + formatDuration(duration));
        System.out.println("Output directory: " + outputDir);

        System.out.println();
        System.out.println("Generated files:");
        System.out.println("  Combined report: combined-report.xlsx");
        if (csvOutput) {
            System.out.println("  Combined CSV: combined-report_test_details.csv, combined-report_coverage.csv");
        }

        for (ModuleResult result : results) {
            if (result.isSuccessful()) {
                String moduleName = result.getModuleInfo().getModuleName();
                System.out.println("  " + moduleName + "/report.xlsx");
                if (csvOutput && result.hasTestCases()) {
                    System.out.println("    " + moduleName + "/report_test_details.csv, report_coverage.csv");
                }
            }
        }

        System.out.println("  Processing summary: modules-summary.json");
        System.out.println("============================================================");

        if (failedModules > 0) {
            System.out.println("WARNING: Some modules failed to process, but other modules were processed successfully");
            System.out.println("See modules-summary.json for details");
        } else {
            System.out.println("All modules were processed successfully");
        }
        System.out.println();
    }

    private void setLogLevel(String logLevel) {
        // Log level configuration is managed by logback.xml
        // Only configuration confirmation is done here
        logger.debug("Log level setting: {}", logLevel);
    }
}