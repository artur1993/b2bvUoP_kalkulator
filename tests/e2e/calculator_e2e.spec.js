import { test, expect } from '@playwright/test';

test.describe('Calculator E2E Tests', () => {
  test.skip('should display results after calculation with default values', async ({ page }) => {
    await page.goto('/');

    // Ensure the form is loaded
    await expect(page.locator('h1')).toHaveText('B2B vs UoP Calculator 2026');
    await expect(page.locator('button', { hasText: 'Calculate Comparison' })).toBeVisible();

    // Click the calculate button with default values
    await page.locator('button', { hasText: 'Calculate Comparison' }).click();

    // Wait for the results to appear
    await expect(page.locator('h2', { hasText: 'Calculation Results' })).toBeVisible();

    // Assert key B2B results
    await expect(page.locator('.bg-blue-50 li:has-text("Total Annual B2B Value:")')).toBeVisible();
    await expect(page.locator('.bg-blue-50 li:has-text("Monthly Net (Total Value):")')).toBeVisible();

    // Assert key UoP results
    await expect(page.locator('.bg-green-50 li:has-text("Total Annual UoP Value:")')).toBeVisible();
    await expect(page.locator('.bg-green-50 li:has-text("Monthly Net (Total Value):")')).toBeVisible();

    // Optionally, check for the break-even point if it appears
    await expect(page.locator('p:has-text("Break-Even Monthly B2B Invoice:")')).toBeVisible();
  });
});
