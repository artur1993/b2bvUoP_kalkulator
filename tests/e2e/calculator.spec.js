import { test, expect } from '@playwright/test';

test.describe('B2B vs UoP Calculator E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5000'); // Assuming Flask app runs on port 5000
  });

  test('Test Case 1: "Happy Path" with Default Values', async ({ page }) => {
    // Verify initial state (default values)
    await expect(page.locator('#monthly_gross_salary')).toHaveValue('10000');
    await expect(page.locator('#b2b_invoice_amount')).toHaveValue('12000');

    // Click calculate button
    await page.click('button:has-text("Calculate")');

    // Wait for results to load (adjust selector if needed)
    await page.waitForSelector('#results-display');

    // Verify some key results (adjust selectors and expected values based on actual calculations)
    await expect(page.locator('#b2b-net-income')).toBeVisible();
    await expect(page.locator('#uop-net-income')).toBeVisible();
    await expect(page.locator('#b2b-net-income')).not.toHaveText('0.00'); // Ensure it's not zero
    await expect(page.locator('#uop-net-income')).not.toHaveText('0.00'); // Ensure it's not zero

    // Verify chart presence
    await expect(page.locator('.comparison-chart')).toBeVisible();
  });

  test('Test Case 2: Complex B2B Scenario', async ({ page }) => {
    // Change monthly gross salary and B2B invoice amount
    await page.fill('#monthly_gross_salary', '15000');
    await page.fill('#b2b_invoice_amount', '18000');

    // Select 'liniowy' tax
    await page.selectOption('#b2b_tax_type', 'liniowy');

    // Select full ZUS
    await page.check('#b2b_zus_type_full');

    // Add a company benefit (e.g., "Prywatna opieka medyczna")
    await page.click('text="Dodaj Benefit Firmowy"');
    await page.fill('input[placeholder="Nazwa Benefitu"]', 'Prywatna opieka medyczna');
    await page.fill('input[placeholder="Wartość roczna"]', '2400'); // 200 PLN/month * 12

    // Click calculate button
    await page.click('button:has-text("Calculate")');

    // Wait for results to load
    await page.waitForSelector('#results-display');

    // Verify some key results for the complex scenario
    await expect(page.locator('#b2b-net-income')).toBeVisible();
    await expect(page.locator('#uop-net-income')).toBeVisible();
    await expect(page.locator('#b2b-net-income')).not.toHaveText('0.00');
    await expect(page.locator('#uop-net-income')).not.toHaveText('0.00');

    // Verify chart presence
    await expect(page.locator('.comparison-chart')).toBeVisible();
  });

  test('Test Case 3: Break-Even Point Verification', async ({ page }) => {
    // Ensure the break-even point is displayed
    await page.click('button:has-text("Calculate")'); // Calculate with default values first
    await page.waitForSelector('#results-display');

    // Verify the break-even invoice amount is visible and not zero
    await expect(page.locator('#break-even-invoice-amount')).toBeVisible();
    await expect(page.locator('#break-even-invoice-amount')).not.toHaveText('0.00');
  });
});
