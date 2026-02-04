import { test, expect } from '@playwright/test';
import { EmployeeListPage } from '../pages/EmployeeListPage';
import { EmployeeFormPage } from '../pages/EmployeeFormPage';
import fs from 'fs';
import path from 'path';

test.describe('Success Scenarios', () => {
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
      const filename = path.join(coverageDir, `coverage-success-${testName}-${timestamp}.json`);

      fs.writeFileSync(filename, JSON.stringify(coverage));
    }
  });

  test('should display employee list with data', async ({ page }) => {
    const mockEmployees = [
      {
        id: 'EMP-001',
        name: '山田太郎',
        email: 'yamada@example.com',
        department: '開発部',
        position: 'シニアエンジニア',
        hireDate: '2020-04-01T00:00:00.000Z',
      },
      {
        id: 'EMP-002',
        name: '佐藤花子',
        email: 'sato@example.com',
        department: '営業部',
        position: 'マネージャー',
        hireDate: '2019-07-15T00:00:00.000Z',
      },
      {
        id: 'EMP-003',
        name: '鈴木一郎',
        email: 'suzuki@example.com',
        department: '人事部',
        position: 'スペシャリスト',
        hireDate: '2021-01-10T00:00:00.000Z',
      },
    ];

    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockEmployees),
      });
    });

    await listPage.navigate();
    await listPage.waitForTableLoad();

    // スクリーンショット: 職員一覧（データあり）
    await page.screenshot({ path: 'tests/coverage/screenshots/10-employee-list-with-data.png', fullPage: true });

    await expect(listPage.table).toBeVisible();
    await expect(listPage.page.getByText('山田太郎')).toBeVisible();
    await expect(listPage.page.getByText('佐藤花子')).toBeVisible();
    await expect(listPage.page.getByText('鈴木一郎')).toBeVisible();
  });

  test('should show create employee form', async ({ page }) => {
    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await formPage.navigateToNew();

    // スクリーンショット: 新規作成フォーム
    await page.screenshot({ path: 'tests/coverage/screenshots/11-create-form.png', fullPage: true });

    await expect(formPage.pageTitle).toHaveText('Add New Employee');
    await expect(formPage.nameInput).toBeVisible();
    await expect(formPage.emailInput).toBeVisible();
    await expect(formPage.departmentInput).toBeVisible();
    await expect(formPage.positionInput).toBeVisible();
    await expect(formPage.hireDateInput).toBeVisible();
  });

  test('should create employee successfully', async ({ page }) => {
    let createdEmployee: any = null;

    await page.route('/api/employees', async (route) => {
      if (route.request().method() === 'POST') {
        const postData = route.request().postDataJSON();
        createdEmployee = {
          id: 'EMP-NEW-001',
          ...postData,
        };
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify(createdEmployee),
        });
      } else if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(createdEmployee ? [createdEmployee] : []),
        });
      }
    });

    await formPage.navigateToNew();

    await formPage.fillForm({
      name: '田中健太',
      email: 'tanaka@example.com',
      department: 'マーケティング部',
      position: 'アシスタント',
      hireDate: '2024-01-15',
    });

    // スクリーンショット: 入力完了したフォーム
    await page.screenshot({ path: 'tests/coverage/screenshots/12-filled-form.png', fullPage: true });

    await formPage.submit();

    await page.waitForURL('/');
    await listPage.waitForTableLoad();

    // スクリーンショット: 作成後の一覧
    await page.screenshot({ path: 'tests/coverage/screenshots/13-after-creation.png', fullPage: true });

    await expect(listPage.page.getByText('田中健太')).toBeVisible();
  });

  test('should edit employee successfully', async ({ page }) => {
    const mockEmployee = {
      id: 'EMP-EDIT-001',
      name: '高橋美咲',
      email: 'takahashi@example.com',
      department: '総務部',
      position: 'リーダー',
      hireDate: '2018-03-20T00:00:00.000Z',
    };

    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([mockEmployee]),
      });
    });

    await page.route(`/api/employees/${mockEmployee.id}`, async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockEmployee),
        });
      } else if (route.request().method() === 'PUT') {
        const updatedData = route.request().postDataJSON();
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ...mockEmployee,
            ...updatedData,
          }),
        });
      }
    });

    await formPage.navigateToEdit(mockEmployee.id);

    // スクリーンショット: 編集フォーム（データ読み込み済み）
    await page.screenshot({ path: 'tests/coverage/screenshots/14-edit-form-loaded.png', fullPage: true });

    await expect(formPage.pageTitle).toHaveText('Edit Employee');
    await expect(formPage.nameInput).toHaveValue('高橋美咲');

    await formPage.fillName('高橋美咲（更新）');
    await formPage.fillPosition('シニアリーダー');

    // スクリーンショット: 編集後のフォーム
    await page.screenshot({ path: 'tests/coverage/screenshots/15-edit-form-modified.png', fullPage: true });

    await formPage.submit();

    await page.waitForURL('/');

    // スクリーンショット: 更新後の一覧
    await page.screenshot({ path: 'tests/coverage/screenshots/16-after-update.png', fullPage: true });
  });

  test('should show delete confirmation and delete employee', async ({ page }) => {
    const mockEmployee = {
      id: 'EMP-DELETE-001',
      name: '伊藤次郎',
      email: 'ito@example.com',
      department: '経理部',
      position: 'アソシエイト',
      hireDate: '2022-06-01T00:00:00.000Z',
    };

    let employees = [mockEmployee];

    await page.route('/api/employees', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(employees),
        });
      }
    });

    await page.route(`/api/employees/${mockEmployee.id}`, async (route) => {
      if (route.request().method() === 'DELETE') {
        employees = [];
        await route.fulfill({ status: 204 });
      } else if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockEmployee),
        });
      }
    });

    await listPage.navigate();
    await listPage.waitForTableLoad();

    // スクリーンショット: 削除前の一覧
    await page.screenshot({ path: 'tests/coverage/screenshots/17-before-delete.png', fullPage: true });

    await expect(listPage.page.getByText('伊藤次郎')).toBeVisible();

    await listPage.clickDeleteButton(mockEmployee.id);

    await page.waitForTimeout(500);

    // スクリーンショット: 削除後の一覧
    await page.screenshot({ path: 'tests/coverage/screenshots/18-after-delete.png', fullPage: true });
  });
});
