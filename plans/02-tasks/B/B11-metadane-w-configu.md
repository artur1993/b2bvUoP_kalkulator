# B11 — Metadane `source_url` w configu

## Cel
Każda gałąź regulacyjna w `dane_wejsciowe_kalkulator.json` dostaje 4 pola metadanych: `source_url`, `source_checked_at`, `valid_from`, `valid_to`. Zgodne z konstytucją.

## Źródło
- [constitution.md](../../../constitution.md) — sekcja „Audyt config"
- [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](../../../AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) — linki do źródeł

## Pliki
- [dane_wejsciowe_kalkulator.json](../../../dane_wejsciowe_kalkulator.json) — refaktor schematu
- [src/config.py](../../../src/config.py) — `ConfigManager` musi obsłużyć nowy schemat (z metadanymi)
- [src/calculations.py](../../../src/calculations.py) — odczyty configu mogą wymagać `[].value` zamiast `[]`
- [tests/unit/test_config.py](../../../tests/unit/test_config.py) — nowy plik testowy

## Strategia: schemat z metadanymi

Opcja A (minimum, mniej zmian w kodzie): osobna gałąź `_meta`:
```json
{
  "tax_thresholds": { ... },
  "zus_2026": { ... },
  "_meta": {
    "tax_thresholds": {
      "source_url": "https://www.podatki.gov.pl/podatki-osobiste/pit/stawki-i-limity/",
      "source_checked_at": "2026-05-23",
      "valid_from": "2026-01-01",
      "valid_to": "2026-12-31"
    },
    "zus_2026": { ... },
    "zus_2026.health_lump_sum_thresholds": { ... }
  }
}
```

Opcja B (czystsza, więcej zmian): każda wartość jako `{ value, source_url, source_checked_at, valid_from, valid_to }`.

**Rekomendacja**: Opcja A (mniejszy rozmiar PR). Opcja B w fazie D02 razem z magic numbers.

## Źródła do wpisania (z AUDYT_LOGIKA_BIZNESOWA)

| Gałąź | source_url |
|-------|-----------|
| `tax_thresholds` | https://www.podatki.gov.pl/podatki-osobiste/pit/stawki-i-limity/ |
| `tax_deductible_costs` | https://www.podatki.gov.pl/podatki-osobiste/pit/stawki-i-limity/ |
| `zus_2026` (społeczne, limit 30x) | https://www.zus.pl/baza-wiedzy/skladki-wskazniki-odsetki/skladki/wysokosc-skladek-na-ubezpieczenia-spoleczne |
| `zus_2026.health_lump_sum_thresholds` | https://www.zus.pl/-/informacja-w-sprawie-podstawy-wymiaru-sk%C5%82adki-oraz-kwoty-sk%C5%82adki-na-ubezpieczenie-zdrowotne-w-2026-r. |
| `zus_2026.minimum_health_contribution*` | j.w. |
| `tax_thresholds.health_contribution_deduction_limit_flat_tax` | https://www.podatki.gov.pl/ulgi-i-odliczenia/odliczenie-skladek-na-ubezpieczenie-zdrowotne-pit/ |
| `pension_limits_2026.ike` | https://www.knf.gov.pl/?articleId=81021&p_id=18 |
| `pension_limits_2026.ikze*` | https://www.gov.pl/web/rodzina/ikze-limit-wplat |
| `ppk` (po B06) | https://www.mojeppk.pl/ |

`source_checked_at`: `2026-05-23` (data audytu).
`valid_from`/`valid_to`: zależnie od pozycji — większość `2026-01-01` / `2026-12-31`, składka zdrowotna minimum ma dwa okresy (patrz B03).

## Acceptance
- [ ] `dane_wejsciowe_kalkulator.json` zawiera sekcję `_meta` (lub schemat z `value`) ze wszystkimi gałęziami
- [ ] Każda kwota regulacyjna ma `source_url` i `source_checked_at`
- [ ] `ConfigManager` ładuje config bez błędu (z nowym schematem)
- [ ] Stare wywołania `config['zus_2026']['full']` działają (jeśli wybrano Opcję A)
- [ ] Test `test_config_has_metadata_for_all_regulatory_branches` — iteruje po listy gałęzi, sprawdza obecność 4 pól w `_meta`

## Test plan
```bash
pytest tests/unit/test_config.py -v
pytest -q
./run_app.sh  # smoke: nadal liczy
```

## Rollback
Revert PR + config rollback.

## Zależności
- **Wymaga ukończenia**: B02, B03, B06 (kolejność edycji configu — wartości najpierw, metadane na końcu)
- Niezależne od innych taksów B
