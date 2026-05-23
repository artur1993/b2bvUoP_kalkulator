# F01 — Testy `validation.py`

## Cel
Dodać `tests/unit/test_validation.py` z testami dla każdego pola w modelach Pydantic.

## Źródło
[AUDYT.md §13.1](../../../AUDYT.md) — WYSOKIE

## Pliki
- `tests/unit/test_validation.py` (nowy)

## Zakres testów

- Każde pole: poprawna wartość → 200/przejdzie walidację
- Każde pole: zła wartość → `ValidationError`
- Każde required pole: pominięte → `ValidationError`
- Każdy pattern (`tax_form`, `zus_type`, `deductible_cost_settings.type`, `calculation_mode`) — testy boundary
- Górne granice (po B10) — testy z wartościami granicznymi
- `b2b.youth_relief` (po B04) — odrzucone
- `uop.youth_relief=True + age>=26` (po B04) — odrzucone

## Acceptance
- [ ] Plik `tests/unit/test_validation.py` istnieje
- [ ] Coverage `validation.py` ≥95%
- [ ] Wszystkie patterny mają test "happy" + "rejected"

## Test plan
```bash
pytest tests/unit/test_validation.py -v --cov=src.validation
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: B04, B09, B10 (zmiany w walidatorze)
