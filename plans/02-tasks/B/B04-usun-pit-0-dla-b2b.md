# B04 — Usuń PIT-0 (ulga dla młodych) z B2B

## Cel
Naprawić KRYTYCZNY błąd merytoryczny: aplikacja stosuje PIT-0 (ulgę dla młodych) do dochodów z B2B, mimo że art. 21 ust. 1 pkt 148 ustawy PIT obejmuje tylko UoP, zlecenia, praktyki absolwenckie i staż uczniowski.

Dodatkowo: frontend AUTOMATYCZNIE ustawia `youth_relief = (age < 26)` dla **obu** formularzy → 25-latek na B2B dostaje zaniżony podatek o ~10 263 PLN/rok (85 528 × 12%).

## Źródło
- [AUDYT.md §3.1](../../../AUDYT.md) — KRYTYCZNE
- [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) — sekcja „Ulga Dla Młodych", **BŁĄD**

Źródło: https://podatki.gov.pl/ulgi-i-odliczenia/ulga-dla-mlodych-pit/

## Pliki
- [src/calculations.py:81-82, 90](../../../src/calculations.py#L81) — bloki `if b2b_data.get('youth_relief', False)` w gałęzi B2B (ryczałt i pozostałe formy)
- [src/validation.py:21](../../../src/validation.py#L21) — pole `youth_relief: bool` w `B2BDataModel`
- [src/dashboard/src/App.jsx:138-141](../../../src/dashboard/src/App.jsx#L138) — automatyczne `setB2bData({ youth_relief: isYouthReliefApplicable })`
- [src/dashboard/src/components/CalculatorForm.jsx:122-128](../../../src/dashboard/src/components/CalculatorForm.jsx#L122) — checkbox „youth_relief" w sekcji B2B
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — nowe testy negatywne

## Zmiana

### Backend
1. **Usunąć** `if b2b_data.get('youth_relief', False)` z [`calculations.py:81-82`](../../../src/calculations.py#L81) (ryczałt).
2. **Usunąć** `if b2b_data.get('youth_relief', False)` z [`calculations.py:90`](../../../src/calculations.py#L90) (skala/liniowy/IP Box).
3. **Usunąć** pole `youth_relief` z `B2BDataModel`. Pydantic odrzuci payload z `b2b.youth_relief=true` jako nieznane pole.
4. W `UoPDataModel`: dodać walidator: jeśli `youth_relief=True` i `age >= 26` → `ValidationError`.

### Frontend
1. Usunąć checkbox „PIT-0" z sekcji B2B w `CalculatorForm.jsx`.
2. W `handleAgeChange` (App.jsx:135): usunąć linijkę `setB2bData(prev => ({ ..., youth_relief: isYouthReliefApplicable }))`. Pozostawić tylko dla UoP.

## Acceptance
- [ ] Backend: `B2BDataModel` nie ma pola `youth_relief`
- [ ] Backend: payload `{"b2b": {..., "youth_relief": true}}` → **400** z `Extra inputs are not permitted`
- [ ] Backend: payload `{"uop": {"age": 30, "youth_relief": true}}` → **400** z custom message (age >= 26)
- [ ] Frontend: brak checkboxa „ulga dla młodych" w sekcji B2B
- [ ] Frontend: automatyczne włączenie PIT-0 dla `age < 26` działa **tylko dla UoP**
- [ ] Nowy test `test_pit_0_not_applied_to_b2b` — 24-latek B2B `flat_tax`, `monthly_invoice_amount=12000` → podatek liczony z pełnej podstawy, **bez** odjęcia 85 528 PLN
- [ ] Nowy test `test_pit_0_payload_rejected_for_b2b` — POST z `b2b.youth_relief=true` → 400
- [ ] Nowy test `test_pit_0_uop_only_when_age_under_26` — UoP `age=30, youth_relief=true` → 400 lub silent disable

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_pit_0_not_applied_to_b2b -v
pytest tests/unit/test_validation.py::test_pit_0_payload_rejected_for_b2b -v
pytest tests/unit/test_validation.py::test_pit_0_uop_only_when_age_under_26 -v
pytest -q
cd src/dashboard && npm test -- --run
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
playwright_screenshot(name="B04-initial")
# Sprawdź sekcję B2B: NIE MA checkboxa PIT-0 / ulgi dla młodych:
playwright_evaluate(script="[...document.querySelectorAll('input[type=checkbox]')].map(el => el.closest('label')?.textContent || el.name || el.id).filter(t => /pit.?0|ulga.{0,15}m.o.d/i.test(t))")
# Oczekiwany wynik: [] — w sekcji B2B nie ma żadnego checkboxa dot. PIT-0

# Sprawdź sekcję UoP: JEST checkbox PIT-0 (wciąż aktywny):
playwright_evaluate(script="[...document.querySelectorAll('input[type=checkbox]')].map(el => el.closest('label')?.textContent || el.name || el.id).filter(t => /pit.?0|ulga.{0,15}m.o.d/i.test(t))")
# Oczekiwany wynik: niepusta tablica — w sekcji UoP checkbox istnieje

# Ustaw wiek 24 i sprawdź, że UoP auto-zaznacza PIT-0, a B2B nie dostaje tej opcji:
playwright_fill(selector="input[name='age'],input[id*='age']", value="24")
playwright_screenshot(name="B04-age-24-uop-pit0-check")
```

## Rollback
Revert PR. Realne ryzyko: użytkownik z 25 lat na B2B nie zobaczy starej (błędnej) niższej kwoty podatku. To **pożądana** zmiana — rollback tylko w wyjątkowym przypadku.

## Zależności
- Niezależne od B01-B03, B05-B12. Idzie równolegle.
- **Blokuje**: F03 (przypadki użycia — szczególnie Case B z 24-latkiem).
