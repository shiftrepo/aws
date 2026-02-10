/**
 * WorkspaceDetector.js
 *
 * Detects and analyzes workspace structure for npm/yarn workspaces and lerna monorepos.
 * Parses root package.json to find workspace configurations and builds ModuleInfo objects.
 *
 * @module core/WorkspaceDetector
 */

import fs from 'fs/promises';
import path from 'path';
import fg from 'fast-glob';
import { ModuleInfo } from '../model/ModuleInfo.js';
import { logger } from '../util/Logger.js';

/**
 * Workspace detector for monorepo projects
 * Supports npm workspaces, yarn workspaces, and lerna
 */
export class WorkspaceDetector {
  constructor() {
    this.rootPath = '';
    this.rootPackageJson = null;
    this.modules = [];
  }

  /**
   * Detect workspace configuration from root directory
   * @param {string} rootPath - Root directory path
   * @returns {Promise<boolean>} True if workspace detected
   */
  async detectWorkspace(rootPath) {
    try {
      this.rootPath = path.resolve(rootPath);
      logger.info('Workspace detection started', { rootPath: this.rootPath });

      // Read root package.json
      const packageJsonPath = path.join(this.rootPath, 'package.json');
      const packageJsonContent = await fs.readFile(packageJsonPath, 'utf8');
      this.rootPackageJson = JSON.parse(packageJsonContent);

      logger.debug('Root package.json loaded', {
        name: this.rootPackageJson.name,
        version: this.rootPackageJson.version
      });

      // Check for workspace configuration
      const hasNpmWorkspaces = this.rootPackageJson.workspaces && Array.isArray(this.rootPackageJson.workspaces);
      const hasYarnWorkspaces = this.rootPackageJson.workspaces && Array.isArray(this.rootPackageJson.workspaces);
      const hasLerna = await this.checkLernaConfig();

      if (hasNpmWorkspaces || hasYarnWorkspaces) {
        logger.info('npm/yarn workspace detected');
        await this.parseWorkspaces(this.rootPackageJson.workspaces);
        return true;
      }

      if (hasLerna) {
        logger.info('Lerna monorepo detected');
        await this.parseLernaWorkspaces();
        return true;
      }

      logger.info('No workspace configuration detected - treating as single module');
      return false;
    } catch (error) {
      logger.error('Workspace detection failed', error);
      return false;
    }
  }

  /**
   * Check if lerna.json exists
   * @returns {Promise<boolean>}
   */
  async checkLernaConfig() {
    try {
      const lernaPath = path.join(this.rootPath, 'lerna.json');
      await fs.access(lernaPath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Parse workspace patterns from package.json
   * @param {Array} workspacePatterns - Workspace glob patterns
   */
  async parseWorkspaces(workspacePatterns) {
    try {
      logger.debug('Parsing workspace patterns', { patterns: workspacePatterns });

      const modulePaths = await fg(
        workspacePatterns.map(pattern => `${pattern}/package.json`),
        {
          cwd: this.rootPath,
          absolute: true,
          ignore: ['**/node_modules/**']
        }
      );

      logger.info('Workspace modules found', { count: modulePaths.length });

      for (const packageJsonPath of modulePaths) {
        const moduleInfo = await this.createModuleInfo(packageJsonPath);
        if (moduleInfo && moduleInfo.validate()) {
          this.modules.push(moduleInfo);
        }
      }

      logger.info('Valid modules loaded', { count: this.modules.length });
    } catch (error) {
      logger.error('Workspace parsing failed', error);
    }
  }

  /**
   * Parse lerna workspaces from lerna.json
   */
  async parseLernaWorkspaces() {
    try {
      const lernaPath = path.join(this.rootPath, 'lerna.json');
      const lernaContent = await fs.readFile(lernaPath, 'utf8');
      const lernaConfig = JSON.parse(lernaContent);

      const packages = lernaConfig.packages || ['packages/*'];
      await this.parseWorkspaces(packages);
    } catch (error) {
      logger.error('Lerna workspace parsing failed', error);
    }
  }

  /**
   * Create ModuleInfo from package.json path
   * @param {string} packageJsonPath - Path to package.json
   * @returns {Promise<ModuleInfo|null>}
   */
  async createModuleInfo(packageJsonPath) {
    try {
      const modulePath = path.dirname(packageJsonPath);
      const packageJsonContent = await fs.readFile(packageJsonPath, 'utf8');
      const packageJson = JSON.parse(packageJsonContent);

      const moduleInfo = new ModuleInfo();
      moduleInfo.setFromPackageJson(modulePath, packageJson);

      logger.debug('Module info created', {
        name: moduleInfo.moduleName,
        path: modulePath
      });

      return moduleInfo;
    } catch (error) {
      logger.warn('Failed to create module info', {
        packageJsonPath,
        error: error.message
      });
      return null;
    }
  }

  /**
   * Get all detected modules
   * @returns {Array<ModuleInfo>}
   */
  getModules() {
    return this.modules;
  }

  /**
   * Get workspace summary
   * @returns {Object}
   */
  getWorkspaceSummary() {
    return {
      rootPath: this.rootPath,
      rootName: this.rootPackageJson?.name || 'Unknown',
      moduleCount: this.modules.length,
      modules: this.modules.map(m => m.getDisplayName())
    };
  }
}
