#!/usr/bin/env node

/**
 * Coverage Collection Script
 *
 * This script aggregates coverage data from multiple sources:
 * 1. Unit test coverage (Vitest)
 * 2. E2E test coverage (Playwright + Istanbul)
 *
 * It uses nyc to merge and generate reports in multiple formats:
 * - HTML report for local viewing
 * - lcov.info for SonarQube
 * - cobertura-coverage.xml for Azure DevOps
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const nycOutputDir = path.join(rootDir, '.nyc_output');
const coverageDir = path.join(rootDir, 'coverage');

console.log('=== Coverage Collection Script ===\n');

function executeCommand(command, description) {
  console.log(`[INFO] ${description}...`);
  try {
    execSync(command, { cwd: rootDir, stdio: 'inherit' });
    console.log(`[SUCCESS] ${description} completed\n`);
    return true;
  } catch (error) {
    console.error(`[ERROR] ${description} failed:`, error.message);
    return false;
  }
}

function ensureDirectoryExists(dir) {
  if (!fs.existsSync(dir)) {
    console.log(`[INFO] Creating directory: ${dir}`);
    fs.mkdirSync(dir, { recursive: true });
  }
}

function checkCoverageFiles() {
  console.log('[INFO] Checking for coverage files...');

  if (!fs.existsSync(nycOutputDir)) {
    console.warn('[WARN] No .nyc_output directory found');
    return false;
  }

  const files = fs.readdirSync(nycOutputDir);
  const coverageFiles = files.filter(f => f.startsWith('coverage-') && f.endsWith('.json'));

  if (coverageFiles.length === 0) {
    console.warn('[WARN] No coverage files found in .nyc_output');
    return false;
  }

  console.log(`[INFO] Found ${coverageFiles.length} coverage file(s)`);
  coverageFiles.forEach(file => console.log(`  - ${file}`));
  console.log();

  return true;
}

function mergeCoverageData() {
  console.log('[INFO] Merging coverage data...');

  if (!fs.existsSync(nycOutputDir)) {
    console.log('[INFO] No coverage data to merge, skipping...\n');
    return true;
  }

  const files = fs.readdirSync(nycOutputDir);
  const coverageFiles = files.filter(f => f.endsWith('.json'));

  if (coverageFiles.length === 0) {
    console.log('[INFO] No coverage files to merge\n');
    return true;
  }

  const mergedCoverage = {};

  coverageFiles.forEach(file => {
    const filePath = path.join(nycOutputDir, file);
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const coverage = JSON.parse(content);

      Object.keys(coverage).forEach(key => {
        if (!mergedCoverage[key]) {
          mergedCoverage[key] = coverage[key];
        } else {
          const existing = mergedCoverage[key];
          const newCov = coverage[key];

          if (existing.s && newCov.s) {
            Object.keys(newCov.s).forEach(k => {
              existing.s[k] = (existing.s[k] || 0) + newCov.s[k];
            });
          }

          if (existing.f && newCov.f) {
            Object.keys(newCov.f).forEach(k => {
              existing.f[k] = (existing.f[k] || 0) + newCov.f[k];
            });
          }

          if (existing.b && newCov.b) {
            Object.keys(newCov.b).forEach(k => {
              if (!existing.b[k]) {
                existing.b[k] = newCov.b[k];
              } else {
                existing.b[k] = existing.b[k].map((v, i) =>
                  (v || 0) + (newCov.b[k][i] || 0)
                );
              }
            });
          }
        }
      });
    } catch (error) {
      console.warn(`[WARN] Failed to process ${file}:`, error.message);
    }
  });

  const mergedFile = path.join(nycOutputDir, 'coverage-merged.json');
  fs.writeFileSync(mergedFile, JSON.stringify(mergedCoverage, null, 2));
  console.log(`[SUCCESS] Merged coverage written to: coverage-merged.json\n`);

  return true;
}

function generateReports() {
  console.log('[INFO] Generating coverage reports...');
  ensureDirectoryExists(coverageDir);

  const reporters = [
    { format: 'html', description: 'HTML report' },
    { format: 'lcov', description: 'LCOV report (for SonarQube)' },
    { format: 'cobertura', description: 'Cobertura report (for Azure DevOps)' },
    { format: 'text-summary', description: 'Text summary' },
  ];

  let success = true;

  reporters.forEach(({ format, description }) => {
    const result = executeCommand(
      `npx nyc report --reporter=${format} --report-dir=coverage`,
      `Generating ${description}`
    );
    if (!result) {
      success = false;
    }
  });

  return success;
}

function displaySummary() {
  console.log('\n=== Coverage Report Summary ===\n');

  const summaryFile = path.join(coverageDir, 'coverage-summary.json');
  if (fs.existsSync(summaryFile)) {
    try {
      const summary = JSON.parse(fs.readFileSync(summaryFile, 'utf8'));
      const total = summary.total;

      console.log('Overall Coverage:');
      console.log(`  Lines      : ${total.lines.pct}%`);
      console.log(`  Statements : ${total.statements.pct}%`);
      console.log(`  Functions  : ${total.functions.pct}%`);
      console.log(`  Branches   : ${total.branches.pct}%`);
      console.log();
    } catch (error) {
      console.warn('[WARN] Failed to read coverage summary:', error.message);
    }
  }

  console.log('Generated Reports:');
  console.log(`  HTML       : coverage/index.html`);
  console.log(`  LCOV       : coverage/lcov.info`);
  console.log(`  Cobertura  : coverage/cobertura-coverage.xml`);
  console.log();
}

function checkThresholds() {
  console.log('[INFO] Checking coverage thresholds...');

  const summaryFile = path.join(coverageDir, 'coverage-summary.json');
  if (!fs.existsSync(summaryFile)) {
    console.warn('[WARN] Coverage summary not found, skipping threshold check');
    return true;
  }

  try {
    const summary = JSON.parse(fs.readFileSync(summaryFile, 'utf8'));
    const total = summary.total;
    const threshold = 80;

    const checks = [
      { name: 'Lines', value: total.lines.pct },
      { name: 'Statements', value: total.statements.pct },
      { name: 'Functions', value: total.functions.pct },
      { name: 'Branches', value: total.branches.pct },
    ];

    let allPassed = true;

    checks.forEach(({ name, value }) => {
      const passed = value >= threshold;
      const status = passed ? '[PASS]' : '[FAIL]';
      const color = passed ? '' : '';

      console.log(`${status} ${name}: ${value}% (threshold: ${threshold}%)`);

      if (!passed) {
        allPassed = false;
      }
    });

    console.log();

    if (allPassed) {
      console.log('[SUCCESS] All coverage thresholds met! ✓\n');
    } else {
      console.log('[WARNING] Some coverage thresholds not met\n');
    }

    return allPassed;
  } catch (error) {
    console.error('[ERROR] Failed to check thresholds:', error.message);
    return false;
  }
}

function main() {
  const startTime = Date.now();

  console.log('[INFO] Starting coverage collection process...\n');

  ensureDirectoryExists(nycOutputDir);
  ensureDirectoryExists(coverageDir);

  const hasCoverage = checkCoverageFiles();

  if (!hasCoverage) {
    console.log('[INFO] No coverage data found. Run tests with coverage enabled first.\n');
    console.log('Commands:');
    console.log('  pnpm test:coverage     - Run E2E tests with coverage');
    console.log('  pnpm test             - Run unit tests\n');
    process.exit(1);
  }

  if (!mergeCoverageData()) {
    console.error('[ERROR] Failed to merge coverage data');
    process.exit(1);
  }

  if (!generateReports()) {
    console.error('[ERROR] Failed to generate some reports');
    process.exit(1);
  }

  displaySummary();

  const thresholdsMet = checkThresholds();

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log(`[INFO] Coverage collection completed in ${duration}s\n`);

  if (!thresholdsMet && process.env.CI === 'true') {
    console.error('[ERROR] Coverage thresholds not met in CI environment');
    process.exit(1);
  }

  console.log('=== Done ===\n');
}

main();
