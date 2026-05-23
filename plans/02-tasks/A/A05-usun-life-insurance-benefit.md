# A05 — Usuń `life_insurance` benefit z UoP

## Cel
Usunąć opcję `life_insurance` z UoP — opcja jest w UI, ale brakuje w `dane_wejsciowe_kalkulator.json.benefits`, więc martwy kod (nie wpływa na wynik).

## Źródło
[AUDYT_UZUPELNIENIE.md §1.3](../../../AUDYT_UZUPELNIENIE.md) — „Benefit UoP `life_insurance` jest widoczny w formularzu, ale nie ma w konfiguracji".

## Pliki
- [src/dashboard/src/components/CalculatorForm.jsx:27](../../../src/dashboard/src/components/CalculatorForm.jsx#L27) — `{ value: 'life_insurance', label: t('form.benefit_life') }`
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — klucz `form.benefit_life`
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.

## Acceptance
- [x] `benefitOptions` w `CalculatorForm.jsx` nie zawiera `life_insurance`
- [x] Klucz `form.benefit_life` usunięty z obu locale files
- [x] UI nie pokazuje checkboxa „ubezpieczenie na życie" w sekcji benefitów UoP
- [x] Test parity i18n zielony (po F04)

## Test plan
```bash
git grep -i 'life_insurance\|benefit_life' src/  # pusto
cd src/dashboard && npm test -- --run
./run_app.sh  # smoke: sekcja UoP benefits ma 4 opcje (medical, sport, training, ppk)
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
# Znajdź sekcję benefitów UoP i sprawdź liczbę opcji:
playwright_evaluate(script="document.querySelectorAll('[name*=benefit],[id*=benefit]').length")
# Sprawdź, że nie ma checkboxa życie / life insurance:
playwright_get_visible_text(selector="body")
# Sprawdź: NIE MA tekstu "ubezpieczenie na życie", "life insurance"
playwright_screenshot(name="A05-uop-benefits")
```

## Rollback
Revert PR.

## Zależności
- Brak. Równolegle z A01-A04.
- **Blokuje**: A06 (README, jeśli benefit life_insurance był tam wymieniony).
