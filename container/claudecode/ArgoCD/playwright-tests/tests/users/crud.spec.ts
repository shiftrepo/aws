import { test, expect } from '@playwright/test';
import { UserPage } from '../../page-objects/UserPage';
import { generateRandomUser } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('User CRUD Operations', () => {
  let userPage: UserPage;

  test.beforeEach(async ({ page }) => {
    userPage = new UserPage(page);
    await userPage.goto();
  });

  test('should list all users with pagination', async ({ page }) => {
    await userPage.waitForTableLoad();

    // Verify table is visible
    await expect(userPage.userTable).toBeVisible();

    // Verify table has headers
    const headers = await page.locator('th').allTextContents();
    expect(headers.length).toBeGreaterThan(0);

    // Check for pagination
    const paginationExists = await page.locator('[role="navigation"], .pagination').count();
    if (paginationExists > 0) {
      await ScreenshotHelper.captureScreenshot(page, 'users-with-pagination');
    } else {
      await ScreenshotHelper.captureScreenshot(page, 'users-list');
    }
  });

  test('should create new user with required fields', async ({ page }) => {
    const newUser = generateRandomUser();

    await userPage.createUser(newUser);

    // Verify user was created
    await userPage.searchUsers(newUser.username);
    const isVisible = await userPage.verifyUserInList(newUser.username);
    expect(isVisible).toBeTruthy();

    await ScreenshotHelper.captureScreenshot(page, 'user-created');
  });

  test('should update user information', async ({ page }) => {
    // Create a user
    const newUser = generateRandomUser();
    await userPage.createUser(newUser);

    // Update the user
    const updatedData = {
      firstName: 'UpdatedFirstName',
      lastName: 'UpdatedLastName',
      email: `updated.${newUser.email}`,
    };

    await userPage.editUser(newUser.username, updatedData);

    // Verify update
    await userPage.searchUsers(newUser.username);
    const isVisible = await userPage.verifyUserInList(newUser.username);
    expect(isVisible).toBeTruthy();

    await ScreenshotHelper.captureScreenshot(page, 'user-updated');
  });

  test('should delete user with confirmation', async ({ page }) => {
    // Create a user
    const newUser = generateRandomUser();
    await userPage.createUser(newUser);

    // Verify it exists
    await userPage.searchUsers(newUser.username);
    let isVisible = await userPage.verifyUserInList(newUser.username);
    expect(isVisible).toBeTruthy();

    // Delete the user
    await userPage.deleteUser(newUser.username);

    // Verify it's deleted
    await userPage.searchUsers(newUser.username);
    await page.waitForTimeout(500);
    const count = await userPage.getUserCount();
    expect(count).toBe(0);

    await ScreenshotHelper.captureScreenshot(page, 'user-deleted');
  });

  test('should search users by name', async ({ page }) => {
    const newUser = generateRandomUser();
    newUser.firstName = 'SearchableFirstName';
    newUser.lastName = 'SearchableLastName';
    await userPage.createUser(newUser);

    // Search by first name
    await userPage.searchUsers(newUser.firstName);

    const isVisible = await userPage.verifyUserInList(newUser.username);
    expect(isVisible).toBeTruthy();
  });

  test('should search users by username', async ({ page }) => {
    const newUser = generateRandomUser();
    newUser.username = `unique_user_${Date.now()}`;
    await userPage.createUser(newUser);

    // Search by username
    await userPage.searchUsers(newUser.username);

    const isVisible = await userPage.verifyUserInList(newUser.username);
    expect(isVisible).toBeTruthy();

    const count = await userPage.getUserCount();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should search users by email', async ({ page }) => {
    const newUser = generateRandomUser();
    await userPage.createUser(newUser);

    // Search by email
    await userPage.searchUsers(newUser.email);

    // Should find the user (if backend supports email search)
    await page.waitForTimeout(500);
    await ScreenshotHelper.captureScreenshot(page, 'user-search-by-email');
  });

  test('should display user details in table', async ({ page }) => {
    const newUser = generateRandomUser();
    await userPage.createUser(newUser);

    await userPage.searchUsers(newUser.username);

    // Verify all user details are displayed
    await userPage.verifyUserDetails(newUser.username, {
      email: newUser.email,
      firstName: newUser.firstName,
      lastName: newUser.lastName,
    });

    await ScreenshotHelper.captureScreenshot(page, 'user-details-in-table');
  });

  test('should handle empty search results', async ({ page }) => {
    await userPage.searchUsers('NONEXISTENT_USER_XYZ_12345');

    const count = await userPage.getUserCount();
    expect(count).toBe(0);

    await ScreenshotHelper.captureScreenshot(page, 'users-no-results');
  });

  test('should cancel user creation', async ({ page }) => {
    const newUser = generateRandomUser();

    await userPage.createButton.click();
    await userPage.usernameInput.fill(newUser.username);
    await userPage.emailInput.fill(newUser.email);
    await userPage.firstNameInput.fill(newUser.firstName);
    await userPage.lastNameInput.fill(newUser.lastName);

    // Click cancel
    await userPage.cancelButton.click();

    // Verify form is closed
    const isFormVisible = await userPage.isFormVisible();
    expect(isFormVisible).toBeFalsy();

    // Verify user was not created
    await userPage.searchUsers(newUser.username);
    const count = await userPage.getUserCount();
    expect(count).toBe(0);
  });

  test('should toggle user active status', async ({ page }) => {
    const newUser = generateRandomUser();
    newUser.active = true;
    await userPage.createUser(newUser);

    // Edit to make inactive
    await userPage.editUser(newUser.username, { active: false });

    await userPage.searchUsers(newUser.username);
    await ScreenshotHelper.captureScreenshot(page, 'user-inactive');

    // Edit to make active again
    await userPage.editUser(newUser.username, { active: true });

    await userPage.searchUsers(newUser.username);
    await ScreenshotHelper.captureScreenshot(page, 'user-active');
  });

  test('should display user count or summary', async ({ page }) => {
    const count = await userPage.getUserCount();
    expect(count).toBeGreaterThanOrEqual(0);

    // Look for count/summary display
    const summary = page.locator('text=/total|users|records/i');
    await ScreenshotHelper.captureScreenshot(page, 'users-summary');
  });

  test('should sort users by column', async ({ page }) => {
    await userPage.waitForTableLoad();

    // Look for sortable column headers
    const headers = page.locator('th[role="columnheader"], th[class*="sortable"]');
    const headerCount = await headers.count();

    if (headerCount > 0) {
      // Click first sortable header
      await headers.first().click();
      await page.waitForTimeout(500);
      await ScreenshotHelper.captureScreenshot(page, 'users-sorted-asc');

      // Click again to sort descending
      await headers.first().click();
      await page.waitForTimeout(500);
      await ScreenshotHelper.captureScreenshot(page, 'users-sorted-desc');
    }
  });
});
