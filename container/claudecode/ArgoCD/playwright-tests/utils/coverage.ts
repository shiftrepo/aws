import { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export interface CoverageData {
  url: string;
  ranges: Array<{ start: number; end: number }>;
  text: string;
}

export class CoverageHelper {
  private static coverageDir = 'coverage';

  static async ensureCoverageDirectory(): Promise<void> {
    if (!fs.existsSync(this.coverageDir)) {
      fs.mkdirSync(this.coverageDir, { recursive: true });
    }
  }

  static async collectCoverage(page: Page): Promise<any> {
    try {
      const coverage = await page.evaluate(() => {
        return (window as any).__coverage__;
      });
      return coverage;
    } catch (error) {
      console.warn('Coverage collection failed:', error);
      return null;
    }
  }

  static async startCoverageCollection(page: Page): Promise<void> {
    await page.coverage.startJSCoverage();
    await page.coverage.startCSSCoverage();
  }

  static async stopCoverageCollection(page: Page): Promise<{
    js: any[];
    css: any[];
  }> {
    const [jsCoverage, cssCoverage] = await Promise.all([
      page.coverage.stopJSCoverage(),
      page.coverage.stopCSSCoverage(),
    ]);

    return {
      js: jsCoverage,
      css: cssCoverage,
    };
  }

  static async saveCoverage(coverage: any, filename: string): Promise<string> {
    await this.ensureCoverageDirectory();
    const filepath = path.join(this.coverageDir, `${filename}.json`);

    fs.writeFileSync(filepath, JSON.stringify(coverage, null, 2));
    console.log(`Coverage saved: ${filepath}`);
    return filepath;
  }

  static async mergeCoverageReports(): Promise<void> {
    if (!fs.existsSync(this.coverageDir)) {
      console.log('No coverage directory found');
      return;
    }

    const files = fs
      .readdirSync(this.coverageDir)
      .filter((file) => file.endsWith('.json'));

    if (files.length === 0) {
      console.log('No coverage files found');
      return;
    }

    const mergedCoverage: any = {};

    files.forEach((file) => {
      const filepath = path.join(this.coverageDir, file);
      const coverage = JSON.parse(fs.readFileSync(filepath, 'utf-8'));

      Object.keys(coverage).forEach((key) => {
        if (!mergedCoverage[key]) {
          mergedCoverage[key] = coverage[key];
        } else {
          // Merge coverage data for the same file
          mergedCoverage[key].s = {
            ...mergedCoverage[key].s,
            ...coverage[key].s,
          };
        }
      });
    });

    const mergedPath = path.join(this.coverageDir, 'merged-coverage.json');
    fs.writeFileSync(mergedPath, JSON.stringify(mergedCoverage, null, 2));
    console.log(`Merged coverage saved: ${mergedPath}`);
  }

  static generateCoverageSummary(coverage: any): {
    totalStatements: number;
    coveredStatements: number;
    percentage: number;
  } {
    let totalStatements = 0;
    let coveredStatements = 0;

    Object.values(coverage).forEach((fileCoverage: any) => {
      if (fileCoverage.s) {
        Object.values(fileCoverage.s).forEach((count: any) => {
          totalStatements++;
          if (count > 0) {
            coveredStatements++;
          }
        });
      }
    });

    const percentage =
      totalStatements > 0
        ? Math.round((coveredStatements / totalStatements) * 100)
        : 0;

    return {
      totalStatements,
      coveredStatements,
      percentage,
    };
  }
}
