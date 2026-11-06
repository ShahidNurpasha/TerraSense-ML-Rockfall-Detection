@echo off
title Rockfall Early Warning and Response Coordination System
cd /d "%~dp0"
echo ============================================================
echo   Rockfall Early Warning and Response Coordination System
echo ============================================================
echo Starting Flask web server...
start "" "http://127.0.0.1:5000"
python app.py
pause
