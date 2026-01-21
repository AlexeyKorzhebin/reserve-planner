#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="/opt/homebrew/bin/python3.12"
if [ ! -x "$PYTHON_BIN" ]; then
  echo "Не найден Homebrew Python 3.12 по пути $PYTHON_BIN"
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

"$PYTHON_BIN" -m venv --upgrade .venv
.venv/bin/python -m pip install -r requirements.txt >/dev/null
.venv/bin/python -m uvicorn web_app:app --host 127.0.0.1 --port 8000
