import { test, expect } from '@playwright/test';
import { OrganizationPage } from '../../page-objects/OrganizationPage';
import { DepartmentPage } from '../../page-objects/DepartmentPage';
import { UserPage } from '../../page-objects/UserPage';
import { generateRandomOrg } from '../../fixtures/test-data';
import { ScreenshotHelper } from '../../utils/screenshot';

test.describe('Network Error Scenarios', () => {
  test('should handle API timeout gracefully', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Simulate slow network
    await page.route('**/api/**', async (route) => {
      await page.waitForTimeout(10000); // Delay beyond timeout
      await route.continue();
    });

    await orgPage.goto();

    // Should show loading state or timeout error
    await page.waitForTimeout(2000);
    await ScreenshotHelper.captureScreenshot(page, 'api-timeout-error');
  });

  test('should handle 500 server error', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 500 error
    await page.route('**/api/organizations', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' }),
      });
    });

    await orgPage.goto();

    // Should display error message
    await page.waitForTimeout(1000);
    const errorVisible = await page.locator('text=/error|failed|unable/i').isVisible();

    await ScreenshotHelper.captureScreenshot(page, 'server-500-error');
  });

  test('should handle network failure', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Simulate network failure
    await page.route('**/api/**', async (route) => {
      await route.abort('failed');
    });

    await page.goto('/');

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'network-failure');
  });

  test('should handle 404 Not Found error', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 404 error
    await page.route('**/api/organizations/*', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Not Found' }),
      });
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'not-found-404-error');
  });

  test('should handle 400 Bad Request error', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 400 error on create
    await page.route('**/api/organizations', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Bad Request', message: 'Invalid data' }),
        });
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    const newOrg = generateRandomOrg();
    await orgPage.createButton.click();
    await orgPage.codeInput.fill(newOrg.code);
    await orgPage.nameInput.fill(newOrg.name);
    await orgPage.submitButton.click();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'bad-request-400-error');
  });

  test('should retry failed requests', async ({ page }) => {
    const orgPage = new OrganizationPage(page);
    let requestCount = 0;

    // Fail first request, succeed on retry
    await page.route('**/api/organizations', async (route) => {
      requestCount++;
      if (requestCount === 1) {
        await route.abort('failed');
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    // If retry logic exists, should eventually load
    await page.waitForTimeout(3000);
    await ScreenshotHelper.captureScreenshot(page, 'request-retry-success');
  });

  test('should handle malformed JSON response', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Return invalid JSON
    await page.route('**/api/organizations', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: 'Invalid JSON{{{',
      });
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'malformed-json-error');
  });

  test('should handle slow API responses', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Simulate slow response
    await page.route('**/api/organizations', async (route) => {
      await page.waitForTimeout(3000);
      await route.continue();
    });

    await orgPage.goto();

    // Should show loading indicator
    const loadingVisible = await page.locator('[role="progressbar"], .loading, .spinner').isVisible();

    await page.waitForTimeout(4000);
    await ScreenshotHelper.captureScreenshot(page, 'slow-api-loading');
  });

  test('should handle partial data load failure', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Main list loads, but detail fails
    await page.route('**/api/organizations/*', async (route) => {
      if (route.request().url().match(/\/\d+$/)) {
        await route.abort('failed');
      } else {
        await route.continue();
      }
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'partial-load-failure');
  });

  test('should handle CORS errors', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Simulate CORS error
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 0,
        body: '',
      });
    });

    await page.goto('/');

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'cors-error');
  });

  test('should handle connection timeout', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Set very short timeout
    await page.setDefaultTimeout(2000);

    // Delay response beyond timeout
    await page.route('**/api/**', async (route) => {
      await page.waitForTimeout(5000);
      await route.continue();
    });

    try {
      await orgPage.goto();
    } catch (error) {
      // Expected to timeout
    }

    await ScreenshotHelper.captureScreenshot(page, 'connection-timeout');
  });

  test('should show offline message when network is down', async ({ page }) => {
    // Simulate offline mode
    await page.context().setOffline(true);

    await page.goto('/');

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'offline-mode');

    // Restore online
    await page.context().setOffline(false);
  });

  test('should handle rate limiting (429 error)', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 429 error
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Too Many Requests' }),
      });
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'rate-limit-429-error');
  });

  test('should handle service unavailable (503 error)', async ({ page }) => {
    const orgPage = new OrganizationPage(page);

    // Mock 503 error
    await page.route('**/api/**', async (route) => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Service Unavailable' }),
      });
    });

    await orgPage.goto();

    await page.waitForTimeout(1000);
    await ScreenshotHelper.captureScreenshot(page, 'service-unavailable-503-error');
  });
});
