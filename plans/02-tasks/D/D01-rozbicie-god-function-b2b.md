# D01 — Rozbicie god function `calculate_b2b_results`

## Cel
Funkcja `calculate_b2b_results` ma 136 linii i 6+ odpowiedzialności. Rozbić na helpery testowalne w izolacji.

## Źródło
[AUDYT.md §4.2](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/calculations.py:13-136](../../../src/calculations.py#L13)
- Cel: `src/domain/b2b/` z osobnymi plikami: `lost_revenue.py`, `social_contributions.py`, `health_contribution.py`, `income_tax.py`, `benefits.py`, `aggregate.py`

Jeśli D08 (reorganizacja) nie ruszony — wystarczy podział wewnątrz `calculations.py` lub w `src/calculations/b2b/`.

## Acceptance
- [x] `calculate_b2b_results` ma <30 linii (orkiestracja)
- [x] Każdy helper pure function: input dict/model → output dict/float
- [x] Wszystkie istniejące testy `test_calculations.py::*b2b*` zielone
- [x] Nowe testy per helper

## Test plan
```bash
pytest tests/unit/test_calculations.py -v
pytest tests/integration/test_real_scenarios.py -v
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: cała faza B (zmiany w logice najpierw, refactor po)
- **Powiązane**: D08 (reorganizacja katalogów)
