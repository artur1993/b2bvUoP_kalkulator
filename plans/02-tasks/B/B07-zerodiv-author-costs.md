# B07 — Naprawa ZeroDivisionError + uproszczenie wzoru kosztów autorskich

## Cel
Wyeliminować ZeroDivisionError w `calculations.py:188` przez algebraicznie równoważne uproszczenie wzoru.

## Źródło
[AUDYT.md §3.10](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/calculations.py:188](../../../src/calculations.py#L188) — wzór `author_costs_base`
- [tests/unit/test_edge_cases.py](../../../tests/unit/test_edge_cases.py) — nowy test (utworzyć plik jeśli nie istnieje)

## Zmiana

Z:
```python
creative_income = monthly_gross_salary * creative_work_percentage
author_costs_base = creative_income - (monthly_social * (creative_income / monthly_gross_salary))
```

Na (uproszczenie matematyczne — `creative_income / monthly_gross_salary == creative_work_percentage`):
```python
creative_income = monthly_gross_salary * creative_work_percentage
author_costs_base = creative_income - monthly_social * creative_work_percentage
```

Wartości obliczone są **identyczne**, ale wyrażenie nie dzieli przez `monthly_gross_salary`.

## Acceptance
- [x] Wzór nie zawiera `creative_income / monthly_gross_salary`
- [x] Test `test_author_costs_no_div_by_zero` — `monthly_gross_salary=0`, `deductible_cost_settings.type='author_50'`, `creative_work_percentage=50` → bez crasha
- [x] Test `test_author_costs_value_unchanged` — dla `monthly_gross_salary=10000`, `creative_work_percentage=70` → wynik **identyczny** jak przed zmianą (regression)

## Test plan
```bash
pytest tests/unit/test_edge_cases.py::test_author_costs_no_div_by_zero -v
pytest tests/unit/test_calculations.py::test_author_costs_value_unchanged -v
pytest -q
```

## Rollback
Revert PR. Brak ryzyka — uproszczenie matematyczne równoważne.

## Zależności
- Niezależne.
- **Blokuje**: F02 (testy edge cases).
