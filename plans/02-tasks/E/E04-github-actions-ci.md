# E04 — GitHub Actions CI

## Cel
Setup CI: pytest, vitest, lint (ruff, mypy, eslint), playwright smoke.

## Źródło
[AUDYT.md §11.1](../../../AUDYT.md) — WYSOKIE

## Pliki
- `.github/workflows/ci.yml` (nowy)

## Zmiana

```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --all-extras
      - run: uv run ruff check src/ tests/
      - run: uv run mypy src/
      - run: uv run pytest -q --cov=src --cov-fail-under=80
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd src/dashboard && npm ci
      - run: cd src/dashboard && npm run lint
      - run: cd src/dashboard && npm test -- --run
      - run: cd src/dashboard && npm run build
  e2e:
    runs-on: ubuntu-latest
    needs: [backend, frontend]
    steps:
      - uses: actions/checkout@v4
      # ... install both, run playwright smoke
```

## Acceptance
- [ ] CI uruchamia się na push/PR
- [ ] Job `backend` zielony (pytest + ruff + mypy + cov ≥80%)
- [ ] Job `frontend` zielony
- [ ] Job `e2e` zielony (smoke)
- [ ] Branch protection: nie da się zmergować PR-a z czerwonym CI

## Test plan
- Push do branch feature → sprawdź Actions tab w GitHub

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: E01, E02, E03 (lockfile + ruff/mypy + eslint config)
- **Powiązane**: F (testy)
