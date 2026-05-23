# F03 — Testy z konkretnymi liczbami (Case A/B/C)

## Cel
Przekształcić [00-spec/0002-przypadki-uzycia.md](../../00-spec/0002-przypadki-uzycia.md) w testy integracyjne z asercjami liczbowymi.

## Źródło
- [AUDYT.md §13.6](../../../AUDYT.md) — NISKIE (ale kluczowe dla regresji)
- [00-spec/0002-przypadki-uzycia.md](../../00-spec/0002-przypadki-uzycia.md)

## Pliki
- `tests/integration/test_real_scenarios.py` (nowy)

## Zakres

3 testy, każdy = jeden case użycia:
1. `test_case_a_mid_career_ryczalt_vs_uop`
2. `test_case_b_junior_youth_relief_only_uop`
3. `test_case_c_senior_ip_box_partial_qualified`

Każdy wysyła payload przez `client.post('/api/calculate', json=...)`, sprawdza response z tolerancją:
- `total_annual_value` B2B: ±1500 PLN
- `total_annual_value` UoP: ±1500 PLN
- `monthly_net_income`: ±50 PLN
- `break_even_invoice_amount` lub `break_even_gross_salary`: ±500 PLN

**WAŻNE**: oczekiwane wartości należy wyliczyć **dopiero po wdrożeniu fazy B** (snapshot), nie z głowy. Pierwsza wersja testu może mieć `pytest.skip` z TODO, dopóki backend nie jest gotów.

## Acceptance
- [ ] 3 testy istnieją
- [ ] Każdy test wysyła payload zgodny z [00-spec/0002-przypadki-uzycia.md](../../00-spec/0002-przypadki-uzycia.md)
- [ ] Tolerancje udokumentowane w komentarzu
- [ ] Po fazie B oczekiwane wartości są wpisane na podstawie snapshot rzeczywistego wyniku
- [ ] Każda przyszła zmiana stawki = aktualizacja oczekiwanych w PR-ze (z notą w PR description)

## Test plan
```bash
pytest tests/integration/test_real_scenarios.py -v
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: cała faza B
- **Powiązane**: F02 (edge cases)
