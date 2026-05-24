# B03 — Minimalna zdrowotna 2026 (styczeń vs luty)

## Cel
Uwzględnić, że w roku składkowym 2026 minimalna składka zdrowotna dla skali, liniowego i IP Box ma dwie wartości:
- **`314.96` PLN** za styczeń 2026
- **`432.54` PLN** za luty 2026 – styczeń 2027

Aplikacja obecnie używa jednej wartości `432.54` dla całego roku → zawyża minimum o ok. 118 PLN za styczeń.

## Źródło
[AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) — sekcja „Minimalna zdrowotna dla skali, liniowego i IP Box", **BŁĄD**.

Źródło ZUS: https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r.

## Pliki
- [dane_wejsciowe_kalkulator.json:28](../../../dane_wejsciowe_kalkulator.json#L28) — `zus_2026.minimum_health_contribution`
- [src/calculations.py:52, 56, 59, 71](../../../src/calculations.py#L52) — użycie `min_health * 12`
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — nowe testy

## Zmiana w configu

Z:
```json
"minimum_health_contribution": 432.54
```

Na (rekomendowana opcja: dwie wartości jako lista):
```json
"minimum_health_contribution_monthly": [
  { "month": 1,  "amount": 314.96 },
  { "month": 2,  "amount": 432.54 },
  { "month": 3,  "amount": 432.54 },
  { "month": 4,  "amount": 432.54 },
  { "month": 5,  "amount": 432.54 },
  { "month": 6,  "amount": 432.54 },
  { "month": 7,  "amount": 432.54 },
  { "month": 8,  "amount": 432.54 },
  { "month": 9,  "amount": 432.54 },
  { "month": 10, "amount": 432.54 },
  { "month": 11, "amount": 432.54 },
  { "month": 12, "amount": 432.54 }
]
```

Lub uproszczenie (jeśli pełna miesięczna kalkulacja byłaby zbyt rozległa):
```json
"minimum_health_annual_2026": 5072.90
```
(= `314.96 + 11 * 432.54 = 5072.90`)

## Zmiana w `calculations.py`

Zamiast `max(min_health * 12, ...)` użyć `max(config['zus_2026']['minimum_health_annual_2026'], ...)`.

## Acceptance
- [x] Config zawiera albo listę miesięcy, albo wartość roczną
- [x] `calculate_b2b_results` używa **rocznej** sumy, nie `* 12` od jednej wartości
- [x] Test `test_minimum_health_annual_2026` — case: `monthly_invoice_amount=0`, `tax_form='flat_tax'` → `annual_health_contribution = 5072.90`
- [x] `pytest` zielony

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_minimum_health_annual_2026 -v
pytest -q
```

## Rollback
Revert PR + config rollback do `minimum_health_contribution: 432.54`.

## Zależności
- **Wymaga ukończenia**: B02 (kolejność edycji configu)
- **Blokuje**: testy z konkretnymi liczbami w F03

## Notatka
Jeśli zakres remontu zaakceptuje uproszczenie roczne (jedna wartość 5072.90), Codex idzie tą ścieżką. Pełna lista miesięczna ma sens dopiero gdy pojawi się obsługa „rok niepełny / przejście w trakcie roku" — co jest OUT OF SCOPE wg [0001-zakres.md](../../00-spec/0001-zakres.md).
