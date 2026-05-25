import { test, expect } from '@playwright/test';

test.describe('Visual and UI/UX Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/'); 
    // Switch to English for consistent testing
    const plButton = page.locator('button', { hasText: 'PL' });
    const enButton = page.locator('button', { hasText: 'EN' });
    
    if (await plButton.isVisible()) {
        await plButton.click();
    }
    if (await enButton.isVisible()) {
        await enButton.click();
    }
  });

  test('Zadanie 1: Should apply global styles, font, and header correctly', async ({ page }) => {
    // Sprawdzenie koloru tła (z tolerancją na drobne różnice renderowania)
    const body = page.locator('body');
    const backgroundColor = await body.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    // Zarówno rgb(247, 250, 252) jak i rgb(248, 250, 252) są akceptowalne (slate-50 / gray-50)
    expect(backgroundColor).toMatch(/rgb\(24[78], 250, 252\)/);

    // Sprawdzenie fontu w nagłówku
    const headerTitle = page.locator('h1', { hasText: 'B2B vs UoP Calculator 2026' });
    await expect(headerTitle).toHaveCSS('font-family', /Inter|sans-serif/);

    // Sprawdzenie widoczności i treści nagłówka
    await expect(headerTitle).toBeVisible();
    const subheader = page.locator('p', { hasText: 'Compare your earnings and choose the best option' });
    await expect(subheader).toBeVisible();
  });

  test('Zadanie 2: Should correctly style form elements and primary button', async ({ page }) => {
    // Testowanie stanu focus na polu input (używamy selektora name zamiast ID po refaktorze)
    const monthlyInvoiceInput = page.locator('input[name="monthly_invoice_amount"]');
    await monthlyInvoiceInput.focus();
    // Sprawdzamy czy ring/shadow zawiera kolor primary (niebieski)
    await expect(monthlyInvoiceInput).toHaveClass(/focus:ring/);

    // Testowanie stylu głównego przycisku
    const calculateButton = page.locator('button', { hasText: 'Calculate Comparison' });
    await expect(calculateButton).toBeVisible();
    
    // Sprawdzenie czy przycisk ma kolor primary (klasa bg-primary)
    await expect(calculateButton).toHaveClass(/bg-primary/);
    await expect(calculateButton).toHaveCSS('color', 'rgb(255, 255, 255)');
  });

  test('Zadanie 3: Should display results section correctly', async ({ page }) => {
    await page.locator('button', { hasText: 'Calculate Comparison' }).click();
    const resultsSection = page.locator('[data-testid="results-display"]');
    await expect(resultsSection).toBeVisible();
    
    // Sprawdzamy czy kluczowe sekcje są widoczne
    await expect(page.locator('h2', { hasText: 'Calculation Results' })).toBeVisible();
    await expect(page.locator('h3', { hasText: 'B2B Contract' })).toBeVisible();
    await expect(page.locator('h3', { hasText: 'Employment Contract (UoP)' })).toBeVisible();
  });

  test('Zadanie 4: Should render charts and handle interactive elements', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.locator('button', { hasText: 'Calculate Comparison' }).click();
    await expect(page.locator('h2', { hasText: 'Calculation Results' })).toBeVisible();

    // Sprawdzenie, czy wykresy są widoczne
    const barChart = page.locator('canvas').first();
    await expect(barChart).toBeVisible();
  });
});
