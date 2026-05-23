# F05 — E2E smoke test

## Cel
Pełny test E2E: wejście → formularz → Oblicz → wynik widoczny → eksport Excel.

## Źródło
[AUDYT.md §13.5](../../../AUDYT.md), konstytucja (E2E smoke MUSI być zielony).

## Pliki
- `tests/e2e/smoke.spec.js` (nowy lub rozbudowany z istniejącego `calculator.spec.js`)

## Zakres testów

1. **Happy path**: domyślne dane → Oblicz → widzi `total_annual_value` dla B2B i UoP.
2. **Excel export**: po Oblicz → kliknij „Eksportuj Excel" → plik pobrany (.xlsx, > 0 bytes).
3. **Dark mode toggle**: kliknij toggle → tło zmienia się na ciemne.
4. **Share URL**: ustaw konkretne wartości → Oblicz → URL zawiera parametry → reload → formularz wypełniony tymi samymi wartościami.

## Acceptance
- [ ] Smoke test pokrywa pełny flow
- [ ] CI uruchamia smoke (E04)
- [ ] Test stabilny (≥10 uruchomień bez flake'a)

## Test plan
```bash
npx playwright test tests/e2e/smoke.spec.js
```

## Playwright MCP Verification (Golden Path)

Po uruchomieniu `./run_app.sh` przeprowadź pełny flow krok po kroku, używając Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_screenshot(name="F05-01-initial")

# --- Krok 1: Wypełnij formularz B2B (Case A z 0002-przypadki-uzycia.md) ---
playwright_fill(selector="input[name*=monthly_invoice_amount],input[id*=monthly_invoice_amount]", value="18000")
playwright_select_option(selector="select[name*=tax_form],select[id*=tax_form]", value="lump_sum_it")
playwright_select_option(selector="select[name*=zus_type],select[id*=zus_type]", value="full")
playwright_fill(selector="input[name*=age],input[id*=age]", value="28")

# --- Krok 2: Wypełnij formularz UoP ---
playwright_fill(selector="input[name*=monthly_gross_salary],input[id*=monthly_gross_salary]", value="12000")

# --- Krok 3: Oblicz ---
playwright_click(selector="[data-testid='calculate-button'],button[type='submit']")
playwright_screenshot(name="F05-02-after-calculate")

# --- Krok 4: Sprawdź wyniki ---
playwright_get_visible_text(selector="[data-testid='results-display'],[class*=results]")
# Sprawdź: widoczne są wartości B2B netto i UoP netto (liczby > 0)
playwright_evaluate(script="document.querySelectorAll('[class*=total],[class*=annual],[class*=netto]').length > 0")
# Oczekiwany wynik: true

# --- Krok 5: Sprawdź Share URL ---
playwright_evaluate(script="window.location.search.length > 0")
# Oczekiwany wynik: true (URL ma parametry po Oblicz)
playwright_screenshot(name="F05-03-share-url")

# --- Krok 6: Eksport Excel ---
playwright_click(selector="[data-testid='excel-export'],button[class*=excel],a[class*=excel]")
playwright_screenshot(name="F05-04-excel-clicked")
# Sprawdź: brak błędów w konsoli po kliknięciu
playwright_evaluate(script="window.__lastError || null")
# Oczekiwany wynik: null

# --- Krok 7: Dark mode ---
playwright_click(selector="[data-testid='dark-mode-toggle'],[aria-label*='dark'],[class*='theme-toggle']")
playwright_screenshot(name="F05-05-dark-mode")
playwright_evaluate(script="document.documentElement.classList.contains('dark')")
# Oczekiwany wynik: true

# --- Krok 8: Reload i sprawdź Share URL ---
playwright_evaluate(script="window.location.href")
# Zapisz URL, załaduj ponownie:
playwright_navigate(url="http://localhost:5173/")  # zastąp pełnym URL z parametrami
playwright_screenshot(name="F05-06-after-reload")
playwright_evaluate(script="document.querySelector('input[name*=monthly_invoice_amount],input[id*=monthly_invoice_amount]')?.value")
# Oczekiwany wynik: "18000" (formularz wypełniony z URL params)
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: cała faza A, B (zmiana UI/wartości)
- **Powiązane**: E04 (CI uruchamia)
