# E02 — Ruff + mypy

## Cel
Dodać `ruff` (lint + format) i `mypy --strict` (typing) do projektu.

## Źródło
[AUDYT.md §11.2](../../../AUDYT.md) — WYSOKIE

## Pliki
- [pyproject.toml](../../../pyproject.toml) — dodać do `[project.optional-dependencies].dev` + konfig `[tool.ruff]`, `[tool.mypy]`
- (Opcjonalnie) `ruff.toml` / `mypy.ini`

## Zmiana

```toml
[project.optional-dependencies]
dev = [
  "pytest",
  "pytest-cov",
  "pytest-flask",
  "playwright",
  "ruff>=0.5",
  "mypy>=1.10",
]

[tool.ruff]
line-length = 100
target-version = "py310"
[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP"]

[tool.mypy]
strict = true
files = ["src/"]
```

## Acceptance
- [ ] `ruff check src/` zielony
- [ ] `mypy src/` zielony (po B07 + ewentualnych poprawkach)
- [ ] Konfig w `pyproject.toml`

## Test plan
```bash
ruff check src/ tests/
mypy src/
```

## Rollback
Revert PR.

## Zależności
- Niezależne od B-D w sensie funkcjonalnym, ale mypy --strict może wykryć błędy → fix w trakcie.
- **Powiązane**: E04 (CI uruchamia te lintery)
