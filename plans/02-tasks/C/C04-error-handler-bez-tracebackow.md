# C04 — Error handler bez tracebacków

## Cel
Wszystkie error handlery zwracają stałą wiadomość. Szczegóły wyłącznie do logu.

## Źródło
[AUDYT.md §2.4](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/app.py:33-37, 50-52, 65-67, 120-122, 151-153](../../../src/app.py#L33) — wszystkie miejsca z `return jsonify({"error": str(e)})` lub `if app.debug`

## Zmiana

Wszystkie handlery → ten sam wzorzec:
```python
except Exception:
    app.logger.exception("Error in <endpoint_name>")
    return jsonify({"error": "An internal server error occurred."}), 500
```

Usunąć `str(e)`, usunąć `if app.debug`. Pozostawić tylko global error handler oraz może per-endpoint loggery (z `app.logger.exception`).

## Acceptance
- [x] `git grep 'str(e)' src/app.py` zwraca pusto (lub tylko w logach)
- [x] `git grep 'app.debug' src/app.py` zwraca pusto
- [x] Test `test_error_handler_no_traceback` — endpoint który celowo crashuje → response zawiera tylko stałą wiadomość, nie zawiera „Traceback" ani „ValueError" itp.

## Test plan
```bash
pytest tests/integration/test_security.py::test_error_handler_no_traceback -v
```

## Rollback
Revert PR.

## Zależności
- **Powiązane**: C01 (debug mode). Razem usuwają wektor wycieku.
