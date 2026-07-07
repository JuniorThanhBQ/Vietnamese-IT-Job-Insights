#!/bin/bash
set -euo pipefail

if [ -f "pyproject.toml" ] || [ -n "$(find . -maxdepth 1 -name 'requirements*.txt' -print -quit)" ] || [ -n "$(find . -name '*.py' -not -path '*/\.*' -not -path '*/node_modules/*' -print -quit)" ]; then
  echo "Python project detected."
  echo "detected=true" >> "$GITHUB_OUTPUT"
else
  echo "No Python source detected. Skipping Pylint."
  echo "detected=false" >> "$GITHUB_OUTPUT"
fi