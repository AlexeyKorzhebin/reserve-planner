# Reserve Planner

## Quick start (macOS)
1) Install Python 3.12+ (recommended via Homebrew):
```
brew install python@3.12
```
2) Install dependencies:
```
bash install.sh
```
3) Run the web UI:
```
bash run_web.sh
```
Open: http://127.0.0.1:8000

## Quick start (Windows)
1) Install Python 3.12+ from python.org (enable "Add Python to PATH").
2) Install dependencies:
```
install.bat
```
3) Run the web UI:
```
run_web.bat
```
Open: http://127.0.0.1:8000

## Version check
- `install.sh` and `install.bat` validate Python 3.12+ and show install hints if missing.
- If dependency install fails, check internet/SSL and retry.

## Files
- `web_app.py` — FastAPI web UI.
- `planner.py` — core allocation logic.
- `requirements.txt` — dependencies.
- `install.sh` / `install.bat` — install dependencies.
- `run_web.sh` / `run_web.bat` — run the web UI.
- `Spec/описание_алгоритма_расчета.md` — подробное описание алгоритма.
