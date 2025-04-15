@echo off
echo MemoTag Voice Analysis Tool Launcher
echo ====================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found! Please install Python 3.7 or higher.
    echo Visit https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Display Python version
echo Using Python:
python --version
echo.

:: Check for required packages and install if missing
echo Checking dependencies...
python -c "import sys, subprocess; subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])"
echo.

:: Check for audio analysis dependencies
python -c "import importlib; print('Audio analysis:', 'ENABLED' if importlib.util.find_spec('librosa') and importlib.util.find_spec('soundfile') else 'DISABLED (see AUDIO_SETUP.md)')"
echo.

echo Starting Voice Analyzer...
echo.
python voice_analyzer.py
echo.

pause
