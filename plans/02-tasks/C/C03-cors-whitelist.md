# C03 — CORS whitelist

## Cel
Zamknąć `CORS(app)` (otwarty na wszystko) na konkretną listę domen z ENV.

## Źródło
[AUDYT.md §2.3](../../../AUDYT.md) — WYSOKIE

## Pliki
- [src/app.py:23](../../../src/app.py#L23) — `CORS(app)`
- `.env.example` (nowy) — przykład `CORS_ORIGINS`

## Zmiana

```python
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=cors_origins)
```

`.env.example`:
```
FLASK_ENV=development
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Acceptance
- [ ] `CORS(app, origins=...)` zamiast `CORS(app)`
- [ ] Domyślna lista: `http://localhost:5173`
- [ ] `.env.example` dokumentuje zmienną
- [ ] Test (manualny): wywołanie z innego Origin → brak `Access-Control-Allow-Origin` w response

## Test plan
```bash
CORS_ORIGINS=http://example.com python src/app.py &
curl -H "Origin: http://attacker.com" http://localhost:5001/api/calculate  # brak ACAO
kill %1
```

## Rollback
Revert PR.

## Zależności
- Niezależne.
