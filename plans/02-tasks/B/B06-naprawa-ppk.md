# B06 — Naprawa PPK (employee vs employer)

## Cel
Naprawić błędny model PPK: aplikacja traktuje 2% jako benefit, mylc wpłatę pracownika z dopłatą pracodawcy. Powinno być:
- **Wpłata pracownika 2%** — z brutto, opodatkowana PIT (potrąca dochód netto).
- **Wpłata pracodawcy 1,5%** — benefit, ale jest **przychodem pracownika** (opodatkowany PIT).

## Źródło
- [AUDYT.md §3.4](../../../AUDYT.md) — WYSOKIE
- [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) — sekcja „PPK", **BŁĄD**

Źródło: https://www.mojeppk.pl/ (oficjalny portal PPK)

## Pliki
- [dane_wejsciowe_kalkulator.json:67](../../../dane_wejsciowe_kalkulator.json#L67) — `benefits.ppk: 0.02`
- [src/calculations.py:222-224](../../../src/calculations.py#L222) — logika PPK w UoP
- [src/dashboard/src/components/CalculatorForm.jsx:29](../../../src/dashboard/src/components/CalculatorForm.jsx#L29) — opcja `ppk`
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucze `form.benefit_ppk*`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — nowe testy

## Zmiana w configu

Z:
```json
"benefits": {
  "ppk": 0.02
}
```

Na:
```json
"ppk": {
  "employee_rate": 0.02,
  "employer_rate": 0.015,
  "source_url": "https://www.mojeppk.pl/",
  "source_checked_at": "2026-05-23",
  "valid_from": "2026-01-01",
  "valid_to": "2026-12-31"
}
```

(Sekcja `benefits` zostaje bez `ppk`.)

## Zmiana w `calculate_uop_results`

Nowa logika PPK (jeśli użytkownik zaznaczył):
1. Wpłata pracownika `monthly_ppk_employee = monthly_gross_salary * 0.02` — odjęta z brutto przed PIT (czyli wpływa na `monthly_tax_base`).
2. Wpłata pracodawcy `monthly_ppk_employer = monthly_gross_salary * 0.015` — dodana do `monthly_tax_base` jako przychód, a po PIT dodana do `total_uop_value` jako benefit netto.

Pseudokod:
```python
if 'ppk' in uop_data.get('selected_benefits', []):
    ppk_rates = config['ppk']
    monthly_ppk_employee = monthly_gross_salary * ppk_rates['employee_rate']
    monthly_ppk_employer = monthly_gross_salary * ppk_rates['employer_rate']
    # 1. employee part lowers tax base
    monthly_tax_base = max(0, monthly_gross_salary - monthly_social - monthly_costs - monthly_ppk_employee)
    # 2. employer part adds to tax base (income for employee)
    monthly_tax_base += monthly_ppk_employer
    # 3. annualnie po PIT dodajemy net employer contribution do benefits
    annual_ppk_employer_net = monthly_ppk_employer * 12 * (1 - effective_tax_rate)
    benefits_value += annual_ppk_employer_net
    # 4. employee 2% nie wraca jako benefit — to są jego pieniądze, lokowane w PPK
```

(Codex może uprościć implementację, ale efekt księgowy musi być zgodny z powyższym.)

## Acceptance
- [x] Config: `ppk.employee_rate=0.02`, `ppk.employer_rate=0.015`
- [x] Sekcja `benefits` nie zawiera `ppk`
- [x] Logika UoP odejmuje wpłatę pracownika z brutto przed PIT
- [x] Logika UoP dodaje wpłatę pracodawcy do `monthly_tax_base` oraz jako net-benefit
- [x] Test `test_ppk_employee_contribution_lowers_net` — pensja 10 000 brutto z PPK → netto **niższe** niż bez PPK (o ~2% × 12 = 240 PLN/mies. mniej w gotówce)
- [x] Test `test_ppk_employer_contribution_is_taxed_benefit` — pensja 10 000 brutto z PPK → `total_annual_value` wyższe o ~1,5% × 12 × (1-stawka_PIT) = ~1 584 PLN
- [x] Test `test_ppk_disabled_no_changes` — pensja 10 000 bez PPK → wynik identyczny jak przed B06

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_ppk_* -v
pytest -q
cd src/dashboard && npm test -- --run
```

## Rollback
Revert PR + config rollback.

## Zależności
- Niezależne od B01-B05, B07-B12.
- **Blokuje**: F03 (Case A z `medical_care`, ale gdy dodamy PPK do dowolnego case'a to wpłynie).

## Notatka
Dokładny model „PIT od dopłaty pracodawcy" wymaga decyzji: czy liczymy efektywną stawkę PIT pracownika (skala 12%/32% lub PIT-0 jeśli <26)? Codex powinien dodać komentarz w kodzie o uproszczeniu i odnotować w pliku planu, jeśli uzna potrzebę uproszczenia.
