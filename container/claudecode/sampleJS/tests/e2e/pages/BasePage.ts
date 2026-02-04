import { Page } from '@playwright/test';

export class BasePage {
  constructor(protected readonly page: Page) {}

  async goto(path: string) {
    await this.page.goto(path);
  }

  async waitForLoadState() {
    await this.page.waitForLoadState('networkidle');
  }

  async getTitle(): Promise<string> {
    return await this.page.title();
  }

  async saveCoverage() {
    const coverage = await this.page.evaluate(() => {
      return (window as any).__coverage__;
    });

    if (coverage) {
      const testName = this.page.url().replace(/[^a-z0-9]/gi, '_');
      const timestamp = Date.now();
      const filename = `.nyc_output/coverage-${testName}-${timestamp}.json`;

      await this.page.evaluate(
        ({ cov, file }) => {
          const fs = require('fs');
          const path = require('path');
          const dir = path.dirname(file);

          if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
          }

          fs.writeFileSync(file, JSON.stringify(cov));
        },
        { cov: coverage, file: filename }
      );
    }
  }
}
