import { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export class ScreenshotHelper {
  private static screenshotDir = 'screenshots';

  static async ensureScreenshotDirectory(): Promise<void> {
    if (!fs.existsSync(this.screenshotDir)) {
      fs.mkdirSync(this.screenshotDir, { recursive: true });
    }
  }

  static async captureScreenshot(
    page: Page,
    name: string,
    options?: { fullPage?: boolean }
  ): Promise<string> {
    await this.ensureScreenshotDirectory();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);

    await page.screenshot({
      path: filepath,
      fullPage: options?.fullPage || false,
    });

    console.log(`Screenshot saved: ${filepath}`);
    return filepath;
  }

  static async captureFullPageScreenshot(page: Page, name: string): Promise<string> {
    return this.captureScreenshot(page, name, { fullPage: true });
  }

  static async captureElementScreenshot(
    page: Page,
    selector: string,
    name: string
  ): Promise<string> {
    await this.ensureScreenshotDirectory();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);

    const element = await page.locator(selector);
    await element.screenshot({ path: filepath });

    console.log(`Element screenshot saved: ${filepath}`);
    return filepath;
  }

  static async saveToScreenshotsFolder(
    buffer: Buffer,
    name: string
  ): Promise<string> {
    await this.ensureScreenshotDirectory();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}_${timestamp}.png`;
    const filepath = path.join(this.screenshotDir, filename);

    fs.writeFileSync(filepath, buffer);
    console.log(`Screenshot saved: ${filepath}`);
    return filepath;
  }

  static cleanOldScreenshots(daysOld: number = 7): void {
    if (!fs.existsSync(this.screenshotDir)) {
      return;
    }

    const now = Date.now();
    const maxAge = daysOld * 24 * 60 * 60 * 1000;

    const files = fs.readdirSync(this.screenshotDir);
    files.forEach((file) => {
      const filepath = path.join(this.screenshotDir, file);
      const stat = fs.statSync(filepath);
      const age = now - stat.mtimeMs;

      if (age > maxAge) {
        fs.unlinkSync(filepath);
        console.log(`Deleted old screenshot: ${filepath}`);
      }
    });
  }
}
