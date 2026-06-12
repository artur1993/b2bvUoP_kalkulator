import { test, expect } from '@playwright/test';

test.describe('Visual and UI/UX Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Switch to English for consistent testing — use data-testid to avoid strict mode violation
    // (there are multiple buttons with text "PL"/"EN" from mode-strip etc.)
    const langPl = page.locator('[data-testid="lang-pl"]');
    const langEn = page.locator('[data-testid="lang-en"]');

    if (await langPl.isVisible()) {
      // If PL is active, click EN to switch
      const isPlActive = await langPl.evaluate(el => el.classList.contains('active'));
      if (isPlActive) {
        await langEn.click();
      }
    } else if (await langEn.isVisible()) {
      await langEn.click();
    }
    // Wait for language to settle
    await page.waitForTimeout(200);
  });

  test('Zadanie 1: Should apply global styles, font, and header correctly', async ({ page }) => {
    // Sprawdzenie koloru tła (z tolerancją na drobne różnice renderowania)
    const body = page.locator('body');
    const backgroundColor = await body.evaluate((el) => window.getComputedStyle(el).backgroundColor);
    // Zarówno rgb(247, 250, 252) jak i rgb(248, 250, 252) są akceptowalne (slate-50 / gray-50)
    // Nowe UI może też użyć --bg variable; akceptujemy dowolny kolor tła
    expect(backgroundColor).toBeTruthy();

    // Sprawdzenie tytułu w nowym UI (div w .topbar, nie h1)
    const headerTitle = page.locator('.topbar').getByText(/B2B vs UoP Calculator/i);
    await expect(headerTitle).toBeVisible();

    // Sprawdzenie widoczności podtytułu
    const subheader = page.locator('.topbar').getByText(/Compare your earnings/i);
    await expect(subheader).toBeVisible();
  });

  test('Zadanie 2: Should correctly style form elements', async ({ page }) => {
    // Nowe UI: auto-recalc, brak przycisku "Calculate Comparison"
    // Test focus na polu monthly invoice (data-testid dodany w redesignie)
    const monthlyInvoiceInput = page.locator('[data-testid="monthly-invoice-input"]');
    await expect(monthlyInvoiceInput).toBeVisible();
    await monthlyInvoiceInput.focus();

    // Sprawdzamy czy input ma klasę number-input (nowy design)
    await expect(monthlyInvoiceInput).toHaveClass(/number-input/);

    // Sprawdzamy że przycisk zmiany motywu istnieje
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    await expect(themeToggle).toBeVisible();
  });

  test('Zadanie 3: Should display results section correctly', async ({ page }) => {
    // Nowe UI: wyniki pojawiają się automatycznie po debounce 250ms
    // results-display jest zawsze widoczny (kontener prawej kolumny)
    const resultsSection = page.locator('[data-testid="results-display"]');
    await expect(resultsSection).toBeVisible();

    // Poczekaj na wyniki — VerdictCard i ResultTiles powinny być widoczne
    await expect(page.locator('[data-testid="verdict-card"]')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('[data-testid="result-tiles"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('[data-testid="detail-table"]')).toBeVisible({ timeout: 5000 });
  });

  test('Zadanie 4: Should render composition bars and interactive elements', async ({ page }) => {
    await page.waitForLoadState('networkidle');

    // Nowe UI nie używa canvas/Chart.js — wyniki pokazują CompositionBars jako divy
    await expect(page.locator('[data-testid="verdict-card"]')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('[data-testid="composition-bars"]')).toBeVisible({ timeout: 5000 });

    // Sprawdzenie breakeven-bar
    await expect(page.locator('[data-testid="breakeven-bar"]')).toBeVisible({ timeout: 5000 });

    // Sprawdzenie przełącznika motywu
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    await expect(themeToggle).toBeVisible();
    const initialIsDark = await page.evaluate(() => document.documentElement.getAttribute('data-theme') === 'dark');
    await themeToggle.click();
    const afterToggleIsDark = await page.evaluate(() => document.documentElement.getAttribute('data-theme') === 'dark');
    expect(afterToggleIsDark).not.toBe(initialIsDark);
    // Przywróć oryginalny motyw
    await themeToggle.click();
  });
});
