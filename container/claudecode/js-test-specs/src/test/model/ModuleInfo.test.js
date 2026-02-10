/**
 * ModuleInfo.test.js
 *
 * Unit tests for ModuleInfo model
 */

import { ModuleInfo } from '../../model/ModuleInfo.js';

describe('ModuleInfo', () => {
  let moduleInfo;

  beforeEach(() => {
    moduleInfo = new ModuleInfo();
  });

  test('should initialize with default values', () => {
    expect(moduleInfo.moduleName).toBe('');
    expect(moduleInfo.modulePath).toBe('');
    expect(moduleInfo.isValid).toBe(false);
    expect(moduleInfo.validationErrors).toEqual([]);
  });

  test('should set module info from package.json', () => {
    const packageJson = {
      name: '@myorg/mypackage',
      version: '1.0.0'
    };

    moduleInfo.setFromPackageJson('/path/to/module', packageJson);

    expect(moduleInfo.moduleName).toBe('@myorg/mypackage');
    expect(moduleInfo.modulePath).toBe('/path/to/module');
    expect(moduleInfo.packageJsonPath).toBe('/path/to/module/package.json');
    expect(moduleInfo.testDirectory).toBe('/path/to/module/src/test');
    expect(moduleInfo.coverageDirectory).toBe('/path/to/module/coverage');
    expect(moduleInfo.sourceDirectory).toBe('/path/to/module/src');
  });

  test('should use directory name when package name is missing', () => {
    const packageJson = {};

    moduleInfo.setFromPackageJson('/path/to/my-module', packageJson);

    expect(moduleInfo.moduleName).toBe('my-module');
  });

  test('should validate successfully when all required fields present', () => {
    const packageJson = { name: 'test-module' };
    moduleInfo.setFromPackageJson('/path/to/module', packageJson);

    const isValid = moduleInfo.validate();

    expect(isValid).toBe(true);
    expect(moduleInfo.isValid).toBe(true);
    expect(moduleInfo.validationErrors).toEqual([]);
  });

  test('should fail validation when module name is missing', () => {
    moduleInfo.modulePath = '/path/to/module';
    moduleInfo.packageJson = {};

    const isValid = moduleInfo.validate();

    expect(isValid).toBe(false);
    expect(moduleInfo.isValid).toBe(false);
    expect(moduleInfo.validationErrors).toContain('Module name is missing');
  });

  test('should fail validation when module path is missing', () => {
    moduleInfo.moduleName = 'test-module';
    moduleInfo.packageJson = { name: 'test-module' };

    const isValid = moduleInfo.validate();

    expect(isValid).toBe(false);
    expect(moduleInfo.validationErrors).toContain('Module path is missing');
  });

  test('should fail validation when package.json is missing', () => {
    moduleInfo.moduleName = 'test-module';
    moduleInfo.modulePath = '/path/to/module';

    const isValid = moduleInfo.validate();

    expect(isValid).toBe(false);
    expect(moduleInfo.validationErrors).toContain('package.json not found or invalid');
  });

  test('should get display name from module name', () => {
    moduleInfo.moduleName = '@myorg/mypackage';
    expect(moduleInfo.getDisplayName()).toBe('@myorg/mypackage');
  });

  test('should get display name from path when name is empty', () => {
    moduleInfo.modulePath = '/path/to/my-module';
    expect(moduleInfo.getDisplayName()).toBe('my-module');
  });

  test('should return Unknown Module when both are empty', () => {
    expect(moduleInfo.getDisplayName()).toBe('Unknown Module');
  });

  test('should generate toString output', () => {
    moduleInfo.moduleName = 'test-module';
    moduleInfo.modulePath = '/path/to/module';
    moduleInfo.isValid = true;

    const str = moduleInfo.toString();
    expect(str).toContain('test-module');
    expect(str).toContain('/path/to/module');
    expect(str).toContain('true');
  });

  test('should convert to JSON', () => {
    const packageJson = { name: 'test-module' };
    moduleInfo.setFromPackageJson('/path/to/module', packageJson);
    moduleInfo.validate();

    const json = moduleInfo.toJSON();

    expect(json.moduleName).toBe('test-module');
    expect(json.modulePath).toBe('/path/to/module');
    expect(json.testDirectory).toBe('/path/to/module/src/test');
    expect(json.isValid).toBe(true);
    expect(json.validationErrors).toEqual([]);
  });
});
