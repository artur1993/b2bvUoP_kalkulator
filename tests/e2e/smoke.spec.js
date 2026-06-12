import { test, expect } from '@playwright/test';

test.describe('E2E Smoke Test', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Switch to English — use data-testid to avoid strict mode violation
    const langEn = page.locator('[data-testid="lang-en"]');
    if (await langEn.isVisible()) {
      const isEnActive = await langEn.evaluate(el => el.classList.contains('active'));
      if (!isEnActive) {
        await langEn.click();
        await page.waitForTimeout(200);
      }
    }
  });

  test('should perform a full calculation flow and verify results', async ({ page }) => {
    // 1. Nowe UI auto-przelicza po zmianie wartości (debounce 250 ms), brak przycisku Calculate.
    //    Poczekaj aż wstępne wyniki się załadują (domyślne wartości: invoice=18000, salary=14500)
    await expect(page.locator('[data-testid="verdict-card"]')).toBeVisible({ timeout: 15000 });

    // 2. Zmień wartość faktury (data-testid="monthly-invoice-input")
    const invoiceInput = page.locator('[data-testid="monthly-invoice-input"]');
    await expect(invoiceInput).toBeVisible();
    await invoiceInput.triple_click ? invoiceInput.triple_click() : invoiceInput.click({ clickCount: 3 });
    await invoiceInput.fill('15000');

    // 3. Zmień wartość wynagrodzenia (data-testid="gross-salary-input")
    const salaryInput = page.locator('[data-testid="gross-salary-input"]');
    await expect(salaryInput).toBeVisible();
    await salaryInput.click({ clickCount: 3 });
    await salaryInput.fill('10000');

    // 4. Poczekaj na przeliczenie (debounce 250 ms + czas żądania)
    await page.waitForTimeout(800);
    await expect(page.locator('[data-testid="verdict-card"]')).toBeVisible({ timeout: 10000 });

    // 5. Sprawdź kluczowe sekcje wyników
    await expect(page.locator('[data-testid="results-display"]')).toBeVisible();
    await expect(page.locator('[data-testid="result-tiles"]')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('[data-testid="detail-table"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('[data-testid="composition-bars"]')).toBeVisible({ timeout: 5000 });

    // 6. Sprawdź obecność wartości B2B i UoP w tile'ach
    const resultTiles = page.locator('[data-testid="result-tiles"]');
    await expect(resultTiles.locator('.badge.b2b')).toBeVisible();
    await expect(resultTiles.locator('.badge.uop')).toBeVisible();

    // 7. Test eksportu do Excela
    const downloadPromise = page.waitForEvent('download');
    await page.locator('[data-testid="export-excel-button"]').click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toBe('kalkulator_wyniki.xlsx');

    // 8. Test przełącznika motywu
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    const initialIsDark = await page.evaluate(() => document.documentElement.getAttribute('data-theme') === 'dark');
    await themeToggle.click();
    const afterToggleIsDark = await page.evaluate(() => document.documentElement.getAttribute('data-theme') === 'dark');
    expect(afterToggleIsDark).not.toBe(initialIsDark);
    // Przywróć motyw
    await themeToggle.click();

    // 9. Test przycisku Share — ustawia URL params (inv=, sal=, mode=)
    await page.locator('button', { hasText: /Share|Udostępnij/i }).click();
    await page.waitForTimeout(300);
    // Sprawdź czy URL zawiera parametr "inv" (nowy format, nie "b2b_invoice")
    await expect(page).toHaveURL(/[?&]inv=\d+/);
  });
});
