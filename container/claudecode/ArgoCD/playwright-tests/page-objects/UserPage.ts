import { Page, Locator, expect } from '@playwright/test';
import { User } from '../fixtures/test-data';

export class UserPage {
  readonly page: Page;
  readonly usersTab: Locator;
  readonly createButton: Locator;
  readonly usernameInput: Locator;
  readonly emailInput: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly departmentSelect: Locator;
  readonly activeCheckbox: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly searchInput: Locator;
  readonly userTable: Locator;
  readonly deleteButton: Locator;
  readonly editButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly assignButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usersTab = page.getByRole('tab', { name: /users|employees/i });
    this.createButton = page.getByRole('button', { name: /create user|new user|add user/i });
    this.usernameInput = page.locator('input[name="username"], input[placeholder*="username" i]');
    this.emailInput = page.locator('input[name="email"], input[placeholder*="email" i]');
    this.firstNameInput = page.locator('input[name="firstName"], input[placeholder*="first name" i]');
    this.lastNameInput = page.locator('input[name="lastName"], input[placeholder*="last name" i]');
    this.departmentSelect = page.locator('select[name="departmentId"], select[name="department"]');
    this.activeCheckbox = page.locator('input[type="checkbox"][name="active"]');
    this.submitButton = page.getByRole('button', { name: /submit|save|create/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
    this.searchInput = page.locator('input[placeholder*="search" i]');
    this.userTable = page.locator('table, [role="table"]');
    this.deleteButton = page.getByRole('button', { name: /delete/i });
    this.editButton = page.getByRole('button', { name: /edit/i });
    this.confirmDeleteButton = page.getByRole('button', { name: /confirm|yes|delete/i });
    this.assignButton = page.getByRole('button', { name: /assign/i });
  }

  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.usersTab.click();
    await this.page.waitForLoadState('networkidle');
  }

  async createUser(data: User): Promise<void> {
    await this.createButton.click();
    await this.usernameInput.fill(data.username);
    await this.emailInput.fill(data.email);
    await this.firstNameInput.fill(data.firstName);
    await this.lastNameInput.fill(data.lastName);

    if (data.departmentId !== undefined) {
      await this.departmentSelect.selectOption({ value: data.departmentId.toString() });
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

  async editUser(username: string, data: Partial<User>): Promise<void> {
    await this.searchUsers(username);
    const row = this.page.locator(`tr:has-text("${username}")`);
    await row.locator(this.editButton).click();

    if (data.username) {
      await this.usernameInput.fill(data.username);
    }
    if (data.email) {
      await this.emailInput.fill(data.email);
    }
    if (data.firstName) {
      await this.firstNameInput.fill(data.firstName);
    }
    if (data.lastName) {
      await this.lastNameInput.fill(data.lastName);
    }
    if (data.departmentId !== undefined) {
      await this.departmentSelect.selectOption({ value: data.departmentId.toString() });
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

  async deleteUser(username: string): Promise<void> {
    await this.searchUsers(username);
    const row = this.page.locator(`tr:has-text("${username}")`);
    await row.locator(this.deleteButton).click();
    await this.confirmDeleteButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async searchUsers(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500); // Wait for debounce
    await this.page.waitForLoadState('networkidle');
  }

  async assignToDepartment(username: string, departmentId: number): Promise<void> {
    await this.searchUsers(username);
    const row = this.page.locator(`tr:has-text("${username}")`);
    await row.locator(this.editButton).click();
    await this.departmentSelect.selectOption({ value: departmentId.toString() });
    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async getUserCount(): Promise<number> {
    const rows = await this.userTable.locator('tbody tr').count();
    return rows;
  }

  async verifyUserInList(username: string): Promise<boolean> {
    const row = this.page.locator(`tr:has-text("${username}")`);
    return await row.isVisible();
  }

  async getUserByUsername(username: string): Promise<Locator> {
    return this.page.locator(`tr:has-text("${username}")`);
  }

  async getUsersByDepartment(departmentName: string): Promise<string[]> {
    const rows = await this.page.locator(`tr:has-text("${departmentName}")`).all();
    const usernames: string[] = [];

    for (const row of rows) {
      const username = await row.locator('td:first-child').textContent();
      if (username) {
        usernames.push(username.trim());
      }
    }

    return usernames;
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
    await this.usernameInput.clear();
    await this.emailInput.clear();
    await this.firstNameInput.clear();
    await this.lastNameInput.clear();
  }

  async isFormVisible(): Promise<boolean> {
    return await this.submitButton.isVisible();
  }

  async waitForTableLoad(): Promise<void> {
    await this.userTable.waitFor({ state: 'visible' });
    await this.page.waitForLoadState('networkidle');
  }

  async verifyUserDetails(username: string, expectedData: Partial<User>): Promise<void> {
    const row = await this.getUserByUsername(username);
    await expect(row).toBeVisible();

    if (expectedData.email) {
      await expect(row.locator(`text="${expectedData.email}"`)).toBeVisible();
    }
    if (expectedData.firstName) {
      await expect(row.locator(`text="${expectedData.firstName}"`)).toBeVisible();
    }
    if (expectedData.lastName) {
      await expect(row.locator(`text="${expectedData.lastName}"`)).toBeVisible();
    }
  }
}
