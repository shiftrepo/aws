#!/usr/bin/env node

import { Command } from 'commander';
import path from 'path';
import { FolderScanner } from './core/FolderScanner.js';
import { AnnotationParser } from './core/AnnotationParser.js';
import { CoverageReportParser } from './core/CoverageReportParser.js';
import { TestExecutionParser } from './core/TestExecutionParser.js';
import { ExcelSheetBuilder } from './core/ExcelSheetBuilder.js';
import { CsvSheetBuilder } from './core/CsvSheetBuilder.js';
import { WorkspaceDetector } from './core/WorkspaceDetector.js';
import { MultiModuleProcessor } from './core/MultiModuleProcessor.js';
import { logger, setLogLevel } from './util/Logger.js';

const program = new Command();

/**
 * Process multi-module/monorepo project
 * @param {Object} options - CLI options
 */
async function processMultiModule(options) {
  try {
    const startTime = Date.now();

    // Step 1: Detect workspace
    logger.info('【ステップ1】ワークスペース検出');
    const detector = new WorkspaceDetector();
    const projectRoot = path.resolve(options.projectRoot || process.cwd());
    const isWorkspace = await detector.detectWorkspace(projectRoot);

    if (!isWorkspace) {
      logger.warn('ワークスペースが検出されませんでした。シングルモジュールとして処理します。');
      return;
    }

    const modules = detector.getModules();
    const workspaceSummary = detector.getWorkspaceSummary();

    logger.info('ワークスペース情報', workspaceSummary);

    if (modules.length === 0) {
      logger.error('有効なモジュールが見つかりませんでした');
      process.exit(1);
    }

    // Step 2: Process modules in parallel
    logger.info('【ステップ2】モジュール並列処理開始');
    const processor = new MultiModuleProcessor({
      maxConcurrency: 4,
      timeout: 300000
    });

    const results = await processor.processModules(modules, {
      parseCoverage: options.coverage,
      parseExecution: true
    });

    // Step 3: Generate reports
    logger.info('【ステップ3】レポート生成');
    const outputDir = path.resolve(options.outputDir || './reports');

    // Ensure output directory exists
    const fs = await import('fs/promises');
    await fs.mkdir(outputDir, { recursive: true });

    // Generate combined report
    const combinedReport = await processor.generateCombinedReport(outputDir, {
      csvOutput: options.csvOutput
    });

    // Generate per-module reports
    const moduleReports = await processor.generateModuleReports(outputDir, {
      csvOutput: options.csvOutput
    });

    // Summary
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);
    const summary = processor.getProcessingSummary();

    logger.info('========================================');
    logger.info('マルチモジュール処理完了サマリー');
    logger.info('========================================');
    logger.info('総モジュール数', { count: summary.totalModules });
    logger.info('成功', { count: summary.successfulModules });
    logger.info('失敗', { count: summary.failedModules });
    logger.info('総テストケース数', { count: summary.totalTestCases });
    logger.info('総合ブランチカバレッジ', {
      percent: summary.combinedCoverage.branchCoverage.toFixed(2) + '%'
    });
    logger.info('総合テスト成功率', { percent: summary.combinedExecution.passRate + '%' });
    logger.info('処理時間', { duration: `${duration}秒` });
    logger.info('出力ディレクトリ', { outputDir });
    logger.info('========================================');
    logger.info('✓ マルチモジュール処理が完了しました');

    process.exit(0);
  } catch (error) {
    logger.error('✗ マルチモジュール処理エラー', error);
    process.exit(1);
  }
}

program
  .name('js-test-spec-gen')
  .description('JavaScript/TypeScript テスト仕様書自動生成ツール')
  .version('1.0.0');

program
  .option('-s, --source-dir <path>', 'テストファイルのソースディレクトリ', './src/test')
  .option('-c, --coverage-dir <path>', 'カバレッジレポートディレクトリ', './coverage')
  .option('-o, --output <path>', '出力Excelファイルパス', 'test_specification.xlsx')
  .option('--no-coverage', 'カバレッジ処理をスキップ')
  .option('--test-results <path>', 'Jestテスト実行結果JSONファイル', 'test-results.json')
  .option('--csv-output', 'CSV形式でも出力')
  .option('--project-root <path>', 'プロジェクトルートディレクトリ（マルチモジュール用）')
  .option('--output-dir <path>', 'モジュールごとのレポート出力ディレクトリ', './reports')
  .option('--single-module', 'シングルモジュールとして処理（ワークスペース検出をスキップ）')
  .option('--log-level <level>', 'ログレベル (DEBUG, INFO, WARN, ERROR)', 'INFO')
  .option('-i, --interactive', 'インタラクティブモードで実行')
  .action(async (options) => {
    try {
      // Set log level from options
      setLogLevel(options.logLevel);

      logger.info('========================================');
      logger.info('JavaScript Test Specification Generator');
      logger.info('バージョン: 1.0.0');
      logger.info('========================================');

      const startTime = Date.now();

      // Check for multi-module mode
      if (options.projectRoot && !options.singleModule) {
        logger.info('マルチモジュールモードで実行');
        await processMultiModule(options);
        return;
      }

      // Auto-detect workspace if running in potential monorepo
      if (!options.singleModule && !options.projectRoot) {
        const detector = new WorkspaceDetector();
        const currentDir = process.cwd();
        const isWorkspace = await detector.detectWorkspace(currentDir);

        if (isWorkspace && detector.getModules().length > 1) {
          logger.info('ワークスペースを検出しました。マルチモジュールモードで実行します。');
          logger.info('シングルモジュールモードで実行する場合は --single-module オプションを使用してください。');
          options.projectRoot = currentDir;
          await processMultiModule(options);
          return;
        }
      }

      logger.info('シングルモジュールモードで実行');

      // ステップ1: ディレクトリスキャン
      logger.info('【ステップ1】ディレクトリスキャン開始');
      const scanner = new FolderScanner();

      const sourceDir = path.resolve(options.sourceDir);
      logger.info('ソースディレクトリ', { sourceDir });

      const testFiles = await scanner.findTestFiles(sourceDir);
      logger.info('検出されたテストファイル数', { count: testFiles.length });

      if (testFiles.length === 0) {
        logger.error('エラー: テストファイルが見つかりませんでした');
        process.exit(1);
      }

      testFiles.slice(0, 5).forEach((file) => logger.debug('テストファイル', { file }));
      if (testFiles.length > 5) {
        logger.debug('その他のテストファイル', { remaining: testFiles.length - 5 });
      }

      // ステップ2: アノテーション解析
      logger.info('【ステップ2】アノテーション解析開始');
      const parser = new AnnotationParser();
      const testCases = await parser.parseFiles(testFiles);
      logger.info('抽出されたテストケース数', { count: testCases.length });

      if (testCases.length === 0) {
        logger.warn('警告: テストケースが抽出されませんでした');
      }

      // ステップ3: カバレッジ解析
      let coverageSummary = {
        branchCoverage: 0,
        lineCoverage: 0,
        methodCoverage: 0,
        totalBranches: 0,
        coveredBranches: 0,
      };

      let coverageParser = null;
      let coverageReportDate = null;

      if (options.coverage) {
        logger.info('【ステップ3】カバレッジ解析開始');
        const coverageDir = path.resolve(options.coverageDir);
        logger.info('カバレッジディレクトリ', { coverageDir });

        coverageParser = new CoverageReportParser();
        await coverageParser.parseCoverageDirectory(coverageDir);
        coverageSummary = coverageParser.getCoverageSummary();

        logger.info('ブランチカバレッジ', { percent: coverageSummary.branchCoverage.toFixed(2) });
        logger.info('行カバレッジ', { percent: coverageSummary.lineCoverage.toFixed(2) });

        // Get coverage report creation date from coverage-final.json
        try {
          const coverageFinalPath = path.join(coverageDir, 'coverage-final.json');
          const fs = await import('fs/promises');
          const stats = await fs.stat(coverageFinalPath);
          coverageReportDate = stats.mtime.toISOString().split('T')[0]; // YYYY-MM-DD
          logger.info('カバレッジレポート作成日', { date: coverageReportDate });
        } catch (error) {
          logger.warn('カバレッジレポート作成日の取得に失敗', { error: error.message });
          coverageReportDate = new Date().toISOString().split('T')[0];
        }

        // テストケースにカバレッジ情報を統合
        for (const testCase of testCases) {
          const coverage = coverageParser.getCoverageForClass(testCase.className);
          if (coverage) {
            testCase.setCoverageInfo(coverage.branchCovered, coverage.branchTotal);
            testCase.coverage = coverage; // Store full coverage info for CSV/Excel
          }
        }
      } else {
        logger.info('【ステップ3】カバレッジ処理をスキップ');
      }

      // ステップ3.5: テスト実行結果の解析
      let executionParser = null;
      let executionSummary = null;

      try {
        const testResultsPath = path.resolve(options.testResults);
        const fs = await import('fs/promises');
        await fs.access(testResultsPath);

        logger.info('【ステップ3.5】テスト実行結果解析開始');
        logger.info('テスト実行結果ファイル', { testResultsPath });

        executionParser = new TestExecutionParser();
        await executionParser.parseTestResults(testResultsPath);
        executionSummary = executionParser.getExecutionSummary();

        logger.info('テスト実行結果サマリー', {
          totalTests: executionSummary.totalTests,
          passed: executionSummary.passed,
          failed: executionSummary.failed,
          skipped: executionSummary.skipped,
          passRate: executionSummary.passRate + '%'
        });

        // Integrate execution info with test cases
        // Use coverage report date as test execution date
        const testExecutionDate = coverageReportDate || new Date().toISOString().split('T')[0];
        for (const testCase of testCases) {
          // Set test execution date (from coverage report creation date)
          testCase.setTestExecutionDate(testExecutionDate);

          const executionInfo = executionParser.getExecutionInfo(
            testCase.className,
            testCase.methodName
          );
          if (executionInfo) {
            testCase.setDetailedExecutionInfo(executionInfo);
          }
        }

        logger.info('テスト実行結果の統合完了');
      } catch (error) {
        logger.warn('テスト実行結果ファイルが見つかりません。スキップします。', {
          path: options.testResults,
          hint: 'npm run test:coverage を実行してテスト結果を生成してください'
        });

        // Set test execution date even if execution info is not available
        // Use coverage report date as test execution date
        const testExecutionDate = coverageReportDate || new Date().toISOString().split('T')[0];
        for (const testCase of testCases) {
          testCase.setTestExecutionDate(testExecutionDate);
        }
      }

      // ステップ4: Excel生成
      logger.info('【ステップ4】Excel生成開始');
      const outputPath = path.resolve(options.output);
      logger.info('出力ファイル', { outputPath });

      const excelBuilder = new ExcelSheetBuilder();
      // Pass coverageParser to enable method-level coverage in Excel
      await excelBuilder.generateExcel(testCases, coverageSummary, outputPath, coverageParser);

      // ステップ5: CSV生成（オプション）
      let csvPaths = null;
      if (options.csvOutput) {
        logger.info('【ステップ5】CSV生成開始');
        const csvBuilder = new CsvSheetBuilder();
        csvPaths = await csvBuilder.generateAllCsvFiles(testCases, coverageSummary, outputPath);
        logger.info('CSV生成完了', csvPaths);
      }

      // 完了サマリー
      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);

      logger.info('========================================');
      logger.info('処理完了サマリー');
      logger.info('========================================');
      logger.info('総テストファイル数', { count: testFiles.length });
      logger.info('総テストケース数', { count: testCases.length });
      logger.info('ブランチカバレッジ', { percent: coverageSummary.branchCoverage.toFixed(2) });
      logger.info('処理時間', { duration: `${duration}秒` });
      logger.info('出力ファイル', { outputPath });
      if (csvPaths) {
        logger.info('CSV出力ファイル', csvPaths);
      }
      logger.info('========================================');

      logger.info('✓ テスト仕様書の生成が完了しました');
      process.exit(0);
    } catch (error) {
      logger.error('✗ エラーが発生しました', error);
      process.exit(1);
    }
  });

// ヘルプコマンド
program
  .command('help')
  .description('ヘルプ情報を表示')
  .action(() => {
    program.help();
  });

// バージョンコマンド
program
  .command('version')
  .description('バージョン情報を表示')
  .action(() => {
    logger.info('JavaScript Test Specification Generator v1.0.0');
  });

// プログラム実行
if (process.argv.length < 3) {
  program.help();
} else {
  program.parse(process.argv);
}
