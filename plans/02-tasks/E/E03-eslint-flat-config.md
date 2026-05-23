# E03 — ESLint flat config

## Cel
Dodać `eslint.config.js` (flat config) z plugin'ami `react`, `react-hooks`, `react-refresh`.

## Źródło
[AUDYT.md §11.6](../../../AUDYT.md) — NISKIE

## Pliki
- `src/dashboard/eslint.config.js` (lub `frontend/eslint.config.js` po D08)

## Acceptance
- [ ] `eslint.config.js` istnieje
- [ ] `npm run lint` zielony
- [ ] CI fails on warnings (z `--max-warnings 0`)

## Test plan
```bash
cd src/dashboard && npm run lint
```

## Rollback
Revert PR.

## Zależności
- **Powiązane**: E04 (CI lint)
