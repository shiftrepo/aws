/**
 * @jest-environment node
 *
 * FolderScanner.test.js
 *
 * Unit tests for FolderScanner
 */

import { FolderScanner } from '../../core/FolderScanner.js';

describe('FolderScanner', () => {
  let scanner;

  beforeEach(() => {
    scanner = new FolderScanner();
  });

  test('should initialize with default excluded directories', () => {
    expect(scanner.excludedDirs).toContain('**/node_modules/**');
    expect(scanner.excludedDirs).toContain('**/.git/**');
    expect(scanner.excludedDirs).toContain('**/coverage/**');
    expect(scanner.excludedDirs).toContain('**/dist/**');
    expect(scanner.excludedDirs).toContain('**/build/**');
  });

  test('should have default max file size', () => {
    expect(scanner.maxFileSize).toBe(10 * 1024 * 1024); // 10MB
  });

  test('should find test files in current directory', async () => {
    const testDir = './src/test';

    const files = await scanner.findTestFiles(testDir);

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
    // Should find at least the example test file
    expect(files.length).toBeGreaterThan(0);

    // Check that found files are test files
    files.forEach(file => {
      const isTestFile = /\.(test|spec)\.(js|jsx|ts|tsx)$/.test(file);
      expect(isTestFile).toBe(true);
    });
  });

  test('should return sorted files', async () => {
    const testDir = './src/test';

    const files = await scanner.findTestFiles(testDir);

    // Check if files are sorted
    const sorted = [...files].sort();
    expect(files).toEqual(sorted);
  });

  test('should check if directory exists for valid directory', async () => {
    const exists = await scanner.directoryExists('./src');

    expect(exists).toBe(true);
  });

  test('should return false if directory does not exist', async () => {
    const exists = await scanner.directoryExists('/nonexistent/path/to/dir');

    expect(exists).toBe(false);
  });

  test('should check if file exists for valid file', async () => {
    const exists = await scanner.fileExists('./package.json');

    expect(exists).toBe(true);
  });

  test('should return false if file does not exist', async () => {
    const exists = await scanner.fileExists('/nonexistent/file.js');

    expect(exists).toBe(false);
  });

  test('should handle directory as file check', async () => {
    const exists = await scanner.fileExists('./src');

    // Directory should not be considered a file
    expect(exists).toBe(false);
  });

  test('should find coverage reports', async () => {
    const coverageDir = './coverage';

    const files = await scanner.findCoverageReports(coverageDir);

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
    // Should find coverage files if coverage exists
    if (files.length > 0) {
      files.forEach(file => {
        expect(file).toMatch(/(coverage-final\.json|lcov\.info|clover\.xml|index\.html)/);
      });
    }
  });

  test('should return empty array for non-existent coverage directory', async () => {
    const files = await scanner.findCoverageReports('/nonexistent/coverage');

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
  });

  test('should find all JavaScript files', async () => {
    const srcDir = './src/main/example';

    const files = await scanner.findAllJavaScriptFiles(srcDir);

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
    expect(files.length).toBeGreaterThan(0);

    // Check that found files are JavaScript files
    files.forEach(file => {
      const isJsFile = /\.(js|jsx)$/.test(file);
      expect(isJsFile).toBe(true);
      // Should not include test files
      const isTestFile = /\.(test|spec)\.(js|jsx)$/.test(file);
      expect(isTestFile).toBe(false);
    });
  });

  test('should return sorted JavaScript files', async () => {
    const srcDir = './src/main/example';

    const files = await scanner.findAllJavaScriptFiles(srcDir);

    // Check if files are sorted
    const sorted = [...files].sort();
    expect(files).toEqual(sorted);
  });

  test('should exclude test files from JavaScript search', async () => {
    const testDir = './src/test';

    const files = await scanner.findAllJavaScriptFiles(testDir);

    // Should not find any test files
    files.forEach(file => {
      const isTestFile = /\.(test|spec)\.(js|jsx)$/.test(file);
      expect(isTestFile).toBe(false);
    });
  });

  test('should handle errors in findTestFiles gracefully', async () => {
    const invalidDir = './nonexistent_directory_12345';

    const files = await scanner.findTestFiles(invalidDir);

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
    expect(files.length).toBe(0);
  });

  test('should handle errors in findCoverageReports gracefully', async () => {
    const invalidDir = './nonexistent_directory_12345';

    const files = await scanner.findCoverageReports(invalidDir);

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
    expect(files.length).toBe(0);
  });

  test('should handle errors in findAllJavaScriptFiles gracefully', async () => {
    const invalidDir = './nonexistent_directory_12345';

    const files = await scanner.findAllJavaScriptFiles(invalidDir);

    expect(files).toBeDefined();
    expect(Array.isArray(files)).toBe(true);
    expect(files.length).toBe(0);
  });
});
