@echo off
setlocal

if not exist .venv (
  echo Virtual env not found. Run install.bat first.
  exit /b 1
)

.\.venv\Scripts\python -m uvicorn web_app:app --host 127.0.0.1 --port 8000
