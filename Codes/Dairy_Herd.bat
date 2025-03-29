
@echo off
REM Check if Python is installed and available in the PATH
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not added to the PATH.
    pause
    exit /b
)

REM Navigate to the directory where your script is located
cd /d %~dp0

REM Install required packages from requirements.txt
REM This assumes you have a requirements.txt file in the same directory as main.py
IF EXIST requirements.txt (
    echo Installing necessary packages...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
) ELSE (
    echo requirements.txt not found, skipping package installation...
)

REM Run the Python script
python main.py

REM Pause the terminal window after execution
pause



