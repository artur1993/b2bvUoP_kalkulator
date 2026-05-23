# F02 — Testy edge cases

## Cel
`tests/unit/test_edge_cases.py` z scenariuszami granicznymi.

## Źródło
[AUDYT.md §13.2](../../../AUDYT.md) — WYSOKIE

## Pliki
- `tests/unit/test_edge_cases.py` (nowy, jeśli nie istnieje po B07)

## Zakres

- `monthly_invoice_amount = 0` → wynik B2B z zerami, bez crasha
- `monthly_gross_salary = 0` + `deductible_cost_settings.type='author_50'` + `creative_work_percentage>0` → no ZeroDivision (regresja po B07)
- Próg 30-krotności dokładnie na limicie (`cumulative_gross == thirty_times_limit`)
- Próg 30-krotności + 1 PLN
- Bardzo wysokie kwoty (>500k mies., danina solidarnościowa po B12)
- `zus_type='small_business'` → 400 (regresja po B09)
- `b2b.youth_relief=True` → 400 (regresja po B04)
- Granice progów zdrowotnej ryczałtu (60k, 60k+1, 300k, 300k+1 — może być w B02)

## Acceptance
- [ ] Plik `test_edge_cases.py` z ≥10 testami
- [ ] Coverage `calculations.py` ≥80% po dodaniu

## Test plan
```bash
pytest tests/unit/test_edge_cases.py -v
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: B02, B04, B07, B09, B12 (testy regresyjne)
