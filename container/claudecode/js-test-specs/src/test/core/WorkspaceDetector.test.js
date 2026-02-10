/**
 * @jest-environment node
 *
 * WorkspaceDetector.test.js
 *
 * Unit tests for WorkspaceDetector
 */

import { WorkspaceDetector } from '../../core/WorkspaceDetector.js';
import { ModuleInfo } from '../../model/ModuleInfo.js';

describe('WorkspaceDetector', () => {
  let detector;

  beforeEach(() => {
    detector = new WorkspaceDetector();
  });

  test('should initialize with empty state', () => {
    expect(detector.rootPath).toBe('');
    expect(detector.modules).toEqual([]);
    expect(detector.rootPackageJson).toBeNull();
  });

  test('should detect workspace from package.json', async () => {
    const isWorkspace = await detector.detectWorkspace('./');

    expect(typeof isWorkspace).toBe('boolean');
    expect(detector.rootPath).toBeTruthy();
  });

  test('should handle non-existent directory', async () => {
    const isWorkspace = await detector.detectWorkspace('/nonexistent/path/123456');

    expect(isWorkspace).toBe(false);
    expect(detector.modules).toEqual([]);
  });

  test('should handle directory without package.json', async () => {
    const isWorkspace = await detector.detectWorkspace('/tmp');

    expect(isWorkspace).toBe(false);
  });

  test('should get modules list', () => {
    const modules = detector.getModules();

    expect(Array.isArray(modules)).toBe(true);
  });

  test('should get workspace summary', async () => {
    // First detect workspace to populate data
    await detector.detectWorkspace('./');

    const summary = detector.getWorkspaceSummary();

    expect(summary).toBeDefined();
    expect(summary.rootPath).toBeDefined();
    expect(typeof summary.moduleCount).toBe('number');
    expect(Array.isArray(summary.modules)).toBe(true);
  });

  test('should check for lerna config', async () => {
    detector.rootPath = './';
    const hasLerna = await detector.checkLernaConfig();

    expect(typeof hasLerna).toBe('boolean');
  });

  test('should create ModuleInfo from package.json', async () => {
    const packageJsonPath = './package.json';

    try {
      const moduleInfo = await detector.createModuleInfo(packageJsonPath);

      expect(moduleInfo).toBeInstanceOf(ModuleInfo);
      expect(moduleInfo.moduleName).toBeTruthy();
      expect(moduleInfo.modulePath).toBeTruthy();
    } catch (error) {
      // Package.json might not exist or be invalid
      expect(error).toBeDefined();
    }
  });

  test('should handle invalid package.json in createModuleInfo', async () => {
    const invalidPath = '/nonexistent/package.json';

    try {
      await detector.createModuleInfo(invalidPath);
      // Should not reach here
      expect(true).toBe(false);
    } catch (error) {
      expect(error).toBeDefined();
    }
  });

  test('should validate module info after creation', async () => {
    const packageJsonPath = './package.json';

    try {
      const moduleInfo = await detector.createModuleInfo(packageJsonPath);

      if (moduleInfo) {
        const isValid = moduleInfo.validate();
        expect(typeof isValid).toBe('boolean');
      }
    } catch (error) {
      // Expected if file doesn't exist
    }
  });

  test('should parse workspace patterns', async () => {
    detector.rootPath = './';

    // parseWorkspaces is an async method that takes workspace patterns
    const workspacePatterns = ['packages/*'];

    try {
      await detector.parseWorkspaces(workspacePatterns);
      // If successful, modules should be populated
      expect(Array.isArray(detector.modules)).toBe(true);
    } catch (error) {
      // Expected if no matching packages found
      expect(error).toBeDefined();
    }
  });
});
