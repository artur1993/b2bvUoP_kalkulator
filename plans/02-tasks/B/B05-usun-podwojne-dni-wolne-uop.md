# B05 — Usuń podwójne liczenie dni wolnych w UoP

## Cel
Naprawić KRYTYCZNY błąd księgowy: `paid_days_off_value` (26 dni × dzienna stawka) jest dodawane do `total_uop_value`, mimo że roczna pensja UoP **już zawiera** płatne urlopy (pracownik dostaje pełną pensję w miesiącu urlopowym). Zawyża wartość UoP o ~10–15%.

## Źródło
[AUDYT.md §3.3](../../../AUDYT.md) — KRYTYCZNE

## Pliki
- [src/calculations.py:226-229](../../../src/calculations.py#L226) — `paid_days_off_value` w `total_uop_value`
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — test snapshot wyniku przed/po

## Zmiana

Z:
```python
daily_rate = monthly_gross_salary / config['general_data']['working_days_monthly']
paid_days_off_value = config['uop_days_off']['vacation']['days'] * daily_rate

total_uop_value = annual_net + benefits_value + paid_days_off_value
```

Na:
```python
total_uop_value = annual_net + benefits_value
```

Usunąć zmienną `paid_days_off_value` i `annual_paid_days_off_value` z returna.

W odpowiedzi API: usunąć klucz `annual_paid_days_off_value`. Sprawdzić, czy frontend nie czyta tego pola — jeśli tak, usunąć użycie (powiązane z A06 i ResultsDisplay).

## Acceptance
- [ ] `calculate_uop_results` nie liczy `paid_days_off_value`
- [ ] Returned dict nie zawiera `annual_paid_days_off_value`
- [ ] `ResultsDisplay.jsx` nie odwołuje się do tego pola
- [ ] Test `test_uop_total_value_without_double_vacation` — pensja 10 000 brutto, KUP standard, brak benefitów → `total_annual_value ≈ annual_net` (z tolerancją ±50 PLN)
- [ ] Test sprawdza, że dla wcześniej zawyżonego wyniku różnica wynosi `vacation_days × daily_rate`

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_uop_total_value_without_double_vacation -v
pytest -q
cd src/dashboard && npm test -- ResultsDisplay
./run_app.sh  # smoke: UoP total wyraźnie niższe niż przed PR
```

## Rollback
Revert PR. Realne ryzyko: pożądana zmiana, rollback tylko w wyjątkowym przypadku.

## Zależności
- Niezależne. Równolegle z B01-B04, B06-B12.
- **Blokuje**: F03 (oczekiwane wyniki przypadków A/B/C).
