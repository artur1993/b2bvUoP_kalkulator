# C02 — Pydantic na wszystkich endpointach

## Cel
Każdy endpoint przyjmujący JSON ma walidację Pydantic. Dziś brakuje na `/api/calculate/break-even-analysis` i `/api/export/excel`. (`/api/calculate/sensitivity-analysis` znika w A02.)

## Źródło
[AUDYT.md §2.2](../../../AUDYT.md) — KRYTYCZNE

## Pliki
- [src/validation.py](../../../src/validation.py) — dodać nowe modele
- [src/app.py:39-52, 124-153](../../../src/app.py#L39) — dodać dekoratory
- [tests/integration/test_security.py](../../../tests/integration/test_security.py) — testy negatywne

## Zmiana

### Nowe modele w `validation.py`
```python
class BreakEvenAnalysisRequest(BaseModel):
    b2b: B2BDataModel
    uop: UoPDataModel

class ExcelExportRequest(BaseModel):
    b2b_results: Dict[str, Any]  # tymczasowo Any, do zaostrzenia w D03
    uop_results: Dict[str, Any]
```

### Uogólnienie dekoratora
```python
def validate(model_class):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                json_data = request.get_json()
                if not json_data:
                    return jsonify({"error": "Request body cannot be empty."}), 400
                validated = model_class(**json_data)
                g.validated_data = validated.model_dump()
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({"error": "Validation failed", "details": e.errors()}), 400
        return wrapper
    return decorator
```

Stare `validate_calculation_request` przepisać na `@validate(CalculationRequestModel)`.

## Acceptance
- [x] `/api/calculate` używa `@validate(CalculationRequestModel)`
- [x] `/api/calculate/break-even-analysis` używa `@validate(BreakEvenAnalysisRequest)`
- [x] `/api/export/excel` używa `@validate(ExcelExportRequest)`
- [x] Test `test_break_even_garbage_payload_returns_400` — `{"junk": 1}` → 400
- [x] Test `test_excel_export_garbage_payload_returns_400` — j.w.
- [x] Brak `try/except` z `request.get_json()` w endpointach (dekorator obsługuje)

## Test plan
```bash
pytest tests/integration/test_security.py -v
curl -X POST http://localhost:5001/api/calculate/break-even-analysis -d '{"junk":1}' -H 'Content-Type: application/json'  # 400
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A02 (sensitivity endpoint nie istnieje)
- Niezależne od C01, C03, C04.
