# G05 — `run_app.sh` / `stop_app.sh`: bezpieczne

## Cel
Dodać `set -euo pipefail`, PID file zamiast `pkill`, eliminować race conditions (hardcoded `sleep 5`).

## Źródło
[AUDYT.md §11.4, §11.5](../../../AUDYT.md)

## Pliki
- [run_app.sh](../../../run_app.sh)
- [stop_app.sh](../../../stop_app.sh)

## Zmiana

### `run_app.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

. .venv/bin/activate

echo "Starting B2B vs UoP Calculator..."

# Backend
echo "-> Starting Flask backend..."
export FLASK_APP=src/app.py
export FLASK_ENV=${FLASK_ENV:-development}
export PYTHONPATH=${PYTHONPATH:-}:$(pwd)
flask run --host 0.0.0.0 --port 5001 &> flask.log &
echo $! > .flask.pid

# Frontend
echo "-> Starting Vite frontend..."
(cd src/dashboard && npm run dev -- --host > "../../vite_output.log" 2>&1 &)
echo $! > .vite.pid

# Wait for Vite (do 30 sek z timeoutem)
echo "Waiting for Vite to start..."
for i in {1..60}; do
  if grep -q 'http://localhost:[0-9]\{4\}' vite_output.log 2>/dev/null; then
    break
  fi
  sleep 0.5
done

VITE_URL=$(grep -o 'http://localhost:[0-9]\{4\}' vite_output.log | head -n 1)

if [ -n "$VITE_URL" ]; then
  echo "Application is running at: $VITE_URL"
else
  echo "Could not determine the frontend URL. Check vite_output.log."
fi
```

### `stop_app.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

for pidfile in .flask.pid .vite.pid; do
  if [ -f "$pidfile" ]; then
    pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" && echo "Killed $pidfile ($pid)"
    fi
    rm -f "$pidfile"
  fi
done
```

## Acceptance
- [ ] `run_app.sh` ma `set -euo pipefail`
- [ ] `stop_app.sh` używa PID files, nie `pkill`
- [ ] Timeout 30s na czekanie na Vite, nie hardcoded sleep
- [ ] `.flask.pid` i `.vite.pid` w `.gitignore` (G01)

## Test plan
```bash
./run_app.sh
sleep 5
./stop_app.sh
ls .flask.pid .vite.pid  # nie istnieją
```

## Rollback
Revert PR.

## Zależności
- **Wymaga ukończenia**: G01 (gitignore zawiera .pid)
- **Powiązane**: C01 (FLASK_ENV zamiast FLASK_DEBUG)
