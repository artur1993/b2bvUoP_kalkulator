# D08 — Reorganizacja katalogów (`src/` → `backend/` + `frontend/`)

## Cel
Przenieść kod do struktury docelowej z [01-arch/0001-architektura-docelowa.md](../../01-arch/0001-architektura-docelowa.md).

## Decyzja
Tak (potwierdzona 2026-05-23).

## Pliki
- Cały `src/` → `backend/` (zachowując strukturę po D01/D03)
- Cały `src/dashboard/` → `frontend/`
- `dane_wejsciowe_kalkulator.json` → `data/dane_wejsciowe_kalkulator.json`

Plus aktualizacja:
- [pyproject.toml](../../../pyproject.toml) — package_dir / source layout
- [run_app.sh](../../../run_app.sh) — ścieżki
- [stop_app.sh](../../../stop_app.sh) — j.w.
- [CLAUDE.md](../../../CLAUDE.md) — ścieżki w opisie architektury
- Wszystkie testy — importy
- [pytest.ini](../../../pytest.ini) — `pythonpath`

## Strategia 3-stage (jeśli zbyt ryzykowne w jednym PR)

- **D08a** — backend `src/` → `backend/`
- **D08b** — frontend `src/dashboard/` → `frontend/`
- **D08c** — data + tests + tooling

## Acceptance
- [ ] `ls src/` zwraca pusto / nie istnieje
- [ ] `ls backend/` i `ls frontend/` zwracają strukturę z architektury docelowej
- [ ] `pytest -q` zielony
- [ ] `cd frontend && npm test -- --run` zielony
- [ ] `./run_app.sh` startuje
- [ ] CI zielony

## Test plan
```bash
pytest -q
cd frontend && npm test -- --run
./run_app.sh
```

## Rollback
Revert PR. Realne ryzyko: duży diff, konflikty z otwartymi PR-ami. Strategia: zmrozić wszystkie inne PR-y na czas tego.

## Zależności
- **Wymaga ukończenia**: D01, D03 (architektura modułowa najpierw, przeniesienie po)
- **Blokuje**: nowe taski, które używają ścieżek `src/`
- Tylko po pełnej zielonej regresji z faz A-C-D01-D07
