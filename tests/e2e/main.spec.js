
const { test, expect } = require('@playwright/test');

test.describe('Kalkulator B2B vs UoP E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the page and display the form', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Kalkulator B2B vs UoP IT 2025');
    await expect(page.locator('#calculator-form')).toBeVisible();
  });

  test('should calculate and display results on form submission', async ({ page }) => {
    // Fill out the form
    await page.locator('#b2b_faktura').fill('21000');
    await page.locator('#uop_brutto').fill('16500');

    // Submit the form
    await page.locator('button[type="submit"]').click();

    // Wait for the results to appear
    const resultsContainer = page.locator('#results');
    await expect(resultsContainer).toBeVisible();

    // Check for specific results
    await expect(resultsContainer.locator('h4').first()).toContainText('zł');
    await expect(resultsContainer.locator('.mt-5')).toHaveText('Szczegółowe Porównanie Roczne');
  });

  test('should show break-even point', async ({ page }) => {
    await page.locator('button[type="submit"]').click();
    const resultsContainer = page.locator('#results');
    await expect(resultsContainer.locator('h4').nth(2)).toContainText('Próg rentowności (Break-even)');
  });
});
