import { test, expect } from '@playwright/test';

test.describe('E2E Smoke Test', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Switch to English for consistent assertions
    const enButton = page.locator('button', { hasText: 'EN' });
    if (await enButton.isVisible()) {
      await enButton.click();
    }
  });

  test('should perform a full calculation flow and verify results', async ({ page }) => {
    // 1. Fill the form
    await page.fill('input[name="monthly_invoice_amount"]', '15000');
    await page.fill('input[name="monthly_gross_salary"]', '10000');
    
    // Select taxation form
    await page.selectOption('select[name="tax_form"]', 'lump_sum_it');
    
    // 2. Click Calculate
    await page.click('button:has-text("Calculate Comparison")');

    // 3. Verify Results are visible
    await expect(page.locator('h2', { hasText: 'Calculation Results' })).toBeVisible();
    await expect(page.locator('[data-testid="results-display"]')).toBeVisible();
    
    // Verify specific values (approximate or just presence)
    await expect(page.locator('text=Total Annual B2B Value')).toBeVisible();
    await expect(page.locator('text=Total Annual UoP Value')).toBeVisible();

    // 4. Verify Charts
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();

    // 5. Test Excel Export
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Export to Excel")');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe('kalkulator_wyniki.xlsx');

    // 6. Test Theme Toggle
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    
    const initialIsDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    await themeToggle.click();
    const afterToggleIsDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
    expect(afterToggleIsDark).not.toBe(initialIsDark);

    // 7. Verify URL parameters and reload
    // After calculation, the URL should have params
    await expect(page).toHaveURL(/b2b_invoice=15000/);
    
    const currentUrl = page.url();
    await page.goto(currentUrl);
    
    // Check if values persisted in inputs (assuming frontend handles these names)
    await expect(page.locator('input[name="monthly_invoice_amount"]')).toHaveValue('15000');
    await expect(page.locator('input[name="monthly_gross_salary"]')).toHaveValue('10000');
    await expect(page.locator('select[name="tax_form"]')).toHaveValue('lump_sum_it');
  });
});
