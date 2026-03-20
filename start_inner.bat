@echo off
echo Starting Inner Agent Lifecycle...
call .\env\Scripts\activate.bat
python src/lifecycle.py
pause
