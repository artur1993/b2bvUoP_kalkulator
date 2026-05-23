import { test, expect } from '@playwright/test';

test.describe.skip('B2B vs UoP Calculator E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5001');
    await page.waitForSelector('h1:has-text("B2B vs UoP Calculator 2025")');
  });

  test('Test Case 1: "Happy Path" with Default Values', async ({ page }) => {
    // Verify initial state (default values)
    await expect(page.locator('#faktura_miesieczna')).toHaveValue('10000'); // Corrected default value
    await expect(page.locator('#wynagrodzenie_brutto')).toHaveValue('8000');

    // Click calculate button
    await page.click('button:has-text("Calculate Comparison")');

    // Wait for results to load
    await page.waitForSelector('text=Calculation Results');

    // Verify some key results
    await expect(page.locator('text=Total Annual B2B Value:')).toBeVisible();
    await expect(page.locator('text=Total Annual UoP Value:')).toBeVisible();
    await expect(page.locator('text=Total Annual B2B Value:')).not.toContainText('0,00');
    await expect(page.locator('text=Total Annual UoP Value:')).not.toContainText('0,00');

    // Verify chart presence
    await expect(page.locator('canvas').first()).toBeVisible();
  });

  test('Test Case 2: Complex B2B Scenario', async ({ page }) => {
    // Change monthly gross salary and B2B invoice amount
    await page.fill('#wynagrodzenie_brutto', '15000');
    await page.fill('#faktura_miesieczna', '18000');

    // Select 'liniowy' tax
    await page.selectOption('#forma_opodatkowania', 'liniowy');

    // Select full ZUS
    await page.selectOption('#zus_rodzaj', 'duza_firma'); // Corrected to 'duza_firma'

    // Enable and set a company benefit
    const medicalCareCheckbox = page.getByLabel('Medical Care (from company)');
    await medicalCareCheckbox.check();
    const medicalCareValueInput = page.getByLabel('Medical Care Value (PLN/year)');
    await expect(medicalCareValueInput).toBeVisible({ timeout: 10000 });
    await expect(medicalCareValueInput).toBeEditable({ timeout: 15000 });
    await medicalCareValueInput.fill('2400');

    // Click calculate button
    await page.click('button:has-text("Calculate Comparison")');

    // Wait for results to load
    await page.waitForSelector('text=Calculation Results', { timeout: 90000 });

    // Verify some key results for the complex scenario
    await expect(page.locator('text=Total Annual B2B Value:')).toBeVisible();
    await expect(page.locator('text=Total Annual UoP Value:')).toBeVisible();
    await expect(page.locator('text=Total Annual B2B Value:')).not.toContainText('0,00');
    await expect(page.locator('text=Total Annual UoP Value:')).not.toContainText('0,00');

    // Verify chart presence
    await expect(page.locator('canvas').first()).toBeVisible();
  });

  test('Test Case 3: Break-Even Point Verification', async ({ page }) => {
    // Ensure the break-even point is displayed
    await page.click('button:has-text("Calculate Comparison")');
    await page.waitForSelector('text=Calculation Results');

    // Verify the break-even invoice amount is visible and contains currency symbol
    await expect(page.locator('text=Break-Even Monthly B2B Invoice:')).toBeVisible();
    await expect(page.locator('text=Break-Even Monthly B2B Invoice:')).toContainText('zł'); // Check for currency symbol
  });

  test('Test Case 4: B2B with Ryczałt 12% and ZUS Ulga na Start', async ({ page }) => {
    await page.fill('#faktura_miesieczna', '12000');
    await page.selectOption('#forma_opodatkowania', 'ryczalt_IT');
    await page.selectOption('#zus_rodzaj', 'ulga_na_start');
    await page.click('button:has-text("Calculate Comparison")');
    await page.waitForSelector('text=Calculation Results');

    await expect(page.locator('text=Total Annual B2B Value:')).not.toContainText('0,00');
    await expect(page.locator('text=Total Annual UoP Value:')).not.toContainText('0,00');
  });

  test('Test Case 5: B2B with Skala Podatkowa and Full ZUS, with custom benefits', async ({ page }) => {
    await page.fill('#faktura_miesieczna', '25000');
    await page.selectOption('#forma_opodatkowania', 'skala');
    await page.selectOption('#zus_rodzaj', 'duza_firma');

    // Enable and set a custom benefit
    const customBenefitCheckbox = page.getByLabel('Custom Benefits (PLN/year)');
    await customBenefitCheckbox.check();
    const customBenefitValueInput = page.locator('#customBenefits');
    await expect(customBenefitValueInput).toBeVisible();
    await customBenefitValueInput.fill('3000');

    await page.click('button:has-text("Calculate Comparison")');
    await page.waitForSelector('text=Calculation Results');

    await expect(page.locator('text=Total Annual B2B Value:')).not.toContainText('0,00');
    await expect(page.locator('text=Total Annual UoP Value:')).not.toContainText('0,00');
  });

  test('Test Case 6: UoP with Youth Relief (Ulga dla Młodych)', async ({ page }) => {
    await page.fill('#wynagrodzenie_brutto', '6000'); // Below the limit for youth relief
    await page.locator('#ulga_dla_mlodych_uop').check();

    await page.click('button:has-text("Calculate Comparison")');
    await page.waitForSelector('text=Calculation Results');

    // Verify that the annual tax for UoP is 0 (or very close to 0) due to youth relief
    await expect(page.locator('text=Roczny podatek:')).toContainText('0,00');
  });

  test('Test Case 7: B2B with IP Box and paid sick days from company', async ({ page }) => {
    await page.fill('#faktura_miesieczna', '20000');
    await page.selectOption('#forma_opodatkowania', 'ip_box');

    // Enable and set paid sick days from company
    const paidSickDaysCheckbox = page.getByLabel('Paid Sick Days (from company)');
    await paidSickDaysCheckbox.check();
    // Ensure the checkbox is checked to make the input visible
    await page.locator('#companyBenefits\.paidSickDays\.enabled').check();
    const paidSickDaysValueInput = page.locator('#companyBenefits\.paidSickDays\.days');
    await expect(paidSickDaysValueInput).toBeVisible();
    await paidSickDaysValueInput.fill('10');

    await page.click('button:has-text("Calculate Comparison")');
    await page.waitForSelector('text=Calculation Results');

    await expect(page.locator('text=Total Annual B2B Value:')).not.toContainText('0,00');
    await expect(page.locator('text=Total Annual UoP Value:')).not.toContainText('0,00');
  });

  test('Test Case 8: Export to Excel functionality', async ({ page }) => {
    await page.click('button:has-text("Calculate Comparison")');
    await page.waitForSelector('text=Calculation Results');

    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Export to Excel")');
    const download = await downloadPromise;

    await expect(download.suggestedFilename()).toBe('kalkulator_wyniki.xlsx');
  });

});
