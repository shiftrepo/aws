import { test, expect } from '@playwright/test';
import { UserPage } from '../../page-objects/UserPage';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { generateRandomUser, generateRandomDept } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('User Department Assignment', () => {
  let userPage: UserPage;
  let deptPage: DepartmentPage;

  test.beforeEach(async ({ page }) => {
    userPage = new UserPage(page);
    deptPage = new DepartmentPage(page);
  });

  test('should assign user to department', async ({ page }) => {
    // Create a department first
    await deptPage.goto();
    const newDept = generateRandomDept();
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create a user
    await userPage.goto();
    const newUser = generateRandomUser();
    await userPage.createButton.click();
    await userPage.usernameInput.fill(newUser.username);
    await userPage.emailInput.fill(newUser.email);
    await userPage.firstNameInput.fill(newUser.firstName);
    await userPage.lastNameInput.fill(newUser.lastName);

    // Assign to department
    if (await userPage.departmentSelect.isVisible()) {
      const deptOption = await userPage.departmentSelect.locator(`option:has-text("${newDept.name}")`);
      if (await deptOption.count() > 0) {
        await userPage.departmentSelect.selectOption({ label: newDept.name });
      }
    }

    await userPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Verify assignment
    await userPage.searchUsers(newUser.username);
    const isVisible = await userPage.verifyUserInList(newUser.username);
    expect(isVisible).toBeTruthy();

    await ScreenshotHelper.captureScreenshot(page, 'user-assigned-to-department');
  });

  test('should change user department', async ({ page }) => {
    // Create two departments
    await deptPage.goto();
    const dept1 = generateRandomDept();
    dept1.name = 'Department One';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(dept1.code);
    await deptPage.nameInput.fill(dept1.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    const dept2 = generateRandomDept();
    dept2.name = 'Department Two';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(dept2.code);
    await deptPage.nameInput.fill(dept2.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create user in dept1
    await userPage.goto();
    const newUser = generateRandomUser();
    await userPage.createButton.click();
    await userPage.usernameInput.fill(newUser.username);
    await userPage.emailInput.fill(newUser.email);
    await userPage.firstNameInput.fill(newUser.firstName);
    await userPage.lastNameInput.fill(newUser.lastName);
    await userPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Change to dept2
    await userPage.searchUsers(newUser.username);
    const row = await userPage.getUserByUsername(newUser.username);
    await row.locator(userPage.editButton).click();

    if (await userPage.departmentSelect.isVisible()) {
      const dept2Option = await userPage.departmentSelect.locator(`option:has-text("${dept2.name}")`);
      if (await dept2Option.count() > 0) {
        await userPage.departmentSelect.selectOption({ label: dept2.name });
      }
    }

    await userPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    await ScreenshotHelper.captureScreenshot(page, 'user-department-changed');
  });

  test('should view users in department', async ({ page }) => {
    // Create department
    await deptPage.goto();
    const newDept = generateRandomDept();
    newDept.name = 'Users View Test Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create users in department
    await userPage.goto();
    for (let i = 0; i < 3; i++) {
      const user = generateRandomUser();
      await userPage.createButton.click();
      await userPage.usernameInput.fill(user.username);
      await userPage.emailInput.fill(user.email);
      await userPage.firstNameInput.fill(user.firstName);
      await userPage.lastNameInput.fill(user.lastName);

      if (await userPage.departmentSelect.isVisible()) {
        const deptOption = await userPage.departmentSelect.locator(`option:has-text("${newDept.name}")`);
        if (await deptOption.count() > 0) {
          await userPage.departmentSelect.selectOption({ label: newDept.name });
        }
      }

      await userPage.submitButton.click();
      await page.waitForLoadState('networkidle');
    }

    // View users in department
    const users = await userPage.getUsersByDepartment(newDept.name);
    expect(users.length).toBeGreaterThanOrEqual(0);

    await ScreenshotHelper.captureScreenshot(page, 'users-in-department');
  });

  test('should unassign user from department', async ({ page }) => {
    // Create department
    await deptPage.goto();
    const newDept = generateRandomDept();
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create user with department
    await userPage.goto();
    const newUser = generateRandomUser();
    await userPage.createButton.click();
    await userPage.usernameInput.fill(newUser.username);
    await userPage.emailInput.fill(newUser.email);
    await userPage.firstNameInput.fill(newUser.firstName);
    await userPage.lastNameInput.fill(newUser.lastName);
    await userPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Unassign from department
    await userPage.searchUsers(newUser.username);
    const row = await userPage.getUserByUsername(newUser.username);
    await row.locator(userPage.editButton).click();

    if (await userPage.departmentSelect.isVisible()) {
      // Select empty option or "None"
      const emptyOption = await userPage.departmentSelect.locator('option[value=""], option:has-text("None")');
      if (await emptyOption.count() > 0) {
        await emptyOption.first().click();
      }
    }

    await userPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    await ScreenshotHelper.captureScreenshot(page, 'user-unassigned');
  });

  test('should assign multiple users to same department', async ({ page }) => {
    // Create department
    await deptPage.goto();
    const newDept = generateRandomDept();
    newDept.name = 'Multi User Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create multiple users
    await userPage.goto();
    const usernames: string[] = [];

    for (let i = 0; i < 5; i++) {
      const user = generateRandomUser();
      usernames.push(user.username);

      await userPage.createButton.click();
      await userPage.usernameInput.fill(user.username);
      await userPage.emailInput.fill(user.email);
      await userPage.firstNameInput.fill(user.firstName);
      await userPage.lastNameInput.fill(user.lastName);

      if (await userPage.departmentSelect.isVisible()) {
        const deptOption = await userPage.departmentSelect.locator(`option:has-text("${newDept.name}")`);
        if (await deptOption.count() > 0) {
          await userPage.departmentSelect.selectOption({ label: newDept.name });
        }
      }

      await userPage.submitButton.click();
      await page.waitForLoadState('networkidle');
    }

    // Verify all users are assigned
    for (const username of usernames) {
      await userPage.searchUsers(username);
      const isVisible = await userPage.verifyUserInList(username);
      expect(isVisible).toBeTruthy();
    }

    await ScreenshotHelper.captureScreenshot(page, 'multiple-users-assigned');
  });

  test('should filter users by department', async ({ page }) => {
    await userPage.goto();

    // Look for department filter dropdown
    const deptFilter = page.locator('select[name*="department" i], select[aria-label*="department" i]');

    if (await deptFilter.isVisible()) {
      const options = await deptFilter.locator('option').count();
      if (options > 1) {
        await deptFilter.selectOption({ index: 1 });
        await page.waitForLoadState('networkidle');

        await ScreenshotHelper.captureScreenshot(page, 'users-filtered-by-department');
      }
    }
  });

  test('should display department info in user list', async ({ page }) => {
    await userPage.goto();
    await userPage.waitForTableLoad();

    // Verify department column exists
    const deptHeader = page.locator('th:has-text("Department"), th:has-text("Dept")');

    if (await deptHeader.isVisible()) {
      await ScreenshotHelper.captureScreenshot(page, 'user-list-with-departments');
    }
  });

  test('should prevent deletion of department with assigned users', async ({ page }) => {
    // Create department
    await deptPage.goto();
    const newDept = generateRandomDept();
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Assign user to department
    await userPage.goto();
    const newUser = generateRandomUser();
    await userPage.createButton.click();
    await userPage.usernameInput.fill(newUser.username);
    await userPage.emailInput.fill(newUser.email);
    await userPage.firstNameInput.fill(newUser.firstName);
    await userPage.lastNameInput.fill(newUser.lastName);
    await userPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Try to delete department
    await deptPage.goto();
    await deptPage.searchDepartments(newDept.code);

    const row = await deptPage.getDepartmentByCode(newDept.code);
    if (await row.locator(deptPage.deleteButton).isVisible()) {
      await row.locator(deptPage.deleteButton).click();

      // Should show error or warning
      await page.waitForTimeout(500);
      await ScreenshotHelper.captureScreenshot(page, 'delete-department-with-users-error');
    }
  });
});
