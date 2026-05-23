# B01 — „2025" → „2026" w UI i README

## Cel
Zsynchronizować UI i README z faktem, że backend liczy wg prawa 2026. Pozbyć się każdej wzmianki „2025" sugerującej, że aplikacja używa starych stawek.

## Źródło
- [AUDYT.md §3.11, §6.1, §12.1](../../../AUDYT.md)

## Pliki
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — globalna zamiana „2025" → „2026"
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [README.md](../../../README.md) — jeśli A06 nie objął już wszystkich wzmianek
- [src/analysis.py](../../../src/analysis.py) — `methodology` (już mówi 2026, ale weryfikacja)
- [src/calculations.py](../../../src/calculations.py) — docstringi mówią „2026", weryfikacja

## Acceptance
- [ ] `git grep -i '2025' src/` zwraca pusto (poza historyczną wzmianką w komentarzu „od 2025" jeśli jest uzasadnione)
- [ ] `git grep -i '2025' README.md` zwraca pusto
- [ ] Tłumaczenia tytułów: „Kalkulator B2B vs UoP **2026**" / „B2B vs UoP Calculator **2026**"
- [ ] Tooltipy, opisy benefitów, footer — wszystko mówi 2026
- [ ] (Stretch) Rok wynika z jednej zmiennej `i18n` interpolation: `t('app.title', { year: 2026 })`

## Test plan
```bash
git grep -i '2025' src/ README.md  # tylko historyczne / uzasadnione
cd src/dashboard && npm test -- --run
./run_app.sh  # smoke: tytuł + footer mówią 2026
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_get_visible_text(selector="h1,header,title,[class*=title],[class*=header]")
# Sprawdź: tytuł zawiera "2026", NIE zawiera "2025"
playwright_screenshot(name="B01-title-2026")
playwright_evaluate(script="document.body.innerText.includes('2025') && !document.body.innerText.includes('2025') === false")
# Alternatywnie — sprawdź, że "2025" NIE pojawia się jako rok obowiązujący:
playwright_evaluate(script="[...document.querySelectorAll('*')].filter(el => el.childElementCount === 0 && el.textContent.includes('2025')).map(el => el.textContent.trim()).filter(t => !t.includes('2026'))")
# Oczekiwany wynik: pusta tablica [] (żaden element nie mówi "2025" bez "2026")
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A06 (jeśli tam już ruszony tytuł).
- Niezależne od B02-B12.
