# C01 — Debug mode z ENV

## Cel
Wyłączyć `app.debug=True` z hardkodu. Tryb debug wyłącznie przez ENV `FLASK_ENV=development`.

## Źródło
[AUDYT.md §2.1](../../../AUDYT.md) — KRYTYCZNE

## Pliki
- [src/app.py:169](../../../src/app.py#L169) — `app.run(debug=True, ...)`
- [src/app.py:122](../../../src/app.py#L122) — `if app.debug` w error handlerze
- [run_app.sh:11](../../../run_app.sh#L11) — `export FLASK_DEBUG=1`
- [tests/integration/test_security.py](../../../tests/integration/test_security.py) — nowy plik testowy

## Zmiana

```python
if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, use_reloader=False, port=5001)
```

W `run_app.sh`: zostaw `FLASK_ENV=development` (dev), usuń `FLASK_DEBUG=1` lub przepisz na opcjonalne.

W error handlerze: zawsze zwracać stałą wiadomość, niezależnie od `app.debug` (powiązane z C04).

## Acceptance
- [ ] `app.run(debug=...)` czyta ENV, nie hardkoduje
- [ ] `FLASK_ENV=production python src/app.py` → brak `/console`, brak hot-reload
- [ ] Test `test_debug_mode_disabled_by_default` — bez ENV, debug=False
- [ ] Test `test_debug_mode_enabled_via_env` — FLASK_ENV=development, debug=True

## Test plan
```bash
FLASK_ENV=production python src/app.py &
curl http://localhost:5001/console  # 404, nie debugger
kill %1
pytest tests/integration/test_security.py::test_debug_mode_* -v
```

## Rollback
Revert PR.

## Zależności
- Niezależne. Równolegle z B.
- **Powiązane**: C04 (error handler).
