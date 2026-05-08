@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting CloudShare Pro...
python run.py
pause
