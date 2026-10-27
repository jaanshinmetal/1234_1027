@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
py -3 -c "import sys; assert sys.version_info >= (3,11)" >nul 2>&1
if not errorlevel 1 (
    py -3 -m venv .venv
    goto check
)
python -c "import sys; assert sys.version_info >= (3,11)" >nul 2>&1
if not errorlevel 1 (
    python -m venv .venv
    goto check
)
echo Python 3.11 or newer is needed for the Streamlit edition.
echo For the no-install edition, open index.html or start.cmd.
echo Download Python from https://www.python.org/downloads/windows/
pause
exit /b 1
:check
if not exist ".venv\Scripts\python.exe" (
    echo Failed to create Python environment.
    pause
    exit /b 1
)
:install
".venv\Scripts\python.exe" -c "import streamlit" >nul 2>&1
if not errorlevel 1 goto run
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed. Check your internet connection, then try again.
    pause
    exit /b 1
)
:run
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
if errorlevel 1 pause
