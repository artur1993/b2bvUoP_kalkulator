#!/bin/bash
set -euo pipefail

echo "Stopping B2B vs UoP Calculator..."

# Stop Flask server
if [ -f .flask.pid ]; then
    PID=$(cat .flask.pid)
    echo "-> Stopping Flask backend (PID $PID)..."
    kill "$PID" 2>/dev/null || echo "Flask process not found."
    rm .flask.pid
else
    echo "-> .flask.pid not found. Is the backend running?"
fi

# Stop Vite server
if [ -f .vite.pid ]; then
    PID=$(cat .vite.pid)
    echo "-> Stopping Vite frontend (PID $PID)..."
    kill "$PID" 2>/dev/null || echo "Vite process not found."
    rm .vite.pid
else
    echo "-> .vite.pid not found. Is the frontend running?"
fi

echo ""
echo "Application stopped."
