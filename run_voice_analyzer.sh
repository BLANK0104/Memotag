#!/bin/bash

echo "MemoTag Voice Analysis Tool Launcher"
echo "===================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found! Please install Python 3.7 or higher."
    echo "Visit https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo "Using Python:"
python3 --version
echo

# Check for required packages and install if missing
echo "Checking dependencies..."
python3 -m pip install -r requirements.txt
echo

# Check for audio analysis dependencies
python3 -c "import importlib; print('Audio analysis:', 'ENABLED' if importlib.util.find_spec('librosa') and importlib.util.find_spec('soundfile') else 'DISABLED (see AUDIO_SETUP.md)')"
echo

echo "Starting Voice Analyzer..."
echo
python3 voice_analyzer.py
echo

read -p "Press Enter to exit..."
