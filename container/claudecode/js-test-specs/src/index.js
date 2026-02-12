#!/usr/bin/env node

import { Command } from 'commander';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import { FolderScanner } from './core/FolderScanner.js';
import { AnnotationParser } from './core/AnnotationParser.js';
import { CoverageReportParser } from './core/CoverageReportParser.js';
import { TestExecutionParser } from './core/TestExecutionParser.js';
import { ExcelSheetBuilder } from './core/ExcelSheetBuilder.js';
import { CsvSheetBuilder } from './core/CsvSheetBuilder.js';
import { WorkspaceDetector } from './core/WorkspaceDetector.js';
import { MultiModuleProcessor } from './core/MultiModuleProcessor.js';
import { logger, setLogLevel } from './util/Logger.js';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

/**
 * Output detailed environment information for debugging
 */
function outputEnvironmentInfo() {
  logger.info('========================================');
  logger.info('環境情報');
  logger.info('========================================');

  // Node.js version
  logger.info('Node.js バージョン', { version: process.version });

  // OS information
  logger.info('OS情報', {
    platform: process.platform,
    type: os.type(),
    release: os.release(),
    arch: process.arch,
    hostname: os.hostname()
  });

  // User information
  try {
    const userInfo = os.userInfo();
    logger.info('実行ユーザー', {
      username: userInfo.username,
      uid: userInfo.uid,
      gid: userInfo.gid,
      homedir: userInfo.homedir
    });
  } catch (error) {
    logger.debug('ユーザー情報の取得に失敗', { error: error.message });
  }

  // Directory information
  logger.info('ディレクトリ情報', {
    cwd: process.cwd(),
    scriptDir: __dirname,
    execPath: process.execPath
  });

  // Memory information
  const memoryUsage = process.memoryUsage();
  logger.info('メモリ使用量', {
    rss: `${Math.round(memoryUsage.rss / 1024 / 1024)}MB`,
    heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)}MB`,
    heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)}MB`,
    external: `${Math.round(memoryUsage.external / 1024 / 1024)}MB`
  });

  // Total system memory
  logger.info('システムメモリ', {
    total: `${Math.round(os.totalmem() / 1024 / 1024 / 1024)}GB`,
    free: `${Math.round(os.freemem() / 1024 / 1024 / 1024)}GB`
  });

  // CPU information
  const cpus = os.cpus();
  logger.info('CPU情報', {
    cores: cpus.length,
    model: cpus[0]?.model || 'Unknown'
  });

  // Environment variables (important ones)
  logger.debug('重要な環境変数', {
    NODE_ENV: process.env.NODE_ENV || 'not set',
    NODE_OPTIONS: process.env.NODE_OPTIONS || 'not set',
    PATH: process.env.PATH ? 'set' : 'not set',
    SHELL: process.env.SHELL || 'not set',
    TERM: process.env.TERM || 'not set'
  });

  // Package version
  try {
    const packageJsonPath = path.join(__dirname, '..', 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    logger.info('ツールバージョン', {
      name: packageJson.name,
      version: packageJson.version,
      description: packageJson.description
    });

    // Key dependencies
    logger.debug('主要な依存パッケージ', {
      commander: packageJson.dependencies?.commander,
      exceljs: packageJson.dependencies?.exceljs,
      'fast-glob': packageJson.dependencies?.['fast-glob'],
      winston: packageJson.dependencies?.winston
    });
  } catch (error) {
    logger.debug('package.jsonの読み込みに失敗', { error: error.message });
  }

  logger.info('========================================');
}

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

      // Output environment information first
      outputEnvironmentInfo();

      logger.info('========================================');
      logger.info('JavaScript Test Specification Generator');
      logger.info('実行開始');
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
      const scanStartTime = Date.now();
      const scanner = new FolderScanner();

      const sourceDir = path.resolve(options.sourceDir);
      logger.info('ソースディレクトリ', { sourceDir });
      logger.debug('ディレクトリ存在確認', { exists: await scanner.directoryExists(sourceDir) });

      const testFiles = await scanner.findTestFiles(sourceDir);
      const scanDuration = Date.now() - scanStartTime;
      logger.info('検出されたテストファイル数', { count: testFiles.length, duration: `${scanDuration}ms` });

      if (testFiles.length === 0) {
        logger.error('エラー: テストファイルが見つかりませんでした');
        logger.debug('検索パターン', { patterns: ['**/*.test.js', '**/*.spec.js', '**/*.test.ts', '**/*.spec.ts'] });
        process.exit(1);
      }

      // Output first 10 test files in DEBUG mode
      testFiles.slice(0, 10).forEach((file, index) => {
        logger.debug(`テストファイル[${index + 1}]`, { file, basename: path.basename(file) });
      });
      if (testFiles.length > 10) {
        logger.debug('その他のテストファイル', { remaining: testFiles.length - 10 });
      }

      // ステップ2: アノテーション解析
      logger.info('【ステップ2】アノテーション解析開始');
      const parseStartTime = Date.now();
      const parser = new AnnotationParser();
      logger.debug('アノテーション解析設定', {
        japaneseAnnotations: Object.keys(parser.japaneseAnnotations).length,
        englishAnnotations: Object.keys(parser.englishAnnotations).length
      });

      const testCases = await parser.parseFiles(testFiles);
      const parseDuration = Date.now() - parseStartTime;
      logger.info('抽出されたテストケース数', { count: testCases.length, duration: `${parseDuration}ms` });

      if (testCases.length === 0) {
        logger.warn('警告: テストケースが抽出されませんでした');
        logger.debug('アノテーション解析結果', {
          filesProcessed: testFiles.length,
          testCasesFound: 0,
          hint: 'JSDocコメントが test() または it() の直前に配置されているか確認してください'
        });
      } else {
        // Show sample test cases in DEBUG mode
        testCases.slice(0, 3).forEach((tc, index) => {
          logger.debug(`テストケース[${index + 1}]`, {
            className: tc.className,
            methodName: tc.methodName,
            testItemName: tc.testItemName,
            softwareService: tc.softwareService
          });
        });
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
        const coverageStartTime = Date.now();
        const coverageDir = path.resolve(options.coverageDir);
        logger.info('カバレッジディレクトリ', { coverageDir });
        logger.debug('カバレッジディレクトリ存在確認', { exists: await scanner.directoryExists(coverageDir) });

        coverageParser = new CoverageReportParser();
        await coverageParser.parseCoverageDirectory(coverageDir);
        coverageSummary = coverageParser.getCoverageSummary();

        const coverageDuration = Date.now() - coverageStartTime;
        logger.info('カバレッジ解析完了', { duration: `${coverageDuration}ms` });
        logger.info('ブランチカバレッジ', {
          percent: coverageSummary.branchCoverage.toFixed(2),
          covered: coverageSummary.coveredBranches,
          total: coverageSummary.totalBranches
        });
        logger.info('行カバレッジ', {
          percent: coverageSummary.lineCoverage.toFixed(2)
        });
        logger.debug('メソッドカバレッジ', {
          percent: coverageSummary.methodCoverage.toFixed(2)
        });

        // Get coverage report creation date from coverage-final.json
        try {
          const coverageFinalPath = path.join(coverageDir, 'coverage-final.json');
          const fs = await import('fs/promises');
          const stats = await fs.stat(coverageFinalPath);
          coverageReportDate = stats.mtime.toISOString().split('T')[0]; // YYYY-MM-DD
          logger.info('カバレッジレポート作成日', { date: coverageReportDate, fullTime: stats.mtime.toISOString() });
          logger.debug('カバレッジファイル情報', {
            path: coverageFinalPath,
            size: `${Math.round(stats.size / 1024)}KB`,
            modified: stats.mtime.toISOString()
          });
        } catch (error) {
          logger.warn('カバレッジレポート作成日の取得に失敗', { error: error.message });
          coverageReportDate = new Date().toISOString().split('T')[0];
        }

        // テストケースにカバレッジ情報を統合
        let coverageIntegrationCount = 0;
        for (const testCase of testCases) {
          const coverage = coverageParser.getCoverageForClass(testCase.className);
          if (coverage) {
            testCase.setCoverageInfo(coverage.branchCovered, coverage.branchTotal);
            testCase.coverage = coverage; // Store full coverage info for CSV/Excel
            coverageIntegrationCount++;
          }
        }
        logger.debug('カバレッジ統合結果', {
          totalTestCases: testCases.length,
          withCoverage: coverageIntegrationCount,
          withoutCoverage: testCases.length - coverageIntegrationCount
        });
      } else {
        logger.info('【ステップ3】カバレッジ処理をスキップ');
      }

      // ステップ3.5: テスト実行結果の解析
      let executionParser = null;
      let executionSummary = null;

      try {
        const executionStartTime = Date.now();
        const testResultsPath = path.resolve(options.testResults);
        const fs = await import('fs/promises');
        await fs.access(testResultsPath);

        logger.info('【ステップ3.5】テスト実行結果解析開始');
        logger.info('テスト実行結果ファイル', { testResultsPath });

        const stats = await fs.stat(testResultsPath);
        logger.debug('テスト結果ファイル情報', {
          size: `${Math.round(stats.size / 1024)}KB`,
          modified: stats.mtime.toISOString()
        });

        executionParser = new TestExecutionParser();
        await executionParser.parseTestResults(testResultsPath);
        executionSummary = executionParser.getExecutionSummary();

        const executionDuration = Date.now() - executionStartTime;
        logger.info('テスト実行結果解析完了', { duration: `${executionDuration}ms` });
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
        logger.debug('テスト実行日', { date: testExecutionDate });

        let executionIntegrationCount = 0;
        for (const testCase of testCases) {
          // Set test execution date (from coverage report creation date)
          testCase.setTestExecutionDate(testExecutionDate);

          const executionInfo = executionParser.getExecutionInfo(
            testCase.className,
            testCase.methodName
          );
          if (executionInfo) {
            testCase.setDetailedExecutionInfo(executionInfo);
            executionIntegrationCount++;
          }
        }

        logger.info('テスト実行結果の統合完了');
        logger.debug('テスト実行統合結果', {
          totalTestCases: testCases.length,
          withExecutionInfo: executionIntegrationCount,
          withoutExecutionInfo: testCases.length - executionIntegrationCount
        });
      } catch (error) {
        logger.warn('テスト実行結果ファイルが見つかりません。スキップします。', {
          path: options.testResults,
          error: error.code || error.message,
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
      const excelStartTime = Date.now();
      const outputPath = path.resolve(options.output);
      logger.info('出力ファイル', { outputPath });
      logger.debug('出力ディレクトリ', { dir: path.dirname(outputPath) });

      const excelBuilder = new ExcelSheetBuilder();
      // Pass coverageParser to enable method-level coverage in Excel
      await excelBuilder.generateExcel(testCases, coverageSummary, outputPath, coverageParser);

      const excelDuration = Date.now() - excelStartTime;
      logger.info('Excel生成完了', { duration: `${excelDuration}ms` });

      // Check output file
      const fs2 = await import('fs/promises');
      try {
        const outputStats = await fs2.stat(outputPath);
        logger.debug('生成されたExcelファイル', {
          path: outputPath,
          size: `${Math.round(outputStats.size / 1024)}KB`,
          created: outputStats.birthtime.toISOString()
        });
      } catch (error) {
        logger.error('Excelファイルの確認に失敗', { error: error.message });
      }

      // ステップ5: CSV生成（オプション）
      let csvPaths = null;
      if (options.csvOutput) {
        logger.info('【ステップ5】CSV生成開始');
        const csvStartTime = Date.now();
        const csvBuilder = new CsvSheetBuilder();
        csvPaths = await csvBuilder.generateAllCsvFiles(testCases, coverageSummary, outputPath);
        const csvDuration = Date.now() - csvStartTime;
        logger.info('CSV生成完了', { ...csvPaths, duration: `${csvDuration}ms` });

        // Check CSV files
        try {
          const detailsStats = await fs2.stat(csvPaths.testDetails);
          const coverageStats = await fs2.stat(csvPaths.coverage);
          logger.debug('生成されたCSVファイル', {
            testDetails: {
              path: csvPaths.testDetails,
              size: `${Math.round(detailsStats.size / 1024)}KB`
            },
            coverage: {
              path: csvPaths.coverage,
              size: `${Math.round(coverageStats.size / 1024)}KB`
            }
          });
        } catch (error) {
          logger.debug('CSVファイルの確認中にエラー', { error: error.message });
        }
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
      logger.error('✗ エラーが発生しました', {
        message: error.message,
        name: error.name,
        code: error.code
      });
      logger.debug('エラースタックトレース', { stack: error.stack });

      // Output error context in DEBUG mode
      if (error.fileName) {
        logger.debug('エラー発生ファイル', { fileName: error.fileName });
      }
      if (error.lineNumber) {
        logger.debug('エラー発生行', { lineNumber: error.lineNumber });
      }

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
