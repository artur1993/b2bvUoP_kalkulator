# B10 — Górne granice w walidatorze Pydantic

## Cel
Dodać górne granice (`le=...`) do pól numerycznych w walidatorze, żeby uniknąć absurdalnych input'ów (`vacation_days=1000`).

## Źródło
[AUDYT.md §3.17](../../../AUDYT.md) — ŚREDNIE

## Pliki
- [src/validation.py:11-35](../../../src/validation.py#L11) — `B2BDataModel`, `DeductibleCostSettingsModel`, `UoPDataModel`
- [tests/unit/test_validation.py](../../../tests/unit/test_validation.py) — testy

## Zmiany

### `B2BDataModel`
```python
monthly_invoice_amount: float = Field(..., ge=0, le=10_000_000)
monthly_business_costs: float = Field(0.0, ge=0, le=10_000_000)
vacation_days: int = Field(0, ge=0, le=365)
sick_days: int = Field(0, ge=0, le=365)
stoppage_months: int = Field(0, ge=0, le=12)
age: int = Field(..., ge=18, le=100)
customBenefits: float = Field(0.0, ge=0, le=10_000_000)
```

### `DeductibleCostSettingsModel`
```python
creative_work_percentage: Optional[float] = Field(0.0, ge=0, le=100)  # już jest
```

### `UoPDataModel`
```python
monthly_gross_salary: float = Field(..., ge=0, le=10_000_000)
age: int = Field(..., ge=18, le=100)
```

## Acceptance
- [ ] Test `test_validation_vacation_days_over_365_rejected` → 400
- [ ] Test `test_validation_stoppage_months_over_12_rejected` → 400
- [ ] Test `test_validation_invoice_amount_over_10m_rejected` → 400
- [ ] Test `test_validation_age_over_100_rejected` → 400
- [ ] Test `test_validation_age_under_18_rejected` → 400

## Test plan
```bash
pytest tests/unit/test_validation.py -v
```

## Rollback
Revert PR.

## Zależności
- Niezależne.
- Naturalny powiązanie: F01 (testy walidatora) — Codex może je wypełnić tutaj zamiast tworzyć osobno.
