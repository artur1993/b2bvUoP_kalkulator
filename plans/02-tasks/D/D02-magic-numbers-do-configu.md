# D02 — Magic numbers do configu

## Cel
Wszystkie stałe regulacyjne (stawki, mnożniki) wyłącznie w `dane_wejsciowe_kalkulator.json`. Zgodne z konstytucją.

## Źródło
[AUDYT.md §4.3](../../../AUDYT.md) — ŚREDNIE

## Pliki
- [src/calculations.py:6-11](../../../src/calculations.py#L6) — `UOP_ZUS_RATES` (do configu)
- [src/calculations.py:31, 114](../../../src/calculations.py#L31) — `0.8` (mnożnik chorobowego)
- [src/calculations.py:80](../../../src/calculations.py#L80) — `0.5` (odliczenie zdrowotnej w ryczałcie)
- [src/calculations.py:56, 59](../../../src/calculations.py#L56) — `0.09`, `0.049` (stawki zdrowotne skala/liniowy)
- [dane_wejsciowe_kalkulator.json](../../../dane_wejsciowe_kalkulator.json) — nowa sekcja `regulatory_rates`

## Zmiana w configu

```json
"regulatory_rates": {
  "uop_pension_employee": 0.0976,
  "uop_disability_employee": 0.0150,
  "uop_sickness_employee": 0.0245,
  "uop_health_employee": 0.09,
  "sick_leave_payment": 0.8,
  "lump_sum_health_deduction_share": 0.5,
  "tax_scale_health_rate": 0.09,
  "flat_tax_health_rate": 0.049
}
```

Plus metadane (B11).

## Acceptance
- [ ] `git grep -E '0\.0?(09|049|0976|0150|0245|5|8)' src/calculations.py` zwraca pusto
- [ ] Wszystkie odwołania przez `config['regulatory_rates'][...]`
- [ ] Wszystkie testy zielone (regresja)

## Test plan
```bash
pytest -q
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: B11 (metadane w configu)
- **Powiązane**: D01
