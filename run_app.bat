@echo off
echo Starting Punjab Farm Water Watch Dashboard...
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run app.py
pause
