# G01 — Aktualizacja `.gitignore`

## Cel
Dodać brakujące wpisy do `.gitignore`.

## Źródło
[AUDYT.md §10.1](../../../AUDYT.md)

## Pliki
- [.gitignore](../../../.gitignore)

## Zmiana

Dodać:
```
.venv/
.playwright-mcp/
*.egg-info/
*_manual.log
src/dashboard/coverage/
.coverage
htmlcov/
```

## Acceptance
- [x] `.gitignore` zawiera powyższe wpisy
- [x] `git status` po `./run_app.sh` nie pokazuje śmieci

## Test plan
```bash
./run_app.sh
git status  # powinno być czysto poza commitowanymi zmianami
```

## Rollback
Revert PR.

## Zależności
- Niezależne. Może iść w dowolnej fazie.
