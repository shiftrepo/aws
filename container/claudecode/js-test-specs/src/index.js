#!/usr/bin/env node

import { Command } from 'commander';
import path from 'path';
import { FolderScanner } from './core/FolderScanner.js';
import { AnnotationParser } from './core/AnnotationParser.js';
import { CoverageReportParser } from './core/CoverageReportParser.js';
import { ExcelSheetBuilder } from './core/ExcelSheetBuilder.js';

const program = new Command();

program
  .name('js-test-spec-gen')
  .description('JavaScript/TypeScript テスト仕様書自動生成ツール')
  .version('1.0.0');

program
  .option('-s, --source-dir <path>', 'テストファイルのソースディレクトリ', './src/test')
  .option('-c, --coverage-dir <path>', 'カバレッジレポートディレクトリ', './coverage')
  .option('-o, --output <path>', '出力Excelファイルパス', 'test_specification.xlsx')
  .option('--no-coverage', 'カバレッジ処理をスキップ')
  .option('--log-level <level>', 'ログレベル (DEBUG, INFO, WARN, ERROR)', 'INFO')
  .option('-i, --interactive', 'インタラクティブモードで実行')
  .action(async (options) => {
    try {
      console.log('========================================');
      console.log('JavaScript Test Specification Generator');
      console.log('バージョン: 1.0.0');
      console.log('========================================\n');

      const startTime = Date.now();

      // ステップ1: ディレクトリスキャン
      console.log('【ステップ1】ディレクトリスキャン開始...');
      const scanner = new FolderScanner();

      const sourceDir = path.resolve(options.sourceDir);
      console.log(`ソースディレクトリ: ${sourceDir}`);

      const testFiles = await scanner.findTestFiles(sourceDir);
      console.log(`検出されたテストファイル数: ${testFiles.length}`);

      if (testFiles.length === 0) {
        console.error('エラー: テストファイルが見つかりませんでした');
        process.exit(1);
      }

      testFiles.slice(0, 5).forEach((file) => console.log(`  - ${file}`));
      if (testFiles.length > 5) {
        console.log(`  ... 他 ${testFiles.length - 5} ファイル`);
      }

      // ステップ2: アノテーション解析
      console.log('\n【ステップ2】アノテーション解析開始...');
      const parser = new AnnotationParser();
      const testCases = await parser.parseFiles(testFiles);
      console.log(`抽出されたテストケース数: ${testCases.length}`);

      if (testCases.length === 0) {
        console.warn('警告: テストケースが抽出されませんでした');
      }

      // ステップ3: カバレッジ解析
      let coverageSummary = {
        branchCoverage: 0,
        lineCoverage: 0,
        methodCoverage: 0,
        totalBranches: 0,
        coveredBranches: 0,
      };

      if (options.coverage) {
        console.log('\n【ステップ3】カバレッジ解析開始...');
        const coverageDir = path.resolve(options.coverageDir);
        console.log(`カバレッジディレクトリ: ${coverageDir}`);

        const coverageParser = new CoverageReportParser();
        await coverageParser.parseCoverageDirectory(coverageDir);
        coverageSummary = coverageParser.getCoverageSummary();

        console.log(`ブランチカバレッジ: ${coverageSummary.branchCoverage.toFixed(2)}%`);
        console.log(`行カバレッジ: ${coverageSummary.lineCoverage.toFixed(2)}%`);

        // テストケースにカバレッジ情報を統合
        for (const testCase of testCases) {
          const coverage = coverageParser.getCoverageForClass(testCase.className);
          if (coverage) {
            testCase.setCoverageInfo(coverage.branchCovered, coverage.branchTotal);
          }
        }
      } else {
        console.log('\n【ステップ3】カバレッジ処理をスキップ');
      }

      // ステップ4: Excel生成
      console.log('\n【ステップ4】Excel生成開始...');
      const outputPath = path.resolve(options.output);
      console.log(`出力ファイル: ${outputPath}`);

      const excelBuilder = new ExcelSheetBuilder();
      await excelBuilder.generateExcel(testCases, coverageSummary, outputPath);

      // 完了サマリー
      const endTime = Date.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);

      console.log('\n========================================');
      console.log('処理完了サマリー');
      console.log('========================================');
      console.log(`総テストファイル数: ${testFiles.length}`);
      console.log(`総テストケース数: ${testCases.length}`);
      console.log(`ブランチカバレッジ: ${coverageSummary.branchCoverage.toFixed(2)}%`);
      console.log(`処理時間: ${duration}秒`);
      console.log(`出力ファイル: ${outputPath}`);
      console.log('========================================\n');

      console.log('✓ テスト仕様書の生成が完了しました');
      process.exit(0);
    } catch (error) {
      console.error('\n✗ エラーが発生しました:', error.message);
      if (options.logLevel === 'DEBUG') {
        console.error(error.stack);
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
    console.log('JavaScript Test Specification Generator v1.0.0');
  });

// プログラム実行
if (process.argv.length < 3) {
  program.help();
} else {
  program.parse(process.argv);
}
