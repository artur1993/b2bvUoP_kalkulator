#!/bin/bash

echo "Starting B2B vs UoP Calculator..."

# Start Flask Backend in the background
echo "-> Starting Flask backend..."
export FLASK_APP=src/app.py
export FLASK_DEBUG=1
flask run --port 5001 &> flask.log &

# Start Vite Frontend in the background and capture its output
echo "-> Starting Vite frontend..."
vite_output_file="vite_output.log"
(cd src/dashboard && npm run dev -- --host > "../../$vite_output_file" 2>&1 &)

echo "Waiting for Vite to start..."
sleep 5 # Give Vite a moment to start up

# Extract the URL from the Vite output
VITE_URL=$(grep -o 'http://localhost:[0-9]\{4\}' "$vite_output_file" | head -n 1)

if [ -n "$VITE_URL" ]; then
    echo ""
    echo "----------------------------------------"
    echo "  Application is running!"
    echo "  Frontend available at: $VITE_URL"
    echo "----------------------------------------"
else
    echo "Could not determine the frontend URL. Please check vite_output.log for details."
fi

echo "Backend logs are in: flask.log"
echo "Frontend logs are in: vite_output.log"
echo "To stop the application, run: ./stop_app.sh"