@echo off
echo Starting Punjab Farm Water Watch Standalone Web App...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python server.py
pause
