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
    
    // Fill minimum required fields
    await page.fill('input[name="monthly_invoice_amount"]', '12000');
    await page.fill('input[name="monthly_gross_salary"]', '10000');
    
    await page.click('button:has-text("Calculate Comparison")');
    
    // Wait for results
    const resultsHeader = page.locator('h2', { hasText: 'Calculation Results' });
    await expect(resultsHeader).toBeVisible();

    // Disable animations to prevent contrast issues during transitions
    await page.addStyleTag({ content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `});
    await page.waitForTimeout(500); // Small buffer for any JS-driven state changes

    // 1. Full axe audit on results state
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
      
    expect(results.violations).toEqual([]);

    // 2. Check for aria-live or role=alert for dynamic content
    // We expect the results container or specific status updates to have aria-live
    const ariaLiveElements = page.locator('[aria-live], [role="alert"]');
    const count = await ariaLiveElements.count();
    expect(count).toBeGreaterThan(0);
  });
});
