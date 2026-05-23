# D05 — Usuń `.replace()` w JSX (i18n-safe)

## Cel
Usunąć wszystkie `.replace(' (from company)', '')` z `CalculatorForm.jsx`. Polskie tłumaczenia mają inny sufiks → wynik to „Opłacony urlop (od firmy) Days".

## Źródło
[AUDYT.md §5.4, §6.2](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/dashboard/src/components/CalculatorForm.jsx:193, 211, 229, 247, 265, 283, 301](../../../src/dashboard/src/components/CalculatorForm.jsx#L193)
- [src/dashboard/src/locales/en/translation.json](../../../src/dashboard/src/locales/en/translation.json) — nowe klucze
- [src/dashboard/src/locales/pl/translation.json](../../../src/dashboard/src/locales/pl/translation.json) — j.w.

## Zmiana

Zamiast:
```jsx
label={t('form.paid_vacation').replace(' (from company)', '') + ' Days'}
```

Nowe klucze:
- `form.paid_vacation_days_label` (PL: „Opłacony urlop — dni" / EN: „Paid vacation — days")
- `form.paid_sick_days_label`
- `form.medical_care_value_label` (PL: „Opieka medyczna — wartość (PLN/rok)" / EN: ...)
- `form.life_insurance_value_label`
- `form.sport_card_value_label`
- `form.training_budget_value_label`
- `form.other_benefits_value_label`

Użycie:
```jsx
label={t('form.paid_vacation_days_label')}
```

## Acceptance
- [ ] `git grep '.replace(' src/dashboard/src/components/` zwraca pusto
- [ ] Każdy zmieniony label ma osobny klucz w obu lokalach
- [ ] Test parity i18n zielony (po F04)

## Test plan
```bash
cd src/dashboard && npm test -- CalculatorForm
./run_app.sh  # smoke: zaznacz benefit, sprawdź label w PL i EN
```

## Playwright MCP Verification

Po uruchomieniu `./run_app.sh` użyj narzędzi Playwright MCP:

```
playwright_navigate(url="http://localhost:5173")
# Przełącz język na PL (jeśli jest przełącznik):
playwright_evaluate(script="document.querySelector('[class*=lang],[id*=lang],[data-lang]')?.textContent")
# Sprawdź labele benefitów — nie powinny zawierać "(from company)":
playwright_get_visible_text(selector="[class*=benefit],[class*=form],[class*=label]")
playwright_screenshot(name="D05-pl-labels")
# Sprawdź: NIE MA tekstu "(from company)" w żadnym labelu
playwright_evaluate(script="document.body.innerText.includes('(from company)')")
# Oczekiwany wynik: false

# Sprawdź w EN (jeśli jest przełącznik językowy):
playwright_click(selector="[data-lang='en'],[data-value='en'],button[aria-label*='English']")
playwright_get_visible_text(selector="[class*=benefit],[class*=form],[class*=label]")
playwright_screenshot(name="D05-en-labels")
playwright_evaluate(script="document.body.innerText.includes('(from company)')")
# Oczekiwany wynik: false (labele osobne, nie sklejane przez .replace())
```

## Rollback
Revert PR.

## Zależności
- Niezależne.
- **Wymaga ukończenia**: A05 (life_insurance benefit z UoP usunięty — ale w B2B `lifeInsurance` zostaje, więc klucz potrzebny)
