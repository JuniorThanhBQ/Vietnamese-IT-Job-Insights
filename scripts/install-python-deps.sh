#!/bin/bash
set -euo pipefail

python -m pip install --upgrade pip

if [ -f "requirements-dev.txt" ]; then
  pip install -r requirements-dev.txt
elif [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

if [ -f "pyproject.toml" ]; then
  pip install .[dev] 2>/dev/null || pip install . 2>/dev/null || true
fi

if ! command -v pylint &> /dev/null; then
  pip install pylint
fi