#!/usr/bin/env bash
# Smart Energy AI - one-command start for macOS and Linux.
set -e
cd "$(dirname "$0")"

PY=python3
command -v $PY >/dev/null 2>&1 || PY=python

if [ ! -d ".venv" ]; then
  echo "Creating a virtual environment..."
  $PY -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "Starting Smart Energy AI on http://127.0.0.1:${PORT:-5000}"
exec python run.py
