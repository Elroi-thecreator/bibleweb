@echo off
setlocal
title Holy Bible - வேதம் Desktop Launcher

echo ========================================================
echo   Launching Holy Bible (வேதம்) Windows Desktop App
echo ========================================================
echo.

cd /d "%~dp0"

:: 1. Check for Virtual Environment Python
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    goto :RUN
)

:: 2. Check for py -3 launcher
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=py -3"
    goto :RUN
)

:: 3. Check for standard python
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto :RUN
)

echo [ERROR] Python 3 was not found on your system!
echo Please install Python from https://www.python.org/ or the Microsoft Store.
pause
exit /b 1

:RUN
echo Using Python: %PYTHON_EXE%
echo.

%PYTHON_EXE% windows_app\app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [NOTE] An error occurred while running the desktop application.
    pause
)
