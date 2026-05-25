#!/bin/bash
set -euo pipefail

# Activate virtual environment
if [ -d ".venv" ]; then
    . .venv/bin/activate
elif [ -d "venv" ]; then
    . venv/bin/activate
fi

echo "Starting B2B vs UoP Calculator..."

# Start Flask Backend in the background
echo "-> Starting Flask backend..."
export FLASK_APP=backend/app.py
export FLASK_ENV=development
export PYTHONPATH=$PYTHONPATH:$(pwd)
nohup flask run --host 0.0.0.0 --port 5001 &> flask.log &
echo $! > .flask.pid

# Start Vite Frontend in the background
echo "-> Starting Vite frontend..."
vite_output_file="vite_output.log"
pushd frontend > /dev/null
nohup npm run dev -- --host > "../$vite_output_file" 2>&1 &
echo $! > ../.vite.pid
popd > /dev/null

echo "Waiting for Vite to start (max 30s)..."
# Loop to wait for Vite to start
timeout=30
counter=0
VITE_URL=""

while [ $counter -lt $timeout ]; do
    VITE_URL=$(grep -o 'http://localhost:[0-9]\{4\}' "$vite_output_file" | head -n 1 || true)
    if [ -n "$VITE_URL" ]; then
        break
    fi
    sleep 1
    counter=$((counter + 1))
done

if [ -n "$VITE_URL" ]; then
    echo ""
    echo "----------------------------------------"
    echo "  Application is running!"
    echo "  Frontend available at: $VITE_URL"
    echo "----------------------------------------"
else
    echo "Timeout reached or Vite failed to start. Please check vite_output.log for details."
fi

echo "Backend logs are in: flask.log"
echo "Frontend logs are in: vite_output.log"
echo "To stop the application, run: ./stop_app.sh"
