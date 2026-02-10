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

      const files = await fg(patterns, {
        cwd: dirPath,
        absolute: true,
        ignore: this.excludedDirs,
      });

      // ファイルサイズチェック
      const validFiles = [];
      for (const file of files) {
        try {
          const stats = await fs.stat(file);
          if (stats.size <= this.maxFileSize) {
            validFiles.push(file);
          } else {
            logger.warn('ファイルサイズが大きすぎるためスキップ', { file, size: stats.size });
          }
        } catch (error) {
          logger.warn('ファイル読み取りエラー', { file, error: error.message });
        }
      }

      return validFiles.sort();
    } catch (error) {
      logger.error('テストファイル検索エラー', error);
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
