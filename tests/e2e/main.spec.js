const { test, expect } = require('@playwright/test');

test.describe('Kalkulator B2B vs UoP E2E Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Base URL is set in playwright.config.js
    await page.goto('/');
  });

  test('should load the page and display the main form elements', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Kalkulator B2B vs UoP IT 2025');
    await expect(page.locator('#calculator-form')).toBeVisible();
    await expect(page.locator('#b2b_faktura')).toHaveValue('21000');
    await expect(page.locator('#uop_brutto')).toHaveValue('16500');
  });

  test('should calculate and display charts on default submission', async ({ page }) => {
    await page.locator('button[type="submit"]').click();

    // Wait for results and charts to be visible
    await expect(page.locator('#results')).toBeVisible();
    await expect(page.locator('#comparisonChart')).toBeVisible();
    await expect(page.locator('#b2bDistributionChart')).toBeVisible();

    // Check if the raw JSON output contains the main keys
    const jsonOutput = await page.locator('#json-output').textContent();
    const results = JSON.parse(jsonOutput);
    expect(results).toHaveProperty('b2b_results');
    expect(results).toHaveProperty('uop_results');
    expect(results).toHaveProperty('break_even_faktura');
  });

  test('should correctly calculate with advanced B2B benefits', async ({ page }) => {
    // Expand the advanced options accordion
    await page.locator('button[data-bs-target="#collapseAdvanced"]').click();
    await expect(page.locator('#collapseAdvanced')).toBeVisible();

    // Set custom benefit
    await page.locator('#customBenefits').fill('5000');

    // Enable and set company-provided benefits
    await page.locator('#privateHealthcare_enabled').check();
    await page.locator('#privateHealthcare_value').fill('3000');
    await page.locator('#sportCard_enabled').check();

    // Submit form
    await page.locator('button[type="submit"]').click();

    // Verify charts are displayed
    await expect(page.locator('#comparisonChart')).toBeVisible();
    await expect(page.locator('#b2bDistributionChart')).toBeVisible();

    // Verify the results in the JSON output
    const jsonOutput = await page.locator('#json-output').textContent();
    const results = JSON.parse(jsonOutput);

    expect(results.b2b_results.roczna_wartosc_wlasnych_korzysci).toBe(5000);
    expect(results.b2b_results.roczna_wartosc_benefitow_od_firmy).toBe(3000 + 1200); // 3000 for healthcare + 1200 default for sportCard
    expect(results.b2b_results.calkowita_roczna_wartosc).toBeGreaterThan(results.b2b_results.roczne_netto_na_reke);
  });

  test('should show a warning for excessive benefit values', async ({ page }) => {
    // Set up a listener for the alert dialog
    let alertMessage = '';
    page.on('dialog', async dialog => {
        alertMessage = dialog.message();
        await dialog.dismiss();
    });

    // Set a low invoice amount
    await page.locator('#b2b_faktura').fill('5000');

    // Expand advanced options
    await page.locator('button[data-bs-target="#collapseAdvanced"]').click();

    // Set a high benefit value (more than 50% of 60,000 annual revenue)
    await page.locator('#customBenefits').fill('35000');

    // Submit the form
    await page.locator('button[type="submit"]').click();

    // Check if the alert was triggered with the correct message
    expect(alertMessage).toContain('Ostrzeżenie: Całkowita wartość benefitów przekracza 50% rocznego przychodu B2B');
  });
});