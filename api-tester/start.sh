#!/bin/bash

echo "Starting XivMind API Tester..."
echo ""
echo "Make sure the main XivMind application is running on port 8000"
echo ""

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "Starting API Tester on port 8001..."
echo "Open http://localhost:8001 in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --port 8001
