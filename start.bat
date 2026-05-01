@echo off
title Influenze Relay - WhatsApp Outreach
echo ==============================================
echo        Influenze Relay - Setup ^& Start
echo ==============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please download and install Python 3.10 or newer from python.org
    echo IMPORTANT: Make sure to check the box "Add Python.exe to PATH" during installation.
    echo.
    pause
    exit /b
)

:: Create Virtual Environment if it doesn't exist
if not exist "venv" (
    echo [1/4] Creating virtual environment (this takes a few seconds)...
    python -m venv venv
)

:: Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate

:: Install requirements
echo [3/4] Checking and installing required packages...
pip install -r requirements.txt

:: Install Playwright browsers
echo [4/4] Ensuring WhatsApp automation browser is installed...
playwright install chromium

echo.
echo ==============================================
echo SETUP COMPLETE! Starting the server...
echo.
echo IMPORTANT: DO NOT close this black window while using the tool!
echo.
echo To open the tool, go to your browser and type:
echo http://localhost:5000
echo ==============================================
echo.
python run.py

pause
