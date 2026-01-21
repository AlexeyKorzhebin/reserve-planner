#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="/opt/homebrew/bin/python3.12"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi

if [ -z "${PYTHON_BIN}" ]; then
  echo "python3 не найден. Установите Python 3.12+ и повторите."
  echo "macOS: brew install python@3.12"
  exit 1
fi

PY_VER="$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
PY_MAJOR="${PY_VER%%.*}"
PY_MINOR="${PY_VER##*.}"
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 12 ]; }; then
  echo "Нужен Python 3.12+, найден $PY_VER."
  echo "macOS: brew install python@3.12"
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
else
  "$PYTHON_BIN" -m venv --upgrade .venv
fi

.venv/bin/python -m pip install -r requirements.txt || {
  echo "Не удалось установить зависимости. Проверьте интернет/SSL."
  exit 1
}
echo "Готово. Запуск: bash run_web.sh"
