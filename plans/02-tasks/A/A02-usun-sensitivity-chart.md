# A02 — Usuń sensitivity chart

## Cel
Usunąć sensitivity (tornado) chart wraz z endpointem, funkcją obliczeniową i komponentem UI.

## Źródło
[budzet-cech.md](../../01-arch/0002-budzet-cech.md) — „Sensitivity chart: TNIJMY (3 sztywne parametry, mała wartość)".

## Pliki
- [src/app.py:54-67](../../../src/app.py#L54) — endpoint `/api/calculate/sensitivity-analysis` + import `calculate_sensitivity_analysis`
- [src/calculations.py:275-285](../../../src/calculations.py#L275) — funkcja `calculate_sensitivity_analysis`
- [src/dashboard/src/components/SensitivityChart.jsx](../../../src/dashboard/src/components/SensitivityChart.jsx) — komponent
- [src/dashboard/src/components/SensitivityChart.test.jsx](../../../src/dashboard/src/components/SensitivityChart.test.jsx) — test
- [src/dashboard/src/App.jsx:8](../../../src/dashboard/src/App.jsx#L8) — import + użycie w drzewie komponentów (`<SensitivityChart>`)
- [src/dashboard/src/services/api.js](../../../src/dashboard/src/services/api.js) — funkcja `calculateSensitivityAnalysis` jeśli istnieje
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze `sensitivity.*`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — testy `test_calculate_sensitivity_*`

## Acceptance
- [x] `grep -r sensitivity` w `src/` zwraca pusto (poza historyczną wzmianką w komentarzach jeśli muszą zostać)
- [x] `curl -X POST http://localhost:5001/api/calculate/sensitivity-analysis -d '{}'` → 404
- [x] `npm test` zielony, `pytest` zielony
- [x] Strona po `npm run dev` nie pokazuje sekcji „Sensitivity" / „Tornado"
- [x] Klucze `sensitivity.*` usunięte z obu locale files

## Test plan
```bash
git grep -i 'sensitivity\|tornado' src/  # tylko historyczne wzmianki
pytest -q
cd src/dashboard && npm test -- --run
./run_app.sh  # smoke: strona ładuje się bez 404 / brakujących komponentów
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_get_visible_text(selector="body")
# Sprawdź: NIE MA sekcji "Sensitivity", "Sensitivity Analysis", "Analiza wrażliwości", "Tornado"
playwright_screenshot(name="A02-no-sensitivity")
# Jeśli istnieje nawigacja/zakładki — sprawdź każdą:
playwright_evaluate(script="document.querySelectorAll('[class*=sensitivity],[id*=sensitivity]').length")
# Oczekiwany wynik: 0
playwright_evaluate(script="document.querySelectorAll('[class*=tornado],[id*=tornado]').length")
# Oczekiwany wynik: 0
```

## Rollback
Revert PR. Brak danych użytkownika do migracji.

## Zależności
- Brak. Równolegle z A01, A03, A04, A05.
- **Blokuje**: A06 (README czystka).
