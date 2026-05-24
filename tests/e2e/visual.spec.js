import { test, expect } from '@playwright/test';

test.describe('Visual and UI/UX Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/'); // Use the correct port
    // Switch to English for consistent testing
    await page.locator('button:has-text("PL")').click();
    await page.locator('button:has-text("EN")').click();
  });

  test('Zadanie 1: Should apply global styles, font, and header correctly', async ({ page }) => {
    // Sprawdzenie koloru tła
    const body = page.locator('body');
    await expect(body).toHaveCSS('background-color', 'rgb(247, 250, 252)');

    // Sprawdzenie fontu w nagłówku
    const headerTitle = page.locator('h1:has-text("B2B vs UoP Calculator 2026")');
    await expect(headerTitle).toHaveCSS('font-family', /Inter/);

    // Sprawdzenie widoczności i treści nagłówka
    await expect(headerTitle).toBeVisible();
    const subheader = page.locator('p:has-text("Compare your earnings and choose the best option")');
    await expect(subheader).toBeVisible();
  });

  test('Zadanie 2: Should correctly style form elements and primary button', async ({ page }) => {
    // Testowanie stanu focus na polu input
    const monthlyInvoiceInput = page.locator('#faktura_miesieczna');
    await monthlyInvoiceInput.focus();
    await expect(monthlyInvoiceInput).toHaveCSS('box-shadow', /rgb\(44, 82, 130\)/); // Kolor primary w cieniu

    // Testowanie stylu głównego przycisku
    const calculateButton = page.locator('button:has-text("Calculate Comparison")');
    await expect(calculateButton).toBeVisible();
    await expect(calculateButton).toHaveCSS('background-color', 'rgb(44, 82, 130)');
    await expect(calculateButton).toHaveCSS('color', 'rgb(255, 255, 255)');

    // Sprawdzenie, czy przycisk zmienia styl po najechaniu (hover)
    // Playwright nie ma bezpośredniej metody na sprawdzanie stylów hover,
    // ale można to zrobić przez zrzut ekranu lub wykonanie JS w przeglądarce.
    // Na razie wystarczy weryfikacja statycznych stylów.
  });

  test('Zadanie 3: Should display results that match the visual snapshot', async ({ page }) => {
    await page.locator('button:has-text("Calculate Comparison")').click();
    await page.waitForSelector('h2:has-text("Calculation Results")');

    const resultsSection = page.locator('.bg-surface > div > .mt-8'); // More specific selector
    await expect(resultsSection).toHaveScreenshot();
  });

  test('Zadanie 4: Should render charts and handle interactive elements', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('button:has-text("Calculate Comparison")');
    await page.locator('button:has-text("Calculate Comparison")').click();
    await page.waitForSelector('h2:has-text("Calculation Results")');

    // Sprawdzenie, czy wykresy są widoczne
    const barChart = page.locator('canvas').first();
    await expect(barChart).toBeVisible();

    // Przykład testu na tooltip (jeśli został dodany)
    // const tooltipIcon = page.locator('span:has-text("Roczny utracony przychód") + svg');
    // await tooltipIcon.hover();
    // const tooltipText = page.locator('div[role="tooltip"]');
    // await expect(tooltipText).toBeVisible();
    // await expect(tooltipText).toContainText('Wyjaśnienie...');
  });
});
