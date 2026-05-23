# E01 — Version pinning + lockfile

## Cel
Wprowadzić version pinning w `pyproject.toml` + lockfile (`uv.lock` lub `requirements.txt`).

## Źródło
[AUDYT.md §9.1, §9.2](../../../AUDYT.md) — WYSOKIE

## Pliki
- [pyproject.toml](../../../pyproject.toml) — pin wersji
- `uv.lock` lub `requirements.txt` + `requirements-dev.txt` (nowy)
- [README.md](../../../README.md) — instrukcja `uv sync` lub `pip install -r requirements.txt`

## Zmiana

```toml
dependencies = [
  "Flask>=3.0,<4.0",
  "Flask-Cors>=4.0,<5.0",
  "openpyxl>=3.1,<4.0",
  "pydantic>=2.5,<3.0",
]
```

Po A01 usuwamy `matplotlib`, `fpdf2`, `pypdf`, `weasyprint`.

Lockfile:
```bash
uv sync  # wygeneruje uv.lock
git add uv.lock
```

## Acceptance
- [ ] `pyproject.toml` ma pinning na każdej dep
- [ ] `uv.lock` (lub `requirements.txt`) commitowany
- [ ] README opisuje instalację z lockfile
- [ ] `uv sync` w czystym env odtwarza identyczne wersje

## Test plan
```bash
rm -rf .venv && uv sync && uv run pytest -q
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: A01 (usunięcie PDF deps)
