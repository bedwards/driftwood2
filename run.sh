#!/bin/bash

# Quick launch script for Philosophical Dialogue System

echo "════════════════════════════════════════════════════════════════"
echo "   Starting Philosophical Dialogue System"
echo "════════════════════════════════════════════════════════════════"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Launch the application
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo
python app.py