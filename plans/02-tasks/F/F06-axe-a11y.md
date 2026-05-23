# F06 — axe-core a11y testy

## Cel
Zastąpić placeholderowy `accessibility.spec.js` (12 linii) prawdziwym audytem WCAG przez `@axe-core/playwright`.

## Źródło
[AUDYT.md §7.4](../../../AUDYT.md)

## Pliki
- [tests/e2e/accessibility.spec.js](../../../tests/e2e/accessibility.spec.js)
- `package.json` (dodać `@axe-core/playwright` do devDeps)

## Zmiana

```javascript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('home page has no detectable WCAG A/AA violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test('results page has no detectable WCAG A/AA violations', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('calculate-button').click();
  await page.waitForSelector('[data-testid="results-display"]');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

## Acceptance
- [ ] `@axe-core/playwright` w devDeps
- [ ] 2 testy (home + results) zielone (lub z udokumentowanym whitelistem znanych odstępstw)

## Test plan
```bash
npx playwright test tests/e2e/accessibility.spec.js
```

## Playwright MCP Verification

Przed napisaniem automatycznego testu, użyj Playwright MCP żeby mieć szybki podgląd naruszeń a11y:

```
playwright_navigate(url="http://localhost:5173")
playwright_screenshot(name="F06-01-home-a11y")

# Sprawdź obecność atrybutów aria (podstawowy wskaźnik):
playwright_evaluate(script="document.querySelectorAll('[aria-label],[aria-labelledby],[role]').length")
# Im więcej, tym lepiej (sprawdź, że nie jest 0)

playwright_evaluate(script="document.querySelectorAll('button:not([aria-label]):not([title])').length")
# Sprawdź: przyciski bez labeli aria (powinno być 0 lub mało)

playwright_evaluate(script="document.querySelectorAll('input:not([aria-label]):not([id])').length")
# Sprawdź: inputy bez powiązanego labela (powinno być 0)

# Kliknij Oblicz i sprawdź wyniki:
playwright_click(selector="[data-testid='calculate-button'],button[type='submit']")
playwright_screenshot(name="F06-02-results-a11y")

playwright_evaluate(script="document.querySelectorAll('[role=alert],[aria-live]').length")
# Sprawdź: komunikaty wyników używają aria-live lub role=alert
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A04 (czyste UI bez insurance), B01 (etykiety 2026), D07 (dark mode w formularzu)
