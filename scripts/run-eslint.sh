#!/bin/bash
set -euo pipefail

echo "Running ESLint..."

if jq -e '.scripts.lint' package.json > /dev/null 2>&1; then
  echo "Found lint script in package.json. Executing..."
  $RUNNER lint
else
  echo "No lint script found. Running npx eslint directly..."
  if ! npx eslint --version &> /dev/null; then
    npm install --no-save eslint
  fi

  npx eslint . --max-warnings=0
fi
