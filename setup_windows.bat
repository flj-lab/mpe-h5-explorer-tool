@echo off
setlocal

REM Script to set up Python virtual environment and install dependencies for the MPE Exporter tool on Windows.

set VENV_DIR=venv
set REQUIREMENTS_FILE=requirements.txt

echo --- MPE Exporter Windows Setup ---

REM 1. Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/ and ensure it's added to your PATH.
    goto :eof
)
echo Python found.

REM 2. Check for pip (usually comes with Python)
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: pip is not installed or not in PATH.
    echo This usually comes with Python. Try reinstalling Python or ensuring your Scripts directory is in PATH.
    goto :eof
)
echo pip found.

REM 3. Check for tkinter
echo Checking for tkinter availability...
python -c "import tkinter" >nul 2>nul
if %errorlevel% neq 0 (
    echo Warning: Python's tkinter module seems to be missing or not correctly installed.
    echo This is often needed for matplotlib GUIs and other parts of the tool.
    echo Please ensure "tcl/tk and IDLE" was selected during Python installation.
    echo You might need to modify your Python installation (via Apps & features) or reinstall Python.
    echo After ensuring tkinter is available, you might need to re-run this script.
)

REM 4. Create virtual environment
if exist "%VENV_DIR%" (
    echo Virtual environment '%VENV_DIR%' already exists. Skipping creation.
) else (
    echo Creating virtual environment in ".\%VENV_DIR%\"...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment.
        echo Make sure the 'venv' module is available with your Python installation.
        goto :eof
    )
    echo Virtual environment created.
)

REM 5. Activate virtual environment and install requirements
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo Installing dependencies from %REQUIREMENTS_FILE%...
pip install -r "%REQUIREMENTS_FILE%"
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    call "%VENV_DIR%\Scripts\deactivate.bat"
    goto :eof
)

echo.
echo --- Setup Complete ---
echo To activate the virtual environment in your current terminal session, run:
echo   %VENV_DIR%\Scripts\activate.bat
echo After activation, you can run the project's Python scripts.
echo To deactivate, simply type 'deactivate' (or close and reopen the command prompt).

:eof
endlocal