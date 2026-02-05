import { Page, Locator, expect } from '@playwright/test';
import { Organization } from '../fixtures/test-data';

export class OrganizationPage {
  readonly page: Page;
  readonly organizationsTab: Locator;
  readonly createButton: Locator;
  readonly codeInput: Locator;
  readonly nameInput: Locator;
  readonly descriptionInput: Locator;
  readonly activeCheckbox: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly searchInput: Locator;
  readonly organizationTable: Locator;
  readonly deleteButton: Locator;
  readonly editButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly treeViewButton: Locator;
  readonly listViewButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.organizationsTab = page.getByRole('tab', { name: /organizations/i });
    this.createButton = page.getByRole('button', { name: /create organization|new organization/i });
    this.codeInput = page.locator('input[name="code"], input[placeholder*="code" i]');
    this.nameInput = page.locator('input[name="name"], input[placeholder*="name" i]');
    this.descriptionInput = page.locator('input[name="description"], textarea[name="description"]');
    this.activeCheckbox = page.locator('input[type="checkbox"][name="active"]');
    this.submitButton = page.getByRole('button', { name: /submit|save|create/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.searchInput = page.locator('input[placeholder*="search" i]');
    this.organizationTable = page.locator('table, [role="table"]');
    this.deleteButton = page.getByRole('button', { name: /delete/i });
    this.editButton = page.getByRole('button', { name: /edit/i });
    this.confirmDeleteButton = page.getByRole('button', { name: /confirm|yes|delete/i });
    this.treeViewButton = page.getByRole('button', { name: /tree view/i });
    this.listViewButton = page.getByRole('button', { name: /list view/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.organizationsTab.click();
    await this.page.waitForLoadState('networkidle');
  }

  async createOrganization(data: Organization): Promise<void> {
    await this.createButton.click();
    await this.codeInput.fill(data.code);
    await this.nameInput.fill(data.name);

    if (data.description) {
      await this.descriptionInput.fill(data.description);
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

  async editOrganization(code: string, data: Partial<Organization>): Promise<void> {
    await this.searchOrganizations(code);
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
    if (data.active !== undefined) {
      const isChecked = await this.activeCheckbox.isChecked();
      if (isChecked !== data.active) {
        await this.activeCheckbox.click();
      }
    }

    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async deleteOrganization(code: string): Promise<void> {
    await this.searchOrganizations(code);
    const row = this.page.locator(`tr:has-text("${code}")`);
    await row.locator(this.deleteButton).click();
    await this.confirmDeleteButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async searchOrganizations(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500); // Wait for debounce
    await this.page.waitForLoadState('networkidle');
  }

  async getOrganizationCount(): Promise<number> {
    const rows = await this.organizationTable.locator('tbody tr').count();
    return rows;
  }

  async verifyOrganizationInList(name: string): Promise<boolean> {
    const row = this.page.locator(`tr:has-text("${name}")`);
    return await row.isVisible();
  }

  async getOrganizationByCode(code: string): Promise<Locator> {
    return this.page.locator(`tr:has-text("${code}")`);
  }

  async switchToTreeView(): Promise<void> {
    await this.treeViewButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async switchToListView(): Promise<void> {
    await this.listViewButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async verifyValidationError(message: string): Promise<void> {
    const errorElement = this.page.locator(`text="${message}"`);
    await expect(errorElement).toBeVisible();
  }

  async getValidationErrors(): Promise<string[]> {
    const errors = await this.page.locator('.error, .validation-error, [role="alert"]').allTextContents();
    return errors;
  }

  async clearForm(): Promise<void> {
    await this.codeInput.clear();
    await this.nameInput.clear();
    await this.descriptionInput.clear();
  }

  async isFormVisible(): Promise<boolean> {
    return await this.submitButton.isVisible();
  }

  async waitForTableLoad(): Promise<void> {
    await this.organizationTable.waitFor({ state: 'visible' });
    await this.page.waitForLoadState('networkidle');
  }
}
