# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Polish B2B vs. UoP (employment contract) net income calculator for IT professionals, based on 2026 tax/ZUS law. A Flask API backend serves a React (Vite) frontend. All financial constants (ZUS rates, tax brackets, etc.) live in `data/dane_wejsciowe_kalkulator.json` — never hardcode them in Python.

## Project remont w toku — SDD workflow

Aktualnie projekt jest w fazie **remontu metodyką Spec-Driven Development**. Przed jakąkolwiek implementacją przeczytaj:

1. [constitution.md](constitution.md) — sztywne reguły (stack, walidacja, testy, linting)
2. [plans/MASTER.md](plans/MASTER.md) — meta-plan + kolejność faz
3. [plans/README.md](plans/README.md) — jak nawigować po `plans/`
4. Konkretny pod-plan w `plans/02-tasks/<faza>/<id>-<slug>.md`

**Reguła**: 1 pod-plan = 1 branch `feature/<id>-<slug>` = 1 PR.

**Stawki 2026** brać wyłącznie z [AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md](AUDYT_LOGIKA_BIZNESOWA_2026-05-23.md) (status `OK` lub `BŁĄD`). Pozycje `WYMAGA KONSULTACJI` są zablokowane — wymagają osobnej decyzji człowieka.

## Development Commands

### Running the App
```bash
./run_app.sh       # Starts Flask on :5001 and Vite dev server on :5173
./stop_app.sh      # Stops both processes
```

### Backend (Python)
```bash
# Activate venv first
source .venv/bin/activate

# Run all backend tests
pytest

# Run a single test file
pytest tests/unit/test_calculations.py

# Run with coverage
./scripts/backend_cov.sh
```

### Frontend (React/Vite)
```bash
cd frontend
npm run dev        # Dev server
npm run build      # Production build (output to frontend/dist/)
npm run test       # Vitest unit tests
npm run lint       # ESLint
./scripts/frontend_cov.sh   # Coverage report → frontend/coverage/index.html
```

### E2E Tests (Playwright)
```bash
npm run test:e2e   # From project root
```

## Architecture

```
backend/
  app.py              # Flask app — API routes only, no business logic
  calculations.py     # Core B2B and UoP financial calculation functions
  analysis.py         # Executive summary, risk analysis, methodology helpers
  validation.py       # Pydantic-based request validation
  config.py           # Singleton ConfigManager loads data/dane_wejsciowe_kalkulator.json
  domain/             # Pure calculation helpers
  services/           # Backend service layer between routes and domain
frontend/             # React frontend (Vite + Tailwind + Chart.js + i18next)
  src/
    App.jsx
    components/calculator/   # Redesigned UI components:
                             #   form: FormCluster, Field, controls/ (NumberInput, PillList,
                             #         Toggle, Slider, CheckList)
                             #   results/ (VerdictCard, ResultTiles, CompositionBars,
                             #             BreakevenBar, DetailTable, PensionNote)
    state/useCalculatorState.js  # All form state, debounced auto-recalc (250 ms),
                                 #   mapFormToPayload, mapResponseToResult
    services/api.js   # All axios calls to Flask API
    locales/          # i18n translations (en/, pl/)
data/dane_wejsciowe_kalkulator.json   # All tax/ZUS constants for 2026
tests/
  unit/               # Python unit tests
  integration/        # Python integration tests (hit real Flask test client)
  e2e/                # Playwright browser tests
```

**Key data flow:** `App.jsx` + `useCalculatorState` (debounce 250 ms, auto-recalc on every field change) → `mapFormToPayload` → `services/api.js` → `POST /api/calculate` → Pydantic `@validate(...)` → `run_full_calculation` → domain calculation helpers → JSON response (including `config_rates`) → `mapResponseToResult` → `calculator/results/` components (VerdictCard, ResultTiles, CompositionBars, BreakevenBar, DetailTable, PensionNote).

**Config singleton:** `config_manager` in `backend/config.py` is a thread-safe singleton. Access constants via `config_manager.get_config()` in any Python module. Never import constants directly.

**Flask serves the built React app** from `frontend/dist/` as static files in production. In development, Vite runs separately with proxy to Flask on :5001.

## Test Naming Convention

Backend tests use suffixes to classify intent:
- `_positive` — expected successful behavior
- `_negative` — error handling / invalid input
- `_neutral` — mixed or ambiguous

## i18n

Translations are in `frontend/src/locales/en/translation.json` and `frontend/src/locales/pl/translation.json`. All user-visible strings in React components must use `useTranslation()` / `t('key')` — never hardcode Polish or English strings in JSX.
