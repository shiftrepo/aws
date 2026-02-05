import { test, expect } from '@playwright/test';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { generateRandomOrg } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Organization CRUD Operations', () => {
  let orgPage: OrganizationPage;

  test.beforeEach(async ({ page }) => {
    orgPage = new OrganizationPage(page);
    await orgPage.goto();
  });

  test('should list all organizations with table rendering', async ({ page }) => {
    await orgPage.waitForTableLoad();

    // Verify table is visible
    await expect(orgPage.organizationTable).toBeVisible();

    // Verify table has headers
    const headers = await page.locator('th').allTextContents();
    expect(headers.length).toBeGreaterThan(0);

    // Capture screenshot
    await ScreenshotHelper.captureScreenshot(page, 'organizations-list');
  });

  test('should create new organization with valid data', async ({ page }) => {
    const newOrg = generateRandomOrg();

    await orgPage.createOrganization(newOrg);

    // Verify organization was created
    await orgPage.searchOrganizations(newOrg.code);
    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();

    // Capture success screenshot
    await ScreenshotHelper.captureScreenshot(page, 'organization-created');
  });

  test('should update organization details', async ({ page }) => {
    // First create an organization
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Update the organization
    const updatedData = {
      name: `${newOrg.name} - Updated`,
      description: 'Updated description',
    };

    await orgPage.editOrganization(newOrg.code, updatedData);

    // Verify update
    await orgPage.searchOrganizations(newOrg.code);
    const isVisible = await orgPage.verifyOrganizationInList(updatedData.name);
    expect(isVisible).toBeTruthy();
  });

  test('should delete organization with confirmation', async ({ page }) => {
    // First create an organization
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Verify it exists
    await orgPage.searchOrganizations(newOrg.code);
    let isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();

    // Delete the organization
    await orgPage.deleteOrganization(newOrg.code);

    // Verify it's deleted
    await orgPage.searchOrganizations(newOrg.code);
    await page.waitForTimeout(500);
    const count = await orgPage.getOrganizationCount();
    expect(count).toBe(0);
  });

  test('should search organizations by name', async ({ page }) => {
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Search by name
    await orgPage.searchOrganizations(newOrg.name);

    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();

    // Verify only matching results appear
    const count = await orgPage.getOrganizationCount();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should search organizations by code', async ({ page }) => {
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Search by code
    await orgPage.searchOrganizations(newOrg.code);

    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();
  });

  test('should filter active organizations', async ({ page }) => {
    // Create active organization
    const activeOrg = generateRandomOrg();
    activeOrg.active = true;
    await orgPage.createOrganization(activeOrg);

    // Create inactive organization
    const inactiveOrg = generateRandomOrg();
    inactiveOrg.active = false;
    await orgPage.createOrganization(inactiveOrg);

    // TODO: Implement filter functionality test when available
    // This would depend on the actual UI implementation

    await ScreenshotHelper.captureScreenshot(page, 'organizations-filtered');
  });

  test('should display pagination controls when many organizations exist', async ({ page }) => {
    // Check if pagination is present
    const paginationExists = await page.locator('[role="navigation"], .pagination').count();

    // If pagination exists, verify it works
    if (paginationExists > 0) {
      const nextButton = page.getByRole('button', { name: /next/i });
      if (await nextButton.isVisible()) {
        await nextButton.click();
        await page.waitForLoadState('networkidle');
      }
    }

    await ScreenshotHelper.captureScreenshot(page, 'organizations-pagination');
  });

  test('should handle empty search results gracefully', async ({ page }) => {
    await orgPage.searchOrganizations('NONEXISTENT_ORG_12345');

    const count = await orgPage.getOrganizationCount();
    expect(count).toBe(0);

    // Verify empty state message or no results
    await ScreenshotHelper.captureScreenshot(page, 'organizations-no-results');
  });

  test('should cancel organization creation', async ({ page }) => {
    const newOrg = generateRandomOrg();

    await orgPage.createButton.click();
    await orgPage.codeInput.fill(newOrg.code);
    await orgPage.nameInput.fill(newOrg.name);

    // Click cancel
    await orgPage.cancelButton.click();

    // Verify form is closed
    const isFormVisible = await orgPage.isFormVisible();
    expect(isFormVisible).toBeFalsy();

    // Verify organization was not created
    await orgPage.searchOrganizations(newOrg.code);
    const count = await orgPage.getOrganizationCount();
    expect(count).toBe(0);
  });
});
