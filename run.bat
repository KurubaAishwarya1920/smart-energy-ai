@echo off
REM Smart Energy AI - one-command start for Windows.
cd /d "%~dp0"

if not exist ".venv" (
  echo Creating a virtual environment...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
echo Starting Smart Energy AI on http://127.0.0.1:5000
python run.py
