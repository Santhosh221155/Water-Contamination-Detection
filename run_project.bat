@echo off
title Water Quality Monitoring System
cls
echo ========================================================
echo   Water Quality Monitoring System - Startup Script
echo ========================================================
echo.
echo [1/3] Starting Flask Backend...
start "Flask Backend" cmd /k "cd backend && python app.py"
echo    - Backend running in new window.
echo.
echo.
echo.
echo [3/3] Waiting for you...
echo.
echo    ACTION REQUIRED:
echo    1. Go to VS Code.
echo    2. Open 'firmware/water_quality_monitor.ino'.
echo    3. Press F1 and run "Wokwi: Start Simulator".
echo.
echo    The Bridge window will automatically connect when
echo    the simulation starts!
echo.
echo ========================================================
echo    Press any key to exit this launcher...
pause >nul
