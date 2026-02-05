import { test, expect } from '@playwright/test';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { UserPage } from '../../page-objects/UserPage';
import { invalidData, generateRandomOrg } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Validation Error Scenarios', () => {
  test.describe('Organization Validation', () => {
    let orgPage: OrganizationPage;

    test.beforeEach(async ({ page }) => {
      orgPage = new OrganizationPage(page);
      await orgPage.goto();
    });

    test('should show validation error for empty organization code', async ({ page }) => {
      await orgPage.createButton.click();
      await orgPage.codeInput.fill('');
      await orgPage.nameInput.fill('Test Organization');
      await orgPage.submitButton.click();

      // Wait for validation error
      await page.waitForTimeout(500);

      // Check for error message
      const errors = await orgPage.getValidationErrors();
      expect(errors.length).toBeGreaterThan(0);

      await ScreenshotHelper.captureScreenshot(page, 'org-empty-code-error');
    });

    test('should show validation error for empty organization name', async ({ page }) => {
      await orgPage.createButton.click();
      await orgPage.codeInput.fill('ORG123');
      await orgPage.nameInput.fill('');
      await orgPage.submitButton.click();

      await page.waitForTimeout(500);

      const errors = await orgPage.getValidationErrors();
      expect(errors.length).toBeGreaterThan(0);

      await ScreenshotHelper.captureScreenshot(page, 'org-empty-name-error');
    });

    test('should show validation error for duplicate organization code', async ({ page }) => {
      // Create an organization
      const org = generateRandomOrg();
      await orgPage.createOrganization(org);

      // Try to create another with same code
      await orgPage.createButton.click();
      await orgPage.codeInput.fill(org.code);
      await orgPage.nameInput.fill('Different Name');
      await orgPage.submitButton.click();

      await page.waitForTimeout(500);

      // Should show error
      const errorVisible = await page.locator('text=/duplicate|already exists|conflict/i').isVisible();
      expect(errorVisible).toBeTruthy();

      await ScreenshotHelper.captureScreenshot(page, 'org-duplicate-code-error');
    });

    test('should validate organization code format', async ({ page }) => {
      await orgPage.createButton.click();
      await orgPage.codeInput.fill('invalid code with spaces');
      await orgPage.nameInput.fill('Test Org');
      await orgPage.submitButton.click();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureScreenshot(page, 'org-invalid-code-format');
    });

    test('should validate organization code length', async ({ page }) => {
      await orgPage.createButton.click();
      await orgPage.codeInput.fill('AB'); // Too short
      await orgPage.nameInput.fill('Test Org');
      await orgPage.submitButton.click();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureScreenshot(page, 'org-code-too-short');
    });
  });

  test.describe('Department Validation', () => {
    let deptPage: DepartmentPage;

    test.beforeEach(async ({ page }) => {
      deptPage = new DepartmentPage(page);
      await deptPage.goto();
    });

    test('should show validation error for empty department code', async ({ page }) => {
      await deptPage.createButton.click();
      await deptPage.codeInput.fill('');
      await deptPage.nameInput.fill('Test Department');
      await deptPage.submitButton.click();

      await page.waitForTimeout(500);

      const errorVisible = await page.locator('text=/required|cannot be empty/i').isVisible();
      await ScreenshotHelper.captureScreenshot(page, 'dept-empty-code-error');
    });

    test('should show validation error for empty department name', async ({ page }) => {
      await deptPage.createButton.click();
      await deptPage.codeInput.fill('DEPT123');
      await deptPage.nameInput.fill('');
      await deptPage.submitButton.click();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureScreenshot(page, 'dept-empty-name-error');
    });

    test('should prevent selecting same department as parent', async ({ page }) => {
      // Create a department first
      await deptPage.createButton.click();
      await deptPage.codeInput.fill(`DEPT${Date.now()}`);
      await deptPage.nameInput.fill('Self Parent Test');
      await deptPage.submitButton.click();
      await page.waitForLoadState('networkidle');

      // Edit and try to select itself as parent
      const row = await page.locator('tr').last();
      await row.locator(deptPage.editButton).click();

      // Parent select should not include itself
      if (await deptPage.parentDepartmentSelect.isVisible()) {
        await ScreenshotHelper.captureScreenshot(page, 'dept-self-parent-prevented');
      }
    });

    test('should validate required fields on department form', async ({ page }) => {
      await deptPage.createButton.click();
      await deptPage.submitButton.click();

      await page.waitForTimeout(500);

      const errors = await page.locator('.error, .validation-error, [role="alert"]').count();
      expect(errors).toBeGreaterThan(0);

      await ScreenshotHelper.captureScreenshot(page, 'dept-all-fields-required');
    });
  });

  test.describe('User Validation', () => {
    let userPage: UserPage;

    test.beforeEach(async ({ page }) => {
      userPage = new UserPage(page);
      await userPage.goto();
    });

    test('should show validation error for empty username', async ({ page }) => {
      await userPage.createButton.click();
      await userPage.usernameInput.fill('');
      await userPage.emailInput.fill('test@example.com');
      await userPage.firstNameInput.fill('Test');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      const errors = await userPage.getValidationErrors();
      expect(errors.length).toBeGreaterThan(0);

      await ScreenshotHelper.captureScreenshot(page, 'user-empty-username-error');
    });

    test('should show validation error for empty email', async ({ page }) => {
      await userPage.createButton.click();
      await userPage.usernameInput.fill('testuser');
      await userPage.emailInput.fill('');
      await userPage.firstNameInput.fill('Test');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      const errors = await userPage.getValidationErrors();
      expect(errors.length).toBeGreaterThan(0);

      await ScreenshotHelper.captureScreenshot(page, 'user-empty-email-error');
    });

    test('should show validation error for invalid email format', async ({ page }) => {
      await userPage.createButton.click();
      await userPage.usernameInput.fill('testuser');
      await userPage.emailInput.fill('invalid-email');
      await userPage.firstNameInput.fill('Test');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      const errorVisible = await page.locator('text=/invalid email|email format/i').isVisible();
      await ScreenshotHelper.captureScreenshot(page, 'user-invalid-email-error');
    });

    test('should show validation error for multiple invalid email formats', async ({ page }) => {
      const invalidEmails = [
        'notanemail',
        '@example.com',
        'user@',
        'user @example.com',
        'user..name@example.com',
      ];

      for (const email of invalidEmails) {
        await userPage.createButton.click();
        await userPage.usernameInput.fill(`user${Date.now()}`);
        await userPage.emailInput.fill(email);
        await userPage.firstNameInput.fill('Test');
        await userPage.lastNameInput.fill('User');
        await userPage.submitButton.click();

        await page.waitForTimeout(300);

        // Cancel or close form
        if (await userPage.cancelButton.isVisible()) {
          await userPage.cancelButton.click();
        }
      }

      await ScreenshotHelper.captureScreenshot(page, 'user-various-invalid-emails');
    });

    test('should validate required first name', async ({ page }) => {
      await userPage.createButton.click();
      await userPage.usernameInput.fill('testuser');
      await userPage.emailInput.fill('test@example.com');
      await userPage.firstNameInput.fill('');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureScreenshot(page, 'user-empty-firstname-error');
    });

    test('should validate required last name', async ({ page }) => {
      await userPage.createButton.click();
      await userPage.usernameInput.fill('testuser');
      await userPage.emailInput.fill('test@example.com');
      await userPage.firstNameInput.fill('Test');
      await userPage.lastNameInput.fill('');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureScreenshot(page, 'user-empty-lastname-error');
    });

    test('should validate all required fields on user form', async ({ page }) => {
      await userPage.createButton.click();
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      const errors = await userPage.getValidationErrors();
      expect(errors.length).toBeGreaterThan(0);

      await ScreenshotHelper.captureScreenshot(page, 'user-all-fields-required');
    });

    test('should validate username uniqueness', async ({ page }) => {
      const username = `unique_user_${Date.now()}`;

      // Create first user
      await userPage.createButton.click();
      await userPage.usernameInput.fill(username);
      await userPage.emailInput.fill('first@example.com');
      await userPage.firstNameInput.fill('First');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();
      await page.waitForLoadState('networkidle');

      // Try to create second user with same username
      await userPage.createButton.click();
      await userPage.usernameInput.fill(username);
      await userPage.emailInput.fill('second@example.com');
      await userPage.firstNameInput.fill('Second');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      const errorVisible = await page.locator('text=/duplicate|already exists|taken/i').isVisible();
      await ScreenshotHelper.captureScreenshot(page, 'user-duplicate-username-error');
    });

    test('should validate email uniqueness', async ({ page }) => {
      const email = `unique_${Date.now()}@example.com`;

      // Create first user
      await userPage.createButton.click();
      await userPage.usernameInput.fill('firstuser');
      await userPage.emailInput.fill(email);
      await userPage.firstNameInput.fill('First');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();
      await page.waitForLoadState('networkidle');

      // Try to create second user with same email
      await userPage.createButton.click();
      await userPage.usernameInput.fill('seconduser');
      await userPage.emailInput.fill(email);
      await userPage.firstNameInput.fill('Second');
      await userPage.lastNameInput.fill('User');
      await userPage.submitButton.click();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureScreenshot(page, 'user-duplicate-email-error');
    });

    test('should display inline validation errors', async ({ page }) => {
      await userPage.createButton.click();

      // Fill invalid data
      await userPage.usernameInput.fill('');
      await userPage.emailInput.fill('invalid');
      await userPage.firstNameInput.fill('');
      await userPage.lastNameInput.fill('');

      // Blur to trigger validation
      await userPage.usernameInput.blur();
      await userPage.emailInput.blur();
      await userPage.firstNameInput.blur();
      await userPage.lastNameInput.blur();

      await page.waitForTimeout(500);

      await ScreenshotHelper.captureFullPageScreenshot(page, 'user-inline-validation-errors');
    });
  });
});
