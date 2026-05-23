# A04 — Usuń insurance configurator

## Cel
Usunąć rozbudowany konfigurator ubezpieczeń (polskie teksty wbite w kod, broken i18n, side-effect modyfikujący `monthly_business_costs`). Pole `monthly_business_costs` zostaje, ale edytowalne ręcznie.

## Źródło
- [AUDYT.md §5.2](../../../AUDYT.md) — „Logika biznesowa w UI: calculateTotalInsuranceCost"
- [AUDYT_UZUPELNIENIE.md §1.5](../../../AUDYT_UZUPELNIENIE.md) — „Polskie teksty zaszyte w danych"

## Pliki
- [src/dashboard/src/components/InsuranceConfigurator.jsx](../../../src/dashboard/src/components/InsuranceConfigurator.jsx) — **usunąć**
- [src/dashboard/src/components/InsuranceConfigurator.test.jsx](../../../src/dashboard/src/components/InsuranceConfigurator.test.jsx) — **usunąć**
- [src/dashboard/src/data/insuranceOptions.js](../../../src/dashboard/src/data/insuranceOptions.js) — **usunąć cały plik**
- [src/dashboard/src/App.jsx:14, 16-34, 65-71, 143-152, 168-172, 220-221](../../../src/dashboard/src/App.jsx#L14) — import, funkcja `calculateTotalInsuranceCost`, state `baseBusinessCosts` i `insuranceConfig`, useEffect modyfikujący `monthly_business_costs`, przekazywanie do `<CalculatorForm>` i `<InsuranceConfigurator>`
- [src/dashboard/src/components/CalculatorForm.jsx:168-172](../../../src/dashboard/src/components/CalculatorForm.jsx#L168) — `<InsuranceConfigurator>`
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze `insurance.*`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.

## Acceptance
- [x] Brak plików `InsuranceConfigurator.*` i `insuranceOptions.js`
- [x] `App.jsx` nie ma `baseBusinessCosts`/`insuranceConfig` state ani `calculateTotalInsuranceCost` ani useEffect modyfikującego `monthly_business_costs`
- [x] Pole `monthly_business_costs` w `CalculatorForm` jest **bezpośrednio** kontrolowane przez `b2bData.monthly_business_costs`
- [x] Klucze `insurance.*` usunięte z obu locale files
- [x] `npm test` zielony, smoke test przejdzie
- [x] Strona nie pokazuje sekcji „Insurance configurator"

## Test plan
```bash
test ! -f src/dashboard/src/components/InsuranceConfigurator.jsx
test ! -f src/dashboard/src/data/insuranceOptions.js
git grep -i 'insurance' src/  # tylko historyczne wzmianki w komentarzach
cd src/dashboard && npm test -- --run
./run_app.sh  # smoke
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_get_visible_text(selector="body")
# Sprawdź: NIE MA sekcji "Insurance Configurator", "Konfigurator ubezpieczeń"
playwright_evaluate(script="document.querySelectorAll('[class*=insurance],[id*=insurance]').length")
# Oczekiwany wynik: 0
playwright_screenshot(name="A04-no-insurance-configurator")
# Sprawdź: JEST pole "Koszty firmowe miesięcznie" jako zwykły input (nie sekcja konfiguratora):
playwright_evaluate(script="document.querySelector('input[name*=business_costs],input[id*=business_costs]') !== null")
# Oczekiwany wynik: true
```

## Rollback
Revert PR. Brak migracji danych — `monthly_business_costs` było już polem w API.

## Zależności
- Brak. Równolegle z A01, A02, A03, A05.
- **Blokuje**: A06 (README).
