import fg from 'fast-glob';
import path from 'path';
import fs from 'fs/promises';
import { logger } from '../util/Logger.js';

/**
 * ディレクトリをスキャンしてファイルを検索するクラス
 */
export class FolderScanner {
  constructor() {
    this.excludedDirs = [
      '**/node_modules/**',
      '**/.git/**',
      '**/dist/**',
      '**/build/**',
      '**/coverage/**',
      '**/.idea/**',
      '**/.vscode/**',
      '**/target/**',
    ];
    this.maxFileSize = 10 * 1024 * 1024; // 10MB
  }

  /**
   * 指定ディレクトリ内のJavaScript/TypeScriptテストファイルを検索
   * @param {string} dirPath - 検索開始ディレクトリ
   * @returns {Promise<string[]>} テストファイルのパス配列
   */
  async findTestFiles(dirPath) {
    try {
      logger.debug('テストファイル検索開始', { dirPath });

      const patterns = [
        '**/*.test.js',
        '**/*.test.jsx',
        '**/*.spec.js',
        '**/*.spec.jsx',
        '**/*.test.ts',
        '**/*.test.tsx',
        '**/*.spec.ts',
        '**/*.spec.tsx',
      ];

      logger.debug('検索パターン', { patterns: patterns.join(', ') });
      logger.debug('除外ディレクトリ', { excluded: this.excludedDirs });

      const files = await fg(patterns, {
        cwd: dirPath,
        absolute: true,
        ignore: this.excludedDirs,
      });

      logger.debug('検出されたファイル数（サイズチェック前）', { count: files.length });

      // ファイルサイズチェック
      const validFiles = [];
      let skippedCount = 0;
      for (const file of files) {
        try {
          const stats = await fs.stat(file);
          if (stats.size <= this.maxFileSize) {
            validFiles.push(file);
          } else {
            skippedCount++;
            logger.warn('ファイルサイズが大きすぎるためスキップ', {
              file,
              size: `${Math.round(stats.size / 1024 / 1024)}MB`,
              maxSize: `${this.maxFileSize / 1024 / 1024}MB`
            });
          }
        } catch (error) {
          skippedCount++;
          logger.warn('ファイル読み取りエラー', { file, error: error.message });
        }
      }

      logger.debug('ファイルサイズチェック完了', {
        valid: validFiles.length,
        skipped: skippedCount
      });

      return validFiles.sort();
    } catch (error) {
      logger.error('テストファイル検索エラー', {
        message: error.message,
        dirPath
      });
      logger.debug('エラースタック', { stack: error.stack });
      return [];
    }
  }

  /**
   * カバレッジレポートファイルを検索
   * @param {string} dirPath - 検索開始ディレクトリ
   * @returns {Promise<string[]>} カバレッジファイルのパス配列
   */
  async findCoverageReports(dirPath) {
    try {
      const patterns = [
        '**/coverage/**/lcov-report/index.html',
        '**/coverage/**/coverage-final.json',
        '**/coverage/**/lcov.info',
        '**/coverage/clover.xml',
        '**/coverage-final.json',
      ];

      const files = await fg(patterns, {
        cwd: dirPath,
        absolute: true,
        ignore: this.excludedDirs,
      });

      return files.sort();
    } catch (error) {
      logger.error('カバレッジファイル検索エラー', error);
      return [];
    }
  }

  /**
   * 指定ディレクトリ内の全JavaScriptファイルを検索
   * @param {string} dirPath - 検索開始ディレクトリ
   * @returns {Promise<string[]>} JavaScriptファイルのパス配列
   */
  async findAllJavaScriptFiles(dirPath) {
    try {
      const patterns = ['**/*.js', '**/*.jsx'];

      const files = await fg(patterns, {
        cwd: dirPath,
        absolute: true,
        ignore: [...this.excludedDirs, '**/*.test.js', '**/*.spec.js'],
      });

      // ファイルサイズチェック
      const validFiles = [];
      for (const file of files) {
        try {
          const stats = await fs.stat(file);
          if (stats.size <= this.maxFileSize) {
            validFiles.push(file);
          }
        } catch (error) {
          logger.warn('ファイル読み取りエラー', { file, error: error.message });
        }
      }

      return validFiles.sort();
    } catch (error) {
      logger.error('JavaScriptファイル検索エラー', error);
      return [];
    }
  }

  /**
   * ディレクトリが存在するかチェック
   * @param {string} dirPath - チェックするディレクトリパス
   * @returns {Promise<boolean>} 存在すればtrue
   */
  async directoryExists(dirPath) {
    try {
      const stats = await fs.stat(dirPath);
      return stats.isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * ファイルが存在するかチェック
   * @param {string} filePath - チェックするファイルパス
   * @returns {Promise<boolean>} 存在すればtrue
   */
  async fileExists(filePath) {
    try {
      const stats = await fs.stat(filePath);
      return stats.isFile();
    } catch {
      return false;
    }
  }
}
