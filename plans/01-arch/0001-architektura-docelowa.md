# 0001 — Architektura docelowa

> Docelowa struktura po fazie D. Fazy A-C działają na obecnym układzie `src/`.

## Backend (po D08)

```
backend/
  app.py                        # cienkie routes, walidacja, error handling
  services/
    calculation_service.py      # run_full_calculation(b2b, uop, mode, lang) → dict
    export_service.py           # build_excel(results) → bytes
  domain/
    b2b/
      lost_revenue.py           # compute_lost_revenue(b2b_data) → float
      social_contributions.py   # compute_social_contributions(b2b_data) → dict
      health_contribution.py    # compute_health_contribution(b2b_data, social) → float
      income_tax.py             # compute_income_tax(b2b_data, ...) → float
      benefits.py               # compute_benefits_value(b2b_data) → dict
      aggregate.py              # assemble_b2b_results(...) → dict
    uop/
      social_contributions.py
      health_contribution.py
      income_tax.py
      author_costs.py
      ppk.py                    # employee_rate + employer_rate
      benefits.py
      aggregate.py
    common/
      break_even.py
      solidarity_tax.py         # compute_solidarity_tax(annual_income) → float
  models/
    b2b.py                      # B2BInput + B2BResult (Pydantic)
    uop.py                      # UoPInput + UoPResult (Pydantic)
    calculation_request.py      # CalculationRequest
  config/
    loader.py                   # ConfigManager (singleton)
    schema.py                   # Pydantic schema dla configu z metadanymi
  utils/
    rounding.py                 # spójne zaokrąglanie (math.ceil → bankers_rounding)
```

## Frontend (po D08)

```
frontend/
  src/
    main.jsx
    App.jsx                     # tylko layout + routing
    state/
      calculatorReducer.js      # useReducer
      CalculatorContext.jsx
    components/
      Form/
        CalculatorForm.jsx
        B2BSection.jsx
        UoPSection.jsx
        BenefitsSection.jsx
      Results/
        ResultsDisplay.jsx
        ComparisonChart.jsx
        WaterfallChart.jsx
        BreakEvenChart.jsx
      common/
        Input.jsx
        Select.jsx
        Checkbox.jsx
        Tooltip.jsx
        Alert.jsx
        ThemeToggle.jsx
    hooks/
      useCalculation.js
      useUrlState.js            # parsing + walidacja URL params
    services/
      api.js                    # tylko transport, bez logiki
    locales/
      en/translation.json
      pl/translation.json
    i18n.js
    index.css
```

## Data

```
data/
  dane_wejsciowe_kalkulator.json   # z metadanymi source_url etc.
```

## Tests

```
tests/
  backend/
    unit/
      test_validation.py
      test_calculations_b2b.py
      test_calculations_uop.py
      test_solidarity_tax.py
      test_edge_cases.py
    integration/
      test_api.py
      test_real_scenarios.py     # Case A/B/C z 00-spec/0002
      test_security.py            # CORS, debug, validation
  frontend/
    components/                  # *.test.jsx obok komponentów (vitest)
  e2e/
    smoke.spec.js
    a11y.spec.js                  # axe-core
    darkmode.spec.js
    urlshare.spec.js
```

## Granice modułów

- **`services/` nie zna Flaska.** Przyjmuje modele Pydantic, zwraca modele Pydantic.
- **`domain/` nie zna `services/` ani Flaska.** Pure functions.
- **`models/` nie zna niczego z `domain/`/`services/`.** Tylko Pydantic + typing.
- **`config/` jest singletonem.** Wszystko inne czyta z niego, nikt do niego nie zapisuje.
- **Frontend `components/` nie zna API.** Tylko propsy + callbacki. API tylko w `services/` i `hooks/`.

## Migracja

Reorganizacja katalogów jest **opcjonalna** dla faz A-C. Codex może zostawić `src/` w fazach A-C i dopiero w D08 zrobić przeniesienie. Powód: minimalizacja konfliktów merge w fazach A/B/C.

Jeśli D08 będzie zbyt ryzykowne (duży diff), Codex może podzielić je na 3 PR-y:
- D08a — backend `src/` → `backend/`
- D08b — frontend `src/dashboard/` → `frontend/`
- D08c — data + tests
