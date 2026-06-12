import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Audits (WCAG 2.1 A/AA)', () => {
  test('Home page should have no automatically detectable violations', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('Results section should have no automatically detectable violations and use aria-live', async ({ page }) => {
    await page.goto('/');

    // Switch to English for consistent selectors
    const langEn = page.locator('[data-testid="lang-en"]');
    if (await langEn.isVisible()) {
      const isEnActive = await langEn.evaluate(el => el.classList.contains('active'));
      if (!isEnActive) {
        await langEn.click();
        await page.waitForTimeout(200);
      }
    }

    // Disable animations to prevent contrast issues during transitions
    await page.addStyleTag({ content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `});

    // Wait for page to fully render
    await page.waitForSelector('[data-testid="results-display"]');
    await page.waitForTimeout(500); // Small buffer for any JS-driven state changes

    // Try to get results (auto-calc with defaults, may or may not succeed depending on backend)
    const verdictCard = page.locator('[data-testid="verdict-card"]');
    const hasResults = await verdictCard.isVisible({ timeout: 8000 }).catch(() => false);

    if (hasResults) {
      // Results are visible — check the results heading
      const resultsHeader = page.locator('h2', { hasText: 'Calculation Results' });
      await expect(resultsHeader).toBeVisible();
    }

    // 1. Full axe audit on current state (form + results or empty state)
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);

    // 2. Check for aria-live or role=alert for dynamic content
    // The results container has aria-live="polite" for screen reader announcements
    const ariaLiveElements = page.locator('[aria-live], [role="alert"]');
    const count = await ariaLiveElements.count();
    expect(count).toBeGreaterThan(0);
  });
});
