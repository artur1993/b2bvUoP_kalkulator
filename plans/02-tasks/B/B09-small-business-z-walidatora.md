# B09 — Usuń `small_business` z walidatora + dodaj `start_relief` do UI

## Cel
Naprawić dwie niespójności walidator/config/UI:
1. Walidator akceptuje `small_business`, config nie ma tej gałęzi → `KeyError 500`.
2. Walidator i config akceptują `start_relief`, ale UI go nie pokazuje.

## Źródło
- [AUDYT.md §3.2](../../../AUDYT.md) — KRYTYCZNE

Mały ZUS Plus jako pełna funkcjonalność: [03-backlog/maly-zus-plus.md](../../03-backlog/maly-zus-plus.md).

## Pliki
- [src/validation.py:14](../../../src/validation.py#L14) — pattern dla `zus_type`
- [src/dashboard/src/components/CalculatorForm.jsx:12-15](../../../src/dashboard/src/components/CalculatorForm.jsx#L12) — `zusOptions`
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucz `form.zus_start_relief`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.
- [tests/unit/test_validation.py](../../../tests/unit/test_validation.py) — nowy test

## Zmiana

### Walidator
Z:
```python
zus_type: str = Field(..., pattern='^(start_relief|small_business|preferential|full)$')
```

Na:
```python
zus_type: str = Field(..., pattern='^(start_relief|preferential|full)$')
```

### UI
W `CalculatorForm.jsx`, `zusOptions`:
```javascript
const zusOptions = [
  { value: 'start_relief', label: t('form.zus_start_relief') },
  { value: 'preferential', label: t('form.zus_preferential') },
  { value: 'full', label: t('form.zus_full') },
];
```

### Tłumaczenia
Dodać `form.zus_start_relief`:
- PL: „Ulga na start (6 miesięcy)"
- EN: „Start relief (first 6 months)"

Opcjonalnie tooltip: „Brak składek społecznych przez pierwsze 6 miesięcy działalności gospodarczej. Składka zdrowotna obowiązuje."

## Acceptance
- [ ] Walidator: payload `{"b2b": {"zus_type": "small_business"}}` → **400**
- [ ] Walidator: payload `{"b2b": {"zus_type": "start_relief"}}` → **200** (działa)
- [ ] UI: dropdown ZUS pokazuje 3 opcje (start_relief, preferential, full)
- [ ] Test `test_zus_type_small_business_rejected` — 400 z message
- [ ] Test `test_zus_type_start_relief_accepted` — działa, wynik liczbowy zgodny z config (zerowe składki społeczne)
- [ ] Test `test_calculate_with_start_relief_zus` — `monthly_invoice_amount=10000`, `zus_type='start_relief'` → ZUS społeczne = 0, zdrowotna = wybrana wg `tax_form`

## Test plan
```bash
pytest tests/unit/test_validation.py::test_zus_type_* -v
pytest tests/unit/test_calculations.py::test_calculate_with_start_relief_zus -v
pytest -q
cd src/dashboard && npm test -- CalculatorForm
./run_app.sh  # smoke: ZUS dropdown ma „Ulga na start"
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
# Sprawdź dropdown ZUS — musi mieć dokładnie 3 opcje:
playwright_evaluate(script="document.querySelector('select[name*=zus_type],select[id*=zus_type]')?.options.length")
# Oczekiwany wynik: 3

# Sprawdź, że "Ulga na start" jest wśród opcji:
playwright_evaluate(script="[...document.querySelector('select[name*=zus_type],select[id*=zus_type]')?.options || []].map(o => o.value)")
# Oczekiwany wynik: ['start_relief', 'preferential', 'full'] (kolejność może się różnić)

playwright_screenshot(name="B09-zus-dropdown-3-options")

# Sprawdź, że 'small_business' NIE jest opcją:
playwright_evaluate(script="[...document.querySelector('select[name*=zus_type],select[id*=zus_type]')?.options || []].map(o => o.value).includes('small_business')")
# Oczekiwany wynik: false
```

## Rollback
Revert PR. `start_relief` w configu zostaje — był tam już wcześniej.

## Zależności
- Niezależne.
- **Powiązane**: [03-backlog/maly-zus-plus.md](../../03-backlog/maly-zus-plus.md) — pełna obsługa Mały ZUS Plus to osobny projekt.
