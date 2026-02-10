/**
 * ModuleInfo.js
 *
 * Data model for module metadata in multi-module/monorepo projects.
 * Stores information about individual npm/yarn workspaces or lerna packages.
 *
 * @module model/ModuleInfo
 */

/**
 * Module information model
 * Represents a single module in a monorepo workspace
 */
export class ModuleInfo {
  constructor() {
    this.moduleName = '';
    this.modulePath = '';
    this.packageJsonPath = '';
    this.testDirectory = '';
    this.coverageDirectory = '';
    this.sourceDirectory = '';
    this.isValid = false;
    this.validationErrors = [];
    this.packageJson = null;
  }

  /**
   * Set module information from package.json
   * @param {string} modulePath - Module root path
   * @param {Object} packageJson - Parsed package.json content
   */
  setFromPackageJson(modulePath, packageJson) {
    this.modulePath = modulePath;
    this.packageJson = packageJson;
    this.moduleName = packageJson.name || modulePath.split('/').pop();
    this.packageJsonPath = `${modulePath}/package.json`;

    // Default directories
    this.testDirectory = `${modulePath}/src/test`;
    this.coverageDirectory = `${modulePath}/coverage`;
    this.sourceDirectory = `${modulePath}/src`;
  }

  /**
   * Validate module structure
   * @returns {boolean} True if module is valid
   */
  validate() {
    this.validationErrors = [];

    if (!this.moduleName) {
      this.validationErrors.push('Module name is missing');
    }

    if (!this.modulePath) {
      this.validationErrors.push('Module path is missing');
    }

    if (!this.packageJson) {
      this.validationErrors.push('package.json not found or invalid');
    }

    this.isValid = this.validationErrors.length === 0;
    return this.isValid;
  }

  /**
   * Get module display name
   * @returns {string}
   */
  getDisplayName() {
    return this.moduleName || this.modulePath.split('/').pop() || 'Unknown Module';
  }

  /**
   * Convert to string representation
   * @returns {string}
   */
  toString() {
    return `ModuleInfo{` +
      `name='${this.moduleName}', ` +
      `path='${this.modulePath}', ` +
      `valid=${this.isValid}}`;
  }

  /**
   * Convert to JSON representation
   * @returns {Object}
   */
  toJSON() {
    return {
      moduleName: this.moduleName,
      modulePath: this.modulePath,
      testDirectory: this.testDirectory,
      coverageDirectory: this.coverageDirectory,
      isValid: this.isValid,
      validationErrors: this.validationErrors
    };
  }
}
