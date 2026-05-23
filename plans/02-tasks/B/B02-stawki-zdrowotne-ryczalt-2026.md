# B02 — Stawki zdrowotne ryczałtu 2026

## Cel
Zaktualizować `health_lump_sum_thresholds` w configu do faktycznych wartości ZUS na 2026 rok.

## Źródło
[AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) — sekcja „Zdrowotna na ryczałcie", **BŁĄD**.

Źródło ZUS: https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r.

## Pliki
- [dane_wejsciowe_kalkulator.json:52-56](../../../dane_wejsciowe_kalkulator.json#L52) — `health_lump_sum_thresholds`
- [tests/unit/test_calculations.py](../../../tests/unit/test_calculations.py) — nowe testy dla granicznych wartości

## Zmiana w configu

Z:
```json
"health_lump_sum_thresholds": [
  { "limit": 60000, "contribution": 432.54 },
  { "limit": 300000, "contribution": 720.90 },
  { "limit": "powyzej", "contribution": 1297.62 }
]
```

Na:
```json
"health_lump_sum_thresholds": [
  { "limit": 60000, "contribution": 498.35 },
  { "limit": 300000, "contribution": 830.58 },
  { "limit": "powyzej", "contribution": 1495.04 }
]
```

Plus metadane (zgodnie z B11):
```json
{
  "source_url": "https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r.",
  "source_checked_at": "2026-05-23",
  "valid_from": "2026-02-01",
  "valid_to": "2027-01-31"
}
```

## Acceptance
- [ ] Config zawiera wartości `498.35`, `830.58`, `1495.04`
- [ ] Test `test_health_contribution_lump_sum_threshold_60k` — input `monthly_invoice_amount=5000` (60k roczne) → `monthly_health = 498.35`
- [ ] Test `test_health_contribution_lump_sum_threshold_60k_plus_1` — input `monthly_invoice_amount=5001` → `monthly_health = 830.58`
- [ ] Test `test_health_contribution_lump_sum_threshold_300k` — input `monthly_invoice_amount=25000` (300k roczne) → `monthly_health = 830.58`
- [ ] Test `test_health_contribution_lump_sum_threshold_300k_plus_1` — input `monthly_invoice_amount=25001` → `monthly_health = 1495.04`
- [ ] `pytest tests/unit/test_calculations.py::test_health_contribution_lump_sum_*` zielony

## Test plan
```bash
pytest tests/unit/test_calculations.py::test_health_contribution_lump_sum_threshold_60k -v
pytest tests/unit/test_calculations.py::test_health_contribution_lump_sum_threshold_60k_plus_1 -v
pytest tests/unit/test_calculations.py::test_health_contribution_lump_sum_threshold_300k -v
pytest tests/unit/test_calculations.py::test_health_contribution_lump_sum_threshold_300k_plus_1 -v
pytest -q
```

## Rollback
Revert PR + config rollback do `432.54`, `720.90`, `1297.62`.

## Zależności
- Brak. Może iść równolegle z B01, B03-B12 (ale konflikt config z B03 i B11 — kolejność: B02 → B03 → B11).
- **Blokuje**: testy z konkretnymi liczbami w F03 (zmiana wartości oczekiwanych).
