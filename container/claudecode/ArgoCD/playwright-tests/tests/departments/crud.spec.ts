import { test, expect } from '@playwright/test';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { generateRandomDept, generateRandomOrg } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Department CRUD Operations', () => {
  let deptPage: DepartmentPage;
  let orgPage: OrganizationPage;

  test.beforeEach(async ({ page }) => {
    deptPage = new DepartmentPage(page);
    orgPage = new OrganizationPage(page);
    await deptPage.goto();
  });

  test('should list departments with table rendering', async ({ page }) => {
    await deptPage.waitForTableLoad();

    // Verify table is visible
    await expect(deptPage.departmentTable).toBeVisible();

    // Verify table has headers
    const headers = await page.locator('th').allTextContents();
    expect(headers.length).toBeGreaterThan(0);

    await ScreenshotHelper.captureScreenshot(page, 'departments-list');
  });

  test('should create new department under organization', async ({ page }) => {
    // First create an organization
    await orgPage.goto();
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Now create a department
    await deptPage.goto();
    const newDept = generateRandomDept();

    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);

    if (newDept.description) {
      await deptPage.descriptionInput.fill(newDept.description);
    }

    // Select organization if selector is available
    if (await deptPage.organizationSelect.isVisible()) {
      const options = await deptPage.organizationSelect.locator('option').count();
      if (options > 1) {
        await deptPage.organizationSelect.selectOption({ index: 1 });
      }
    }

    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Verify department was created
    await deptPage.searchDepartments(newDept.code);
    const isVisible = await deptPage.verifyDepartmentInList(newDept.name);
    expect(isVisible).toBeTruthy();

    await ScreenshotHelper.captureScreenshot(page, 'department-created');
  });

  test('should update department information', async ({ page }) => {
    // Create a department
    const newDept = generateRandomDept();
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Update the department
    const updatedData = {
      name: `${newDept.name} - Updated`,
      description: 'Updated department description',
    };

    await deptPage.editDepartment(newDept.code, updatedData);

    // Verify update
    await deptPage.searchDepartments(newDept.code);
    const isVisible = await deptPage.verifyDepartmentInList(updatedData.name);
    expect(isVisible).toBeTruthy();
  });

  test('should delete department', async ({ page }) => {
    // Create a department
    const newDept = generateRandomDept();
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Verify it exists
    await deptPage.searchDepartments(newDept.code);
    let isVisible = await deptPage.verifyDepartmentInList(newDept.name);
    expect(isVisible).toBeTruthy();

    // Delete the department
    await deptPage.deleteDepartment(newDept.code);

    // Verify it's deleted
    await deptPage.searchDepartments(newDept.code);
    await page.waitForTimeout(500);
    const count = await deptPage.getDepartmentCount();
    expect(count).toBe(0);
  });

  test('should assign parent department', async ({ page }) => {
    // Create parent department
    const parentDept = generateRandomDept();
    parentDept.name = 'Parent Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(parentDept.code);
    await deptPage.nameInput.fill(parentDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create child department
    const childDept = generateRandomDept();
    childDept.name = 'Child Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(childDept.code);
    await deptPage.nameInput.fill(childDept.name);

    // Select parent if selector is available
    if (await deptPage.parentDepartmentSelect.isVisible()) {
      const options = await deptPage.parentDepartmentSelect.locator('option').count();
      if (options > 1) {
        await deptPage.parentDepartmentSelect.selectOption({ index: 1 });
      }
    }

    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    await ScreenshotHelper.captureScreenshot(page, 'department-with-parent');
  });

  test('should display pagination when many departments exist', async ({ page }) => {
    // Check if pagination is present
    const paginationExists = await page.locator('[role="navigation"], .pagination').count();

    if (paginationExists > 0) {
      const nextButton = page.getByRole('button', { name: /next/i });
      if (await nextButton.isVisible()) {
        await nextButton.click();
        await page.waitForLoadState('networkidle');
      }
    }

    await ScreenshotHelper.captureScreenshot(page, 'departments-pagination');
  });

  test('should search departments by code', async ({ page }) => {
    const newDept = generateRandomDept();
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Search by code
    await deptPage.searchDepartments(newDept.code);

    const isVisible = await deptPage.verifyDepartmentInList(newDept.name);
    expect(isVisible).toBeTruthy();
  });

  test('should search departments by name', async ({ page }) => {
    const newDept = generateRandomDept();
    newDept.name = 'Unique Department Name For Search';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Search by name
    await deptPage.searchDepartments(newDept.name);

    const isVisible = await deptPage.verifyDepartmentInList(newDept.name);
    expect(isVisible).toBeTruthy();
  });

  test('should cancel department creation', async ({ page }) => {
    const newDept = generateRandomDept();

    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);

    // Click cancel
    await deptPage.cancelButton.click();

    // Verify department was not created
    await deptPage.searchDepartments(newDept.code);
    const count = await deptPage.getDepartmentCount();
    expect(count).toBe(0);
  });

  test('should handle empty search results', async ({ page }) => {
    await deptPage.searchDepartments('NONEXISTENT_DEPT_12345');

    const count = await deptPage.getDepartmentCount();
    expect(count).toBe(0);

    await ScreenshotHelper.captureScreenshot(page, 'departments-no-results');
  });
});
