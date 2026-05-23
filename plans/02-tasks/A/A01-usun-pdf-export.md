# A01 — Usuń eksport PDF

## Cel
Usunąć wszystkie wzmianki o eksporcie PDF z dokumentacji, tłumaczeń, testów i kodu. Zostawiamy tylko Excel.

## Źródło
[AUDYT_UZUPELNIENIE.md §1.1](../../../AUDYT_UZUPELNIENIE.md) — „Eksport PDF jest deklarowany, ale nie istnieje w aktualnym kodzie".

## Pliki
- [README.md](../../../README.md) — sekcja Key Features (wzmianki o „PDF report", „Advanced PDF Report", „Internationalized PDF Reports", „Transparent Methodology")
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze typu `*.pdf_*`, `*.export_pdf`, `methodology.*` (jeśli odnoszą się do PDF)
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [src/dashboard/src/components/ResultsDisplay.jsx](../../../src/dashboard/src/components/ResultsDisplay.jsx) — przyciski/sekcje PDF jeśli istnieją
- [tests/e2e/calculator.spec.js](../../../tests/e2e/calculator.spec.js) — pominięte testy PDF (`test.skip`)
- [pyproject.toml](../../../pyproject.toml) — usunąć `fpdf2`, `pypdf`, `weasyprint` z `dependencies`
- [src/dashboard/src/services/api.js](../../../src/dashboard/src/services/api.js) — funkcja `exportToPdf` jeśli istnieje

## Acceptance
- [ ] Grep `git grep -i pdf` zwraca tylko: ten plan, audyty (historyczne), wzmiankę „Excel zamiast PDF" w README
- [ ] `npm test` zielony, `pytest` zielony
- [ ] `pyproject.toml` nie zawiera bibliotek PDF
- [ ] Frontend: zero przycisków „Eksportuj PDF"
- [ ] E2E: zero testów o PDF (skipped lub usunięte)
- [ ] README sekcja „Key Features" nie wymienia PDF

## Test plan
```bash
git grep -i 'pdf\|fpdf\|weasyprint\|pypdf' -- ':!plans/' ':!AUDYT*.md'  # powinno być puste
pytest -q
cd src/dashboard && npm test -- --run
cd .. && npx playwright test tests/e2e/ --grep-invert pdf
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_screenshot(name="A01-initial")
playwright_get_visible_text(selector="body")
# Sprawdź: w widocznym tekście NIE MA słów "PDF", "Eksportuj PDF", "Export PDF"
# Jeśli jest sekcja wyników — wypełnij formularz i kliknij Oblicz:
playwright_click(selector="[data-testid='calculate-button']")
playwright_screenshot(name="A01-results")
playwright_get_visible_text(selector="[data-testid='results-display']")
# Sprawdź: w wynikach NIE MA przycisku/linku PDF
```

## Rollback
Revert PR — czyste usunięcie, brak risk.

## Zależności
- Brak. Może iść równolegle z innymi taskami fazy A.
- **Blokuje**: A06 (czystka README — A06 zakłada że PDF już nie ma).
