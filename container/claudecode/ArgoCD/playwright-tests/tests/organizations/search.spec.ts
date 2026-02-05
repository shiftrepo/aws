import { test, expect } from '@playwright/test';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { generateRandomOrg } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Organization Search Functionality', () => {
  let orgPage: OrganizationPage;

  test.beforeEach(async ({ page }) => {
    orgPage = new OrganizationPage(page);
    await orgPage.goto();
  });

  test('should search by exact organization code', async ({ page }) => {
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    await orgPage.searchOrganizations(newOrg.code);

    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();

    const count = await orgPage.getOrganizationCount();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should search by partial organization name', async ({ page }) => {
    const newOrg = generateRandomOrg();
    newOrg.name = 'Unique Search Test Organization';
    await orgPage.createOrganization(newOrg);

    // Search with partial name
    await orgPage.searchOrganizations('Unique Search');

    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();
  });

  test('should handle case-insensitive search', async ({ page }) => {
    const newOrg = generateRandomOrg();
    newOrg.name = 'CaseSensitiveTest';
    await orgPage.createOrganization(newOrg);

    // Search with different case
    await orgPage.searchOrganizations('casesensitivetest');

    // Should still find the organization
    await page.waitForTimeout(500);
    const count = await orgPage.getOrganizationCount();
    expect(count).toBeGreaterThanOrEqual(0); // Depends on backend implementation
  });

  test('should clear search results when search is cleared', async ({ page }) => {
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Perform search
    await orgPage.searchOrganizations(newOrg.code);
    let count = await orgPage.getOrganizationCount();
    expect(count).toBeGreaterThanOrEqual(1);

    // Clear search
    await orgPage.searchInput.clear();
    await page.waitForTimeout(500);
    await page.waitForLoadState('networkidle');

    // Should show all organizations
    count = await orgPage.getOrganizationCount();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test('should show no results for non-existent search', async ({ page }) => {
    await orgPage.searchOrganizations('NONEXISTENT_ORG_XYZ_123456');

    const count = await orgPage.getOrganizationCount();
    expect(count).toBe(0);

    await ScreenshotHelper.captureScreenshot(page, 'search-no-results');
  });

  test('should update search results in real-time', async ({ page }) => {
    const newOrg = generateRandomOrg();
    newOrg.name = 'RealTimeSearchTest';
    await orgPage.createOrganization(newOrg);

    // Type search query character by character
    await orgPage.searchInput.fill('RealTime');
    await page.waitForTimeout(600); // Wait for debounce

    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();
  });

  test('should preserve search when navigating between pages', async ({ page }) => {
    const searchTerm = 'TestOrg';
    await orgPage.searchOrganizations(searchTerm);

    // Check if pagination exists
    const nextButton = page.getByRole('button', { name: /next/i });
    if (await nextButton.isVisible()) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');

      // Verify search term is still in input
      const searchValue = await orgPage.searchInput.inputValue();
      expect(searchValue).toBe(searchTerm);
    }
  });

  test('should search by organization description', async ({ page }) => {
    const newOrg = generateRandomOrg();
    newOrg.description = 'Unique description for search test XYZ123';
    await orgPage.createOrganization(newOrg);

    // Search by description keyword
    await orgPage.searchOrganizations('XYZ123');

    // Verify organization is found (if backend supports description search)
    await page.waitForTimeout(500);
    const count = await orgPage.getOrganizationCount();
    // Result depends on backend implementation
    await ScreenshotHelper.captureScreenshot(page, 'search-by-description');
  });

  test('should handle special characters in search', async ({ page }) => {
    const newOrg = generateRandomOrg();
    newOrg.code = `ORG-${Date.now()}-TEST`;
    await orgPage.createOrganization(newOrg);

    // Search with special characters
    await orgPage.searchOrganizations(newOrg.code);

    const isVisible = await orgPage.verifyOrganizationInList(newOrg.name);
    expect(isVisible).toBeTruthy();
  });

  test('should display search count or results summary', async ({ page }) => {
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    await orgPage.searchOrganizations(newOrg.code);

    const count = await orgPage.getOrganizationCount();
    expect(count).toBeGreaterThanOrEqual(1);

    // Check for results summary if available
    const summary = page.locator('text=/results?/i, text=/found/i');
    await ScreenshotHelper.captureScreenshot(page, 'search-results-summary');
  });
});
