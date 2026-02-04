import { test, expect } from '@playwright/test';
import { EmployeeListPage } from '../pages/EmployeeListPage';
import { EmployeeFormPage } from '../pages/EmployeeFormPage';
import fs from 'fs';
import path from 'path';

test.describe('Employee Management', () => {
  let listPage: EmployeeListPage;
  let formPage: EmployeeFormPage;

  test.beforeEach(async ({ page }) => {
    listPage = new EmployeeListPage(page);
    formPage = new EmployeeFormPage(page);

    await page.route('/api/employees', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    await page.route('/api/employees/*', async (route) => {
      const url = route.request().url();
      const method = route.request().method();

      if (method === 'GET') {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Not found' }),
        });
      } else if (method === 'PUT') {
        const id = url.split('/').pop();
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id,
            ...route.request().postDataJSON(),
          }),
        });
      } else if (method === 'DELETE') {
        await route.fulfill({
          status: 204,
        });
      } else {
        await route.continue();
      }
    });

    await page.route('/api/employees', async (route) => {
      if (route.request().method() === 'POST') {
        const postData = route.request().postDataJSON();
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: `EMP-${Date.now()}`,
            ...postData,
          }),
        });
      } else {
        await route.continue();
      }
    });
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
      const filename = path.join(coverageDir, `coverage-${testName}-${timestamp}.json`);

      fs.writeFileSync(filename, JSON.stringify(coverage));
    }
  });

  test('should display employee list page', async () => {
    await listPage.navigate();

    await expect(listPage.pageTitle).toBeVisible();
    await expect(listPage.pageTitle).toHaveText('Employee Management');
    await expect(listPage.addEmployeeButton).toBeVisible();
  });

  test('should navigate to create employee form', async () => {
    await listPage.navigate();
    await listPage.clickAddEmployee();

    await expect(formPage.pageTitle).toBeVisible();
    await expect(formPage.pageTitle).toHaveText('Add New Employee');
  });

  test('should create a new employee', async ({ page }) => {
    let createdEmployee: any = null;

    await page.route('/api/employees', async (route) => {
      if (route.request().method() === 'POST') {
        const postData = route.request().postDataJSON();
        createdEmployee = {
          id: 'EMP-TEST-001',
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
      name: 'John Doe',
      email: 'john.doe@example.com',
      department: 'Engineering',
      position: 'Senior Developer',
      hireDate: '2023-01-01',
    });

    await formPage.submit();

    await page.waitForURL('/');
    await listPage.waitForTableLoad();

    await expect(listPage.page.getByText('John Doe')).toBeVisible();
  });

  test('should validate required fields', async () => {
    await formPage.navigateToNew();

    await formPage.submit();

    await expect(formPage.form).toBeVisible();
  });

  test('should edit an existing employee', async ({ page }) => {
    const mockEmployee = {
      id: 'EMP-EDIT-001',
      name: 'Jane Smith',
      email: 'jane.smith@example.com',
      department: 'Marketing',
      position: 'Manager',
      hireDate: '2022-06-15T00:00:00.000Z',
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

    await expect(formPage.nameInput).toHaveValue('Jane Smith');

    await formPage.fillName('Jane Doe');
    await formPage.fillPosition('Senior Manager');

    await formPage.submit();

    await page.waitForURL('/');
  });

  test('should delete an employee', async ({ page }) => {
    const mockEmployee = {
      id: 'EMP-DELETE-001',
      name: 'Delete Me',
      email: 'delete@example.com',
      department: 'Test',
      position: 'Tester',
      hireDate: '2023-01-01T00:00:00.000Z',
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

    await expect(listPage.page.getByText('Delete Me')).toBeVisible();

    await listPage.clickDeleteButton(mockEmployee.id);

    await listPage.page.waitForTimeout(500);

    await expect(listPage.page.getByText('Delete Me')).not.toBeVisible();
  });

  test('should cancel form and return to list', async () => {
    await formPage.navigateToNew();

    await formPage.fillName('Test User');
    await formPage.cancel();

    await expect(listPage.pageTitle).toBeVisible();
    await expect(listPage.pageTitle).toHaveText('Employee Management');
  });
});
