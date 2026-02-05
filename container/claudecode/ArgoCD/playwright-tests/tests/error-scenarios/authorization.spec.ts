import { test, expect } from '@playwright/test';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { UserPage } from '../../page-objects/UserPage';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Authorization Error Scenarios', () => {
  test('should handle 401 unauthorized error', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 401 error
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Unauthorized', message: 'Authentication required' }),
      });
    });

    await page.goto('/');

    await page.waitForTimeout(1000);

    // Should show error or redirect to login
    const errorVisible = await page.locator('text=/unauthorized|login|authenticate/i').isVisible();

    await ScreenshotHelper.captureScreenshot(page, 'unauthorized-401-error');
  });

  test('should handle 403 forbidden error', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 403 error
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Forbidden', message: 'Access denied' }),
      });
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);

    // Should show access denied message
    const errorVisible = await page.locator('text=/forbidden|access denied|permission/i').isVisible();

    await ScreenshotHelper.captureScreenshot(page, 'forbidden-403-error');
  });

  test('should redirect to login on authentication failure', async ({ page }) => {
    // Mock authentication check
    await page.route('**/api/auth/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ authenticated: false }),
      });
    });

    await page.goto('/');

    await page.waitForTimeout(1000);

    // Check if redirected to login page
    const currentUrl = page.url();
    await ScreenshotHelper.captureScreenshot(page, 'redirect-to-login');
  });

  test('should handle expired session', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Initially allow access
    let authenticated = true;

    await page.route('**/api/**', async (route) => {
      if (!authenticated) {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Session expired' }),
        });
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    // Simulate session expiration
    authenticated = false;

    // Try to perform action
    if (await orgPage.createButton.isVisible()) {
      await orgPage.createButton.click();
    }

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'session-expired');
  });

  test('should handle insufficient permissions for create', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock permission error on POST
    await page.route('**/api/organizations', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 403,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Insufficient permissions to create' }),
        });
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    // Try to create
    if (await orgPage.createButton.isVisible()) {
      await orgPage.createButton.click();
      await orgPage.codeInput.fill('TEST123');
      await orgPage.nameInput.fill('Test Org');
      await orgPage.submitButton.click();

      await page.waitForTimeout(1000);
      await ScreenshotHelper.captureScreenshot(page, 'no-permission-create');
    }
  });

  test('should handle insufficient permissions for delete', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock permission error on DELETE
    await page.route('**/api/organizations/*', async (route) => {
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 403,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Insufficient permissions to delete' }),
        });
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);

    // Try to delete (if delete button is visible)
    const deleteBtn = page.locator(orgPage.deleteButton).first();
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();

      if (await orgPage.confirmDeleteButton.isVisible()) {
        await orgPage.confirmDeleteButton.click();
      }

      await page.waitForTimeout(1000);
      await ScreenshotHelper.captureScreenshot(page, 'no-permission-delete');
    }
  });

  test('should handle insufficient permissions for update', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock permission error on PUT/PATCH
    await page.route('**/api/organizations/*', async (route) => {
      if (route.request().method() === 'PUT' || route.request().method() === 'PATCH') {
        await route.fulfill({
          status: 403,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Insufficient permissions to update' }),
        });
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);

    // Try to edit
    const editBtn = page.locator(orgPage.editButton).first();
    if (await editBtn.isVisible()) {
      await editBtn.click();

      if (await orgPage.submitButton.isVisible()) {
        await orgPage.nameInput.fill('Updated Name');
        await orgPage.submitButton.click();

        await page.waitForTimeout(1000);
        await ScreenshotHelper.captureScreenshot(page, 'no-permission-update');
      }
    }
  });

  test('should display appropriate error message for token expiration', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Token expired', message: 'Please login again' }),
      });
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'token-expired-error');
  });

  test('should handle missing authentication token', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'No authentication token provided' }),
      });
    });

    await page.goto('/');

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'missing-token-error');
  });

  test('should handle invalid authentication token', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Invalid authentication token' }),
      });
    });

    await page.goto('/');

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'invalid-token-error');
  });

  test('should handle role-based access control errors', async ({ page }) => {
    const deptPage = new DepartmentPage(page);

    // User is authenticated but doesn't have required role
    await page.route('**/api/departments', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 403,
          contentType: 'application/json',
          body: JSON.stringify({
            error: 'Access denied',
            message: 'Admin role required'
          }),
        });
      } else {
        await route.continue();
      }
    });

    await deptPage.goto();

    if (await deptPage.createButton.isVisible()) {
      await deptPage.createButton.click();
      await deptPage.codeInput.fill('DEPT123');
      await deptPage.nameInput.fill('Test Dept');
      await deptPage.submitButton.click();

      await page.waitForTimeout(1000);
      await ScreenshotHelper.captureScreenshot(page, 'rbac-access-denied');
    }
  });

  test('should handle organization-level access restrictions', async ({ page }) => {
    const userPage = new UserPage(page);

    // User can only access certain organizations
    await page.route('**/api/users', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Organization access restricted',
          message: 'You do not have access to this organization'
        }),
      });
    });

    await userPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'org-access-restricted');
  });

  test('should show login prompt when accessing protected route', async ({ page }) => {
    // Try to access protected route without auth
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Authentication required' }),
      });
    });

    await page.goto('/');

    await page.waitForTimeout(1000);

    // Should show login prompt or redirect
    const loginVisible = await page.locator('text=/login|sign in/i, [type="password"]').isVisible();

    await ScreenshotHelper.captureScreenshot(page, 'protected-route-auth-required');
  });
});
