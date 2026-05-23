# E05 — Pre-commit hooks

## Cel
Dodać `.pre-commit-config.yaml` z hookami: ruff, mypy, eslint, prettier.

## Źródło
[AUDYT.md §11.3](../../../AUDYT.md) — ŚREDNIE

## Pliki
- `.pre-commit-config.yaml` (nowy)
- README: instrukcja `pre-commit install`

## Zmiana

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        files: ^src/
  - repo: local
    hooks:
      - id: eslint
        name: eslint
        entry: bash -c 'cd src/dashboard && npx eslint .'
        language: system
        files: ^src/dashboard/.*\.(js|jsx)$
```

## Acceptance
- [ ] `.pre-commit-config.yaml` istnieje
- [ ] `pre-commit install` w README
- [ ] Lokalny `git commit` triggeruje hooki

## Test plan
```bash
pre-commit install
pre-commit run --all-files
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: E02, E03
