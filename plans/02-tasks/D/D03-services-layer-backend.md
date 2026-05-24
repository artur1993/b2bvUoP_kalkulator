# D03 — Services layer w backendzie

## Cel
Wprowadzić warstwę `services/` między routes a `domain/`. `app.py` staje się cienkim adapterem (walidacja → service → response).

## Źródło
[AUDYT.md §4.1](../../../AUDYT.md) — WYSOKIE

## Pliki
- Cel: `src/services/calculation_service.py` z funkcją `run_full_calculation(b2b, uop, mode, lang) -> dict`
- [src/app.py:69-122](../../../src/app.py#L69) — przepisać `calculate()` na cienką funkcję

## Zmiana

```python
# src/services/calculation_service.py
def run_full_calculation(request: CalculationRequest) -> CalculationResponse:
    b2b_results = calculate_b2b_results(request.b2b)
    uop_results = calculate_uop_results(request.uop)
    break_even = calculate_break_even(...)
    return CalculationResponse(
        b2b_results=b2b_results,
        uop_results=uop_results,
        ...
    )
```

W `app.py`:
```python
@app.route('/api/calculate', methods=['POST'])
@validate(CalculationRequestModel)
def calculate():
    return jsonify(run_full_calculation(g.validated_data).model_dump())
```

## Acceptance
- [x] `src/services/calculation_service.py` istnieje
- [x] `app.py:calculate()` ma <15 linii
- [x] Wszystkie istniejące testy zielone

## Test plan
```bash
pytest -q
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: B (cała), C02 (Pydantic dekorator)
- **Powiązane**: D01, D08
