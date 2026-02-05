import { Page, Locator, expect } from '@playwright/test';
import { Department } from '../fixtures/test-data';

export class DepartmentPage {
  readonly page: Page;
  readonly departmentsTab: Locator;
  readonly createButton: Locator;
  readonly codeInput: Locator;
  readonly nameInput: Locator;
  readonly descriptionInput: Locator;
  readonly organizationSelect: Locator;
  readonly parentDepartmentSelect: Locator;
  readonly activeCheckbox: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly searchInput: Locator;
  readonly departmentTable: Locator;
  readonly deleteButton: Locator;
  readonly editButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly treeView: Locator;
  readonly expandButton: Locator;
  readonly collapseButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.departmentsTab = page.getByRole('tab', { name: /departments/i });
    this.createButton = page.getByRole('button', { name: /create department|new department/i });
    this.codeInput = page.locator('input[name="code"], input[placeholder*="code" i]');
    this.nameInput = page.locator('input[name="name"], input[placeholder*="name" i]');
    this.descriptionInput = page.locator('input[name="description"], textarea[name="description"]');
    this.organizationSelect = page.locator('select[name="organizationId"], select[name="organization"]');
    this.parentDepartmentSelect = page.locator('select[name="parentId"], select[name="parent"]');
    this.activeCheckbox = page.locator('input[type="checkbox"][name="active"]');
    this.submitButton = page.getByRole('button', { name: /submit|save|create/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.searchInput = page.locator('input[placeholder*="search" i]');
    this.departmentTable = page.locator('table, [role="table"]');
    this.deleteButton = page.getByRole('button', { name: /delete/i });
    this.editButton = page.getByRole('button', { name: /edit/i });
    this.confirmDeleteButton = page.getByRole('button', { name: /confirm|yes|delete/i });
    this.treeView = page.locator('[class*="tree"], [role="tree"]');
    this.expandButton = page.locator('button[aria-label*="expand" i]');
    this.collapseButton = page.locator('button[aria-label*="collapse" i]');
  }

  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.departmentsTab.click();
    await this.page.waitForLoadState('networkidle');
  }

  async createDepartment(data: Department): Promise<void> {
    await this.createButton.click();
    await this.codeInput.fill(data.code);
    await this.nameInput.fill(data.name);

    if (data.description) {
      await this.descriptionInput.fill(data.description);
    }

    if (data.organizationId !== undefined) {
      await this.organizationSelect.selectOption({ value: data.organizationId.toString() });
    }

    if (data.parentId !== undefined) {
      await this.parentDepartmentSelect.selectOption({ value: data.parentId.toString() });
    }

    if (data.active !== undefined) {
      const isChecked = await this.activeCheckbox.isChecked();
      if (isChecked !== data.active) {
        await this.activeCheckbox.click();
      }
    }

    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async editDepartment(code: string, data: Partial<Department>): Promise<void> {
    await this.searchDepartments(code);
    const row = this.page.locator(`tr:has-text("${code}")`);
    await row.locator(this.editButton).click();

    if (data.code) {
      await this.codeInput.fill(data.code);
    }
    if (data.name) {
      await this.nameInput.fill(data.name);
    }
    if (data.description !== undefined) {
      await this.descriptionInput.fill(data.description);
    }
    if (data.parentId !== undefined) {
      await this.parentDepartmentSelect.selectOption({ value: data.parentId.toString() });
    }
    if (data.active !== undefined) {
      const isChecked = await this.activeCheckbox.isChecked();
      if (isChecked !== data.active) {
        await this.activeCheckbox.click();
      }
    }

    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async deleteDepartment(code: string): Promise<void> {
    await this.searchDepartments(code);
    const row = this.page.locator(`tr:has-text("${code}")`);
    await row.locator(this.deleteButton).click();
    await this.confirmDeleteButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async searchDepartments(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500); // Wait for debounce
    await this.page.waitForLoadState('networkidle');
  }

  async assignParentDepartment(deptCode: string, parentCode: string): Promise<void> {
    await this.searchDepartments(deptCode);
    const row = this.page.locator(`tr:has-text("${deptCode}")`);
    await row.locator(this.editButton).click();

    // Find parent department by code and select it
    const parentRow = await this.page.locator(`tr:has-text("${parentCode}")`).first();
    const parentId = await parentRow.getAttribute('data-id');

    if (parentId) {
      await this.parentDepartmentSelect.selectOption({ value: parentId });
    }

    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async expandDepartmentNode(deptName: string): Promise<void> {
    const node = this.page.locator(`[role="treeitem"]:has-text("${deptName}")`);
    const expandBtn = node.locator(this.expandButton);

    if (await expandBtn.isVisible()) {
      await expandBtn.click();
      await this.page.waitForTimeout(300);
    }
  }

  async collapseDepartmentNode(deptName: string): Promise<void> {
    const node = this.page.locator(`[role="treeitem"]:has-text("${deptName}")`);
    const collapseBtn = node.locator(this.collapseButton);

    if (await collapseBtn.isVisible()) {
      await collapseBtn.click();
      await this.page.waitForTimeout(300);
    }
  }

  async getDepartmentCount(): Promise<number> {
    const rows = await this.departmentTable.locator('tbody tr').count();
    return rows;
  }

  async verifyDepartmentInList(name: string): Promise<boolean> {
    const row = this.page.locator(`tr:has-text("${name}")`);
    return await row.isVisible();
  }

  async getDepartmentByCode(code: string): Promise<Locator> {
    return this.page.locator(`tr:has-text("${code}")`);
  }

  async verifyDepartmentInTree(name: string): Promise<boolean> {
    const treeNode = this.page.locator(`[role="treeitem"]:has-text("${name}")`);
    return await treeNode.isVisible();
  }

  async getChildDepartments(parentName: string): Promise<string[]> {
    await this.expandDepartmentNode(parentName);
    const parentNode = this.page.locator(`[role="treeitem"]:has-text("${parentName}")`);
    const children = await parentNode.locator('[role="treeitem"]').allTextContents();
    return children;
  }

  async verifyValidationError(message: string): Promise<void> {
    const errorElement = this.page.locator(`text="${message}"`);
    await expect(errorElement).toBeVisible();
  }

  async waitForTableLoad(): Promise<void> {
    await this.departmentTable.waitFor({ state: 'visible' });
    await this.page.waitForLoadState('networkidle');
  }
}
