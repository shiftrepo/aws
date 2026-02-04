import { test, expect } from '@playwright/test';
import { EmployeeListPage } from '../pages/EmployeeListPage';
import { EmployeeFormPage } from '../pages/EmployeeFormPage';
import fs from 'fs';
import path from 'path';

test.describe('Error Scenarios', () => {
  let listPage: EmployeeListPage;
  let formPage: EmployeeFormPage;

  test.beforeEach(async ({ page }) => {
    listPage = new EmployeeListPage(page);
    formPage = new EmployeeFormPage(page);
  });

  test.afterEach(async ({ page }) => {
    const coverage = await page.evaluate(() => (window as any).__coverage__);

    if (coverage) {
      const coverageDir = path.resolve(process.cwd(), '.nyc_output');
      if (!fs.existsSync(coverageDir)) {
        fs.mkdirSync(coverageDir, { recursive: true });
      }

      const testInfo = test.info();
      const testName = testInfo.title.replace(/[^a-z0-9]/gi, '_');
      const timestamp = Date.now();
      const filename = path.join(coverageDir, `coverage-error-${testName}-${timestamp}.json`);

      fs.writeFileSync(filename, JSON.stringify(coverage));
    }
  });

  test('should show validation errors for empty form submission', async ({ page }) => {
    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await formPage.navigateToNew();

    // スクリーンショット: 空のフォーム
    await page.screenshot({ path: 'tests/coverage/screenshots/01-empty-form.png', fullPage: true });

    // 空のまま送信
    await formPage.submit();

    // 検証エラーが表示されることを確認
    await page.waitForTimeout(500);

    // スクリーンショット: バリデーションエラー
    await page.screenshot({ path: 'tests/coverage/screenshots/02-validation-errors.png', fullPage: true });

    await expect(formPage.form).toBeVisible();
  });

  test('should show error for invalid email format', async ({ page }) => {
    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await formPage.navigateToNew();

    await formPage.fillName('Test User');
    await formPage.fillEmail('invalid-email');
    await formPage.fillDepartment('IT');
    await formPage.fillPosition('Developer');
    await formPage.fillHireDate('2023-01-01');

    // スクリーンショット: 無効なメールアドレス
    await page.screenshot({ path: 'tests/coverage/screenshots/03-invalid-email.png', fullPage: true });

    await formPage.submit();

    await page.waitForTimeout(500);

    // スクリーンショット: メールバリデーションエラー
    await page.screenshot({ path: 'tests/coverage/screenshots/04-email-validation-error.png', fullPage: true });
  });

  test('should show API error when server returns 500', async ({ page }) => {
    await page.route('/api/employees', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      }
    });

    await formPage.navigateToNew();

    await formPage.fillForm({
      name: 'Test User',
      email: 'test@example.com',
      department: 'Engineering',
      position: 'Developer',
      hireDate: '2023-01-01',
    });

    // スクリーンショット: 送信前の有効なフォーム
    await page.screenshot({ path: 'tests/coverage/screenshots/05-valid-form-before-submit.png', fullPage: true });

    await formPage.submit();

    await page.waitForTimeout(1000);

    // スクリーンショット: APIエラー
    await page.screenshot({ path: 'tests/coverage/screenshots/06-api-error.png', fullPage: true });
  });

  test('should show network error when API is unreachable', async ({ page }) => {
    await page.route('/api/employees', async (route) => {
      await route.abort('failed');
    });

    await listPage.navigate();

    await page.waitForTimeout(1000);

    // スクリーンショット: ネットワークエラー
    await page.screenshot({ path: 'tests/coverage/screenshots/07-network-error.png', fullPage: true });
  });

  test('should show error when employee not found', async ({ page }) => {
    await page.route('/api/employees/NOTFOUND', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Employee not found' }),
      });
    });

    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await formPage.navigateToEdit('NOTFOUND');

    await page.waitForTimeout(1000);

    // スクリーンショット: 404エラー（リストにリダイレクト）
    await page.screenshot({ path: 'tests/coverage/screenshots/08-not-found-error.png', fullPage: true });
  });

  test('should show empty state when no employees exist', async ({ page }) => {
    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await listPage.navigate();
    await listPage.waitForTableLoad();

    // スクリーンショット: 空の状態
    await page.screenshot({ path: 'tests/coverage/screenshots/09-empty-state.png', fullPage: true });

    await expect(listPage.emptyMessage).toBeVisible();
  });
});
