#!/bin/bash

echo "Stopping B2B vs UoP Calculator..."

# Stop Flask server by finding the process running it
echo "-> Stopping Flask backend..."
pkill -f "flask run"

# Stop Vite server by finding the process
echo "-> Stopping Vite frontend..."
pkill -f "vite"

echo ""
echo "Application stopped."
