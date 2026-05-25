# D06 — „Calculating..." → t()

## Cel
Zastąpić hardkodowany angielski tekst „Calculating..." na `t('form.loading_button')`.

## Źródło
[AUDYT.md §5.3](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/dashboard/src/components/CalculatorForm.jsx:393](../../../src/dashboard/src/components/CalculatorForm.jsx#L393)
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — nowy klucz `form.loading_button`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.

## Zmiana

```jsx
{loading ? t('form.loading_button') : t('form.calculate_button')}
```

Tłumaczenia:
- PL: „Obliczanie..."
- EN: „Calculating..."

## Acceptance
- [x] `git grep "'Calculating'" src/dashboard/` zwraca pusto
- [x] PL po kliknięciu „Oblicz" widzi „Obliczanie..."

## Test plan
```bash
cd src/dashboard && npm test -- CalculatorForm
./run_app.sh  # smoke z language=pl
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
# Przełącz na język PL jeśli to nie jest domyślny:
# playwright_click(selector="[data-lang='pl']")

# Ustaw opóźnioną obserwację — kliknij przycisk i szybko zrób screenshot:
playwright_click(selector="[data-testid='calculate-button'],button[type='submit']")
playwright_screenshot(name="D06-calculating-button-pl")
# Sprawdź: przycisk podczas ładowania pokazuje "Obliczanie..." NIE "Calculating..."
playwright_get_visible_text(selector="button[type='submit'],[data-testid='calculate-button']")
# Oczekiwany wynik dla PL: "Obliczanie..." lub "Oblicz" (gdy skończy)

# Jeśli możliwe — spowal sieć przez devtools i sprawdź stan podczas ładowania:
playwright_evaluate(script="document.querySelector('[data-testid=calculate-button]')?.textContent")
```

## Rollback
Revert PR.

## Zależności
- Niezależne.
