@echo off
echo ========================================
echo     Starting AEGIS System
echo ========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Please run as Administrator!
    pause
    exit /b 1
)

REM Activate virtual environment
call aegis_venv\Scripts\activate

REM Check requirements
if not exist requirements.txt (
    echo requirements.txt not found!
    pause
    exit /b 1
)

REM Install missing packages
echo Checking dependencies...
pip install -r requirements.txt

REM Run AEGIS
echo.
echo Starting AEGIS...
python main.py

REM If AEGIS crashes
echo.
echo AEGIS has stopped.
pause