#!/bin/bash
set -euo pipefail

echo "Running Pylint..."
py_files=$(find backend \
  -type f \
  -name "*.py" \
  -not -path '*/\.*' \
  -not -path '*/venv/*' \
  -not -path '*/env/*' \
  -not -path '*/node_modules/*')

if [ -n "$py_files" ]; then
  echo "$py_files" | xargs pylint --output-format=text
else
  echo "No Python files found to lint."
fi