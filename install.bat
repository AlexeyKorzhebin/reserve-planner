@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install Python 3.12+ and try again.
  echo Download: https://www.python.org/downloads/windows/
  exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python -V 2^>^&1') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYVER%") do (
  set PYMAJOR=%%a
  set PYMINOR=%%b
)
if %PYMAJOR% LSS 3 (
  echo Python 3.12+ required. Found %PYVER%.
  exit /b 1
)
if %PYMAJOR% EQU 3 if %PYMINOR% LSS 12 (
  echo Python 3.12+ required. Found %PYVER%.
  exit /b 1
)

if not exist .venv (
  python -m venv .venv
) else (
  python -m venv --upgrade .venv
)

.\.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install dependencies. Check internet/SSL.
  exit /b 1
)
echo Ready. Run: run_web.bat
