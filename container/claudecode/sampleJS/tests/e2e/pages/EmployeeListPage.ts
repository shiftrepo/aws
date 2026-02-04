import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class EmployeeListPage extends BasePage {
  readonly pageTitle: Locator;
  readonly addEmployeeButton: Locator;
  readonly table: Locator;
  readonly loadingMessage: Locator;
  readonly errorMessage: Locator;
  readonly emptyMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.pageTitle = page.getByTestId('page-title');
    this.addEmployeeButton = page.getByTestId('add-employee-button');
    this.table = page.getByTestId('table');
    this.loadingMessage = page.getByTestId('loading');
    this.errorMessage = page.getByTestId('error-message');
    this.emptyMessage = page.getByTestId('table-empty');
  }

  async navigate() {
    await this.goto('/');
    await this.waitForLoadState();
  }

  async clickAddEmployee() {
    await this.addEmployeeButton.click();
  }

  async getEmployeeRow(employeeId: string): Promise<Locator> {
    return this.page.getByTestId(`table-row-${employeeId}`);
  }

  async clickEditButton(employeeId: string) {
    const editButton = this.page.getByTestId(`edit-button-${employeeId}`);
    await editButton.click();
  }

  async clickDeleteButton(employeeId: string) {
    const deleteButton = this.page.getByTestId(`delete-button-${employeeId}`);

    this.page.once('dialog', (dialog) => {
      dialog.accept();
    });

    await deleteButton.click();
  }

  async getEmployeeCount(): Promise<number> {
    const rows = await this.page.locator('[data-testid^="table-row-"]').count();
    return rows;
  }

  async isEmployeeVisible(name: string): Promise<boolean> {
    return await this.page.getByText(name).isVisible();
  }

  async waitForTableLoad() {
    await this.page.waitForSelector('[data-testid="table"], [data-testid="table-empty"]');
  }
}
