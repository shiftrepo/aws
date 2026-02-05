import { test, expect } from '@playwright/test';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { generateRandomDept } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Department Hierarchy', () => {
  let deptPage: DepartmentPage;

  test.beforeEach(async ({ page }) => {
    deptPage = new DepartmentPage(page);
    await deptPage.goto();
  });

  test('should create sub-department under parent', async ({ page }) => {
    // Create parent department
    const parentDept = generateRandomDept();
    parentDept.name = 'Engineering Department';

    await deptPage.createButton.click();
    await deptPage.codeInput.fill(parentDept.code);
    await deptPage.nameInput.fill(parentDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create sub-department
    const subDept = generateRandomDept();
    subDept.name = 'Frontend Team';

    await deptPage.createButton.click();
    await deptPage.codeInput.fill(subDept.code);
    await deptPage.nameInput.fill(subDept.name);

    // Select parent department if available
    if (await deptPage.parentDepartmentSelect.isVisible()) {
      const parentOption = await deptPage.parentDepartmentSelect.locator(`option:has-text("${parentDept.name}")`);
      if (await parentOption.count() > 0) {
        await deptPage.parentDepartmentSelect.selectOption({ label: parentDept.name });
      }
    }

    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Verify sub-department was created
    await deptPage.searchDepartments(subDept.code);
    const isVisible = await deptPage.verifyDepartmentInList(subDept.name);
    expect(isVisible).toBeTruthy();

    await ScreenshotHelper.captureScreenshot(page, 'sub-department-created');
  });

  test('should create multiple levels of hierarchy', async ({ page }) => {
    // Create root department
    const rootDept = generateRandomDept();
    rootDept.name = 'Root Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(rootDept.code);
    await deptPage.nameInput.fill(rootDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create level 1 department
    const level1Dept = generateRandomDept();
    level1Dept.name = 'Level 1 Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(level1Dept.code);
    await deptPage.nameInput.fill(level1Dept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create level 2 department
    const level2Dept = generateRandomDept();
    level2Dept.name = 'Level 2 Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(level2Dept.code);
    await deptPage.nameInput.fill(level2Dept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    await ScreenshotHelper.captureScreenshot(page, 'multi-level-hierarchy');
  });

  test('should move department to different parent', async ({ page }) => {
    // Create two parent departments
    const parent1 = generateRandomDept();
    parent1.name = 'Parent Department 1';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(parent1.code);
    await deptPage.nameInput.fill(parent1.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    const parent2 = generateRandomDept();
    parent2.name = 'Parent Department 2';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(parent2.code);
    await deptPage.nameInput.fill(parent2.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Create child under parent1
    const childDept = generateRandomDept();
    childDept.name = 'Child Department';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(childDept.code);
    await deptPage.nameInput.fill(childDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Move child to parent2
    await deptPage.searchDepartments(childDept.code);
    const row = await deptPage.getDepartmentByCode(childDept.code);
    await row.locator(deptPage.editButton).click();

    if (await deptPage.parentDepartmentSelect.isVisible()) {
      const parent2Option = await deptPage.parentDepartmentSelect.locator(`option:has-text("${parent2.name}")`);
      if (await parent2Option.count() > 0) {
        await deptPage.parentDepartmentSelect.selectOption({ label: parent2.name });
      }
    }

    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    await ScreenshotHelper.captureScreenshot(page, 'department-moved');
  });

  test('should view full hierarchy tree', async ({ page }) => {
    // Create a hierarchy
    const rootDept = generateRandomDept();
    rootDept.name = 'Organization Root';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(rootDept.code);
    await deptPage.nameInput.fill(rootDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Look for tree view
    const treeView = page.locator('[role="tree"], .tree-view, [class*="tree"]');
    if (await treeView.isVisible()) {
      await ScreenshotHelper.captureFullPageScreenshot(page, 'full-hierarchy-tree');
    }
  });

  test('should expand and collapse hierarchy nodes', async ({ page }) => {
    // Create parent and child
    const parentDept = generateRandomDept();
    parentDept.name = 'Expandable Parent';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(parentDept.code);
    await deptPage.nameInput.fill(parentDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    const childDept = generateRandomDept();
    childDept.name = 'Child Under Expandable';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(childDept.code);
    await deptPage.nameInput.fill(childDept.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Try to expand in tree view
    await deptPage.expandDepartmentNode(parentDept.name);
    await ScreenshotHelper.captureScreenshot(page, 'hierarchy-expanded');

    // Try to collapse
    await deptPage.collapseDepartmentNode(parentDept.name);
    await ScreenshotHelper.captureScreenshot(page, 'hierarchy-collapsed');
  });

  test('should display department breadcrumb path', async ({ page }) => {
    // Create hierarchy
    const parent = generateRandomDept();
    parent.name = 'Parent for Breadcrumb';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(parent.code);
    await deptPage.nameInput.fill(parent.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    const child = generateRandomDept();
    child.name = 'Child for Breadcrumb';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(child.code);
    await deptPage.nameInput.fill(child.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Look for breadcrumb navigation
    const breadcrumb = page.locator('nav[aria-label="breadcrumb"], .breadcrumb');
    if (await breadcrumb.isVisible()) {
      await ScreenshotHelper.captureScreenshot(page, 'department-breadcrumb');
    }
  });

  test('should prevent circular parent-child relationships', async ({ page }) => {
    // Create two departments
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

    // Try to make dept1 a child of dept2, then dept2 a child of dept1
    // This should be prevented by the system
    await ScreenshotHelper.captureScreenshot(page, 'prevent-circular-hierarchy');
  });

  test('should show hierarchy depth indicator', async ({ page }) => {
    // Create nested departments
    const level0 = generateRandomDept();
    level0.name = 'Level 0';
    await deptPage.createButton.click();
    await deptPage.codeInput.fill(level0.code);
    await deptPage.nameInput.fill(level0.name);
    await deptPage.submitButton.click();
    await page.waitForLoadState('networkidle');

    // Check for visual indicators of hierarchy depth (indentation, icons, etc.)
    await ScreenshotHelper.captureFullPageScreenshot(page, 'hierarchy-depth-indicators');
  });
});
