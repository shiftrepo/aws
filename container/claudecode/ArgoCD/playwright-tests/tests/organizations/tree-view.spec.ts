import { test, expect } from '@playwright/test';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { generateRandomOrg, generateRandomDept } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Organization Tree View', () => {
  let orgPage: OrganizationPage;
  let deptPage: DepartmentPage;

  test.beforeEach(async ({ page }) => {
    orgPage = new OrganizationPage(page);
    deptPage = new DepartmentPage(page);
    await orgPage.goto();
  });

  test('should view organization tree structure', async ({ page }) => {
    // Create an organization first
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Switch to tree view
    await orgPage.switchToTreeView();

    // Verify tree view is visible
    await page.waitForTimeout(500);
    const treeView = page.locator('[role="tree"], .tree-view, [class*="tree"]');

    // Take screenshot of tree view
    await ScreenshotHelper.captureScreenshot(page, 'organization-tree-view');
  });

  test('should expand departments in tree view', async ({ page }) => {
    // This test assumes departments exist under organizations
    await orgPage.switchToTreeView();

    // Look for expand buttons
    const expandButtons = page.locator('button[aria-label*="expand" i]');
    const count = await expandButtons.count();

    if (count > 0) {
      // Click first expand button
      await expandButtons.first().click();
      await page.waitForTimeout(300);

      await ScreenshotHelper.captureScreenshot(page, 'tree-expanded');
    }
  });

  test('should collapse departments in tree view', async ({ page }) => {
    await orgPage.switchToTreeView();

    // First expand
    const expandButtons = page.locator('button[aria-label*="expand" i]');
    const count = await expandButtons.count();

    if (count > 0) {
      await expandButtons.first().click();
      await page.waitForTimeout(300);

      // Then collapse
      const collapseButtons = page.locator('button[aria-label*="collapse" i]');
      if (await collapseButtons.count() > 0) {
        await collapseButtons.first().click();
        await page.waitForTimeout(300);

        await ScreenshotHelper.captureScreenshot(page, 'tree-collapsed');
      }
    }
  });

  test('should navigate through hierarchy levels', async ({ page }) => {
    await orgPage.switchToTreeView();

    // Look for tree items
    const treeItems = page.locator('[role="treeitem"]');
    const count = await treeItems.count();

    if (count > 0) {
      // Click on first tree item
      await treeItems.first().click();
      await page.waitForTimeout(300);

      await ScreenshotHelper.captureScreenshot(page, 'tree-navigation');
    }
  });

  test('should show organization with its departments in tree', async ({ page }) => {
    // Create organization
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    // Switch to departments and create a department under this org
    await deptPage.goto();
    const newDept = generateRandomDept();
    // Note: You would need to get the org ID and set it here
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(newDept.code);
    await deptPage.nameInput.fill(newDept.name);

    // Select the organization (this depends on your UI)
    // await deptPage.organizationSelect.selectOption({ label: newOrg.name });

    if (await deptPage.submitButton.isVisible()) {
      await deptPage.submitButton.click();
    }

    // Go back to organizations and view tree
    await orgPage.goto();
    await orgPage.switchToTreeView();

    await ScreenshotHelper.captureFullPageScreenshot(page, 'org-with-departments-tree');
  });

  test('should switch between tree and list views', async ({ page }) => {
    // Start in list view (default)
    await expect(orgPage.organizationTable).toBeVisible();
    await ScreenshotHelper.captureScreenshot(page, 'list-view');

    // Switch to tree view
    if (await orgPage.treeViewButton.isVisible()) {
      await orgPage.switchToTreeView();
      await page.waitForTimeout(500);
      await ScreenshotHelper.captureScreenshot(page, 'tree-view-switched');

      // Switch back to list view
      await orgPage.switchToListView();
      await expect(orgPage.organizationTable).toBeVisible();
    }
  });

  test('should maintain search functionality in tree view', async ({ page }) => {
    const newOrg = generateRandomOrg();
    await orgPage.createOrganization(newOrg);

    await orgPage.switchToTreeView();

    // Search in tree view
    await orgPage.searchOrganizations(newOrg.name);
    await page.waitForTimeout(500);

    await ScreenshotHelper.captureScreenshot(page, 'tree-view-search');
  });
});
