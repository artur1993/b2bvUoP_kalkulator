# A03 — Usuń equalize pension + `pension_calculator.py`

## Cel
Usunąć cały moduł symulacji emerytalnej (model sztywny, UI nie pokazuje wyniku). Zastąpić info-boxem z linkiem do IKE/IKZE.

## Źródło
- [AUDYT_UZUPELNIENIE.md §1.2](../../../AUDYT_UZUPELNIENIE.md) — „equalizePension zwraca dane z backendu, ale UI ich nie pokazuje"
- [AUDYT.md §3.19](../../../AUDYT.md) — „Model emerytalny mocno uproszczony"

## Pliki
- [src/pension_calculator.py](../../../src/pension_calculator.py) — **usunąć cały plik**
- [src/app.py:17, 113-117](../../../src/app.py#L17) — import + użycie `calculate_pension_details`
- [src/validation.py:24](../../../src/validation.py#L24) — pole `equalizePension: bool` w `B2BDataModel`
- [src/dashboard/src/App.jsx:62, 220](../../../src/dashboard/src/App.jsx#L62) — `equalizePension` w state
- [src/dashboard/src/components/CalculatorForm.jsx:130-139](../../../src/dashboard/src/components/CalculatorForm.jsx#L130) — checkbox „equalize_pension" + Tooltip
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze `form.equalize_pension*`, `analysis.pension*`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [dane_wejsciowe_kalkulator.json:58-62](../../../dane_wejsciowe_kalkulator.json#L58) — `pension_limits_2026` — **ZOSTAJE** (używane w info-boxie)
- [tests/unit/test_pension_calculator.py](../../../tests/unit/test_pension_calculator.py) — **usunąć cały plik**

## Acceptance
- [x] `src/pension_calculator.py` nie istnieje
- [x] `tests/unit/test_pension_calculator.py` nie istnieje
- [x] `B2BDataModel` nie ma pola `equalizePension`
- [x] UI nie pokazuje checkboxa „equalize pension"
- [x] Nowy info-box w `ResultsDisplay.jsx` (lub w sekcji B2B): „Pamiętaj o emeryturze: rozważ [IKE](https://www.knf.gov.pl) lub [IKZE](https://www.gov.pl/web/rodzina/ikze-limit-wplat). Limity 2026: IKE 28 260 PLN, IKZE 11 304 PLN (B2B: 16 956 PLN)." (treść do tłumaczenia w obu lokalach)
- [x] `pytest` zielony, `npm test` zielony
- [x] `curl /api/calculate -d '{...,"b2b":{"equalizePension":true}}'` → 400 (pole nieznane)

## Test plan
```bash
test ! -f src/pension_calculator.py
test ! -f tests/unit/test_pension_calculator.py
git grep -i 'equalize_pension\|equalizePension\|pension_calculator' src/ tests/  # tylko nowy info-box
pytest -q
cd src/dashboard && npm test -- --run
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_get_visible_text(selector="body")
# Sprawdź: NIE MA checkboxa "equalize pension", "Wyrównaj emeryturę"
playwright_evaluate(script="document.querySelectorAll('input[name*=equalize],input[id*=pension]').length")
# Oczekiwany wynik: 0
# Sprawdź: JEST info-box IKE/IKZE (po kliknięciu Oblicz):
playwright_click(selector="[data-testid='calculate-button']")
playwright_screenshot(name="A03-results-with-ike-info")
playwright_get_visible_text(selector="body")
# Sprawdź: tekst zawiera "IKE" i "IKZE" oraz wartości limitów (28 260 i/lub 11 304)
```

## Rollback
Revert PR. `pension_limits_2026` w configu pozostaje, więc info-box może odwołać się do tych wartości.

## Zależności
- Brak. Równolegle z A01, A02, A04, A05.
- **Blokuje**: A06 (README).
