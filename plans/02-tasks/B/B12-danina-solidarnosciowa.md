# B12 — Danina solidarnościowa 4% > 1M PLN (prosty model + disclaimer)

## Cel
Dodać obliczenia daniny solidarnościowej zgodnie z art. 30h ustawy PIT: 4% od nadwyżki rocznego dochodu ponad 1 000 000 PLN. Prosty model, z disclaimerem „pełne rozliczenie wymaga PIT-DS".

## Źródło
- [AUDYT.md §3.5](../../../AUDYT.md) — WYSOKIE
- Decyzja użytkownika (2026-05-23): „tak — implementujemy prosty model + disclaimer"

Źródło prawa: art. 30h ustawy z 26 lipca 1991 r. o PIT (Dz.U. 2024 poz. 226 z późn. zm.).

## Pliki
- [dane_wejsciowe_kalkulator.json](../../../dane_wejsciowe_kalkulator.json) — `tax_thresholds.solidarity_tax`
- [src/calculations.py](../../../src/calculations.py) — `calculate_b2b_results` i `calculate_uop_results` (dodać `compute_solidarity_tax`)
- [src/dashboard/src/components/ResultsDisplay.jsx](../../../src/dashboard/src/components/ResultsDisplay.jsx) — pokazanie kwoty + disclaimer
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze `results.solidarity_tax*`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py)

## Zmiana w configu

Dodać w `tax_thresholds`:
```json
"solidarity_tax": {
  "threshold": 1000000,
  "rate": 0.04
}
```

Plus metadane (B11): `source_url: art. 30h ustawy PIT`.

## Zmiana w `calculations.py`

Nowa funkcja (lub helper w common):
```python
def compute_solidarity_tax(annual_taxable_base: float, config: dict) -> float:
    """Returns 4% of taxable base over 1M PLN, else 0."""
    threshold = config['tax_thresholds']['solidarity_tax']['threshold']
    rate = config['tax_thresholds']['solidarity_tax']['rate']
    return max(0, annual_taxable_base - threshold) * rate
```

W `calculate_b2b_results` po obliczeniu `annual_tax`:
```python
solidarity_tax = compute_solidarity_tax(taxable_base, config)
annual_tax += solidarity_tax
# w returnie dodać kluczek 'annual_solidarity_tax'
```

Analogicznie w `calculate_uop_results`:
```python
solidarity_tax = compute_solidarity_tax(annual_tax_base, config)
annual_tax += solidarity_tax
```

**Uproszczenie**: art. 30h liczy daninę od **sumy** dochodów ze wszystkich źródeł (B2B + UoP + inne). Aplikacja zakłada, że użytkownik podaje tylko jedno źródło naraz. W disclaimerze trzeba to ujawnić.

## Zmiana w UI

W `ResultsDisplay.jsx` (sekcja breakdown):
- Jeśli `annual_solidarity_tax > 0`, pokazać osobny wiersz „Danina solidarnościowa: X PLN".
- Pod sekcją: alert `<Alert type="info">{t('results.solidarity_tax_disclaimer')}</Alert>`

Tłumaczenia:
- PL: „Uwaga: Danina solidarnościowa 4% dotyczy łącznych dochodów >1 000 000 PLN ze wszystkich źródeł. Kalkulator zakłada jedno źródło — w deklaracji PIT-DS uwzględnij wszystkie dochody."
- EN: analogicznie.

## Acceptance
- [ ] Config zawiera `tax_thresholds.solidarity_tax`
- [ ] `compute_solidarity_tax` wyodrębnione jako helper
- [ ] B2B i UoP doliczają daninę po naliczeniu zwykłego podatku
- [ ] Response API zawiera `annual_solidarity_tax` (osobny klucz)
- [ ] UI pokazuje wiersz „Danina solidarnościowa" tylko gdy >0
- [ ] Disclaimer widoczny zawsze gdy `annual_solidarity_tax > 0`
- [ ] Test `test_solidarity_tax_below_threshold` — `taxable_base=500000` → `solidarity_tax = 0`
- [ ] Test `test_solidarity_tax_at_threshold` — `taxable_base=1000000` → `solidarity_tax = 0`
- [ ] Test `test_solidarity_tax_above_threshold` — `taxable_base=1200000` → `solidarity_tax = 8000` (= 200k × 4%)
- [ ] Test `test_b2b_high_income_includes_solidarity_tax` — B2B `monthly_invoice_amount=100000`, ryczałt → `annual_solidarity_tax > 0` w response

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_solidarity_tax_* -v
pytest tests/unit/test_calculations.py::test_b2b_high_income_includes_solidarity_tax -v
pytest -q
cd src/dashboard && npm test -- ResultsDisplay
./run_app.sh  # smoke: faktura 100k/mies → widać daninę + disclaimer
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")

# --- Scenariusz: dochód poniżej progu → NIE MA wiersza daniny ---
playwright_fill(selector="input[name*=monthly_invoice_amount],input[id*=monthly_invoice_amount]", value="18000")
playwright_click(selector="[data-testid='calculate-button'],button[type='submit']")
playwright_get_visible_text(selector="[data-testid='results-display'],[class*=results]")
# Sprawdź: NIE MA tekstu "Danina solidarnościowa"
playwright_screenshot(name="B12-no-solidarity-18k")

# --- Scenariusz: dochód powyżej progu (100k/mies = 1.2M/rok) → JEST wiersz daniny ---
playwright_fill(selector="input[name*=monthly_invoice_amount],input[id*=monthly_invoice_amount]", value="100000")
playwright_click(selector="[data-testid='calculate-button'],button[type='submit']")
playwright_screenshot(name="B12-with-solidarity-100k")
playwright_get_visible_text(selector="[data-testid='results-display'],[class*=results]")
# Sprawdź: tekst zawiera "Danina solidarnościowa" i kwotę > 0
# Sprawdź: widoczny disclaimer o PIT-DS i łącznych dochodach
playwright_evaluate(script="document.body.innerText.includes('PIT-DS') || document.body.innerText.includes('łącznych dochodów') || document.body.innerText.includes('wszystkich źródeł')")
# Oczekiwany wynik: true
```

## Rollback
Revert PR + config rollback. Brak ryzyka — danina dotyczy <1% użytkowników (>1M PLN/rok).

## Zależności
- Niezależne od B01-B11.
- **Blokuje**: F03 (jeśli któryś case użycia ma high-income).
