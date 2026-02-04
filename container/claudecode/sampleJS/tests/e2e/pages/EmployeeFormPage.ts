import { Page, Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class EmployeeFormPage extends BasePage {
  readonly pageTitle: Locator;
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly departmentInput: Locator;
  readonly positionInput: Locator;
  readonly hireDateInput: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;
  readonly errorMessage: Locator;
  readonly form: Locator;

  constructor(page: Page) {
    super(page);
    this.pageTitle = page.getByTestId('page-title');
    this.nameInput = page.getByTestId('input-name');
    this.emailInput = page.getByTestId('input-email');
    this.departmentInput = page.getByTestId('input-department');
    this.positionInput = page.getByTestId('input-position');
    this.hireDateInput = page.getByTestId('input-hire-date');
    this.submitButton = page.getByTestId('submit-button');
    this.cancelButton = page.getByTestId('cancel-button');
    this.errorMessage = page.getByTestId('error-message');
    this.form = page.getByTestId('employee-form');
  }

  async navigateToNew() {
    await this.goto('/employees/new');
    await this.waitForLoadState();
  }

  async navigateToEdit(id: string) {
    await this.goto(`/employees/${id}/edit`);
    await this.waitForLoadState();
  }

  async fillName(name: string) {
    await this.nameInput.fill(name);
  }

  async fillEmail(email: string) {
    await this.emailInput.fill(email);
  }

  async fillDepartment(department: string) {
    await this.departmentInput.fill(department);
  }

  async fillPosition(position: string) {
    await this.positionInput.fill(position);
  }

  async fillHireDate(date: string) {
    await this.hireDateInput.fill(date);
  }

  async fillForm(data: {
    name: string;
    email: string;
    department: string;
    position: string;
    hireDate: string;
  }) {
    await this.fillName(data.name);
    await this.fillEmail(data.email);
    await this.fillDepartment(data.department);
    await this.fillPosition(data.position);
    await this.fillHireDate(data.hireDate);
  }

  async submit() {
    await this.submitButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }

  async getNameValue(): Promise<string> {
    return await this.nameInput.inputValue();
  }

  async getEmailValue(): Promise<string> {
    return await this.emailInput.inputValue();
  }

  async getDepartmentValue(): Promise<string> {
    return await this.departmentInput.inputValue();
  }

  async getPositionValue(): Promise<string> {
    return await this.positionInput.inputValue();
  }

  async getHireDateValue(): Promise<string> {
    return await this.hireDateInput.inputValue();
  }

  async hasFieldError(fieldName: string): Promise<boolean> {
    const errorLocator = this.page.locator(`[data-testid*="${fieldName}"][data-testid*="error"]`);
    return await errorLocator.isVisible();
  }
}
